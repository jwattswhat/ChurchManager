from decimal import Decimal
import unittest

from accounting.draft_service import AccountingDraftError
from accounting.posting_service import AccountingPostingService


class Cursor:
    def __init__(self, status="APPROVED", creator=7, reviewer=8, total=Decimal("500"),
                 original_id=None, override=False, transaction_type="JOURNAL",
                 attachments=0):
        self.status, self.creator, self.reviewer, self.total = status, creator, reviewer, total
        self.original_id, self.override = original_id, override
        self.transaction_type, self.attachments = transaction_type, attachments
        self.statements, self.one, self.rows, self.rowcount = [], None, [], 0
    def execute(self, sql, values=()):
        self.statements.append((sql, values))
        if sql.startswith("SELECT t.OrganizationID"):
            self.one = (1, 12, self.status, 4, self.creator, self.reviewer,
                        Decimal("500"), 27, self.original_id, self.override,
                        self.transaction_type, Decimal("250"))
        elif sql.startswith("SELECT p.Status"):
            self.one = ("OPEN", "OPEN")
        elif sql.startswith("SELECT l.Debit"):
            self.rows = [(self.total, 0, 1, 1, 1, None, "OPTIONAL", None),
                         (0, self.total, 1, 1, 1, None, "OPTIONAL", None)]
        elif sql.startswith("SELECT COUNT(*) FROM tblAccountingAttachment"):
            self.one = (self.attachments,)
        elif sql.startswith("UPDATE"):
            self.rowcount = 1
    def fetchone(self): return self.one
    def fetchall(self): return self.rows
    def close(self): pass

class Connection:
    def __init__(self, **values):
        self.cursor_value, self.commits, self.rollbacks = Cursor(**values), 0, 0
    def cursor(self): return self.cursor_value
    def commit(self): self.commits += 1
    def rollback(self): self.rollbacks += 1

class TestAccountingPosting(unittest.TestCase):
    def test_posting_screen_is_read_only_and_permission_protected(self):
        from pathlib import Path
        source = (Path(__file__).parents[1] / "accounting" / "posting_dialog.py").read_text(
            encoding="utf-8-sig")
        self.assertIn('label="Post Transaction"', source)
        self.assertIn("Transaction lines (read only)", source)
        self.assertIn('authorization.require("accounting.transactions.post"', source)
        self.assertNotIn("Add Line", source)
        self.assertIn('("Description", 255)', source)

    def test_posting_assigns_number_and_commits_everything_together(self):
        connection = Connection()
        self.assertEqual(AccountingPostingService(connection, 9).post(41, 4), 27)
        self.assertEqual(connection.commits, 1)
        sql = "\n".join(item[0] for item in connection.cursor_value.statements)
        self.assertIn("NextTransactionNumber", sql)
        self.assertIn("Status='POSTED'", sql)
        self.assertIn("TRANSACTION_POSTED", sql)

    def test_ready_transaction_at_threshold_requires_independent_approval(self):
        connection = Connection(status="READY", reviewer=None)
        with self.assertRaisesRegex(AccountingDraftError, "different user"):
            AccountingPostingService(connection, 9).post(41, 4)
        self.assertEqual(connection.rollbacks, 1)

    def test_ready_transaction_below_threshold_can_post_without_approval(self):
        connection = Connection(status="READY", reviewer=None, total=Decimal("25"))
        self.assertEqual(AccountingPostingService(connection, 9).post(41, 4), 27)

    def test_reversal_can_post_after_audited_solo_override(self):
        connection = Connection(status="APPROVED", creator=7, reviewer=7,
                                total=Decimal("25"), original_id=41, override=True)
        self.assertEqual(AccountingPostingService(connection, 7).post(52, 4), 27)
        header_query = connection.cursor_value.statements[0][0]
        self.assertIn("CAST(ae.EntityID AS UNSIGNED)=t.ID", header_query)
        self.assertNotIn("CAST(t.ID AS CHAR)", header_query)

    def test_reversal_rejects_same_user_without_override_audit(self):
        connection = Connection(status="APPROVED", creator=7, reviewer=7,
                                total=Decimal("25"), original_id=41, override=False)
        with self.assertRaisesRegex(AccountingDraftError, "different user"):
            AccountingPostingService(connection, 7).post(52, 4)

    def test_disbursement_at_attachment_threshold_requires_document(self):
        connection = Connection(transaction_type="CASH_DISBURSEMENT", attachments=0)
        with self.assertRaisesRegex(AccountingDraftError, "receipt, invoice, or voucher"):
            AccountingPostingService(connection, 9).post(41, 4)

    def test_disbursement_with_attachment_can_post(self):
        connection = Connection(transaction_type="CASH_DISBURSEMENT", attachments=1)
        self.assertEqual(AccountingPostingService(connection, 9).post(41, 4), 27)

    def test_small_disbursement_does_not_require_attachment(self):
        connection = Connection(transaction_type="CASH_DISBURSEMENT",
                                total=Decimal("25"), attachments=0)
        self.assertEqual(AccountingPostingService(connection, 9).post(41, 4), 27)

    def test_restriction_release_always_requires_supporting_document(self):
        connection = Connection(transaction_type="RESTRICTION_RELEASE",
                                total=Decimal("25"), attachments=0)
        with self.assertRaisesRegex(AccountingDraftError, "supporting authority"):
            AccountingPostingService(connection, 9).post(41, 4)

    def test_restriction_release_always_requires_independent_approval(self):
        connection = Connection(status="READY", reviewer=None,
                                transaction_type="RESTRICTION_RELEASE",
                                total=Decimal("25"), attachments=1)
        with self.assertRaisesRegex(AccountingDraftError, "different user"):
            AccountingPostingService(connection, 9).post(41, 4)

if __name__ == "__main__": unittest.main()
