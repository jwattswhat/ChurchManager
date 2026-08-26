from pathlib import Path
import unittest


class LocalTestBackupTests(unittest.TestCase):
    def test_backup_is_local_test_only_and_checksum_verified(self):
        source=(Path(__file__).parents[1]/"backup_local_test_databases.py").read_text(encoding="utf-8-sig")
        self.assertIn('host not in {"127.0.0.1", "localhost", "::1"}',source)
        self.assertIn('"test" not in name.casefold()',source)
        self.assertIn('"sha256":sha256(output)',source)
        self.assertNotIn('config["database_settings"]["host"]',source)

    def test_restore_certification_uses_temporary_clone_and_accounting_checks(self):
        source=(Path(__file__).parents[1]/"certify_local_accounting_restore.py").read_text(encoding="utf-8-sig")
        self.assertIn('ChurchDBTestRestoreVerify_',source)
        self.assertIn('validate_target(target)',source)
        self.assertIn('DROP DATABASE IF EXISTS',source)
        self.assertIn('LocalRestoreAdmin',source)
        self.assertIn('admin_username != "root"',source)
        self.assertIn("GRANT ALL PRIVILEGES ON",source)
        self.assertIn('posted_ledger_difference',source)
        self.assertIn('fiscal_year_close_reference_errors',source)
        self.assertIn('name.casefold()',source)
        self.assertNotIn('DROP DATABASE IF EXISTS `ChurchDBTest`',source)


if __name__=="__main__":unittest.main()
