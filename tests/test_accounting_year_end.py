from pathlib import Path
import unittest


class YearEndPreviewTests(unittest.TestCase):
    def test_preview_checks_required_close_safeguards(self):
        source = (Path(__file__).parents[1] / "accounting" / "year_end_service.py").read_text(encoding="utf-8")
        self.assertIn("fiscal period(s) are not closed", source)
        self.assertIn("unposted transaction(s) remain", source)
        self.assertIn("posted ledger is out of balance", source)
        self.assertIn("no net-asset account", source)
        self.assertIn('account_type != "NET_ASSET"', source)
        self.assertIn("AccountType IN ('REVENUE','EXPENSE','TRANSFER')", source)

    def test_preview_is_registered_with_override_permission(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertIn("lblAccountingYearEnd", SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingYearEnd"], "accounting.periods.override")
        source = (Path(__file__).parents[1] / "accounting" / "year_end_dialog.py").read_text(encoding="utf-8")
        self.assertIn('title="Year-End Close Preview"', source)
        self.assertIn('authorization.require("accounting.periods.override"', source)
        self.assertIn('label="Close Fiscal Year"', source)
        self.assertIn('label="Reopen Fiscal Year"', source)

    def test_close_is_atomic_numbered_and_audited(self):
        source = (Path(__file__).parents[1] / "accounting" / "year_end_service.py").read_text(encoding="utf-8")
        self.assertIn("NextTransactionNumber", source)
        self.assertIn("'YEAR_END_CLOSE','POSTED'", source)
        self.assertIn("ClosingTransactionID", source)
        self.assertIn("FISCAL_YEAR_CLOSED_OVERRIDE", source)
        self.assertIn("generated year-end closing transaction is not balanced", source)

    def test_reopen_reverses_close_and_reopens_final_period(self):
        source = (Path(__file__).parents[1] / "accounting" / "year_end_service.py").read_text(encoding="utf-8")
        self.assertIn("FISCAL_YEAR_REOPENED_OVERRIDE", source)
        self.assertIn("YEAR_END_CLOSE_REVERSED", source)
        self.assertIn("SET Status='OPEN',ClosingTransactionID=NULL", source)
        self.assertIn("SET Status='OPEN' WHERE ID=? AND Status='CLOSED'", source)


if __name__ == "__main__":
    unittest.main()
