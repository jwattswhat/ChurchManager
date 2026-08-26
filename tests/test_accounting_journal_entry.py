from pathlib import Path
import unittest


class JournalEntryReportTests(unittest.TestCase):
    def test_report_contains_audit_and_supporting_document_fields(self):
        service=(Path(__file__).parents[1]/"accounting"/"journal_entry_service.py").read_text(encoding="utf-8")
        dialog=(Path(__file__).parents[1]/"accounting"/"journal_entry_dialog.py").read_text(encoding="utf-8")
        self.assertIn("CreatedByUserID",service)
        self.assertIn("ReviewedByUserID",service)
        self.assertIn("PostedByUserID",service)
        self.assertIn("OriginalTransactionID",service)
        self.assertIn("ReversalTransactionID",service)
        self.assertIn("tblAccountingAttachment",service)
        self.assertIn("Save / Print Report",dialog)
        self.assertIn("window.print()",dialog)
        self.assertIn('class="amount"',dialog)

    def test_register_opens_report_by_button_or_double_click(self):
        source=(Path(__file__).parents[1]/"accounting"/"register_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn('label="Journal Entry Report"',source)
        self.assertIn("wx.EVT_LIST_ITEM_ACTIVATED, self.on_journal_entry",source)


if __name__=="__main__":unittest.main()
