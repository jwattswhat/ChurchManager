"""Structural checks for retirement of JSForm-owned database storage."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OBSOLETE = ("jsChoices", "jsConfig", "jsEnhancemnet", "jsOptions", "jsReports")


class JSFormTableRetirementTests(unittest.TestCase):
    """Keep the removal migration complete and explicit."""

    def test_migration_drops_every_obsolete_jsform_table(self):
        migration = (
            ROOT / "migrations" / "121_remove_jsform_framework_tables.sql"
        ).read_text(encoding="utf-8")
        for table in OBSOLETE:
            with self.subTest(table=table):
                self.assertIn(f"DROP TABLE IF EXISTS {table}", migration)


if __name__ == "__main__":
    unittest.main()
