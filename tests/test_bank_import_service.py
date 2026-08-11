from pathlib import Path
from tempfile import TemporaryDirectory
from decimal import Decimal
import unittest
from accounting.bank_import import CsvMapping
from accounting.bank_import_service import BankImportService

class Cursor:
    def __init__(self):self.statements=[];self.one=None;self.lastrowid=31
    def execute(self,sql,values=()):
        self.statements.append((sql,values))
        if sql.startswith("SELECT OrganizationID"):self.one=(1,)
        elif sql.startswith("SELECT r.MatchStatus, r.Amount"):
            self.one=("UNMATCHED",Decimal("100.00"),8,1)
        elif sql.startswith("SELECT r.MatchStatus,r.Matched"):
            self.one=("MATCHED",99,1)
        elif sql.startswith("SELECT r.MatchStatus"):self.one=("UNMATCHED",1)
        elif sql.startswith("SELECT l.ID FROM"):self.one=(99,)
        elif sql.startswith("SELECT ID FROM tblAccountingBankImportBatch"):self.one=None
    def fetchone(self):return self.one
    def fetchall(self):return []
    def close(self):pass
class Connection:
    def __init__(self):self.cursor_value=Cursor();self.commits=0;self.rollbacks=0
    def cursor(self):return self.cursor_value
    def commit(self):self.commits+=1
    def rollback(self):self.rollbacks+=1

class TestBankImportService(unittest.TestCase):
    def test_csv_is_staged_and_audited_without_ledger_writes(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/"statement.csv";path.write_text("Date,Memo,Amount\n01/15/2027,Deposit,100.00\n",encoding="utf-8")
            connection=Connection();result=BankImportService(connection,7).stage_csv(2,path,CsvMapping("Date","Memo",amount_column="Amount"))
        self.assertEqual(result,(31,1));self.assertEqual(connection.commits,1)
        sql="\n".join(v[0] for v in connection.cursor_value.statements)
        self.assertIn("tblAccountingBankImportBatch",sql);self.assertIn("tblAccountingBankImportRow",sql);self.assertIn("BANK_FILE_STAGED",sql)
        self.assertNotIn("tblAccountingTransaction (",sql);self.assertNotIn("Status='POSTED'",sql)

    def test_staged_review_queries_are_read_only(self):
        connection = Connection()
        service = BankImportService(connection, 7)
        service.staged_batches()
        service.staged_rows(31)
        sql = "\n".join(value[0] for value in connection.cursor_value.statements)
        self.assertIn("FROM tblAccountingBankImportBatch", sql)
        self.assertIn("FROM tblAccountingBankImportRow", sql)
        self.assertNotIn("INSERT", sql)
        self.assertNotIn("UPDATE", sql)

    def test_ignoring_row_updates_status_and_writes_audit(self):
        connection = Connection()
        changed = BankImportService(connection, 7).set_row_ignored(42, True)
        self.assertTrue(changed)
        self.assertEqual(connection.commits, 1)
        sql = "\n".join(value[0] for value in connection.cursor_value.statements)
        self.assertIn("UPDATE tblAccountingBankImportRow", sql)
        self.assertIn("BANK_IMPORT_ROW", sql)
        self.assertIn("BeforeJSON", sql)

    def test_matched_row_cannot_be_ignored(self):
        connection = Connection()
        connection.cursor_value.one = ("MATCHED", 1)
        original_execute = connection.cursor_value.execute
        def execute(sql, values=()):
            original_execute(sql, values)
            if sql.startswith("SELECT r.MatchStatus"):
                connection.cursor_value.one = ("MATCHED", 1)
        connection.cursor_value.execute = execute
        with self.assertRaisesRegex(ValueError, "matched"):
            BankImportService(connection, 7).set_row_ignored(42, True)
        self.assertEqual(connection.commits, 0)
        self.assertEqual(connection.rollbacks, 1)

    def test_match_requires_posted_same_account_same_amount_line(self):
        connection = Connection()
        BankImportService(connection, 7).match_row(42, 99)
        self.assertEqual(connection.commits, 1)
        sql = "\n".join(value[0] for value in connection.cursor_value.statements)
        self.assertIn("t.Status='POSTED'", sql)
        self.assertIn("l.AccountID=?", sql)
        self.assertIn("l.Debit-l.Credit=?", sql)
        self.assertIn("BANK_IMPORT_ROW", sql)

    def test_match_candidates_are_exact_unused_posted_lines_within_seven_days(self):
        connection = Connection()
        BankImportService(connection, 7).match_candidates(42)
        sql = connection.cursor_value.statements[-1][0]
        self.assertIn("t.Status='POSTED'", sql)
        self.assertIn("l.Debit-l.Credit=r.Amount", sql)
        self.assertIn("INTERVAL 7 DAY", sql)
        self.assertIn("used.ID IS NULL", sql)

    def test_unmatch_is_audited_and_clears_the_line(self):
        connection = Connection()
        BankImportService(connection, 7).unmatch_row(42)
        self.assertEqual(connection.commits, 1)
        sql = "\n".join(value[0] for value in connection.cursor_value.statements)
        self.assertIn("MatchedTransactionLineID=NULL", sql)
        self.assertIn("BANK_IMPORT_ROW", sql)

if __name__=="__main__":unittest.main()
