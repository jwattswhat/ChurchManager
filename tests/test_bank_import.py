from decimal import Decimal
import unittest
from pathlib import Path
from accounting.bank_import import BankImportError,CsvMapping,csv_headers,file_hash,parse_csv

class TestBankImport(unittest.TestCase):
    def test_staged_activity_review_is_read_only_and_right_aligned(self):
        source = (Path(__file__).parents[1] / "accounting" / "bank_import_dialog.py").read_text(encoding="utf-8")
        self.assertIn("Staged Bank Activity", source)
        self.assertIn("LIST_FORMAT_RIGHT", source)
        self.assertIn("staged_rows", source)
        self.assertIn("Only exact amounts within seven days", source)
        self.assertIn("Confirm Bank Match", source)
    def test_csv_headers_support_utf8_bom(self):
        self.assertEqual(csv_headers(b"\xef\xbb\xbfDate,Memo,Amount\n"), ("Date", "Memo", "Amount"))

    def test_csv_headers_must_be_unique(self):
        with self.assertRaisesRegex(BankImportError, "unique"):
            csv_headers(b"Date,Memo,Memo\n")
    def test_single_amount_csv_is_parsed_without_posting(self):
        content=b"Date,Description,Amount,ID\n01/15/2027,Offering,1000.00,A1\n01/16/2027,Utility,-250.00,A2\n"
        rows=parse_csv(content,CsvMapping("Date","Description",amount_column="Amount",external_id_column="ID"))
        self.assertEqual((rows[0].amount,rows[1].amount),(Decimal("1000.00"),Decimal("-250.00")))
        self.assertEqual(len(rows[0].fingerprint),64);self.assertEqual(len(file_hash(content)),64)
    def test_debit_credit_columns_become_signed_bank_amount(self):
        content=b"Date,Memo,Debit,Credit\n01/15/2027,Check,25.00,\n01/16/2027,Deposit,,50.00\n"
        rows=parse_csv(content,CsvMapping("Date","Memo",debit_column="Debit",credit_column="Credit"))
        self.assertEqual((rows[0].amount,rows[1].amount),(Decimal("-25.00"),Decimal("50.00")))
    def test_missing_mapping_column_is_readable_error(self):
        with self.assertRaisesRegex(BankImportError,"missing"):
            parse_csv(b"Date,Memo\n01/15/2027,Test\n",CsvMapping("Date","Memo",amount_column="Amount"))

if __name__=="__main__":unittest.main()
