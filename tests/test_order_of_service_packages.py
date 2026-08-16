"""Contract tests for safe Order of Service package catalogs."""

from copy import deepcopy
from pathlib import Path
import unittest

from order_of_service_packages import (
    OrderOfServicePackageError, OrderOfServicePackageImporter,
    OrderOfServicePackageValidator,
)


ROOT = Path(__file__).parents[1]


class RecordingCursor:
    def __init__(self, connection):
        self.connection = connection; self.current = None; self.lastrowid = None

    def execute(self, sql, values=()):
        self.connection.calls.append((sql, values))
        if self.connection.fail_on and self.connection.fail_on in sql:
            raise RuntimeError("fictional database failure")
        if "SELECT ID,PackageVersion" in sql:
            self.current = self.connection.package_row
        elif "SELECT ID,PackageID,IsStarter" in sql:
            self.current = self.connection.template_row
        else:
            self.current = None
        if "INSERT INTO tblOrderOfServicePackage " in sql: self.lastrowid = 7
        if "INSERT INTO tblBulletinOrderTemplate " in sql: self.lastrowid = 11

    def fetchone(self): return self.current
    def close(self): pass


class RecordingConnection:
    def __init__(self, package_row=None, template_row=None, fail_on=None):
        self.package_row = package_row; self.template_row = template_row
        self.fail_on = fail_on; self.calls = []; self.commits = 0; self.rollbacks = 0

    def cursor(self): return RecordingCursor(self)
    def commit(self): self.commits += 1
    def rollback(self): self.rollbacks += 1


def package():
    return {
        "package_code": "sample-service-outlines",
        "package_version": "1.0.0",
        "title": "Sample Service Outlines",
        "template_prefix": "SMP ",
        "source_name": "ChurchManager",
        "source_reference": "Approved outline source",
        "package_notice": "Planning metadata only",
        "hymnal_package_code": "sample-hymnal",
        "minimum_hymnal_version": "1.0.0",
        "schema_version": 1,
        "checksum": "a" * 64,
        "templates": [{
            "template_key": "sample-service-one",
            "name": "SMP Sample Service One",
            "description": "A short planning outline.",
            "hymnal_package_code": "sample-hymnal",
            "lines": [
                {"line_key": "gathering.heading", "sequence": 1,
                 "line_type": "HEADING", "label": "Gathering"},
                {"line_key": "gathering.hymn", "sequence": 2,
                 "line_type": "HYMN", "label": "Opening Hymn",
                 "value_source": "SUGGESTED_USE", "value_key": "opening-hymn",
                 "reference": "Opening Hymn", "condition": "ALWAYS"},
            ],
            "required_positions": [{"role_key": "reader", "required_count": 1}],
        }],
    }


class OrderOfServicePackageTests(unittest.TestCase):
    def validator(self):
        return OrderOfServicePackageValidator(installed_hymnals={"sample-hymnal"})

    def test_valid_metadata_only_package_returns_counts(self):
        result = self.validator().validate(package(), actual_checksum="a" * 64)
        self.assertEqual(result.package_code, "sample-service-outlines")
        self.assertEqual((result.template_count, result.line_count, result.role_count), (1, 2, 1))

    def test_missing_hymnal_dependency_is_rejected(self):
        with self.assertRaisesRegex(OrderOfServicePackageError, "not installed"):
            OrderOfServicePackageValidator().validate(package())

    def test_no_hymnal_package_is_allowed(self):
        value = package(); value["hymnal_package_code"] = None
        value["templates"][0]["hymnal_package_code"] = None
        self.assertEqual(self.validator().validate(value).template_count, 1)

    def test_template_prefix_uses_abbreviation_and_space(self):
        value = package(); value["template_prefix"] = "LSB_"
        with self.assertRaisesRegex(OrderOfServicePackageError, "followed by one space"):
            self.validator().validate(value)
        value = package(); value["templates"][0]["name"] = "SMP_Sample Service One"
        with self.assertRaisesRegex(OrderOfServicePackageError, "must begin"):
            self.validator().validate(value)

    def test_checksum_mismatch_is_rejected(self):
        with self.assertRaisesRegex(OrderOfServicePackageError, "does not match"):
            self.validator().validate(package(), actual_checksum="b" * 64)

    def test_prohibited_content_fields_are_rejected(self):
        for field in ("full_body", "lyrics", "music_notation", "attachment"):
            with self.subTest(field=field):
                value = package(); value["templates"][0]["lines"][0][field] = "prohibited"
                with self.assertRaisesRegex(OrderOfServicePackageError, "Prohibited content field"):
                    self.validator().validate(value)

    def test_markup_media_and_long_text_are_rejected(self):
        for content in ("<p>Published text</p>", "data:image/png;base64,abc", "music.pdf"):
            with self.subTest(content=content):
                value = package(); value["templates"][0]["lines"][0]["note"] = content
                with self.assertRaisesRegex(OrderOfServicePackageError, "prohibited"):
                    self.validator().validate(value)
        value = package(); value["templates"][0]["lines"][0]["label"] = "x" * 121
        with self.assertRaisesRegex(OrderOfServicePackageError, "120"):
            self.validator().validate(value)

    def test_local_namespace_and_duplicate_keys_are_rejected(self):
        value = package(); value["templates"][0]["template_key"] = "local-copy"
        with self.assertRaises(OrderOfServicePackageError): self.validator().validate(value)
        value = package(); duplicate = deepcopy(value["templates"][0]["lines"][0]); duplicate["sequence"] = 3
        value["templates"][0]["lines"].append(duplicate)
        with self.assertRaisesRegex(OrderOfServicePackageError, "unique"):
            self.validator().validate(value)

    def test_unknown_types_conditions_and_fields_fail_closed(self):
        value = package(); value["templates"][0]["lines"][0]["line_type"] = "FULL_SERVICE"
        with self.assertRaisesRegex(OrderOfServicePackageError, "Unsupported"):
            self.validator().validate(value)
        value = package(); value["templates"][0]["lines"][0]["condition"] = "MAYBE"
        with self.assertRaisesRegex(OrderOfServicePackageError, "Unsupported"):
            self.validator().validate(value)
        value = package(); value["surprise"] = True
        with self.assertRaisesRegex(OrderOfServicePackageError, "Unknown field"):
            self.validator().validate(value)

    def test_migration_adds_package_ownership_and_removes_prohibited_columns(self):
        source = (ROOT / "migrations" / "072_add_order_of_service_package_catalog.sql").read_text(encoding="utf-8")
        self.assertIn("tblOrderOfServicePackage", source)
        self.assertIn("TemplateKey", source)
        self.assertIn("PackageID", source)
        self.assertIn("LineKey", source)
        self.assertIn("DROP COLUMN IF EXISTS LegacyContent", source)
        self.assertIn("DROP COLUMN IF EXISTS GeneratedHtml", source)
        self.assertIn("ON DELETE RESTRICT", source)
        self.assertNotIn("SourceLegacyName", source)

    def test_import_fields_add_display_prefix_and_package_role_metadata(self):
        source = (ROOT / "migrations" / "073_add_order_of_service_package_import_fields.sql").read_text(encoding="utf-8")
        self.assertIn("TemplatePrefix", source)
        self.assertIn("tblOrderOfServicePackageRoleRequirement", source)
        self.assertIn("tblOrderOfServicePackageImport", source)

    def test_import_is_transactional_and_records_package_counts(self):
        connection = RecordingConnection()
        result = OrderOfServicePackageImporter(
            connection, installed_hymnals={"sample-hymnal"},
            hymnal_ids={"sample-hymnal": 2},
        ).install(package(), actual_checksum="a" * 64)
        self.assertEqual(result.line_count, 2)
        self.assertEqual(connection.commits, 1)
        self.assertEqual(connection.rollbacks, 0)
        sql = "\n".join(call[0] for call in connection.calls)
        self.assertIn("INSERT INTO tblOrderOfServicePackageImport", sql)
        self.assertIn("INSERT INTO tblBulletinOrderLine", sql)
        self.assertIn("INSERT INTO tblOrderOfServicePackageRoleRequirement", sql)
        self.assertNotIn("DELETE FROM tblServiceBulletinOrder", sql)

    def test_import_failure_rolls_back_everything(self):
        connection = RecordingConnection(fail_on="INSERT INTO tblBulletinOrderLine")
        importer = OrderOfServicePackageImporter(
            connection, installed_hymnals={"sample-hymnal"},
            hymnal_ids={"sample-hymnal": 2},
        )
        with self.assertRaisesRegex(RuntimeError, "fictional"):
            importer.install(package())
        self.assertEqual(connection.commits, 0)
        self.assertEqual(connection.rollbacks, 1)

    def test_validation_happens_before_database_access(self):
        value = package(); value["templates"][0]["lines"][0]["lyrics"] = "No"
        connection = RecordingConnection()
        with self.assertRaises(OrderOfServicePackageError):
            OrderOfServicePackageImporter(connection).install(value)
        self.assertEqual(connection.calls, [])

    def test_package_cannot_overwrite_local_template(self):
        connection = RecordingConnection(template_row=(44, None, 0))
        importer = OrderOfServicePackageImporter(
            connection, installed_hymnals={"sample-hymnal"},
            hymnal_ids={"sample-hymnal": 2},
        )
        with self.assertRaisesRegex(OrderOfServicePackageError, "cannot overwrite"):
            importer.install(package())
        self.assertEqual(connection.rollbacks, 1)


if __name__ == "__main__":
    unittest.main()
