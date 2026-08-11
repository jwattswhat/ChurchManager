from datetime import date
from decimal import Decimal
from pathlib import Path
import unittest

from accounting.fund_balance_service import FundBalanceService


class Cursor:
    def __init__(self): self.calls = []; self.rows = []
    def execute(self, sql, values=()):
        self.calls.append((sql, values))
        self.rows = [
            ("GEN", "General", "WITHOUT_DONOR_RESTRICTIONS",
             Decimal("1000"), Decimal("1300"), Decimal("1200"),
             Decimal("800"), Decimal("-100")),
        ]
    def fetchall(self): return self.rows
    def close(self): pass


class Connection:
    def __init__(self): self.cursor_value = Cursor()
    def cursor(self): return self.cursor_value


class FundBalanceTests(unittest.TestCase):
    def test_activity_reconciles_beginning_to_ending_with_other_adjustments(self):
        result = FundBalanceService(Connection()).report(
            1, date(2026, 1, 1), date(2026, 1, 31)
        )
        row = result[0]
        self.assertEqual(row[3], Decimal("1000"))
        self.assertEqual(row[4], Decimal("1200"))
        self.assertEqual(row[5], Decimal("800"))
        self.assertEqual(row[6], Decimal("-100"))
        self.assertEqual(row[7], Decimal("0"))
        self.assertEqual(row[8], Decimal("1300"))

    def test_invalid_date_range_is_rejected(self):
        connection = Connection()
        with self.assertRaisesRegex(ValueError, "Through date"):
            FundBalanceService(connection).report(
                1, date(2026, 2, 1), date(2026, 1, 31)
            )
        self.assertEqual(connection.cursor_value.calls, [])

    def test_menu_and_currency_columns_are_protected_and_right_aligned(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS

        self.assertIn("lblAccountingFundBalances", SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingFundBalances"],
                         "accounting.reports.run")
        source = (Path(__file__).parents[1] / "accounting" /
                  "fund_balance_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn("for index in range(3, 9)", source)
        self.assertIn("wx.LIST_FORMAT_RIGHT", source)


if __name__ == "__main__":
    unittest.main()
