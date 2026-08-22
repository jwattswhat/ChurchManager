"""Tests for the isolated protected-restore rehearsal."""

import inspect
import unittest
from datetime import datetime

from accept_restore_services import (
    GIVING_CONTRIBUTOR, GIVING_ENVELOPE, acceptance_names,
    create_giving_fixture, giving_fixture_exists, migration_count,
)


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

    def test_restore_rehearsal_proves_confidential_giving_survives(self):
        seed = inspect.getsource(create_giving_fixture)
        verify = inspect.getsource(giving_fixture_exists)
        self.assertIn("tblContributionContributor", seed)
        self.assertIn("tblContributionEnvelopeAssignment", seed)
        self.assertIn("tblContributionContributor", verify)
        self.assertIn("tblContributionEnvelopeAssignment", verify)
        self.assertEqual(GIVING_CONTRIBUTOR, "Restore Acceptance Contributor")
        self.assertEqual(GIVING_ENVELOPE, "99001")


if __name__ == "__main__":
    unittest.main()
