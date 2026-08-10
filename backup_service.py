"""Secure, testable MariaDB backup service."""

import os
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class BackupError(RuntimeError):
    pass


@dataclass(frozen=True)
class BackupResult:
    path: Path
    timestamp: str


class BackupService:
    def __init__(self, runner=subprocess.run, clock=datetime.now):
        self.runner = runner
        self.clock = clock

    def create(self, settings, mysqldump_directory, backup_prefix):
        stamp = self.clock().strftime("%Y-%m-%d.%H%M")
        output = Path(
            "{}.{}.Backup.{}.SQL".format(backup_prefix, settings["database"], stamp)
        )
        option_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", suffix=".cnf", delete=False
            ) as option_file:
                option_file.write("[client]\n")
                option_file.write("user={}\n".format(settings["user"]))
                option_file.write("password={}\n".format(settings["password"]))
                option_path = Path(option_file.name)
            os.chmod(option_path, 0o600)
            command = [
                str(Path(mysqldump_directory) / "mysqldump"),
                "--defaults-extra-file={}".format(option_path),
                "--host", settings["server"], settings["database"],
            ]
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("wb") as destination:
                self.runner(command, stdout=destination, check=True)
        except (OSError, subprocess.SubprocessError) as error:
            raise BackupError("The database backup could not be created.") from error
        finally:
            if option_path:
                option_path.unlink(missing_ok=True)
        return BackupResult(output, stamp)

