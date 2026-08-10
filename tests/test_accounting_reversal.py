from datetime import date
from decimal import Decimal
import unittest

from accounting.draft_service import AccountingDraftError
from accounting.reversal_service import AccountingReversalService

class Cursor:
    def __init__(self, original=(1, 1, "POSTED", None, None)):
        self.original, self.one, self.rows = original, None, []
        self.statements, self.lastrowid = [], 52
    def execute(self, sql, values=()):
        self.statements.append((sql, values))
        if sql.startswith("SELECT OrganizationID"): self.one = self.original
        elif sql.startswith("SELECT p.ID"): self.rows = [(12,)]
        elif sql.startswith("SELECT LineNumber"): self.rows = [
            (1, 20, 3, None, None, "Expense", Decimal("25"), Decimal("0")),
            (2, 10, 3, None, None, "Cash", Decimal("0"), Decimal("25"))]
    def fetchone(self): return self.one
    def fetchall(self): return self.rows
    def close(self): pass

class Connection:
    def __init__(self, original=(1, 1, "POSTED", None, None)):
        self.cursor_value, self.commits, self.rollbacks = Cursor(original), 0, 0
    def cursor(self): return self.cursor_value
    def commit(self): self.commits += 1
    def rollback(self): self.rollbacks += 1

class TestAccountingReversal(unittest.TestCase):
    def test_reversal_swaps_debits_and_credits_and_links_original(self):
        connection = Connection()
        self.assertEqual(AccountingReversalService(connection, 7).create(
            41, date(2027, 1, 20), "Wrong vendor"), 52)
        inserts = [item for item in connection.cursor_value.statements
                   if item[0].startswith("INSERT INTO tblAccountingTransactionLine")]
        self.assertEqual(inserts[0][1][-2:], (Decimal("0"), Decimal("25")))
        self.assertEqual(inserts[1][1][-2:], (Decimal("25"), Decimal("0")))
        header = next(item for item in connection.cursor_value.statements
                      if item[0].startswith("INSERT INTO tblAccountingTransaction "))
        self.assertIn("'REVERSAL', 'READY'", header[0])
        self.assertIn(41, header[1])
        self.assertEqual(connection.commits, 1)

    def test_reversal_of_reversal_is_refused(self):
        connection = Connection((1, 2, "POSTED", 41, None))
        with self.assertRaisesRegex(AccountingDraftError, "cannot itself"):
            AccountingReversalService(connection, 7).create(52, date(2027,1,20), "No")
        self.assertEqual(connection.rollbacks, 1)

    def test_duplicate_reversal_is_refused(self):
        connection = Connection((1, 1, "POSTED", None, 52))
        with self.assertRaisesRegex(AccountingDraftError, "already exists"):
            AccountingReversalService(connection, 7).create(41, date(2027,1,20), "No")

    def test_register_collects_date_and_reason(self):
        from pathlib import Path
        source = (Path(__file__).parents[1] / "accounting" / "register_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn('label="Create Reversal"', source)
        self.assertIn("DatePickerCtrl", source)
        self.assertIn("reversal_service.create", source)

if __name__ == "__main__": unittest.main()
