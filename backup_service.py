"""Secure, testable MariaDB backup service."""

import os
import shutil
import subprocess
import tempfile
import time
import json
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
        stamp = self.clock().strftime("%Y-%m-%d.%H%M%S")
        output = Path(
            "{}.{}.Backup.{}.SQL".format(backup_prefix, settings["database"], stamp)
        )
        option_path = None
        dump_path = None
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
                str(self._tool(mysqldump_directory, "mysqldump", "mariadb-dump")),
                "--defaults-extra-file={}".format(option_path),
                "--host", settings["server"],
            ]
            if settings.get("port"):
                command.extend(["--port", str(settings["port"])])
            command.append(settings["database"])
            output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w+b", suffix=".sql", dir=output.parent, delete=False
            ) as dump_file:
                dump_path = Path(dump_file.name)
                self.runner(command, stdout=dump_file, check=True)
            with output.open("wb") as destination, dump_path.open("rb") as dump_source:
                destination.write(b"-- ChurchManager database backup\n")
                destination.write("-- Database: {}\n".format(settings["database"]).encode("utf-8"))
                shutil.copyfileobj(dump_source, destination)
        except (OSError, subprocess.SubprocessError) as error:
            raise BackupError("The database backup could not be created: {}".format(error)) from error
        finally:
            if option_path:
                option_path.unlink(missing_ok=True)
            if dump_path:
                dump_path.unlink(missing_ok=True)
        return BackupResult(output, stamp)

    def create_in_folder(self, settings, mysqldump_directory, folder, automatic=False):
        folder = Path(folder).expanduser().resolve()
        label = "Automatic" if automatic else "Manual"
        prefix = folder / label
        return self.create(settings, mysqldump_directory, prefix)

    @staticmethod
    def _tool(directory, *names):
        directory = Path(directory)
        for name in names:
            for candidate in (directory / name, directory / (name + ".exe")):
                if candidate.is_file():
                    return candidate
        raise FileNotFoundError(
            "MariaDB tool not found in {} (expected {}).".format(
                directory, " or ".join(names)
            )
        )

    @staticmethod
    def prune_automatic(folder, database, keep=30):
        root = Path(folder)
        files = sorted(
            set(root.glob("Automatic.{}.Backup.*.SQL".format(database)))
            | set(root.glob("{}.Automatic.{}.Backup.*.SQL".format(database, database))),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        for obsolete in files[max(1, int(keep)):]:
            obsolete.unlink()
        return len(files[:max(1, int(keep))])

    @staticmethod
    def inspect_dump(path):
        path = Path(path)
        if not path.is_file():
            raise BackupError("The selected backup file does not exist.")
        with path.open("rb") as source:
            header = source.read(4096).decode("utf-8", errors="replace")
        marker = "-- ChurchManager database backup"
        database_line = next((line for line in header.splitlines() if line.startswith("-- Database: ")), None)
        if marker not in header or not database_line:
            raise BackupError("The selected file is not a recognized ChurchManager backup.")
        return database_line.split(":", 1)[1].strip()

    def restore(self, settings, mariadb_directory, dump_path, pre_restore_folder):
        source_database = self.inspect_dump(dump_path)
        if source_database.casefold() != str(settings["database"]).casefold():
            raise BackupError(
                "This backup was created from {} but the active database is {}.".format(
                    source_database, settings["database"]
                )
            )
        safety = self.create_in_folder(
            settings, mariadb_directory, pre_restore_folder, automatic=False,
        )
        option_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".cnf", delete=False) as option_file:
                option_file.write("[client]\nuser={}\npassword={}\n".format(settings["user"], settings["password"]))
                option_path = Path(option_file.name)
            os.chmod(option_path, 0o600)
            executable = self._tool(mariadb_directory, "mariadb", "mysql")
            command = [str(executable), "--defaults-extra-file={}".format(option_path),
                       "--host", settings["server"]]
            if settings.get("port"):
                command.extend(["--port", str(settings["port"])])
            command.append(settings["database"])
            with Path(dump_path).open("rb") as source:
                self.runner(command, stdin=source, check=True)
        except (OSError, subprocess.SubprocessError) as error:
            raise BackupError("The database could not be restored. The pre-restore backup was preserved.") from error
        finally:
            if option_path: option_path.unlink(missing_ok=True)
        return safety


class BackupPreferences:
    def __init__(self, path=None):
        base = Path(os.environ.get("LOCALAPPDATA", Path.cwd())) / "ChurchManager"
        self.path = Path(path) if path else base / "backup-preferences.json"

    def load(self):
        defaults = {"folder": str(Path(__file__).resolve().parent.parent / "Backups"),
                    "automatic_on_exit": True, "last_automatic_date": "",
                    "last_successful_backup": "", "last_successful_at": ""}
        try:
            values = json.loads(self.path.read_text(encoding="utf-8"))
            defaults.update({key: values[key] for key in defaults if key in values})
        except (OSError, ValueError, TypeError):
            pass
        return defaults

    def save(self, values):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(values, indent=2)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", suffix=".tmp",
                dir=self.path.parent, delete=False,
            ) as stream:
                stream.write(content)
                temporary = Path(stream.name)
            for attempt in range(4):
                try:
                    temporary.replace(self.path)
                    return
                except PermissionError:
                    if attempt == 3:
                        break
                    time.sleep(0.05 * (attempt + 1))
            # Some Windows processes briefly prevent replacement while still
            # allowing the existing user-owned file to be updated in place.
            self.path.write_text(content, encoding="utf-8")
        except OSError as error:
            raise BackupError(
                "Backup preferences could not be saved: {}".format(error)
            ) from error
        finally:
            if temporary:
                temporary.unlink(missing_ok=True)
