from datetime import date
from decimal import Decimal
import unittest
from accounting.trial_balance_service import TrialBalanceService

class Cursor:
    def __init__(self): self.rows=[]; self.statements=[]
    def execute(self, sql, values=()):
        self.statements.append((sql, values))
        self.rows = [("1000", "Cash", "ASSET", "DEBIT", Decimal("125"), Decimal("25")),
                     ("4000", "Offerings", "REVENUE", "CREDIT", Decimal("0"), Decimal("100"))]
    def fetchall(self): return self.rows
    def close(self): pass
class Connection:
    def __init__(self): self.cursor_value=Cursor()
    def cursor(self): return self.cursor_value

class TestTrialBalance(unittest.TestCase):
    def test_rows_calculate_net_debit_and_credit_balances(self):
        connection=Connection(); rows=TrialBalanceService(connection).rows(1,date(2027,1,31))
        self.assertEqual(rows[0][6:], (Decimal("100"), Decimal("0")))
        self.assertEqual(rows[1][6:], (Decimal("0"), Decimal("100")))
        sql=connection.cursor_value.statements[0][0]
        self.assertIn("t.Status IN ('POSTED','REVERSED')", sql)
        self.assertIn("CASE WHEN t.ID IS NOT NULL", sql)
    def test_screen_is_read_only_and_permission_protected(self):
        from pathlib import Path
        source=(Path(__file__).parents[1]/"accounting"/"trial_balance_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn('title="Trial Balance"', source)
        self.assertIn('authorization.require("accounting.reports.run"', source)
        self.assertNotIn("Add Line", source)
        self.assertIn('("Account",180)', source)
        self.assertIn("All posted activity nets to zero", source)

if __name__ == "__main__": unittest.main()
