"""Create cryptographic proof of the first fresh-install database backup."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from backup_service import BackupError, BackupService


@dataclass(frozen=True)
class InstallationBackupProof:
    """Non-secret evidence for one verified initial SQL dump."""

    path: Path
    size_bytes: int
    sha256: str


class InitialBackupVerifier:
    """Create and independently inspect the first ChurchManager SQL backup."""

    def __init__(self, service=None):
        self.service = service or BackupService()

    def create(self, settings, tool_directory, backup_folder):
        """Create a dump and verify its label, content, size, and SHA-256 digest."""
        result = self.service.create_in_folder(
            settings, tool_directory, backup_folder, automatic=False,
        )
        path = Path(result.path)
        try:
            if self.service.inspect_dump(path).casefold() != str(settings["database"]).casefold():
                raise BackupError("The first backup database label did not verify.")
            size = path.stat().st_size
            if size < 1024:
                raise BackupError("The first database backup is unexpectedly small.")
            with path.open("rb") as stream:
                sample = stream.read(min(size, 256 * 1024)).lower()
            if b"create table" not in sample:
                raise BackupError("The first database backup contains no table definitions.")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if len(digest) != 64:
                raise BackupError("The first database backup digest did not verify.")
            return InstallationBackupProof(path, size, digest)
        except Exception:
            path.unlink(missing_ok=True)
            raise
