import unittest
from pathlib import Path

from authorization import AuthorizationDenied
from report_access import ReportAccessService


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.result = []

    def execute(self, sql, values=()):
        if "WHERE r.ID=?" in sql:
            self.result = [(row[1], row[3]) for row in self.rows if row[0] == values[0]]
        else:
            self.result = list(self.rows)

    def fetchall(self):
        return self.result

    def fetchone(self):
        return self.result[0] if self.result else None

    def close(self):
        pass


class FakeConnection:
    __module__ = "mariadb.connections"
    def __init__(self, rows):
        self.rows = rows

    def cursor(self):
        return FakeCursor(self.rows)


class FakeAuthorization:
    def __init__(self, allowed):
        self.allowed = set(allowed)

    def has_permission(self, permission):
        return permission in self.allowed

    def require(self, permission, operation=None):
        if not self.has_permission(permission):
            raise AuthorizationDenied(operation or permission)


class FakeChoices:
    id = []
    display = []
    fielddata = []


class FakeControl:
    def __init__(self):
        self.choices = FakeChoices()
        self.items = None
        self.value = None

    def Set(self, items):
        self.items = items

    def ChangeValue(self, value):
        self.value = value


class FakeCatalogControl:
    def SetCatalogRows(self, rows):
        self.rows = rows


class TestReportAccessService(unittest.TestCase):
    ROWS = (
        (1, "CMWS01", "Worship Planning", "reports.worship.run"),
        (2, "CMMB01", "Member Directory", "reports.membership.contact"),
    )

    def service(self, allowed):
        return ReportAccessService(FakeConnection(self.ROWS), FakeAuthorization(allowed))

    def test_picker_contains_only_authorized_reports(self):
        control = FakeControl()
        count = self.service({"reports.worship.run"}).configure_picker(control)
        self.assertEqual(count, 1)
        self.assertEqual(control.choices.id, [1])
        self.assertEqual(control.items, ["Worship Planning (CMWS01)"])
        self.assertEqual(control.value, "")

    def test_catalog_grid_marks_customized_reports_blue(self):
        control = FakeCatalogControl()
        count = self.service({"reports.worship.run", "reports.membership.contact"}).configure_picker(
            control, {"CMMB01"},
        )
        self.assertEqual(count, 2)
        by_code = {row["values"][0]: row for row in control.rows}
        self.assertEqual(by_code["CMMB01"]["values"], ["CMMB01", "Member Directory", "Customized"])
        self.assertEqual(by_code["CMMB01"]["foreground"], "#0066CC")
        self.assertEqual(by_code["CMWS01"]["values"], ["CMWS01", "Worship Planning", "Starter"])

    def test_direct_report_invocation_rechecks_permission(self):
        service = self.service({"reports.worship.run"})
        self.assertEqual(service.require_report(1)[0], "CMWS01")
        with self.assertRaises(AuthorizationDenied):
            service.require_report(2)

    def test_missing_or_uncataloged_report_fails_closed(self):
        with self.assertRaises(AuthorizationDenied):
            self.service({"reports.worship.run"}).require_report(999)


class TestReportViewMigration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.sql = (root / "migrations" / "017_add_nonaccounting_report_views.sql").read_text(
            encoding="utf-8"
        )

    def test_private_contact_details_are_filtered_in_views(self):
        self.assertIn("FROM tblPersonContact WHERE Unlisted=0", self.sql)
        self.assertIn("FROM tblPersonAddress WHERE Unlisted=0", self.sql)
        self.assertIn("FROM tblFamilyContact WHERE Unlisted=0", self.sql)
        self.assertIn("FROM tblFamilyAddress WHERE Unlisted=0", self.sql)

    def test_directory_view_excludes_non_directory_families(self):
        self.assertIn("FROM tblFamily WHERE Directory=1", self.sql)

    def test_nonaccounting_migration_does_not_expose_security_or_ledger_tables(self):
        forbidden = (
            "tblUser",
            "tblRole",
            "tblUserRole",
            "tblPermission",
            "tblRolePermission",
            "tblAccountingTransaction",
            "tblAccountingTransactionLine",
        )
        for table in forbidden:
            self.assertNotIn(f"FROM {table}", self.sql)
            self.assertNotIn(f"JOIN {table}", self.sql)

if __name__ == "__main__":
    unittest.main()
