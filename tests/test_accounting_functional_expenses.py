from datetime import date
from decimal import Decimal
from pathlib import Path
import unittest

from accounting.functional_expense_service import FunctionalExpenseService


class Cursor:
    def __init__(self):
        self.rows = []
    def execute(self, sql, values=()):
        self.rows = [
            ("5000", "Worship supplies", 1, "Worship", Decimal("125.00")),
            ("5000", "Worship supplies", 2, "Education", Decimal("25.00")),
            ("5100", "Utilities", 0, "Unassigned", Decimal("400.00")),
        ]
    def fetchall(self):
        return self.rows
    def close(self):
        pass


class Connection:
    def cursor(self):
        return Cursor()


class FunctionalExpenseTests(unittest.TestCase):
    def test_report_builds_account_by_function_matrix(self):
        report = FunctionalExpenseService(Connection()).report(1, date(2027, 1, 1), date(2027, 1, 31))
        self.assertEqual([item[1] for item in report["functions"]], ["Worship", "Education", "Unassigned"])
        self.assertEqual(report["rows"][0][3], Decimal("150.00"))
        self.assertEqual(report["grand_total"], Decimal("550.00"))

    def test_rejects_reversed_date_range(self):
        with self.assertRaisesRegex(ValueError, "start date"):
            FunctionalExpenseService(Connection()).report(1, date(2027, 2, 1), date(2027, 1, 1))

    def test_menu_and_permission_are_registered(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertIn("lblAccountingFunctionalExpenses", SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingFunctionalExpenses"], "accounting.reports.run")
        source = (Path(__file__).parents[1] / "accounting" / "functional_expense_dialog.py").read_text(encoding="utf-8")
        self.assertIn('title="Functional Expense Report"', source)
        self.assertIn('authorization.require("accounting.reports.run"', source)


if __name__ == "__main__":
    unittest.main()
