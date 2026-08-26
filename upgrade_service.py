"""Preview and safely apply ChurchManager database upgrades."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from installation_backup import InitialBackupVerifier, InstallationBackupProof
from migration_hooks import after_migration, before_migration
from migration_service import MigrationService, MigrationServiceError


class UpgradeError(RuntimeError):
    """Raised when an upgrade cannot be safely previewed or completed."""


@dataclass(frozen=True)
class UpgradePreview:
    """Password-free list of installed and pending migration versions."""

    applied: tuple[str, ...]
    pending: tuple[str, ...]


@dataclass(frozen=True)
class UpgradeResult:
    """Evidence returned after a successful upgrade or current-state check."""

    newly_applied: tuple[str, ...]
    backup: InstallationBackupProof | None


class DatabaseUpgradeService:
    """Require a verified backup before applying only pending migrations."""

    def __init__(
        self, connection, migration_directory, *, database_errors=(Exception,),
        backup_verifier=None,
    ):
        self.connection = connection
        self.migration_directory = Path(migration_directory)
        self.database_errors = database_errors
        self.backups = backup_verifier or InitialBackupVerifier()

    def _migrations(self):
        return MigrationService(
            self.connection, self.migration_directory,
            database_errors=self.database_errors,
            before_apply=before_migration, after_apply=after_migration,
        )

    def preview(self):
        """Verify immutable history and report pending versions without writes."""
        try:
            result = self._migrations().run(apply=False)
            return UpgradePreview(result.applied, result.pending)
        except MigrationServiceError as error:
            raise UpgradeError(str(error)) from error

    def apply(self, settings, dump_directory, backup_folder, notify=None):
        """Back up, apply pending migrations, and require a clean re-preview."""
        notify = notify or (lambda _message: None)
        preview = self.preview()
        if not preview.pending:
            return UpgradeResult((), None)
        notify("Creating and verifying the pre-upgrade backup...")
        backup = self.backups.create(settings, dump_directory, backup_folder)
        try:
            notify(f"Applying {len(preview.pending)} database upgrade(s)...")
            result = self._migrations().run(apply=True, notify=notify)
            self.connection.commit()
            final = self.preview()
            if final.pending or tuple(result.newly_applied) != tuple(preview.pending):
                raise UpgradeError(
                    "The database upgrade did not verify. The pre-upgrade backup was preserved."
                )
            return UpgradeResult(tuple(result.newly_applied), backup)
        except Exception as error:
            try:
                self.connection.rollback()
            except Exception:
                pass
            if isinstance(error, UpgradeError):
                raise
            raise UpgradeError(
                "The database upgrade did not complete. The verified pre-upgrade backup was preserved."
            ) from error
