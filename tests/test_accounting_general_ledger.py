from datetime import date
from decimal import Decimal
from pathlib import Path
import unittest

from accounting.general_ledger_service import GeneralLedgerService, normal_balance


class Cursor:
    def __init__(self):
        self.calls = []
        self.one = None
        self.rows = []

    def execute(self, sql, values=()):
        self.calls.append((sql, values))
        if sql.startswith("SELECT Code,Name,NormalBalance"):
            self.one = ("1000", "Checking", "DEBIT")
        elif sql.startswith("SELECT COALESCE(SUM"):
            self.one = (Decimal("100.00"),)
        elif sql.startswith("SELECT t.TransactionDate"):
            self.rows = [
                (date(2026, 1, 5), 1, "CASH_RECEIPT", "Offering", "DEP-1",
                 "GEN - General", "Sunday", Decimal("25.00"), Decimal("0.00")),
                (date(2026, 1, 6), 2, "CASH_DISBURSEMENT", "Supplies", "CHK-1",
                 "GEN - General", "Paper", Decimal("0.00"), Decimal("10.00")),
            ]

    def fetchone(self): return self.one
    def fetchall(self): return self.rows
    def close(self): pass


class Connection:
    def __init__(self): self.cursor_value = Cursor()
    def cursor(self): return self.cursor_value


class GeneralLedgerTests(unittest.TestCase):
    def test_running_balance_includes_opening_balance(self):
        connection = Connection()
        result = GeneralLedgerService(connection).report(
            1, 10, date(2026, 1, 1), date(2026, 1, 31)
        )
        self.assertEqual(result["opening_balance"], Decimal("100.00"))
        self.assertEqual(result["rows"][0][9], Decimal("125.00"))
        self.assertEqual(result["rows"][1][9], Decimal("115.00"))
        sql = "\n".join(item[0] for item in connection.cursor_value.calls)
        self.assertIn("t.Status IN ('POSTED','REVERSED')", sql)

    def test_credit_normal_balance_reverses_raw_sign(self):
        self.assertEqual(normal_balance(Decimal("-75"), "CREDIT"), Decimal("75"))

    def test_invalid_date_range_is_rejected_before_query(self):
        connection = Connection()
        with self.assertRaisesRegex(ValueError, "Through date"):
            GeneralLedgerService(connection).report(
                1, 10, date(2026, 2, 1), date(2026, 1, 31)
            )
        self.assertEqual(connection.cursor_value.calls, [])

    def test_menu_and_amount_columns_are_protected_and_right_aligned(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS

        self.assertIn("lblAccountingGeneralLedger", SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingGeneralLedger"],
                         "accounting.reports.run")
        source = (Path(__file__).parents[1] / "accounting" /
                  "general_ledger_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn("for index in (7, 8, 9)", source)
        self.assertIn("wx.LIST_FORMAT_RIGHT", source)


if __name__ == "__main__":
    unittest.main()
