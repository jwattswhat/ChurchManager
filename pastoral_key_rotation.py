"""Fail-closed rotation of restricted pastoral-note encryption keys."""

from __future__ import annotations

import base64
from dataclasses import dataclass

from pastoral_note_crypto import (
    ALGORITHM,
    EncryptedPastoralNote,
    PastoralNoteCryptoError,
    pastoral_note_binding,
)
from pastoral_restricted_notes import _encrypted_values


class PastoralKeyRotationError(RuntimeError):
    """Raised when rotation or its recovery verification cannot complete."""


@dataclass(frozen=True)
class PastoralKeyRotationResult:
    """Describe one completed and recovery-verified rotation."""

    previous_version: int
    active_version: int
    notes_rotated: int
    pre_rotation_backup: object
    verification_backup: object


class PastoralKeyRotationService:
    """Coordinate authorized rotation with matched before/after backups."""

    PERMISSION = "pastoral.care.admin"

    def __init__(self, repository, key_manager, cipher, recovery, session,
                 authorization, pre_rotation_backup, verification_backup):
        self.repository = repository
        self.key_manager = key_manager
        self.cipher = cipher
        self.recovery = recovery
        self.session = session
        self.authorization = authorization
        self.pre_rotation_backup = pre_rotation_backup
        self.verification_backup = verification_backup

    def rotate(self, recovery_password):
        """Rotate all current ciphertext and prove both recovery checkpoints."""

        self.authorization.require(self.PERMISSION, "rotate pastoral-note encryption")
        previous = self.repository.active_version()
        package_version = self.recovery.validate_protected_package(recovery_password)
        if package_version != previous:
            raise PastoralKeyRotationError(
                "The pastoral recovery package does not match the active key."
            )
        before = self._verified_backup(
            self.pre_rotation_backup, recovery_password, previous,
            "pre-rotation backup",
        )
        next_version = previous + 1
        while self.key_manager.has_key(next_version):
            next_version += 1
        self.key_manager.provision(next_version)

        def transform(metadata, encrypted):
            binding = pastoral_note_binding(
                metadata["church_id"], metadata["id"],
                metadata["care_need_id"], metadata["care_action_id"],
            )
            plaintext = self.cipher.decrypt(encrypted, binding)
            try:
                return self.cipher.encrypt(
                    plaintext, binding, key_version=next_version
                )
            finally:
                plaintext = None

        count = self.repository.rotate(
            previous, next_version, transform, self.session.user_id,
            self.session.workstation,
        )
        try:
            self.recovery.create_protected_package(
                recovery_password, key_version=next_version
            )
            after = self._verified_backup(
                self.verification_backup, recovery_password, next_version,
                "post-rotation verification backup",
            )
            self.repository.mark_recovery_verified(
                next_version, self.session.user_id, self.session.workstation
            )
        except Exception as error:
            raise PastoralKeyRotationError(
                "The key was rotated, but recovery verification failed. "
                "Restricted-note editing remains disabled."
            ) from error
        return PastoralKeyRotationResult(previous, next_version, count, before, after)

    def _verified_backup(self, callback, password, expected_version, label):
        result = callback()
        path = getattr(result, "path", result)
        validated = self.recovery.validate_restore(path, password)
        if validated is None or validated.key_version != expected_version:
            raise PastoralKeyRotationError(
                "The {} does not contain matching pastoral recovery data.".format(label)
            )
        return result


class MariaDBPastoralKeyRotationRepository:
    """Atomically rewrite current note rows and switch the active key version."""

    def __init__(self, connection):
        self.connection = connection
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def active_version(self):
        """Return the authoritative active version without reading note content."""

        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT ActiveKeyVersion FROM tblPastoralEncryptionState WHERE ID=1",
            )
            row = cursor.fetchone()
            if not row or int(row[0]) <= 0:
                raise PastoralKeyRotationError(
                    "Pastoral-note encryption is not configured."
                )
            return int(row[0])
        finally:
            cursor.close()

    def rotate(self, expected_version, next_version, transform, user_id, workstation):
        """Rewrite every row and active state in one database transaction."""

        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT ActiveKeyVersion FROM tblPastoralEncryptionState "
                "WHERE ID=1 FOR UPDATE",
            )
            row = cursor.fetchone()
            if not row or int(row[0]) != int(expected_version):
                raise PastoralKeyRotationError(
                    "The active pastoral-note key changed before rotation began."
                )
            self._execute(
                cursor,
                "SELECT ID,ChurchID,CareNeedID,CareActionID,Algorithm,KeyVersion,"
                "Nonce,Ciphertext,AuthenticationTag FROM tblPastoralRestrictedNote "
                "ORDER BY ID FOR UPDATE",
            )
            rows = cursor.fetchall()
            for row in rows:
                metadata = {
                    "id": row[0], "church_id": row[1], "care_need_id": row[2],
                    "care_action_id": row[3],
                }
                if row[4] != ALGORITHM:
                    raise PastoralNoteCryptoError(
                        "A restricted note uses an unsupported encryption algorithm."
                    )
                encrypted = EncryptedPastoralNote(
                    algorithm=row[4], key_version=row[5],
                    nonce=_encode(row[6]), ciphertext=_encode(row[7]),
                    authentication_tag=_encode(row[8]),
                )
                replacement = transform(metadata, encrypted)
                values = _encrypted_values(replacement)
                self._execute(
                    cursor,
                    "UPDATE tblPastoralRestrictedNote SET Ciphertext=?,Nonce=?,"
                    "AuthenticationTag=?,Algorithm=?,KeyVersion=?,Version=Version+1 "
                    "WHERE ID=? AND KeyVersion=?",
                    (*values, row[0], row[5]),
                )
                if cursor.rowcount != 1:
                    raise PastoralKeyRotationError(
                        "A restricted note changed during key rotation."
                    )
            self._execute(
                cursor,
                "UPDATE tblPastoralEncryptionState SET ActiveKeyVersion=?,"
                "RecoveryVerified=0 WHERE ID=1 AND ActiveKeyVersion=?",
                (next_version, expected_version),
            )
            if cursor.rowcount != 1:
                raise PastoralKeyRotationError(
                    "The active pastoral-note key changed during rotation."
                )
            self._audit(
                cursor, user_id, "PASTORAL_KEY_ROTATED",
                "v{}-to-v{}".format(expected_version, next_version), workstation,
            )
            self.connection.commit()
            return len(rows)
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def mark_recovery_verified(self, key_version, user_id, workstation):
        """Enable the active version only after its recovery backup was verified."""

        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "UPDATE tblPastoralEncryptionState SET RecoveryVerified=1 "
                "WHERE ID=1 AND ActiveKeyVersion=?",
                (key_version,),
            )
            if cursor.rowcount != 1:
                raise PastoralKeyRotationError(
                    "The rotated key could not be marked recovery-verified."
                )
            self._audit(
                cursor, user_id, "PASTORAL_KEY_RECOVERY_VERIFIED",
                "v{}".format(key_version), workstation,
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def _audit(self, cursor, user_id, action, entity_id, workstation):
        self._execute(
            cursor,
            "INSERT INTO tblSecurityAuditEvent "
            "(UserID,Action,EntityType,EntityID,Workstation) VALUES "
            "(?,?,'PastoralEncryptionKey',?,?)",
            (user_id, action, entity_id, workstation),
        )


def _encode(value):
    return base64.b64encode(bytes(value)).decode("ascii")
