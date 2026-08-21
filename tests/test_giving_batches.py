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

    def execute(self, sql, values=()):
        self.connection.calls.append((sql, values))
        if "SELECT ID FROM tblChurch" in sql:
            self.rows = [(7,)]
        elif "FROM tblContributionBatch" in sql and "FOR UPDATE" in sql:
            self.rows = [self.connection.batch]
        elif "FROM tblContributionEnvelopeAssignment" in sql:
            self.rows = list(self.connection.envelopes)
        elif sql.startswith("INSERT INTO tblContributionBatch"):
            self.lastrowid = 21
        elif sql.startswith("INSERT INTO tblContribution "):
            self.lastrowid = 31
        else:
            self.rows = []

    def fetchall(self): return self.rows
    def fetchone(self): return self.rows[0] if self.rows else None
    def close(self): pass


class Connection:
    def __init__(self):
        self.calls, self.commits, self.rollbacks = [], 0, 0
        self.batch, self.envelopes = (4, "DRAFT"), []
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


if __name__ == "__main__": unittest.main()
