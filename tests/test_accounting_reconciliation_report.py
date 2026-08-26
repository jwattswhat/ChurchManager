from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import unittest

from accounting.reconciliation_report_service import ReconciliationReportService


class Cursor:
    def __init__(self): self.calls=[]; self.one=None; self.rows=[]
    def execute(self, sql, values=()):
        self.calls.append((sql, values))
        if sql.startswith("SELECT r.BankAccountID"):
            self.one=(3,10,date(2026,1,31),Decimal("100"),Decimal("125"),"Checking")
        elif sql.startswith("SELECT 'Cleared'"):
            self.rows=[("Cleared",date(2026,1,5),1,"Deposit","D1",Decimal("25"),date(2026,1,5))]
        elif sql.startswith("SELECT 'Outstanding'"):
            self.rows=[("Outstanding",date(2026,1,30),2,"Check","C1",Decimal("-10"),None)]
    def fetchone(self): return self.one
    def fetchall(self): return self.rows
    def close(self): pass


class Connection:
    def __init__(self): self.cursor_value=Cursor()
    def cursor(self): return self.cursor_value


class ReconciliationReportTests(unittest.TestCase):
    def test_completed_proof_and_outstanding_items_are_separate(self):
        result=ReconciliationReportService(Connection()).detail(7)
        self.assertEqual(result["difference"],Decimal("0"))
        self.assertEqual(result["outstanding_total"],Decimal("-10"))
        self.assertEqual([row[0] for row in result["items"]],["Cleared","Outstanding"])

    def test_menu_is_report_protected_and_amounts_are_right_aligned(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertIn("lblAccountingReconciliationReport",SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingReconciliationReport"],
                         "accounting.reports.run")
        source=(Path(__file__).parents[1]/"accounting"/"reconciliation_report_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn("wx.LIST_FORMAT_RIGHT",source)
        self.assertIn("Outstanding",source)


if __name__=="__main__": unittest.main()
