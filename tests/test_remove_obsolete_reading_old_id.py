"""Regression coverage for removing the obsolete reading identifier."""

from pathlib import Path
import unittest


class RemoveObsoleteReadingOldIDTests(unittest.TestCase):
    def test_migration_removes_old_id_without_recreating_it(self):
        sql = Path(
            "migrations/084_remove_obsolete_reading_old_id.sql"
        ).read_text(encoding="utf-8")
        self.assertIn("ALTER TABLE tblReading", sql)
        self.assertIn("DROP COLUMN IF EXISTS OldID", sql)
        self.assertNotIn("ADD COLUMN", sql.upper())


if __name__ == "__main__":
    unittest.main()
