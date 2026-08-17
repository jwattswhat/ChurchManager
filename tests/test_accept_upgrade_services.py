"""Tests for the isolated guarded-upgrade rehearsal."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from accept_upgrade_services import (
    PROBE_MIGRATION,
    acceptance_names,
    prepare_migrations,
)


class UpgradeAcceptanceTests(unittest.TestCase):
    """Verify bounded names and isolated acceptance migration preparation."""

    def test_acceptance_names_are_unique_resource_labels(self):
        database, account = acceptance_names(datetime(2026, 8, 17, 13, 45, 6))
        self.assertEqual(database, "CMUpgradeAcceptance_20260817134506")
        self.assertEqual(account, "cm_upgrade_20260817134506")

    def test_prepare_migrations_adds_probe_without_touching_release_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            prepare_migrations(folder)
            self.assertTrue((folder / PROBE_MIGRATION).is_file())
            self.assertIn("cm_upgrade_acceptance_probe", (folder / PROBE_MIGRATION).read_text())
            self.assertGreater(len(list(folder.glob("[0-9][0-9][0-9]_*.sql"))), 84)


if __name__ == "__main__":
    unittest.main()
