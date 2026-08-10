from datetime import date
from decimal import Decimal
import unittest
from accounting.position_service import FinancialPositionService

class Cursor:
    def __init__(self): self.rows=[]; self.statements=[]
    def execute(self,sql,values=()):
        self.statements.append((sql,values)); self.rows=[
            ("1000","Cash","ASSET","WITHOUT_DONOR_RESTRICTIONS",Decimal("100"),0),
            ("2000","Payable","LIABILITY","WITHOUT_DONOR_RESTRICTIONS",0,Decimal("20")),
            ("3000","Net assets","NET_ASSET","WITHOUT_DONOR_RESTRICTIONS",0,Decimal("50")),
            ("4000","Revenue","REVENUE","WITHOUT_DONOR_RESTRICTIONS",0,Decimal("40")),
            ("6000","Expense","EXPENSE","WITHOUT_DONOR_RESTRICTIONS",Decimal("10"),0)]
    def fetchall(self):return self.rows
    def close(self):pass
class Connection:
    def __init__(self):self.cursor_value=Cursor()
    def cursor(self):return self.cursor_value

class TestFinancialPosition(unittest.TestCase):
    def test_current_activity_is_included_in_net_assets(self):
        connection=Connection(); assets,liabilities,net_accounts,activity=FinancialPositionService(connection).rows(1,date(2027,1,31))
        self.assertEqual(assets[0][2],Decimal("100")); self.assertEqual(liabilities[0][2],Decimal("20"))
        self.assertEqual(net_accounts[0][3],Decimal("50")); self.assertEqual(activity["WITHOUT_DONOR_RESTRICTIONS"],Decimal("30"))
        self.assertIn("t.Status IN ('POSTED','REVERSED')",connection.cursor_value.statements[0][0])
    def test_screen_is_read_only_and_shows_balance_check(self):
        from pathlib import Path
        source=(Path(__file__).parents[1]/"accounting"/"position_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn('title="Statement of Financial Position"',source)
        self.assertIn("Liabilities + net assets",source)
        self.assertIn('authorization.require("accounting.reports.run"',source)

if __name__=="__main__":unittest.main()
