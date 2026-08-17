import tempfile
import unittest
from pathlib import Path

from backup_service import BackupError, BackupResult
from installation_backup import InitialBackupVerifier


class Service:
    def __init__(self, body):
        self.body = body

    def create_in_folder(self, settings, _tools, folder, automatic=False):
        self.path = Path(folder) / "Manual.Test.Backup.SQL"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(self.body)
        return BackupResult(self.path, "now")

    @staticmethod
    def inspect_dump(_path):
        return "ChurchManager"


class InstallationBackupTests(unittest.TestCase):
    def settings(self):
        return {
            "database": "ChurchManager", "server": "127.0.0.1",
            "user": "cm_churchmanager", "password": "secret",
        }

    def test_verifies_nonempty_labeled_schema_dump(self):
        with tempfile.TemporaryDirectory() as folder:
            body = b"-- ChurchManager database backup\nCREATE TABLE tblChurch (ID int);\n" + b" " * 1200
            proof = InitialBackupVerifier(Service(body)).create(
                self.settings(), folder, folder,
            )
            self.assertGreater(proof.size_bytes, 1024)
            self.assertEqual(len(proof.sha256), 64)
            self.assertTrue(proof.path.exists())

    def test_rejects_and_removes_incomplete_dump(self):
        with tempfile.TemporaryDirectory() as folder:
            service = Service(b"not a useful dump")
            with self.assertRaisesRegex(BackupError, "small"):
                InitialBackupVerifier(service).create(self.settings(), folder, folder)
            self.assertFalse(service.path.exists())


if __name__ == "__main__":
    unittest.main()
