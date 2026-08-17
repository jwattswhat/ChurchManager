"""Generate the reviewed fresh-install schema from local ChurchDBTest."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import subprocess
import tempfile
from pathlib import Path

import mariadb

from baseline_schema import build_baseline_artifact, write_baseline_artifact
from churchmanager_mode import resolve_database
from churchmanager_version import __version__
from installation_readiness import find_mariadb_tool
from migration_service import MigrationService
from run_churchdb_migrations import MIGRATIONS


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "installation"


def settings():
    """Resolve only local ChurchDBTest and prompt privately when necessary."""
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    database = config["database_settings"]
    arguments = {
        "server": config["testing"]["host"],
        "database": config["testing"]["database"],
        "user": database["user"], "password": None, "test_mode": True,
        "jsform_database": None,
    }
    try:
        resolved = resolve_database(arguments, config)
    except KeyError:
        arguments["password"] = getpass.getpass(f"MariaDB password for {database['user']}: ")
        resolved = resolve_database(arguments, config)
    if str(resolved["server"]).casefold() not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("Safety stop: baseline generation requires local MariaDB.")
    if str(resolved["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: baseline generation requires ChurchDBTest.")
    resolved["port"] = int(config["testing"].get("port", 3306))
    return resolved


def verify_history(resolved):
    """Require ChurchDBTest to represent every immutable migration exactly."""
    connection = mariadb.connect(
        host=resolved["server"], port=resolved["port"],
        database=resolved["database"], user=resolved["user"],
        password=resolved["password"], autocommit=True,
    )
    try:
        result = MigrationService(
            connection, MIGRATIONS, database_errors=(mariadb.Error,),
        ).run(apply=False)
        if result.pending:
            raise RuntimeError(
                "ChurchDBTest has pending migrations; apply and verify them before baseline generation."
            )
    finally:
        connection.close()


def dump_schema(resolved, runner=subprocess.run):
    """Return a structure-only dump without exposing its password in arguments."""
    executable = find_mariadb_tool("mariadb-dump.exe") or find_mariadb_tool("mysqldump.exe")
    if not executable:
        raise RuntimeError("The MariaDB schema export tool was not found.")
    option_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".cnf", delete=False,
        ) as option_file:
            option_file.write("[client]\n")
            option_file.write(f"user={resolved['user']}\n")
            option_file.write(f"password={resolved['password']}\n")
            option_path = Path(option_file.name)
        os.chmod(option_path, 0o600)
        command = [
            str(executable), f"--defaults-extra-file={option_path}",
            "--host", str(resolved["server"]), "--port", str(resolved["port"]),
            "--no-data", "--routines", "--events", "--triggers",
            "--skip-comments", "--skip-add-drop-table", "--skip-add-locks",
            "--skip-lock-tables", "--skip-dump-date",
            "--default-character-set=utf8mb4", str(resolved["database"]),
        ]
        completed = runner(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return completed.stdout.decode("utf-8-sig")
    except (OSError, UnicodeError, subprocess.SubprocessError) as error:
        raise RuntimeError("The clean schema export could not be generated.") from error
    finally:
        if option_path:
            option_path.unlink(missing_ok=True)


def main():
    """Validate by default and write release artifacts only with ``--write``."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the validated baseline files")
    args = parser.parse_args()
    resolved = settings()
    verify_history(resolved)
    artifact = build_baseline_artifact(
        dump_schema(resolved), resolved["database"], MIGRATIONS, __version__,
    )
    print(f"schema_sha256={artifact.manifest['schema_sha256']}")
    print(f"migrations={len(artifact.manifest['represented_migrations'])}")
    if not args.write:
        print("Baseline is clean. No files written; re-run with --write.")
        return 0
    schema, manifest = write_baseline_artifact(artifact, OUTPUT)
    print(f"schema={schema}")
    print(f"manifest={manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
