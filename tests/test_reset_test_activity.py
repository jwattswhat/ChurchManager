"""Contract tests for the guarded ChurchDBTest activity reset."""

from pathlib import Path
import unittest

import reset_test_activity as reset


class ResetTestActivityTests(unittest.TestCase):
    def test_reset_is_exactly_local_churchdbtest_and_preview_first(self):
        source = Path(reset.__file__).read_text(encoding="utf-8")
        self.assertIn('!= "churchdbtest"', source)
        self.assertIn("LOCAL_HOSTS", source)
        self.assertIn("read_credential", source)
        self.assertIn("getpass", source)
        self.assertIn('parser.add_argument("--apply"', source)
        self.assertIn("No changes made", source)

    def test_reset_creates_and_verifies_backup_before_deletion(self):
        source = Path(reset.__file__).read_text(encoding="utf-8")
        self.assertLess(source.index("create_backup(resolved)"), source.index("reset_activity(cursor)"))
        self.assertIn("sha256", source)
        self.assertIn("ChurchDBTest.pre-activity-reset", source)

    def test_reset_preserves_configuration_and_catalogs(self):
        source = Path(reset.__file__).read_text(encoding="utf-8")
        for table in (
            "tblChurch", "tblPerson", "tblFamily", "tblUser", "tblRole",
            "tblHymnal", "tblHymn", "tblLectionaryPackage", "tblBulletinOrderTemplate",
            "tblAccountingAccount", "tblAccountingFund",
        ):
            self.assertNotIn(f'DELETE FROM {table}"', source)

    def test_reset_covers_worship_and_accounting_activity(self):
        source = Path(reset.__file__).read_text(encoding="utf-8")
        for table in (
            "tblService", "tblServiceChecklistItem", "tblServiceReadingSnapshot",
            "tblHymnUsage", "tblAccountingReconciliationItem",
            "tblAccountingBankImportRow", "tblAccountingBudgetLine",
            "tblAccountingTransactionLine", "tblAccountingAuditEvent",
        ):
            self.assertIn(table, source)


if __name__ == "__main__":
    unittest.main()
