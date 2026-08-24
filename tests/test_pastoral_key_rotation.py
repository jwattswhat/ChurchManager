"""Acceptance-oriented tests for fail-closed pastoral key rotation."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from pastoral_key_rotation import (
    PastoralKeyRotationError,
    PastoralKeyRotationService,
)
from pastoral_note_crypto import (
    PastoralKeyManager,
    PastoralNoteCipher,
    PastoralRecoveryBackup,
    pastoral_note_binding,
)


class MemoryCredentialStore:
    def __init__(self):
        self.values = {}

    def exists(self, target):
        return target in self.values

    def write(self, target, username, secret):
        self.values[target] = (username, secret)

    def read(self, target):
        if target not in self.values:
            raise KeyError(target)
        return self.values[target]


class AuthorizationStub:
    def __init__(self, allowed=True):
        self.allowed = allowed

    def require(self, permission, operation):
        if not self.allowed:
            raise PermissionError(operation)


class AtomicRepositoryStub:
    def __init__(self, active_version, notes):
        self.active = active_version
        self.notes = list(notes)
        self.verified = False

    def active_version(self):
        return self.active

    def rotate(self, expected, replacement, transform, _user, _workstation):
        if self.active != expected:
            raise PastoralKeyRotationError("active changed")
        staged = []
        for metadata, encrypted in self.notes:
            staged.append((metadata, transform(metadata, encrypted)))
        self.notes = staged
        self.active = replacement
        self.verified = False
        return len(staged)

    def mark_recovery_verified(self, version, _user, _workstation):
        if self.active != version:
            raise PastoralKeyRotationError("active changed")
        self.verified = True


class PastoralKeyRotationTests(unittest.TestCase):
    password = "correct horse battery staple"

    def build(self, root, encrypted, allowed=True):
        store = MemoryCredentialStore()
        keys = PastoralKeyManager(store, "ChurchManager/Test/PastoralNotes")
        keys.provision(1)
        cipher = PastoralNoteCipher(keys)
        metadata = {"id": 40, "church_id": 1, "care_need_id": 12,
                    "care_action_id": 23}
        if encrypted is None:
            encrypted = cipher.encrypt(
                "Hospital visit completed.",
                pastoral_note_binding(1, 40, 12, 23),
            )
        repository = AtomicRepositoryStub(1, [(metadata, encrypted)])
        recovery = PastoralRecoveryBackup(keys, Path(root) / "recovery.json")
        recovery.create_protected_package(self.password)
        backups = []

        def backup():
            path = Path(root) / "backup-{}.sql".format(len(backups) + 1)
            path.write_text("-- test backup", encoding="utf-8")
            recovery.attach_to_backup(path)
            result = SimpleNamespace(path=path)
            backups.append(result)
            return result

        service = PastoralKeyRotationService(
            repository, keys, cipher, recovery,
            SimpleNamespace(user_id=7, workstation="TEST-PC"),
            AuthorizationStub(allowed), backup, backup,
        )
        return service, repository, keys, cipher, recovery, backups

    def test_rotation_reencrypts_notes_and_verifies_matched_backups(self):
        with tempfile.TemporaryDirectory() as root:
            service, repository, keys, cipher, recovery, backups = self.build(root, None)
            result = service.rotate(self.password)
            self.assertEqual((result.previous_version, result.active_version), (1, 2))
            self.assertEqual(result.notes_rotated, 1)
            self.assertEqual(repository.active, 2)
            self.assertTrue(repository.verified)
            self.assertTrue(keys.has_key(1))
            self.assertTrue(keys.has_key(2))
            self.assertEqual(len(backups), 2)
            self.assertEqual(
                recovery.validate_restore(backups[0].path, self.password).key_version, 1
            )
            self.assertEqual(
                recovery.validate_restore(backups[1].path, self.password).key_version, 2
            )
            metadata, encrypted = repository.notes[0]
            self.assertEqual(encrypted.key_version, 2)
            self.assertEqual(
                cipher.decrypt(
                    encrypted,
                    pastoral_note_binding(1, metadata["id"], 12, 23),
                ),
                "Hospital visit completed.",
            )

    def test_wrong_password_changes_nothing_and_creates_no_backup(self):
        with tempfile.TemporaryDirectory() as root:
            service, repository, keys, _cipher, _recovery, backups = self.build(root, None)
            with self.assertRaises(Exception):
                service.rotate("this password is not correct")
            self.assertEqual(repository.active, 1)
            self.assertFalse(keys.has_key(2))
            self.assertEqual(backups, [])

    def test_ciphertext_failure_does_not_switch_active_version(self):
        with tempfile.TemporaryDirectory() as root:
            service, repository, keys, cipher, _recovery, backups = self.build(root, None)
            metadata, encrypted = repository.notes[0]
            repository.notes[0] = (metadata, encrypted.__class__(
                encrypted.algorithm, encrypted.key_version, encrypted.nonce,
                encrypted.ciphertext, "AAAAAAAAAAAAAAAAAAAAAA==",
            ))
            with self.assertRaises(Exception):
                service.rotate(self.password)
            self.assertEqual(repository.active, 1)
            self.assertFalse(repository.verified)
            self.assertTrue(keys.has_key(2))
            self.assertEqual(len(backups), 1)

    def test_permission_is_required_before_recovery_or_backup_access(self):
        with tempfile.TemporaryDirectory() as root:
            service, repository, keys, _cipher, _recovery, backups = self.build(
                root, None, allowed=False
            )
            with self.assertRaises(PermissionError):
                service.rotate(self.password)
            self.assertEqual(repository.active, 1)
            self.assertFalse(keys.has_key(2))
            self.assertEqual(backups, [])


class PastoralKeyRotationRepositoryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (
            Path(__file__).resolve().parents[1] / "pastoral_key_rotation.py"
        ).read_text(encoding="utf-8")

    def test_database_rows_and_state_are_locked_and_atomic(self):
        self.assertGreaterEqual(self.source.count("FOR UPDATE"), 2)
        self.assertIn("RecoveryVerified=0", self.source)
        self.assertIn("RecoveryVerified=1", self.source)
        self.assertIn("self.connection.rollback()", self.source)

    def test_audit_contract_never_contains_note_content(self):
        audit = self.source.split("def _audit", 1)[1]
        self.assertNotIn("plaintext", audit)
        self.assertNotIn("Ciphertext", audit)


if __name__ == "__main__":
    unittest.main()
