from decimal import Decimal
import unittest

from accounting.draft_service import AccountingDraftError
from accounting.review_service import AccountingReviewService


class Cursor:
    def __init__(self, creator=8, threshold=Decimal("500.00"), total=Decimal("500.00")):
        self.creator = creator
        self.threshold = threshold
        self.total = total
        self.statements = []
        self.one = None
        self.rows = []
        self.rowcount = 0

    def execute(self, sql, values=()):
        self.statements.append((sql, values))
        if sql.startswith("SELECT t.OrganizationID"):
            self.one = (1, self.creator, "READY", 3, self.threshold, "JOURNAL",
                        "INDEPENDENT_PREFERRED")
        elif sql.startswith("SELECT Debit, Credit"):
            self.rows = [(self.total, Decimal("0")), (Decimal("0"), self.total)]
        elif sql.startswith("UPDATE tblAccountingTransaction"):
            self.rowcount = 1

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.rows

    def close(self):
        pass


class Connection:
    def __init__(self, **cursor_values):
        self.cursor_value = Cursor(**cursor_values)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.cursor_value

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class TestAccountingReview(unittest.TestCase):
    def test_independent_reviewer_can_approve_at_threshold(self):
        connection = Connection(creator=8)
        AccountingReviewService(connection, 7).approve(41, 3)
        self.assertEqual(connection.commits, 1)
        sql = "\n".join(item[0] for item in connection.cursor_value.statements)
        self.assertIn("Status='APPROVED'", sql)
        self.assertIn("ReviewedByUserID", sql)
        audit = next(item for item in connection.cursor_value.statements
                     if "INSERT INTO tblAccountingAuditEvent" in item[0])
        self.assertIn("TRANSACTION_APPROVED", audit[1])

    def test_creator_cannot_approve_at_or_above_threshold(self):
        connection = Connection(creator=7)
        with self.assertRaisesRegex(AccountingDraftError, "cannot approve"):
            AccountingReviewService(connection, 7).approve(41, 3)
        self.assertEqual(connection.commits, 0)
        self.assertEqual(connection.rollbacks, 1)

    def test_creator_may_approve_below_threshold(self):
        connection = Connection(creator=7, total=Decimal("499.99"))
        AccountingReviewService(connection, 7).approve(41, 3)
        self.assertEqual(connection.commits, 1)

    def test_reversal_always_requires_an_independent_reviewer(self):
        connection = Connection(creator=7, total=Decimal("25"))
        original = connection.cursor_value.execute
        def execute(sql, values=()):
            original(sql, values)
            if sql.startswith("SELECT t.OrganizationID"):
                connection.cursor_value.one = (1, 7, "READY", 3, Decimal("500"), "REVERSAL",
                                               "INDEPENDENT_PREFERRED")
        connection.cursor_value.execute = execute
        with self.assertRaisesRegex(AccountingDraftError, "cannot approve"):
            AccountingReviewService(connection, 7).approve(52, 3)

    def test_authorized_solo_override_requires_and_audits_reason(self):
        connection = Connection(creator=7, total=Decimal("25"))
        original = connection.cursor_value.execute
        def execute(sql, values=()):
            original(sql, values)
            if sql.startswith("SELECT t.OrganizationID"):
                connection.cursor_value.one = (1, 7, "READY", 3, Decimal("500"), "REVERSAL",
                                               "INDEPENDENT_PREFERRED")
        connection.cursor_value.execute = execute
        with self.assertRaisesRegex(AccountingDraftError, "Enter a reason"):
            AccountingReviewService(connection, 7).approve(52, 3, can_override=True)
        connection = Connection(creator=7, total=Decimal("25"))
        original = connection.cursor_value.execute
        def execute_reason(sql, values=()):
            original(sql, values)
            if sql.startswith("SELECT t.OrganizationID"):
                connection.cursor_value.one = (1, 7, "READY", 3, Decimal("500"), "REVERSAL",
                                               "INDEPENDENT_PREFERRED")
        connection.cursor_value.execute = execute_reason
        AccountingReviewService(connection, 7).approve(
            52, 3, "Only accounting operator available", can_override=True)
        audit = next(item for item in connection.cursor_value.statements
                     if "INSERT INTO tblAccountingAuditEvent" in item[0])
        self.assertIn("TRANSACTION_APPROVED_OVERRIDE", audit[1])
        self.assertIn("Only accounting operator available", audit[1])

    def test_review_is_a_separate_protected_read_only_screen(self):
        from pathlib import Path

        root = Path(__file__).parents[1]
        source = (root / "accounting" / "review_dialog.py").read_text(encoding="utf-8-sig")
        self.assertIn('title="Accounting Transaction Review"', source)
        self.assertIn("Transaction lines (read only)", source)
        self.assertIn('authorization.require("accounting.transactions.approve"', source)
        self.assertNotIn("Add Line", source)


if __name__ == "__main__":
    unittest.main()
