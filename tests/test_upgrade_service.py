"""Tests for guarded ChurchManager database upgrades."""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from upgrade_service import DatabaseUpgradeService, UpgradeError


def migration_result(*, applied=(), pending=(), newly_applied=()):
    """Return the small migration-result interface used by the upgrade service."""

    return type(
        "MigrationResult",
        (),
        {
            "applied": tuple(applied),
            "pending": tuple(pending),
            "newly_applied": tuple(newly_applied),
        },
    )()


class UpgradeServiceTests(unittest.TestCase):
    """Verify preview, backup, application, and failure guarantees."""

    @patch("upgrade_service.MigrationService")
    def test_preview_reports_pending_without_applying(self, migration_class):
        migration_class.return_value.run.return_value = migration_result(
            applied=("001.sql",), pending=("002.sql",)
        )
        service = DatabaseUpgradeService(Mock(), Path("migrations"))

        preview = service.preview()

        self.assertEqual(preview.applied, ("001.sql",))
        self.assertEqual(preview.pending, ("002.sql",))
        migration_class.return_value.run.assert_called_once_with(apply=False)

    @patch("upgrade_service.MigrationService")
    def test_current_database_needs_no_backup(self, migration_class):
        migration_class.return_value.run.return_value = migration_result(
            applied=("001.sql",), pending=()
        )
        backup = Mock()
        service = DatabaseUpgradeService(Mock(), Path("migrations"), backup_verifier=backup)

        result = service.apply(Mock(), Path("bin"), Path("backups"))

        self.assertEqual(result.newly_applied, ())
        self.assertIsNone(result.backup)
        backup.create.assert_not_called()

    @patch("upgrade_service.MigrationService")
    def test_upgrade_requires_backup_and_clean_final_preview(self, migration_class):
        migration_class.return_value.run.side_effect = (
            migration_result(applied=("001.sql",), pending=("002.sql",)),
            migration_result(
                applied=("001.sql", "002.sql"),
                pending=(),
                newly_applied=("002.sql",),
            ),
            migration_result(applied=("001.sql", "002.sql"), pending=()),
        )
        backup_record = Mock()
        backup = Mock()
        backup.create.return_value = backup_record
        connection = Mock()
        service = DatabaseUpgradeService(connection, Path("migrations"), backup_verifier=backup)

        result = service.apply(Mock(), Path("bin"), Path("backups"))

        self.assertEqual(result.newly_applied, ("002.sql",))
        self.assertIs(result.backup, backup_record)
        backup.create.assert_called_once()
        connection.commit.assert_called_once()

    @patch("upgrade_service.MigrationService")
    def test_failed_upgrade_preserves_verified_backup(self, migration_class):
        migration_class.return_value.run.side_effect = (
            migration_result(applied=("001.sql",), pending=("002.sql",)),
            RuntimeError("migration failed"),
        )
        backup_record = Mock()
        backup_record.path = Path("backups/pre-upgrade.sql")
        backup = Mock()
        backup.create.return_value = backup_record
        connection = Mock()
        service = DatabaseUpgradeService(connection, Path("migrations"), backup_verifier=backup)

        with self.assertRaisesRegex(UpgradeError, "pre-upgrade backup"):
            service.apply(Mock(), Path("bin"), Path("backups"))

        connection.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
