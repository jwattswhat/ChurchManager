"""Opt-in, read-only ChurchManager test-database checks.

The class is skipped unless CHURCHMANAGER_RUN_DB_TESTS=1.  It refuses to use a
database named ChurchDB and performs SELECT statements only.  It does not use or
test JSForm.
"""

from __future__ import annotations

import os
import json
import re
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
    "tblAccountingBudget",
    "tblAccountingBudgetLine",
    "tblLectionarySystem",
}
REMOVED_REPORT_CODES = {"CFCA01", "CFCR01", "CFGR01", "CMDN01", "CMDN02"}


def database_tests_enabled() -> bool:
    return os.environ.get("CHURCHMANAGER_RUN_DB_TESTS") == "1"


@unittest.skipUnless(database_tests_enabled(), "Set CHURCHMANAGER_RUN_DB_TESTS=1 for read-only test-database checks")
class TestChurchManagerDatabase(unittest.TestCase):
    def test_json_form_fields_exist_and_temporal_types_match(self):
        schema_rows = self.query(
            "SELECT TABLE_NAME,COLUMN_NAME,DATA_TYPE FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA=DATABASE()"
        )
        schema = {
            (table.casefold(), column.casefold()): data_type.casefold()
            for table, column, data_type in schema_rows
        }
        missing = []
        incompatible = []
        temporal_controls = {
            "date": {"DatePickerCtrl"},
            "datetime": {"DateTime"},
            "timestamp": {"DateTime"},
            "time": {"TimePickerCtrl"},
        }
        for path in sorted((ROOT / "Forms").glob("*.json")):
            document = json.loads(path.read_text(encoding="utf-8-sig"))
            form = document[next(iter(document))]
            table = form.get("FORM", {}).get("table", {})
            table_name = table.get("name")
            if not table_name:
                continue
            controls = form.get("CONTROLS", {})
            for field in table.get("fields", []):
                if not isinstance(field, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", field):
                    continue
                key = (table_name.casefold(), field.casefold())
                data_type = schema.get(key)
                if data_type is None:
                    missing.append(f"{path.name}: {table_name}.{field}")
                    continue
                control = controls.get(field)
                allowed = temporal_controls.get(data_type)
                if control and allowed and control.get("type") not in allowed:
                    incompatible.append(
                        f"{path.name}: {field} is {data_type}, control is {control.get('type')}"
                    )
        self.assertEqual(missing, [])
        self.assertEqual(incompatible, [])

    def test_printed_lsb_tunes_are_loaded_without_service_builder_guesses(self):
        rows = self.query(
            "SELECT "
            "SUM(CASE WHEN CAST(SUBSTRING_INDEX(TRIM(h.Hymn),' ',-1) AS UNSIGNED) "
            "BETWEEN 331 AND 966 AND h.Tune IS NOT NULL THEN 1 ELSE 0 END), "
            "SUM(CASE WHEN CAST(SUBSTRING_INDEX(TRIM(h.Hymn),' ',-1) AS UNSIGNED) "
            "NOT BETWEEN 331 AND 966 AND h.Tune IS NOT NULL THEN 1 ELSE 0 END) "
            "FROM tblHymn h JOIN tblHymnal y ON y.ID=h.HymnalID WHERE y.Hymnal='LSB'"
        )
        self.assertEqual(rows, [(634, 0)])

    def test_copyrighted_introit_storage_is_removed(self):
        columns = {
            (row[0], row[1])
            for row in self.query(
                "SELECT TABLE_NAME,COLUMN_NAME FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA=DATABASE() AND "
                "((TABLE_NAME='tblService' AND COLUMN_NAME='PsalmorIntroit') OR "
                "(TABLE_NAME='tblPropers' AND COLUMN_NAME='Introit'))"
            )
        }
        self.assertEqual(columns, set())
        self.assertEqual(
            self.query(
                "SELECT version FROM schema_migrations "
                "WHERE version='037_remove_copyrighted_introit_fields.sql'"
            ),
            [("037_remove_copyrighted_introit_fields.sql",)],
        )

    def test_used_fiscal_period_boundary_trigger_exists(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.TRIGGERS "
                "WHERE TRIGGER_SCHEMA=DATABASE() "
                "AND TRIGGER_NAME='trg_acct_period_lock_used_boundaries'"
            )
            self.assertEqual(cursor.fetchone()[0], 1)
        finally:
            cursor.close()
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
        available = {row[0].casefold() for row in rows}
        required = {name.casefold() for name in REQUIRED_TABLES}
        self.assertEqual(required - available, set())

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

    def test_attendance_report_views_are_readable(self):
        self.query(
            "SELECT ID, ChurchID, DateTime, AttendanceType, HandCount, "
            "KnownAttendance, UnnamedAttendance, HandCountCommunion "
            "FROM rpt_attendance_event LIMIT 1"
        )
        self.query(
            "SELECT ID, ChurchID, DateTime, AttendanceType, EventCount, Attendance, "
            "KnownAttendance, UnnamedAttendance, Communion "
            "FROM rpt_attendance_weekly LIMIT 1"
        )

    def test_propers_use_lectionary_systems_and_lookup_labels(self):
        migration = self.query(
            "SELECT version FROM schema_migrations "
            "WHERE version='007_normalize_lectionary_systems.sql'"
        )
        self.assertEqual(migration, [("007_normalize_lectionary_systems.sql",)])
        orphan_count = self.query(
            "SELECT COUNT(*) FROM tblPropers p "
            "LEFT JOIN tblLectionarySystem ls ON ls.ID=p.LectionarySystemID "
            "WHERE ls.ID IS NULL"
        )[0][0]
        self.assertEqual(orphan_count, 0)
        proper_count = self.query("SELECT COUNT(*) FROM tblPropers")[0][0]
        lookup_count = self.query(
            "SELECT COUNT(*) FROM vwPropersLookup "
            "WHERE DisplayName IS NOT NULL AND TRIM(DisplayName) <> ''"
        )[0][0]
        self.assertEqual(lookup_count, proper_count)
        old_column = self.query(
            "SELECT COUNT(*) FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tblPropers' "
            "AND COLUMN_NAME='Lectionary'"
        )[0][0]
        self.assertEqual(old_column, 0)
        obsolete_option = self.query(
            "SELECT COUNT(*) FROM tblOptions "
            "WHERE OptionFor='Lectionary' AND OptionType='Current'"
        )[0][0]
        self.assertEqual(obsolete_option, 0)

    def test_lsb_readings_use_liturgical_roles(self):
        migration = self.query(
            "SELECT version FROM schema_migrations "
            "WHERE version='032_normalize_lsb_reading_roles.sql'"
        )
        self.assertEqual(migration, [("032_normalize_lsb_reading_roles.sql",)])
        ordinal_count = self.query(
            "SELECT COUNT(*) FROM tblReading r "
            "JOIN tblPropers p ON p.ID=r.PropersID "
            "JOIN tblLectionarySystem ls ON ls.ID=p.LectionarySystemID "
            "WHERE ls.Name LIKE 'LSB %' "
            "AND LOWER(TRIM(r.Reading)) IN "
            "('first','first reading','second','second reading','third','third reading')"
        )[0][0]
        self.assertEqual(ordinal_count, 0)
        roles = {
            row[0] for row in self.query(
                "SELECT DISTINCT r.Reading FROM tblReading r "
                "JOIN tblPropers p ON p.ID=r.PropersID "
                "JOIN tblLectionarySystem ls ON ls.ID=p.LectionarySystemID "
                "WHERE ls.Name LIKE 'LSB %'"
            )
        }
        self.assertTrue({"Old Testament", "Epistle", "Gospel"}.issubset(roles))

    def test_suggested_hymns_use_full_liturgical_role_names(self):
        migration = self.query(
            "SELECT version FROM schema_migrations "
            "WHERE version='033_rename_suggested_hymn_roles.sql'"
        )
        self.assertEqual(migration, [("033_rename_suggested_hymn_roles.sql",)])
        old_names = self.query(
            "SELECT COUNT(*) FROM tblProperHymnSuggestion "
            "WHERE SuggestedAs IN ('Entrance','Of the Day')"
        )[0][0]
        self.assertEqual(old_names, 0)
        roles = {
            row[0] for row in self.query(
                "SELECT DISTINCT SuggestedAs FROM tblProperHymnSuggestion"
            )
        }
        self.assertTrue({"Hymn of Invocation", "Hymn of the Day"}.issubset(roles))

    def test_ds1_starter_and_suggestions_use_distribution_hymns(self):
        migration = self.query(
            "SELECT version FROM schema_migrations "
            "WHERE version='034_add_ds1_distribution_hymns.sql'"
        )
        self.assertEqual(migration, [("034_add_ds1_distribution_hymns.sql",)])
        old_role_count = self.query(
            "SELECT COUNT(*) FROM tblProperHymnSuggestion WHERE SuggestedAs='Communion'"
        )[0][0]
        self.assertEqual(old_role_count, 0)
        new_role_count = self.query(
            "SELECT COUNT(*) FROM tblProperHymnSuggestion "
            "WHERE SuggestedAs='Distribution Hymn'"
        )[0][0]
        self.assertGreater(new_role_count, 0)
        slots = self.query(
            "SELECT l.Sequence,l.Label,l.ValueKey FROM tblBulletinOrderLine l "
            "JOIN tblBulletinOrderTemplate t ON t.ID=l.TemplateID "
            "WHERE t.Name='LCMS Divine Service One' AND t.IsStarter=1 "
            "AND l.ValueSource='SERVICE_HYMN' AND l.ValueKey='Distribution Hymn' "
            "ORDER BY l.Sequence"
        )
        self.assertEqual(
            slots,
            [
                (240, "Distribution Hymn", "Distribution Hymn"),
                (241, "Distribution Hymn", "Distribution Hymn"),
                (242, "Distribution Hymn", "Distribution Hymn"),
            ],
        )

    def test_bulletin_order_hymnal_link_is_optional_and_seeded(self):
        migration = self.query(
            "SELECT version FROM schema_migrations "
            "WHERE version='028_link_bulletin_orders_to_hymnals.sql'"
        )
        self.assertEqual(migration, [("028_link_bulletin_orders_to_hymnals.sql",)])
        column = self.query(
            "SELECT IS_NULLABLE FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tblBulletinOrderTemplate' "
            "AND COLUMN_NAME='HymnalID'"
        )
        self.assertEqual(column, [("YES",)])
        starter = self.query(
            "SELECT h.Hymnal FROM tblBulletinOrderTemplate t "
            "JOIN tblHymnal h ON h.ID=t.HymnalID "
            "WHERE t.Name='LCMS Divine Service One'"
        )
        self.assertEqual(starter, [("LSB",)])
        self.assertGreater(
            self.query(
                "SELECT COUNT(*) FROM tblBulletinOrderTemplate WHERE HymnalID IS NULL"
            )[0][0],
            0,
        )

    def test_church_default_lectionary_link_is_optional(self):
        migration = self.query(
            "SELECT version FROM schema_migrations "
            "WHERE version='029_add_church_primary_lectionary.sql'"
        )
        self.assertEqual(migration, [("029_add_church_primary_lectionary.sql",)])
        column = self.query(
            "SELECT IS_NULLABLE FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tblChurch' "
            "AND COLUMN_NAME='PrimaryLectionarySystemID'"
        )
        self.assertEqual(column, [("YES",)])
        orphan_count = self.query(
            "SELECT COUNT(*) FROM tblChurch c "
            "LEFT JOIN tblLectionarySystem ls ON ls.ID=c.PrimaryLectionarySystemID "
            "WHERE c.PrimaryLectionarySystemID IS NOT NULL AND ls.ID IS NULL"
        )[0][0]
        self.assertEqual(orphan_count, 0)

    def test_imported_lsb_lectionary_names_use_abbreviation(self):
        migration = self.query(
            "SELECT version FROM schema_migrations "
            "WHERE version='030_abbreviate_lsb_lectionary_names.sql'"
        )
        self.assertEqual(migration, [("030_abbreviate_lsb_lectionary_names.sql",)])
        names = {
            row[0] for row in self.query(
                "SELECT Name FROM tblLectionarySystem WHERE Name LIKE 'LSB %'"
            )
        }
        self.assertEqual(
            names,
            {
                "LSB Three-Year Lectionary",
                "LSB One-Year Lectionary",
                "LSB Feasts and Festivals",
                "LSB Occasions",
            },
        )
        long_names = self.query(
            "SELECT Name FROM tblLectionarySystem "
            "WHERE Name LIKE 'Lutheran Service Book %'"
        )
        self.assertEqual(long_names, [])

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

    def test_weekly_orders_are_independent_condition_aware_snapshots(self):
        migration = self.query(
            "SELECT version FROM schema_migrations "
            "WHERE version='054_preserve_weekly_order_snapshots.sql'"
        )
        self.assertEqual(migration, [("054_preserve_weekly_order_snapshots.sql",)])
        columns = {
            row[0]: row[1]
            for row in self.query(
                "SELECT COLUMN_NAME,IS_NULLABLE FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tblServiceBulletinOrder' "
                "AND COLUMN_NAME IN ('TemplateID','TemplateName')"
            )
        }
        self.assertEqual(columns, {"TemplateID": "YES", "TemplateName": "YES"})
        line_columns = {
            row[0] for row in self.query(
                "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tblServiceBulletinOrderLine' "
                "AND COLUMN_NAME IN ('ConditionType','ConditionValue')"
            )
        }
        self.assertEqual(line_columns, {"ConditionType", "ConditionValue"})
        delete_rule = self.query(
            "SELECT DELETE_RULE FROM information_schema.REFERENTIAL_CONSTRAINTS "
            "WHERE CONSTRAINT_SCHEMA=DATABASE() AND TABLE_NAME='tblServiceBulletinOrder' "
            "AND CONSTRAINT_NAME='fk_service_bulletin_order_template'"
        )
        self.assertEqual(delete_rule, [("SET NULL",)])

    def test_weekly_hymn_value_is_title_and_reference_is_number(self):
        migration = self.query(
            "SELECT version FROM schema_migrations "
            "WHERE version='055_separate_weekly_hymn_title_and_number.sql'"
        )
        self.assertEqual(migration, [("055_separate_weekly_hymn_title_and_number.sql",)])
        mismatches = self.query(
            "SELECT COUNT(*) FROM tblServiceBulletinOrderLine weekly_line "
            "JOIN tblHymnUsage hymn_usage "
            "ON hymn_usage.ServiceBulletinOrderLineID=weekly_line.ID "
            "JOIN tblHymn hymn_record ON hymn_record.ID=hymn_usage.HymnID "
            "WHERE weekly_line.ValueSource='SERVICE_HYMN' AND "
            "(COALESCE(weekly_line.WeeklyValue,'')<>COALESCE(hymn_record.Title,'') OR "
            "COALESCE(weekly_line.ReferenceText,'')<>COALESCE(hymn_record.Hymn,''))"
        )[0][0]
        self.assertEqual(mismatches, 0)

    def test_service_has_optional_liturgical_color_override(self):
        columns = self.query(
            "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tblService'"
        )
        self.assertIn("LiturgicalColorOverride", {row[0] for row in columns})

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
