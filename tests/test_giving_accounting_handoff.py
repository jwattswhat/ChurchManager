"""Tests for privacy-safe giving-to-accounting handoff."""

import unittest
from datetime import date
from decimal import Decimal

from giving.accounting_handoff import GivingAccountingHandoff
from giving.validation import GivingValidationError


class Authorization:
    def require(self, _permission, _operation=None):
        return None


class Cursor:
    def __init__(self, connection):
        self.connection = connection; self.rows = []; self.one = None
        self.lastrowid = 0; self.rowcount = 0

    def execute(self, sql, values=()):
        self.connection.calls.append((sql, values)); self.rowcount = 0
        if sql.startswith("SELECT b.ChurchID"):
            self.one = (7, 4, date(2026, 8, 21), "READY", Decimal("25.00"),
                        None, "Sunday offering", 11, "PROHIBITED", None, 2)
        elif sql.startswith("SELECT ID FROM tblAccountingOrganization"):
            self.one = (values[0],) if self.connection.organization_owned else None
        elif sql.startswith("SELECT ba.ID FROM tblAccountingBankAccount"):
            self.one = (values[0],) if self.connection.bank_owned else None
        elif sql.startswith("SELECT COUNT(*) FROM tblContributionAllocation"):
            self.one = (1 if self.connection.invalid_allocations else 0,)
        elif sql.startswith("SELECT p.ID FROM tblAccountingFiscalPeriod"):
            self.rows = [(31,)]
        elif sql.startswith("SELECT a.FundID"):
            self.rows = [(5, 12, None, Decimal("20.00")),
                         (6, 13, 9, Decimal("5.00"))]
        elif sql.startswith("INSERT INTO tblAccountingTransaction "):
            self.lastrowid = 77
        elif sql.startswith("UPDATE tblContributionBatch"):
            self.rowcount = 1

    def fetchone(self): return self.one
    def fetchall(self): return self.rows
    def close(self): pass


class Connection:
    def __init__(self):
        self.calls = []; self.commits = 0; self.rollbacks = 0
        self.organization_owned = True; self.bank_owned = True; self.invalid_allocations = False
    def cursor(self): return Cursor(self)
    def commit(self): self.commits += 1
    def rollback(self): self.rollbacks += 1


class GivingAccountingHandoffTests(unittest.TestCase):
    def test_creates_balanced_fund_summary_without_donor_identity(self):
        connection = Connection()
        transaction_id = GivingAccountingHandoff(connection, 3, Authorization()).send(21)
        self.assertEqual((transaction_id, connection.commits), (77, 1))
        sql = "\n".join(item[0] for item in connection.calls)
        self.assertIn("'CASH_RECEIPT','READY'", sql)
        self.assertIn("BATCH_SENT_TO_ACCOUNTING", sql)
        self.assertNotIn("ContributorID", sql)
        self.assertNotIn("EnvelopeNumber", sql)
        self.assertIn("HAVING SUM(a.Amount)>0", sql)
        self.assertIn("DirectionStatus<>'RETURNED'", sql)
        lines = [values for statement, values in connection.calls
                 if statement.startswith("INSERT INTO tblAccountingTransactionLine")]
        self.assertEqual(len(lines), 4)
        self.assertEqual(sum((Decimal(row[-1]) for row in lines[:2])), Decimal("25.00"))

    def test_rejects_cross_church_organization_before_accounting_insert(self):
        connection = Connection(); connection.organization_owned = False
        with self.assertRaisesRegex(GivingValidationError, "belonging to this church"):
            GivingAccountingHandoff(connection, 3, Authorization()).send(21)
        self.assertFalse(any(sql.startswith("INSERT INTO tblAccountingTransaction ")
                             for sql, _values in connection.calls))
        self.assertEqual((connection.commits, connection.rollbacks), (0, 1))


if __name__ == "__main__": unittest.main()
