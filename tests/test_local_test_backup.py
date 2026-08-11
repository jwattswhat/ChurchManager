from pathlib import Path
import unittest


class LocalTestBackupTests(unittest.TestCase):
    def test_backup_is_local_test_only_and_checksum_verified(self):
        source=(Path(__file__).parents[1]/"backup_local_test_databases.py").read_text(encoding="utf-8-sig")
        self.assertIn('host not in {"127.0.0.1", "localhost", "::1"}',source)
        self.assertIn('"test" not in name.casefold()',source)
        self.assertIn('"sha256":sha256(output)',source)
        self.assertNotIn('config["database_settings"]["host"]',source)


if __name__=="__main__":unittest.main()
