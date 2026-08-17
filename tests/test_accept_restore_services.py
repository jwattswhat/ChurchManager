"""Tests for the isolated protected-restore rehearsal."""

import inspect
import unittest
from datetime import datetime

from accept_restore_services import acceptance_names, migration_count


class RestoreAcceptanceTests(unittest.TestCase):
    """Verify restore rehearsal resource names remain isolated and bounded."""

    def test_acceptance_names_are_unique_resource_labels(self):
        database, account = acceptance_names(datetime(2026, 8, 17, 14, 45, 6))
        self.assertEqual(database, "CMRestoreAcceptance_20260817144506")
        self.assertEqual(account, "cm_restore_20260817144506")

    def test_restore_verifies_the_canonical_migration_ledger(self):
        source = inspect.getsource(migration_count)
        self.assertIn("FROM schema_migrations", source)
        self.assertNotIn("tblSchemaMigration", source)


if __name__ == "__main__":
    unittest.main()
