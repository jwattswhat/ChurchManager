"""Encrypt restricted pastoral notes and protect their recovery key.

This module contains no database or user-interface behavior.  Callers must
authorize access before invoking it and must supply record-specific associated
data so ciphertext cannot be moved between congregations or care records.
"""

from __future__ import annotations

import base64
import json
import secrets
import shutil
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

from argon2.low_level import Type, hash_secret_raw
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


ALGORITHM = "AES-256-GCM"
KEY_BYTES = 32
NONCE_BYTES = 12
TAG_BYTES = 16
RECOVERY_FORMAT = "ChurchManager-Pastoral-Key-Recovery"
RECOVERY_FORMAT_VERSION = 1
ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST_KIB = 65536
ARGON2_PARALLELISM = 1
MINIMUM_RECOVERY_PASSWORD_LENGTH = 12


class PastoralNoteCryptoError(RuntimeError):
    """Raised when pastoral-note encryption or recovery cannot be completed."""


class _MemoryCredentialStore:
    """Hold a validated recovery key only for the current restore operation."""

    def __init__(self):
        self.values = {}

    def exists(self, target):
        return target in self.values

    def read(self, target):
        return self.values[target]

    def write(self, target, username, password):
        self.values[target] = (username, password)


@dataclass(frozen=True)
class EncryptedPastoralNote:
    """Database-safe encrypted representation of one restricted note."""

    algorithm: str
    key_version: int
    nonce: str
    ciphertext: str
    authentication_tag: str


def pastoral_note_binding(church_id, note_id, care_need_id, care_action_id=None):
    """Return canonical authenticated context for one pastoral note record."""

    values = {
        "care_action_id": _positive_optional(care_action_id, "care action ID"),
        "care_need_id": _positive(care_need_id, "care need ID"),
        "church_id": _positive(church_id, "church ID"),
        "note_id": _positive(note_id, "note ID"),
        "purpose": "ChurchManager restricted pastoral note",
    }
    return _canonical_json(values)


class PastoralNoteCipher:
    """Encrypt and decrypt restricted notes using an injected key provider."""

    def __init__(self, key_provider):
        self.key_provider = key_provider

    def encrypt(self, plaintext, binding, key_version=1):
        """Encrypt non-empty UTF-8 text and return database-safe fields."""

        if not isinstance(plaintext, str) or not plaintext.strip():
            raise ValueError("Restricted pastoral note text is required.")
        associated_data = _binding_bytes(binding)
        key = self.key_provider.load_key(key_version)
        nonce = secrets.token_bytes(NONCE_BYTES)
        sealed = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), associated_data)
        ciphertext, tag = sealed[:-TAG_BYTES], sealed[-TAG_BYTES:]
        return EncryptedPastoralNote(
            algorithm=ALGORITHM,
            key_version=int(key_version),
            nonce=_encode(nonce),
            ciphertext=_encode(ciphertext),
            authentication_tag=_encode(tag),
        )

    def decrypt(self, encrypted, binding):
        """Authenticate and decrypt one note or fail without returning content."""

        if isinstance(encrypted, dict):
            encrypted = EncryptedPastoralNote(**encrypted)
        if encrypted.algorithm != ALGORITHM:
            raise PastoralNoteCryptoError("The restricted note uses an unsupported encryption algorithm.")
        try:
            nonce = _decode(encrypted.nonce)
            ciphertext = _decode(encrypted.ciphertext)
            tag = _decode(encrypted.authentication_tag)
        except (TypeError, ValueError) as error:
            raise PastoralNoteCryptoError("The restricted note is not valid encrypted data.") from error
        if len(nonce) != NONCE_BYTES or len(tag) != TAG_BYTES:
            raise PastoralNoteCryptoError("The restricted note is not valid encrypted data.")
        key = self.key_provider.load_key(encrypted.key_version)
        try:
            plaintext = AESGCM(key).decrypt(
                nonce, ciphertext + tag, _binding_bytes(binding)
            )
            return plaintext.decode("utf-8")
        except (InvalidTag, UnicodeDecodeError) as error:
            raise PastoralNoteCryptoError(
                "The restricted note could not be authenticated or decrypted."
            ) from error


class PastoralKeyManager:
    """Manage versioned note keys in a protected operating-system store."""

    def __init__(self, credential_store, target):
        self.credential_store = credential_store
        self.target = str(target or "").strip()
        if not self.target:
            raise ValueError("A pastoral-note credential target is required.")

    def provision(self, key_version=1):
        """Create and store a new random key, refusing to replace an existing key."""

        key_version = _positive(key_version, "key version")
        target = self._version_target(key_version)
        if self.credential_store.exists(target):
            raise PastoralNoteCryptoError("A pastoral-note encryption key already exists.")
        key = secrets.token_bytes(KEY_BYTES)
        self._store_key(key_version, key)
        return key_version

    def has_key(self, key_version=1):
        """Return whether protected storage contains the requested key version."""

        return self.credential_store.exists(
            self._version_target(_positive(key_version, "key version"))
        )

    def _store_key(self, key_version, key):
        self.credential_store.write(
            self._version_target(key_version), self._key_label(key_version), _encode(key)
        )

    def _version_target(self, key_version):
        return "{}/Key/v{}".format(self.target.rstrip("/"), int(key_version))

    @staticmethod
    def _key_label(key_version):
        return "{}:v{}".format(ALGORITHM, int(key_version))

    @staticmethod
    def _validate_header(header):
        expected = {
            "format": RECOVERY_FORMAT,
            "format_version": RECOVERY_FORMAT_VERSION,
            "kdf": "Argon2id",
            "memory_cost_kib": ARGON2_MEMORY_COST_KIB,
            "parallelism": ARGON2_PARALLELISM,
            "time_cost": ARGON2_TIME_COST,
        }
        if any(header.get(name) != value for name, value in expected.items()):
            raise PastoralNoteCryptoError("The pastoral-note recovery package is unsupported.")

    def load_key(self, key_version=1):
        """Return one validated key or fail closed when it is unavailable."""

        key_version = _positive(key_version, "key version")
        try:
            username, encoded = self.credential_store.read(
                self._version_target(key_version)
            )
            key = _decode(encoded)
        except (KeyError, TypeError, ValueError) as error:
            raise PastoralNoteCryptoError(
                "The restricted-note encryption key is unavailable."
            ) from error
        if username != self._key_label(key_version) or len(key) != KEY_BYTES:
            raise PastoralNoteCryptoError("The restricted-note encryption key is invalid.")
        return key

    def create_recovery_package(self, recovery_password, key_version=1):
        """Return a password-protected portable package for one stored key."""

        password = _recovery_password(recovery_password)
        key_version = _positive(key_version, "key version")
        data_key = self.load_key(key_version)
        salt = secrets.token_bytes(16)
        wrapping_key = _derive_recovery_key(password, salt)
        nonce = secrets.token_bytes(NONCE_BYTES)
        header = {
            "format": RECOVERY_FORMAT,
            "format_version": RECOVERY_FORMAT_VERSION,
            "key_version": key_version,
            "kdf": "Argon2id",
            "memory_cost_kib": ARGON2_MEMORY_COST_KIB,
            "parallelism": ARGON2_PARALLELISM,
            "salt": _encode(salt),
            "time_cost": ARGON2_TIME_COST,
        }
        associated_data = _canonical_json(header)
        sealed = AESGCM(wrapping_key).encrypt(nonce, data_key, associated_data)
        package = dict(header)
        package.update({"nonce": _encode(nonce), "sealed_key": _encode(sealed)})
        return json.dumps(package, indent=2, sort_keys=True).encode("utf-8")

    def restore_recovery_package(self, package, recovery_password, replace=False):
        """Validate a recovery package and install its key into protected storage."""

        password = _recovery_password(recovery_password)
        try:
            values = json.loads(bytes(package).decode("utf-8"))
            header = {
                "format": values["format"],
                "format_version": values["format_version"],
                "key_version": values["key_version"],
                "kdf": values["kdf"],
                "memory_cost_kib": values["memory_cost_kib"],
                "parallelism": values["parallelism"],
                "salt": values["salt"],
                "time_cost": values["time_cost"],
            }
            self._validate_header(header)
            salt = _decode(header["salt"])
            nonce = _decode(values["nonce"])
            sealed_key = _decode(values["sealed_key"])
        except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise PastoralNoteCryptoError("The pastoral-note recovery package is invalid.") from error
        if len(salt) != 16 or len(nonce) != NONCE_BYTES:
            raise PastoralNoteCryptoError("The pastoral-note recovery package is invalid.")
        wrapping_key = _derive_recovery_key(password, salt)
        try:
            key = AESGCM(wrapping_key).decrypt(
                nonce, sealed_key, _canonical_json(header)
            )
        except InvalidTag as error:
            raise PastoralNoteCryptoError(
                "The recovery password or pastoral-note recovery package is invalid."
            ) from error
        if len(key) != KEY_BYTES:
            raise PastoralNoteCryptoError("The pastoral-note recovery package is invalid.")
        key_version = _positive(header["key_version"], "key version")
        target = self._version_target(key_version)
        if self.credential_store.exists(target) and not replace:
            existing = self.load_key(key_version)
            if not secrets.compare_digest(existing, key):
                raise PastoralNoteCryptoError(
                    "A different pastoral-note encryption key already exists."
                )
            return key_version
        self._store_key(key_version, key)
        return key_version


@dataclass(frozen=True)
class ValidatedPastoralRecovery:
    """Opaque validated package retained only until database restore completes."""

    package: bytes
    password: str = field(repr=False)
    key_version: int


class PastoralRecoveryBackup:
    """Maintain the protected recovery sidecar paired with SQL backups."""

    SUFFIX = ".PastoralRecovery.json"

    def __init__(self, key_manager, protected_package_path):
        self.key_manager = key_manager
        self.protected_package_path = Path(protected_package_path)

    @classmethod
    def sidecar_path(cls, database_backup):
        """Return the recovery sidecar name belonging to one SQL backup."""

        database_backup = Path(database_backup)
        return database_backup.with_name(database_backup.name + cls.SUFFIX)

    def create_protected_package(self, recovery_password, key_version=1):
        """Create or refresh the reusable encrypted package atomically."""

        package = self.key_manager.create_recovery_package(
            recovery_password, key_version
        )
        self._write_protected_package(package)
        return self.protected_package_path

    def _write_protected_package(self, package):
        self.protected_package_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", suffix=".tmp", dir=self.protected_package_path.parent,
                delete=False,
            ) as stream:
                stream.write(package)
                temporary = Path(stream.name)
            temporary.replace(self.protected_package_path)
        finally:
            if temporary:
                temporary.unlink(missing_ok=True)

    def attach_to_backup(self, database_backup):
        """Copy the encrypted package beside a completed SQL backup."""

        if not self.protected_package_path.is_file():
            return None
        destination = self.sidecar_path(database_backup)
        shutil.copyfile(self.protected_package_path, destination)
        return destination

    def validate_restore(self, database_backup, recovery_password):
        """Authenticate a backup sidecar without changing the active key."""

        sidecar = self.sidecar_path(database_backup)
        if not sidecar.is_file():
            return None
        package = sidecar.read_bytes()
        temporary = PastoralKeyManager(
            _MemoryCredentialStore(), self.key_manager.target
        )
        key_version = temporary.restore_recovery_package(package, recovery_password)
        return ValidatedPastoralRecovery(package, recovery_password, key_version)

    def complete_restore(self, validated):
        """Install the already validated key after SQL restore succeeds."""

        if not isinstance(validated, ValidatedPastoralRecovery):
            raise PastoralNoteCryptoError("Pastoral-note recovery was not validated.")
        key_version = self.key_manager.restore_recovery_package(
            validated.package, validated.password, replace=True
        )
        self._write_protected_package(validated.package)
        return key_version

def encrypted_note_values(encrypted):
    """Return the serializable fields of an encrypted note dataclass."""

    return asdict(encrypted)


def _derive_recovery_key(password, salt):
    return hash_secret_raw(
        secret=password.encode("utf-8"), salt=salt,
        time_cost=ARGON2_TIME_COST, memory_cost=ARGON2_MEMORY_COST_KIB,
        parallelism=ARGON2_PARALLELISM, hash_len=KEY_BYTES, type=Type.ID,
    )


def _recovery_password(value):
    if not isinstance(value, str) or len(value) < MINIMUM_RECOVERY_PASSWORD_LENGTH:
        raise ValueError(
            "The recovery password must contain at least {} characters.".format(
                MINIMUM_RECOVERY_PASSWORD_LENGTH
            )
        )
    return value


def _positive(value, label):
    try:
        number = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError("{} must be a positive integer.".format(label.capitalize())) from error
    if number <= 0:
        raise ValueError("{} must be a positive integer.".format(label.capitalize()))
    return number


def _positive_optional(value, label):
    return None if value in (None, "") else _positive(value, label)


def _binding_bytes(binding):
    if not isinstance(binding, (bytes, bytearray)) or not binding:
        raise ValueError("Authenticated pastoral-note record binding is required.")
    return bytes(binding)


def _canonical_json(values):
    return json.dumps(values, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _encode(value):
    return base64.b64encode(value).decode("ascii")


def _decode(value):
    return base64.b64decode(str(value).encode("ascii"), validate=True)
