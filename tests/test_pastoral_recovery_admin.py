"""Tests for authorized pastoral-note recovery setup and safe audit events."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from pastoral_note_crypto import PastoralKeyManager, PastoralRecoveryBackup
from pastoral_recovery_admin import PastoralRecoveryAdministration


class MemoryCredentialStore:
    def __init__(self):
        self.values = {}

    def exists(self, target):
        return target in self.values

    def write(self, target, username, secret):
        self.values[target] = (username, secret)

    def read(self, target):
        return self.values[target]


class RecordingCursor:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, sql, values):
        self.connection.executed.append((sql, values))

    def close(self):
        pass


class RecordingConnection:
    def __init__(self):
        self.executed = []
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return RecordingCursor(self)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class AuthorizationStub:
    def __init__(self, allowed=True):
        self.allowed = allowed

    def require(self, permission, operation):
        if not self.allowed:
            raise PermissionError(operation)


class PastoralRecoveryAdministrationTests(unittest.TestCase):
    def service(self, root, allowed=True):
        recovery = PastoralRecoveryBackup(
            PastoralKeyManager(
                MemoryCredentialStore(), "ChurchManager/Test/PastoralNotes"
            ),
            Path(root) / "pastoral-recovery.json",
        )
        connection = RecordingConnection()
        service = PastoralRecoveryAdministration(
            connection,
            SimpleNamespace(user_id=7, workstation="TEST-PC"),
            AuthorizationStub(allowed),
            recovery,
        )
        return service, connection

    def test_setup_provisions_key_creates_package_and_audits_without_password(self):
        with tempfile.TemporaryDirectory() as root:
            service, connection = self.service(root)
            password = "correct horse battery staple"
            path = service.configure(password)
            self.assertTrue(service.configured)
            self.assertTrue(path.is_file())
            sql, values = connection.executed[0]
            self.assertIn("tblSecurityAuditEvent", sql)
            self.assertEqual(values[1], "PASTORAL_RECOVERY_CONFIGURED")
            self.assertNotIn(password, repr(connection.executed))
            self.assertEqual(connection.commits, 1)

    def test_replacing_password_keeps_key_and_records_distinct_event(self):
        with tempfile.TemporaryDirectory() as root:
            service, connection = self.service(root)
            service.configure("correct horse battery staple")
            key = service.recovery.key_manager.load_key()
            service.configure("a different secure recovery phrase")
            self.assertEqual(service.recovery.key_manager.load_key(), key)
            self.assertEqual(
                connection.executed[-1][1][1],
                "PASTORAL_RECOVERY_PASSWORD_REPLACED",
            )

    def test_permission_is_required_before_key_or_file_is_created(self):
        with tempfile.TemporaryDirectory() as root:
            service, connection = self.service(root, allowed=False)
            with self.assertRaises(PermissionError):
                service.configure("correct horse battery staple")
            self.assertFalse(service.recovery.key_manager.has_key())
            self.assertFalse(service.recovery.protected_package_path.exists())
            self.assertEqual(connection.executed, [])


if __name__ == "__main__":
    unittest.main()
