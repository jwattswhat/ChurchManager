from pathlib import Path
import unittest

class BudgetEditorTests(unittest.TestCase):
    def test_editor_supports_account_only_and_detailed_modes(self):
        source=(Path(__file__).parents[1]/"accounting"/"budget_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn('choices=["Account Only","Detailed"]',source)
        self.assertIn('"General account"',source)
        self.assertIn('"Detailed line item"',source)
        self.assertIn("wx.EVT_LIST_ITEM_ACTIVATED,self.on_edit",source)
        self.assertIn('label="Propose"',source)
        self.assertIn('label="Solo Adopt"',source)
        self.assertIn("accounting.budgets.adopt",source)

    def test_service_locks_adopted_budget_and_audits_override(self):
        source=(Path(__file__).parents[1]/"accounting"/"budget_service.py").read_text(encoding="utf-8-sig")
        self.assertIn("Only a draft budget can be edited",source)
        self.assertIn("BUDGET_PROPOSED",source)
        self.assertIn("BUDGET_ADOPTED_OVERRIDE",source)
        self.assertIn("Status='SUPERSEDED'",source)
    def test_budget_menu_has_manage_permission(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertIn("lblAccountingBudgets",SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingBudgets"],"accounting.budgets.manage")

if __name__=="__main__":unittest.main()
