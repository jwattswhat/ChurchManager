"""Contract tests for removal of the non-distributable LSB lectionary data."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RemoveLSBLectionaryCatalogTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / "migrations" / "081_remove_lsb_lectionary_catalog.sql").read_text(
            encoding="utf-8"
        )

    def test_cleanup_is_scoped_and_preserves_service_records(self):
        self.assertIn("Name LIKE 'LSB %'", self.source)
        self.assertIn("Name LIKE 'Lutheran Service Book%'", self.source)
        self.assertIn("UPDATE tblService\nSET PropersID=NULL", self.source)
        self.assertNotIn("DELETE FROM tblService\n", self.source)

    def test_dependencies_and_old_snapshots_are_removed_safely(self):
        for table in (
            "tblProperHymnSuggestion", "tblReading", "tblPropers",
            "tblLectionaryCycle", "tblLectionaryEdition", "tblLectionarySystem",
        ):
            self.assertIn(f"DELETE FROM {table}", self.source)
        self.assertIn("DELETE FROM tblServiceReadingSnapshot", self.source)
        self.assertNotIn("tblServiceReadingSelection", self.source)
        self.assertLess(
            self.source.index("DELETE FROM tblReading"),
            self.source.index("DELETE FROM tblPropers"),
        )

    def test_obsolete_import_utilities_are_gone(self):
        self.assertFalse((ROOT / "import_lsb_propers_from_production.py").exists())
        self.assertFalse((ROOT / "inspect_lsb_propers.py").exists())


if __name__ == "__main__":
    unittest.main()
