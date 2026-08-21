"""Tests for confidential draft contribution-batch persistence."""

import unittest
from datetime import date
from decimal import Decimal

from giving.batch_service import DraftBatchService
from giving.validation import GivingValidationError


class Cursor:
    def __init__(self, connection):
        self.connection = connection
        self.lastrowid = 0
        self.rows = []
        self.rowcount = 0

    def execute(self, sql, values=()):
        self.connection.calls.append((sql, values))
        self.rowcount = 0
        if "SELECT ID FROM tblChurch" in sql:
            self.rows = [(7,)]
        elif "SELECT OrganizationID,Status FROM tblContributionBatch" in sql:
            self.rows = [self.connection.batch]
        elif "SELECT Status FROM tblContributionBatch" in sql:
            self.rows = [(self.connection.batch[1],)]
        elif "SELECT ControlTotal,CalculatedTotal" in sql:
            self.rows = [self.connection.totals]
        elif sql.startswith("SELECT COUNT(*)"):
            self.rows = [(self.connection.review_counts.pop(0),)]
        elif "FROM tblContributionEnvelopeAssignment" in sql:
            self.rows = list(self.connection.envelopes)
        elif sql.startswith("INSERT INTO tblContributionBatch"):
            self.lastrowid = 21
        elif sql.startswith("INSERT INTO tblContribution "):
            self.lastrowid = 31
        elif sql.startswith("UPDATE tblContribution SET") or sql.startswith("DELETE FROM tblContribution WHERE"):
            self.rowcount = 1
        else:
            self.rows = []

    def fetchall(self): return self.rows
    def fetchone(self): return self.rows[0] if self.rows else None
    def close(self): pass


class Connection:
    def __init__(self):
        self.calls, self.commits, self.rollbacks = [], 0, 0
        self.batch, self.envelopes = (4, "DRAFT"), []
        self.totals, self.review_counts = (Decimal("25.00"), Decimal("25.00")), [0, 0, 0, 0, 0]
    def cursor(self): return Cursor(self)
    def commit(self): self.commits += 1
    def rollback(self): self.rollbacks += 1


class DraftBatchServiceTests(unittest.TestCase):
    def test_creates_draft_batch_with_safe_audit(self):
        connection = Connection()
        batch_id = DraftBatchService(connection, 3).create_batch(
            batch_date=date(2026, 8, 21), description="Sunday offering",
            organization_id=4, control_total="125.00")
        self.assertEqual((batch_id, connection.commits), (21, 1))
        self.assertTrue(any("BATCH_CREATED" in str(values) for _, values in connection.calls))

    def test_resolves_numeric_envelope_without_leading_zero_distinction(self):
        connection = Connection(); connection.envelopes = [(45,)]
        contributor = DraftBatchService(connection, 3).resolve_envelope("0012", date(2026, 8, 21))
        self.assertEqual(contributor, 45)
        call = next(item for item in connection.calls if "EnvelopeAssignment" in item[0])
        self.assertEqual(call[1][1], 12)

    def test_saves_balanced_gift_and_updates_batch_total(self):
        connection = Connection()
        contribution_id = DraftBatchService(connection, 3).save_monetary_gift(
            batch_id=21, received_date=date(2026, 8, 21), amount="25.00",
            contributor_id=45, method="CHECK", reference="1001",
            allocations=[(8, 4, 5, 6, "20.00", None), (9, 4, 7, 6, "5.00", None)])
        self.assertEqual((contribution_id, connection.commits), (31, 1))
        inserts = [item for item in connection.calls if "INSERT INTO tblContributionAllocation" in item[0]]
        self.assertEqual([item[1][5] for item in inserts], [Decimal("20.00"), Decimal("5.00")])
        self.assertTrue(any("CalculatedTotal" in sql for sql, _ in connection.calls))

    def test_rejects_unbalanced_or_non_draft_gift(self):
        with self.assertRaises(GivingValidationError):
            DraftBatchService(Connection(), 3).save_monetary_gift(
                batch_id=21, received_date=date.today(), amount="25.00",
                allocations=[(8, 4, 5, 6, "24.99", None)])
        connection = Connection(); connection.batch = (4, "READY")
        with self.assertRaises(GivingValidationError):
            DraftBatchService(connection, 3).save_monetary_gift(
                batch_id=21, received_date=date.today(), amount="25.00",
                allocations=[(8, 4, 5, 6, "25.00", None)])
        self.assertEqual(connection.rollbacks, 1)

    def test_review_reports_control_difference_and_unresolved_items(self):
        connection = Connection()
        connection.totals = (Decimal("30.00"), Decimal("25.00"))
        connection.review_counts = [1, 0, 0, 0, 0]
        issues = DraftBatchService(connection, 3).review_issues(21)
        self.assertIn("control total", " ".join(issues))
        self.assertIn("envelope", " ".join(issues))

    def test_complete_draft_is_marked_ready_and_audited(self):
        connection = Connection()
        DraftBatchService(connection, 3).mark_ready(21)
        self.assertEqual(connection.commits, 1)
        self.assertTrue(any("Status='READY'" in sql for sql, _ in connection.calls))
        self.assertTrue(any("BATCH_MARKED_READY" in str(values) for _, values in connection.calls))

    def test_update_replaces_allocations_and_recalculates_total(self):
        connection = Connection()
        DraftBatchService(connection, 3).update_monetary_gift(
            31, batch_id=21, received_date=date.today(), amount="30.00",
            allocations=[(8, 4, 5, 6, "30.00", None)], contributor_id=45,
            envelope_number="12", method="CHECK", reference="1002",
            statement_eligibility="ELIGIBLE", note=None)
        sql = "\n".join(item[0] for item in connection.calls)
        self.assertIn("UPDATE tblContribution SET", sql)
        self.assertIn("DELETE FROM tblContributionAllocation", sql)
        self.assertIn("CONTRIBUTION_UPDATED", str(connection.calls))
        self.assertEqual(connection.commits, 1)

    def test_delete_removes_allocations_then_gift_and_recalculates(self):
        connection = Connection()
        DraftBatchService(connection, 3).delete_gift(21, 31)
        calls = [item[0] for item in connection.calls]
        allocation = next(i for i, sql in enumerate(calls) if sql.startswith("DELETE FROM tblContributionAllocation"))
        gift = next(i for i, sql in enumerate(calls) if sql.startswith("DELETE FROM tblContribution WHERE"))
        self.assertLess(allocation, gift)
        self.assertIn("CONTRIBUTION_DELETED", str(connection.calls))


if __name__ == "__main__": unittest.main()
