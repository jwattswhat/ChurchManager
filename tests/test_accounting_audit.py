import unittest
from datetime import date

from accounting.audit_service import AccountingAuditService


class Cursor:
    def __init__(self):
        self.calls = []
    def execute(self, sql, values=()):
        self.calls.append((sql, values))
    def fetchall(self):
        return [(1,)]
    def close(self):
        pass


class Connection:
    def __init__(self):
        self.cursors = []
    def cursor(self):
        cursor = Cursor(); self.cursors.append(cursor); return cursor


class AccountingAuditServiceTests(unittest.TestCase):
    def test_events_are_read_only_and_newest_first(self):
        connection = Connection()
        result = AccountingAuditService(connection).events()
        sql, values = connection.cursors[0].calls[0]
        self.assertEqual(result, [(1,)])
        self.assertTrue(sql.startswith("SELECT"))
        self.assertIn("ORDER BY ae.OccurredAt DESC, ae.ID DESC", sql)
        self.assertIn("LIMIT 1000", sql)
        self.assertEqual(values, ())

    def test_all_filters_are_parameterized(self):
        connection = Connection()
        AccountingAuditService(connection).events(
            3, "Sarah", "POST", "TRANSACTION", date(2026, 1, 1), date(2026, 1, 31)
        )
        sql, values = connection.cursors[0].calls[0]
        self.assertNotIn("Sarah", sql)
        self.assertIn("ae.OrganizationID=?", sql)
        self.assertIn("DATE_ADD(?, INTERVAL 1 DAY)", sql)
        self.assertEqual(values, (3, "%Sarah%", "%Sarah%", "%POST%",
                                  "%TRANSACTION%", "%TRANSACTION%",
                                  date(2026, 1, 1), date(2026, 1, 31)))

    def test_organizations_are_alphabetical(self):
        connection = Connection()
        AccountingAuditService(connection).organizations()
        sql, values = connection.cursors[0].calls[0]
        self.assertIn("ORDER BY LegalName", sql)
        self.assertEqual(values, ())

    def test_through_date_cannot_precede_from_date(self):
        connection = Connection()
        with self.assertRaisesRegex(ValueError, "Through date"):
            AccountingAuditService(connection).events(
                date_from=date(2026, 2, 1), date_to=date(2026, 1, 31)
            )
        self.assertEqual(connection.cursors, [])


if __name__ == "__main__":
    unittest.main()
