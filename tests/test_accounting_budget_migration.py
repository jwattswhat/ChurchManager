from pathlib import Path
import unittest


class BudgetMigrationTests(unittest.TestCase):
    def setUp(self):
        self.source=(Path(__file__).parents[1]/"migrations"/"013_add_accounting_budgets.sql").read_text(encoding="utf-8-sig")

    def test_budget_header_has_versioned_locked_status_lifecycle(self):
        for value in ("DRAFT","PROPOSED","ADOPTED","SUPERSEDED"):
            self.assertIn(value,self.source)
        self.assertIn("VersionNumber",self.source)
        self.assertIn("BasedOnBudgetID",self.source)

    def test_detail_line_has_general_account_and_descriptive_line_item(self):
        self.assertIn("AccountID int NOT NULL",self.source)
        self.assertIn("LineItemName varchar(255) NULL",self.source)
        self.assertIn("FiscalPeriodID int NOT NULL",self.source)
        self.assertIn("Amount decimal(19,2) NOT NULL",self.source)

    def test_budget_can_use_account_only_or_detailed_reporting(self):
        self.assertIn("DetailMode varchar(20) NOT NULL DEFAULT 'ACCOUNT_ONLY'",self.source)
        self.assertIn("'ACCOUNT_ONLY','DETAILED'",self.source)

    def test_budget_permissions_are_separate(self):
        self.assertIn("accounting.budgets.manage",self.source)
        self.assertIn("accounting.budgets.adopt",self.source)


if __name__=="__main__":unittest.main()
