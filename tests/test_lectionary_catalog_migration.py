"""Structural tests for the additive versioned lectionary catalog migration."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LectionaryCatalogMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (
            ROOT / "migrations" / "076_add_versioned_lectionary_catalog.sql"
        ).read_text(encoding="utf-8-sig")

    def test_migration_adds_versioned_package_edition_and_cycle_structure(self):
        for table in (
            "tblLectionaryPackage", "tblLectionaryPackageImport",
            "tblLectionaryEdition", "tblLectionaryCycle",
        ):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", self.source)
        for field in ("SystemCode", "EditionCode", "CycleCode", "ProperKey", "AppointmentKey"):
            self.assertIn(field, self.source)

    def test_current_catalog_remains_available_during_additive_transition(self):
        self.assertNotIn("DROP TABLE", self.source)
        self.assertNotIn("DELETE FROM tblPropers", self.source)
        self.assertNotIn("DELETE FROM tblReading", self.source)
        self.assertIn("PrimaryLectionaryEditionID", self.source)

    def test_stable_keys_and_history_use_restrictive_foreign_keys(self):
        self.assertIn("uq_propers_stable_key", self.source)
        self.assertIn("uq_reading_appointment_key", self.source)
        self.assertGreaterEqual(self.source.count("ON DELETE RESTRICT"), 8)
        self.assertNotIn("FOREIGN_KEY_CHECKS", self.source)

    def test_package_import_log_records_all_entity_counts(self):
        for field in (
            "SystemCount", "EditionCount", "CycleCount", "ProperCount", "AppointmentCount",
        ):
            self.assertIn(field, self.source)


if __name__ == "__main__":
    unittest.main()
