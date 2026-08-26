"""Contract tests for durable lectionary package distribution scope."""

from pathlib import Path
import unittest


class LectionaryDistributionScopeMigrationTests(unittest.TestCase):
    def test_migration_defaults_existing_packages_to_local_only(self):
        source = Path(
            "migrations/079_preserve_lectionary_distribution_scope.sql"
        ).read_text(encoding="utf-8-sig")
        self.assertIn("DistributionScope varchar(20) NOT NULL", source)
        self.assertIn("DEFAULT 'LOCAL_ONLY'", source)
        self.assertIn("'REDISTRIBUTABLE','LOCAL_ONLY'", source)
        self.assertNotIn("UPDATE tblLectionaryPackage", source)


if __name__ == "__main__":
    unittest.main()
