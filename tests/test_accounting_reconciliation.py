from datetime import date
from decimal import Decimal
from pathlib import Path
import unittest

from accounting.reconciliation_service import BankReconciliationService


class Cursor:
    def __init__(self, unmatched=0, activity=Decimal("750.00")):
        self.statements = []
        self.one = None
        self.lastrowid = 51
        self.unmatched = unmatched
        self.activity = activity

    def execute(self, sql, values=()):
        self.statements.append((sql, values))
        if sql.startswith("SELECT OrganizationID"):
            self.one = (1,)
        elif sql.startswith("SELECT ID FROM tblAccountingReconciliation"):
            self.one = None
        elif sql.startswith("SELECT MAX(StatementDate)"):
            self.one = (None,)
        elif sql.startswith("SELECT r.BankAccountID"):
            self.one = (1, date(2027, 1, 31), Decimal("0"), Decimal("750"), "DRAFT", 1)
        elif sql.startswith("SELECT COUNT(*)"):
            self.one = (self.unmatched,)
        elif sql.startswith("SELECT COALESCE(SUM(ClearedAmount)"):
            self.one = (self.activity,)

    def fetchone(self):
        return self.one

    def fetchall(self):
        return []

    def close(self):
        pass


class Connection:
    def __init__(self, unmatched=0, activity=Decimal("750.00")):
        self.value = Cursor(unmatched, activity)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.value

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class TestBankReconciliation(unittest.TestCase):
    def test_draft_collects_only_matched_unreconciled_rows_without_ledger_writes(self):
        connection = Connection()
        result = BankReconciliationService(connection, 7).create_draft(
            1, date(2027, 1, 31), Decimal("0"), Decimal("750")
        )
        self.assertEqual(result, 51)
        self.assertEqual(connection.commits, 1)
        sql = "\n".join(item[0] for item in connection.value.statements)
        self.assertIn("r.MatchStatus='MATCHED'", sql)
        self.assertIn("NOT EXISTS", sql)
        self.assertNotIn("INSERT INTO tblAccountingTransaction ", sql)

    def test_zero_difference_draft_can_complete_atomically(self):
        connection = Connection()
        BankReconciliationService(connection, 7).complete(51)
        self.assertEqual(connection.commits, 1)
        sql = "\n".join(item[0] for item in connection.value.statements)
        self.assertIn("Status='COMPLETED'", sql)
        self.assertIn("BANK_RECONCILIATION", sql)

    def test_unmatched_rows_block_completion(self):
        connection = Connection(unmatched=1)
        with self.assertRaisesRegex(ValueError, "Resolve or ignore"):
            BankReconciliationService(connection, 7).complete(51)
        self.assertEqual(connection.commits, 0)

    def test_nonzero_difference_blocks_completion(self):
        connection = Connection(activity=Decimal("700"))
        with self.assertRaisesRegex(ValueError, "difference"):
            BankReconciliationService(connection, 7).complete(51)

    def test_dialog_right_aligns_money_and_requires_confirmation(self):
        source = (Path(__file__).parents[1] / "accounting" / "reconciliation_dialog.py").read_text(encoding="utf-8")
        self.assertIn("LIST_FORMAT_RIGHT", source)
        self.assertIn("Confirm Reconciliation", source)


if __name__ == "__main__":
    unittest.main()
