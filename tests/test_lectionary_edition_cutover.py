"""Contract tests for the edition-only congregation lectionary setting."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LectionaryEditionCutoverTests(unittest.TestCase):
    def test_migration_removes_obsolete_system_default_and_adds_lookup(self):
        source = (ROOT / "migrations" / "080_complete_lectionary_edition_cutover.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("DROP COLUMN IF EXISTS PrimaryLectionarySystemID", source)
        self.assertIn("CREATE OR REPLACE SQL SECURITY DEFINER VIEW", source)
        self.assertIn("vwLectionaryEditionLookup", source)
        self.assertIn("e.IsActive=1", source)
        self.assertIn("s.Active=1", source)

    def test_worship_runtime_has_no_system_default_fallback(self):
        source = (ROOT / "unified_worship_service_dialog.py").read_text(encoding="utf-8")
        self.assertNotIn("PrimaryLectionarySystemID", source)
        self.assertIn("COALESCE(DisplayRole,Reading)", source)
        self.assertIn("IsActive=1 AND IsDefault=1", source)


if __name__ == "__main__":
    unittest.main()
