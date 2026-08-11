from datetime import date
from decimal import Decimal
import unittest

from accounting.draft_service import AccountingDraftError, AccountingDraftService
from accounting.models import JournalLine, JournalTransaction


class Cursor:
    def __init__(self, period_rows=((12,),)):
        self.period_rows = period_rows
        self.rows = []
        self.statements = []
        self.lastrowid = 41
        self.rowcount = 0
        self.one = None

    def execute(self, sql, values=()):
        self.statements.append((sql, values))
        self.rows = self.period_rows if sql.startswith("SELECT p.ID") else []
        if sql.startswith("SELECT Version"):
            self.one = (2, 7, "DRAFT")
        elif sql.startswith("UPDATE tblAccountingTransaction"):
            self.rowcount = 1

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.rows

    def close(self):
        pass


class Connection:
    def __init__(self, period_rows=((12,),)):
        self.cursor_value = Cursor(period_rows)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.cursor_value

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class SubmitCursor(Cursor):
    def __init__(self, total=Decimal("25.00"), attachments=0):
        super().__init__()
        self.total = total
        self.attachments = attachments

    def execute(self, sql, values=()):
        self.statements.append((sql, values))
        if sql.startswith("SELECT OrganizationID"):
            self.one = (1, date(2027, 1, 15), "CASH_DISBURSEMENT",
                        "Office supplies", "Invoice 17", 2, 7, "DRAFT")
            self.rows = []
        elif sql.startswith("SELECT LineNumber"):
            self.rows = [
                (1, 20, 3, self.total, Decimal("0.00"), None, None, ""),
                (2, 10, 3, Decimal("0.00"), self.total, None, None, ""),
            ]
        elif sql.startswith("SELECT p.ID"):
            self.rows = self.period_rows
        elif sql.startswith("SELECT AttachmentThreshold"):
            self.one = (Decimal("250.00"),)
            self.rows = []
        elif sql.startswith("SELECT COUNT(*) FROM tblAccountingAttachment"):
            self.one = (self.attachments,)
            self.rows = []
        elif sql.startswith("UPDATE tblAccountingTransaction"):
            self.rowcount = 1
            self.rows = []
        else:
            self.rows = []


class SubmitConnection(Connection):
    def __init__(self, total=Decimal("25.00"), attachments=0):
        super().__init__()
        self.cursor_value = SubmitCursor(total, attachments)


class DeleteCursor(Cursor):
    def __init__(self, status="DRAFT", creator=7, attachments=0):
        super().__init__()
        self.status = status
        self.creator = creator
        self.attachments = attachments

    def execute(self, sql, values=()):
        self.statements.append((sql, values))
        if sql.startswith("SELECT OrganizationID,TransactionDate"):
            self.one = (
                1, date(2027, 1, 15), "JOURNAL", "Test draft", None,
                2, self.creator, self.status,
            )
        elif sql.startswith("SELECT COUNT(*) FROM tblAccountingAttachment"):
            self.one = (self.attachments,)
        elif sql.startswith("DELETE FROM tblAccountingTransaction WHERE"):
            self.rowcount = 1


class DeleteConnection(Connection):
    def __init__(self, status="DRAFT", creator=7, attachments=0):
        super().__init__()
        self.cursor_value = DeleteCursor(status, creator, attachments)


def balanced(transaction_type="CASH_DISBURSEMENT", reference="Invoice 17"):
    return JournalTransaction(
        organization_id=1,
        transaction_date=date(2027, 1, 15),
        transaction_type=transaction_type,
        description="Office supplies",
        reference=reference,
        lines=(
            JournalLine(1, 20, 3, debit=Decimal("25.00")),
            JournalLine(2, 10, 3, credit=Decimal("25.00")),
        ),
    )


class TestAccountingDraftService(unittest.TestCase):
    def test_own_unposted_draft_deletes_lines_header_and_audits_atomically(self):
        connection = DeleteConnection()
        AccountingDraftService(connection, 7).delete(41, 2)
        self.assertEqual(connection.commits, 1)
        sql = "\n".join(item[0] for item in connection.cursor_value.statements)
        self.assertIn("DELETE FROM tblAccountingTransactionLine", sql)
        self.assertIn("DELETE FROM tblAccountingTransaction WHERE", sql)
        self.assertIn("DRAFT_DELETED", sql)

    def test_ready_or_posted_transaction_cannot_be_deleted(self):
        connection = DeleteConnection(status="READY")
        with self.assertRaisesRegex(AccountingDraftError, "unposted draft"):
            AccountingDraftService(connection, 7).delete(41, 2)
        self.assertEqual(connection.commits, 0)

    def test_another_users_draft_cannot_be_deleted(self):
        connection = DeleteConnection(creator=8)
        with self.assertRaisesRegex(AccountingDraftError, "only drafts"):
            AccountingDraftService(connection, 7).delete(41, 2)

    def test_draft_with_attachment_must_be_cleaned_up_first(self):
        connection = DeleteConnection(attachments=1)
        with self.assertRaisesRegex(AccountingDraftError, "attachments"):
            AccountingDraftService(connection, 7).delete(41, 2)

    def test_dialog_requires_confirmation_for_draft_deletion(self):
        from pathlib import Path
        source = (Path(__file__).parents[1] / "accounting" / "draft_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn("Confirm Draft Deletion", source)
        self.assertIn("accounting.transactions.delete_draft", source)
    def test_line_dialog_uses_one_amount_and_a_debit_credit_selector(self):
        from pathlib import Path

        source = (Path(__file__).parents[1] / "accounting" / "draft_dialog.py").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn('choices=["Debit", "Credit"]', source)
        self.assertIn("Enter one positive amount", source)
        self.assertIn("debit = amount if", source)
        self.assertNotIn("self.credit = wx.TextCtrl", source)

    def test_guided_cash_workflows_create_reviewable_balanced_lines(self):
        from pathlib import Path

        source = (Path(__file__).parents[1] / "accounting" / "draft_dialog.py").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn('label="Guided Receipt"', source)
        self.assertIn('label="Guided Disbursement"', source)
        self.assertIn('label="Guided Transfer"', source)
        self.assertIn("lines = [cash_line, offset_line] if self.receipt", source)
        self.assertIn("self.transaction_type.SetSelection(1 if receipt else 0)", source)
        self.assertIn("Configure an active Bank Account", source)

    def test_master_choices_include_template_account_groups(self):
        from pathlib import Path

        source = (Path(__file__).parents[1] / "accounting" / "draft_service.py").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn('"cash_accounts"', source)
        self.assertIn('"revenue_accounts"', source)
        self.assertIn('"expense_accounts"', source)
        self.assertIn('"transfer_out_accounts"', source)
        self.assertIn('"transfer_in_accounts"', source)
        self.assertIn("FROM tblAccountingBankAccount", source)

    def test_transaction_grid_columns_fit_inside_dialog(self):
        from pathlib import Path

        source = (Path(__file__).parents[1] / "accounting" / "draft_dialog.py").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn('size=(980, 650)', source)
        widths = (35, 175, 135, 120, 110, 150, 80, 80)
        self.assertLess(sum(widths), 980 - 40)

    def test_balanced_draft_saves_header_lines_and_audit_atomically(self):
        connection = Connection()
        transaction_id = AccountingDraftService(connection, 7).create(balanced())
        self.assertEqual(transaction_id, 41)
        self.assertEqual(connection.commits, 1)
        self.assertEqual(connection.rollbacks, 0)
        sql = "\n".join(item[0] for item in connection.cursor_value.statements)
        self.assertIn("INSERT INTO tblAccountingTransaction ", sql)
        self.assertEqual(sql.count("INSERT INTO tblAccountingTransactionLine "), 2)
        audit = next(item for item in connection.cursor_value.statements
                     if "INSERT INTO tblAccountingAuditEvent" in item[0])
        self.assertIn("DRAFT_CREATED", audit[1])

    def test_update_replaces_lines_and_increments_version_atomically(self):
        connection = Connection()
        version = AccountingDraftService(connection, 7).update(41, 2, balanced())
        self.assertEqual(version, 3)
        self.assertEqual(connection.commits, 1)
        sql = "\n".join(item[0] for item in connection.cursor_value.statements)
        self.assertIn("WHERE ID=? FOR UPDATE", sql)
        self.assertIn("Version=Version+1", sql)
        self.assertIn("DELETE FROM tblAccountingTransactionLine", sql)
        audit = next(item for item in connection.cursor_value.statements
                     if "INSERT INTO tblAccountingAuditEvent" in item[0])
        self.assertIn("DRAFT_UPDATED", audit[1])

    def test_update_rejects_stale_version_and_rolls_back(self):
        connection = Connection()
        with self.assertRaisesRegex(AccountingDraftError, "changed after"):
            AccountingDraftService(connection, 7).update(41, 1, balanced())
        self.assertEqual(connection.commits, 0)
        self.assertEqual(connection.rollbacks, 1)

    def test_update_rejects_another_users_draft(self):
        connection = Connection()
        connection.cursor_value.one = (2, 8, "DRAFT")
        original_execute = connection.cursor_value.execute
        def execute(sql, values=()):
            original_execute(sql, values)
            if sql.startswith("SELECT Version"):
                connection.cursor_value.one = (2, 8, "DRAFT")
        connection.cursor_value.execute = execute
        with self.assertRaisesRegex(AccountingDraftError, "only drafts"):
            AccountingDraftService(connection, 7).update(41, 2, balanced())
        self.assertEqual(connection.rollbacks, 1)

    def test_dialog_includes_open_and_update_workflow(self):
        from pathlib import Path

        source = (Path(__file__).parents[1] / "accounting" / "draft_dialog.py").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn('label="Open Draft"', source)
        self.assertIn('self.save.SetLabel("Update Draft")', source)
        self.assertIn("self.service.update(", source)

    def test_submit_rereads_and_locks_draft_before_marking_ready(self):
        connection = SubmitConnection()
        version = AccountingDraftService(connection, 7).submit(41, 2)
        self.assertEqual(version, 3)
        self.assertEqual(connection.commits, 1)
        sql = "\n".join(item[0] for item in connection.cursor_value.statements)
        self.assertIn("WHERE ID=? FOR UPDATE", sql)
        self.assertIn("ORDER BY LineNumber FOR UPDATE", sql)
        self.assertIn("SET Status='READY'", sql)
        audit = next(item for item in connection.cursor_value.statements
                     if "INSERT INTO tblAccountingAuditEvent" in item[0])
        self.assertIn("DRAFT_MARKED_READY", audit[1])

    def test_dialog_submits_only_a_loaded_draft_for_review(self):
        from pathlib import Path

        source = (Path(__file__).parents[1] / "accounting" / "draft_dialog.py").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn('label="Submit for Review"', source)
        self.assertIn("self.service.submit(", source)
        self.assertIn("self.submit.Enable(False)", source)

    def test_large_disbursement_requires_attachment_before_submit(self):
        connection = SubmitConnection(total=Decimal("250.00"), attachments=0)
        with self.assertRaisesRegex(AccountingDraftError, "receipt, invoice, or voucher"):
            AccountingDraftService(connection, 7).submit(41, 2)

    def test_large_disbursement_with_attachment_can_submit(self):
        connection = SubmitConnection(total=Decimal("250.00"), attachments=1)
        self.assertEqual(AccountingDraftService(connection, 7).submit(41, 2), 3)

    def test_transaction_date_requires_one_open_period(self):
        connection = Connection(period_rows=())
        with self.assertRaisesRegex(AccountingDraftError, "exactly one open"):
            AccountingDraftService(connection, 7).create(balanced())
        self.assertEqual(connection.commits, 0)
        self.assertEqual(connection.rollbacks, 1)

    def test_disbursement_requires_source_document_reference(self):
        with self.assertRaisesRegex(AccountingDraftError, "source-document"):
            AccountingDraftService(Connection(), 7).create(balanced(reference=""))

    def test_unbalanced_draft_never_reaches_database(self):
        transaction = balanced()
        transaction = JournalTransaction(
            transaction.organization_id,
            transaction.transaction_date,
            transaction.description,
            (transaction.lines[0],),
            transaction.reference,
            transaction.transaction_type,
        )
        connection = Connection()
        with self.assertRaises(ValueError):
            AccountingDraftService(connection, 7).create(transaction)
        self.assertEqual(connection.cursor_value.statements, [])


if __name__ == "__main__":
    unittest.main()
