from decimal import Decimal
from pathlib import Path
import unittest
from accounting.budget_actual_service import variance,percent

class BudgetActualTests(unittest.TestCase):
    def test_variance_and_percentage(self):
        self.assertEqual(variance(Decimal("100"),Decimal("75")),Decimal("25"))
        self.assertEqual(percent(Decimal("75"),Decimal("100")),Decimal("75.0"))
        self.assertIsNone(percent(Decimal("0"),Decimal("0")))
    def test_report_exposes_account_summary_and_optional_detail(self):
        source=(Path(__file__).parents[1]/"accounting"/"budget_actual_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn("General account",source);self.assertIn("Detailed line item",source)
        self.assertIn("actuals remain at the general-account level",source)
        self.assertIn("wx.LIST_FORMAT_RIGHT",source)
    def test_menu_is_report_protected(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertIn("lblAccountingBudgetActual",SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingBudgetActual"],"accounting.reports.run")
if __name__=="__main__":unittest.main()
