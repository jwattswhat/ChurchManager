import hashlib
import tempfile
import unittest
from pathlib import Path

from baseline_schema import (
    build_baseline_artifact,
    canonical_schema_dump,
    write_baseline_artifact,
)


class BaselineSchemaTests(unittest.TestCase):
    def test_normalizes_qualifier_definer_and_increment_state(self):
        source = (
            "-- MariaDB dump\n"
            "CREATE TABLE `ChurchDBTest`.`tblChurch` (`ID` int) AUTO_INCREMENT=27;\n"
            "CREATE DEFINER=`church`@`localhost` VIEW `rpt_church` AS SELECT ID FROM `ChurchDBTest`.`tblChurch`;\n"
        )
        result = canonical_schema_dump(source, "ChurchDBTest")
        self.assertNotIn("ChurchDBTest", result)
        self.assertNotIn("DEFINER", result)
        self.assertNotIn("AUTO_INCREMENT=27", result)
        self.assertIn("CREATE TABLE `tblChurch`", result)

    def test_does_not_sanitize_obsolete_identifiers(self):
        with self.assertRaisesRegex(ValueError, "hygiene check failed"):
            canonical_schema_dump("CREATE TABLE tblReading (OldID int);", "ChurchDBTest")

    def test_manifest_contains_schema_and_migration_checksums(self):
        with tempfile.TemporaryDirectory() as folder:
            migrations = Path(folder) / "migrations"
            migrations.mkdir()
            sql = "CREATE TABLE sample (ID int);"
            migration = migrations / "001_sample.sql"
            migration.write_text(sql, encoding="utf-8")
            artifact = build_baseline_artifact(sql, "ChurchDBTest", migrations, "0.1.0")
        self.assertEqual(
            artifact.manifest["schema_sha256"],
            hashlib.sha256(artifact.sql.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            artifact.manifest["represented_migrations"][0]["checksum"],
            hashlib.sha256(sql.encode("utf-8")).hexdigest(),
        )

    def test_writes_only_validated_artifact(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            migrations = root / "migrations"
            migrations.mkdir()
            (migrations / "001_sample.sql").write_text("SELECT 1;", encoding="utf-8")
            artifact = build_baseline_artifact(
                "CREATE TABLE sample (ID int);", "ChurchDBTest", migrations, "0.1.0",
            )
            schema, manifest = write_baseline_artifact(artifact, root / "installation")
            self.assertTrue(schema.is_file())
            self.assertTrue(manifest.is_file())


if __name__ == "__main__":
    unittest.main()
