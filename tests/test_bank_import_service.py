from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from accounting.bank_import import CsvMapping
from accounting.bank_import_service import BankImportService

class Cursor:
    def __init__(self):self.statements=[];self.one=None;self.lastrowid=31
    def execute(self,sql,values=()):
        self.statements.append((sql,values))
        if sql.startswith("SELECT OrganizationID"):self.one=(1,)
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

if __name__=="__main__":unittest.main()
