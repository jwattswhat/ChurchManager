"""Opt-in, read-only ChurchManager test-database checks.

The class is skipped unless CHURCHMANAGER_RUN_DB_TESTS=1.  It refuses to use a
database named ChurchDB and performs SELECT statements only.  It does not use or
test JSForm.
"""

from __future__ import annotations

import os
import json
import unittest
from pathlib import Path

from churchmanager_mode import resolve_database


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TABLES = {
    "tblAnnouncement",
    "tblAttendanceEvent",
    "tblChurch",
    "tblFamily",
    "tblPerson",
    "tblPrayer",
    "tblReports",
    "tblService",
    "tblSermon",
    "tblUser",
    "tblRole",
    "tblPermission",
    "tblUserRole",
    "tblRolePermission",
    "tblSecurityAuditEvent",
    "tblAccountingOrganization",
    "tblAccountingAccount",
    "tblAccountingFund",
    "tblAccountingFunction",
    "tblAccountingFiscalYear",
    "tblAccountingFiscalPeriod",
    "tblAccountingPayee",
    "tblAccountingTransaction",
    "tblAccountingTransactionLine",
    "tblAccountingAttachment",
    "tblAccountingAuditEvent",
}
REMOVED_REPORT_CODES = {"CFCA01", "CFCR01", "CFGR01", "CMDN01", "CMDN02"}


def database_tests_enabled() -> bool:
    return os.environ.get("CHURCHMANAGER_RUN_DB_TESTS") == "1"


@unittest.skipUnless(database_tests_enabled(), "Set CHURCHMANAGER_RUN_DB_TESTS=1 for read-only test-database checks")
class TestChurchManagerDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
        configured = config["database_settings"]
        settings = resolve_database(
            {
                "server": configured["host"], "database": configured["database"],
                "user": configured["user"], "password": None,
                "test_mode": True, "jsform_database": None,
            }, config,
        )
        database = settings["database"]
        if not database:
            raise unittest.SkipTest("CHURCHMANAGER_TEST_DB_NAME is not set")
        if database.casefold() == "churchdb":
            raise RuntimeError("Safety stop: database tests refuse to run against ChurchDB")
        if "test" not in database.casefold():
            raise RuntimeError("Safety stop: test database name must contain the word 'test'")

        try:
            import mariadb
        except ImportError as error:
            raise unittest.SkipTest("The mariadb Python connector is unavailable") from error

        cls.connection = mariadb.connect(
            host=settings["server"],
            port=int(configured.get("port", 3306)),
            database=database,
            user=settings["user"],
            password=settings["password"],
            connect_timeout=5,
        )

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "connection"):
            cls.connection.close()

    def query(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def test_required_operational_tables_exist(self):
        rows = self.query(
            "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE()"
        )
        available = {row[0] for row in rows}
        self.assertEqual(REQUIRED_TABLES - available, set())

    def test_sermon_ids_are_present_and_unique(self):
        missing = self.query("SELECT COUNT(*) FROM tblSermon WHERE ID IS NULL")[0][0]
        duplicates = self.query(
            "SELECT ID, COUNT(*) FROM tblSermon GROUP BY ID HAVING COUNT(*) > 1"
        )
        self.assertEqual(missing, 0, "Sermon records without IDs were found")
        self.assertEqual(duplicates, [], "Duplicate sermon IDs were found")

    def test_report_catalog_codes_are_unique(self):
        duplicates = self.query(
            "SELECT Report, COUNT(*) FROM tblReports "
            "WHERE Report IS NOT NULL AND Report <> '' GROUP BY Report HAVING COUNT(*) > 1"
        )
        self.assertEqual(duplicates, [], "Duplicate report codes were found in tblReports")

    def test_report_catalog_patterns_exist(self):
        rows = self.query(
            "SELECT DISTINCT Report FROM tblReports "
            "WHERE Report IS NOT NULL AND Report <> '' "
            "AND (Batch IS NULL OR TRIM(Batch) = '')"
        )
        available = {
            path.stem.casefold()
            for pattern in ("*.lrxml", "*.lrsml")
            for path in (ROOT / "LimeReportPattern").glob(pattern)
        }
        removed = {code.casefold() for code in REMOVED_REPORT_CODES}
        missing = sorted(
            code for (code,) in rows
            if str(code).casefold() not in available and str(code).casefold() not in removed
        )
        self.assertEqual(missing, [], "Report catalog codes without local LimeReport patterns")

    def test_sample_operational_tables_are_readable(self):
        for table in sorted(REQUIRED_TABLES):
            with self.subTest(table=table):
                self.query(f"SELECT 1 FROM `{table}` LIMIT 1")

    def test_security_catalog_is_seeded(self):
        roles = {row[0] for row in self.query("SELECT Name FROM tblRole WHERE Active=1")}
        permissions = {
            row[0] for row in self.query("SELECT Name FROM tblPermission WHERE Active=1")
        }
        self.assertIn("Master Administrator", roles)
        self.assertIn("Treasurer", roles)
        self.assertIn("security.users.manage", permissions)
        self.assertIn("accounting.transactions.post", permissions)

    def test_security_migration_is_recorded(self):
        rows = self.query(
            "SELECT version FROM schema_migrations WHERE version='003_add_user_security.sql'"
        )
        self.assertEqual(rows, [("003_add_user_security.sql",)])

    def test_record_attendance_compatibility_views_are_readable(self):
        self.query("SELECT ID, dt, Description, AttendanceType FROM vwattendance LIMIT 1")
        self.query("SELECT ID, FirstName, LastName, Member FROM vmperson LIMIT 1")

    def test_accounting_foundation_and_role_defaults_are_installed(self):
        rows = self.query(
            "SELECT version FROM schema_migrations "
            "WHERE version='006_add_accounting_ledger_foundation.sql'"
        )
        self.assertEqual(rows, [("006_add_accounting_ledger_foundation.sql",)])
        permissions = {
            row[0] for row in self.query(
                "SELECT p.Name FROM tblRole r "
                "JOIN tblRolePermission rp ON rp.RoleID=r.ID "
                "JOIN tblPermission p ON p.ID=rp.PermissionID "
                "WHERE r.Name='Accounting Entry Clerk'"
            )
        }
        self.assertIn("accounting.transactions.create", permissions)
        self.assertNotIn("accounting.transactions.post", permissions)

    def test_sample_accounting_setup_is_complete(self):
        rows = self.query(
            "SELECT o.ID, "
            "(SELECT COUNT(*) FROM tblAccountingAccount a WHERE a.OrganizationID=o.ID), "
            "(SELECT COUNT(*) FROM tblAccountingFund f WHERE f.OrganizationID=o.ID), "
            "(SELECT COUNT(*) FROM tblAccountingFunction fn WHERE fn.OrganizationID=o.ID), "
            "(SELECT COUNT(*) FROM tblAccountingFiscalPeriod p "
            " JOIN tblAccountingFiscalYear y ON y.ID=p.FiscalYearID "
            " WHERE y.OrganizationID=o.ID) "
            "FROM tblAccountingOrganization o "
            "WHERE o.LegalName='ChurchManager Sample Congregation'"
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1:], (34, 7, 7, 12))
        audit = self.query(
            "SELECT Action FROM tblAccountingAuditEvent "
            "WHERE OrganizationID=? AND Action='ACCOUNTING_SETUP_CREATED'",
            (rows[0][0],),
        )
        self.assertEqual(audit, [("ACCOUNTING_SETUP_CREATED",)])
