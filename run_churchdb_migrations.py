"""Apply versioned SQL migrations to the isolated ChurchDB test database."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mariadb

from churchmanager_mode import resolve_database
from migration_service import MigrationService, split_sql_statements
from migration_hooks import after_migration, before_migration


ROOT = Path(__file__).resolve().parent
MIGRATIONS = ROOT / "migrations"


def migration_files():
    return sorted(MIGRATIONS.glob("[0-9][0-9][0-9]_*.sql"))


def statements(sql):
    """Backward-compatible facade for migration statement parsing."""
    return split_sql_statements(sql)


def settings():
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    database = config["database_settings"]
    resolved = resolve_database(
        {
            "server": database["host"],
            "database": database["database"],
            "user": database["user"],
            "password": None,
            "test_mode": True,
            "jsform_database": None,
        },
        config,
    )
    name = str(resolved["database"])
    if name.casefold() == "churchdb" or "test" not in name.casefold():
        raise RuntimeError("Safety stop: migrations may run only against a test database.")
    return config, resolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply pending migrations")
    args = parser.parse_args()
    config, resolved = settings()
    connection = mariadb.connect(
        host=resolved["server"],
        port=int(config["database_settings"].get("port", 3306)),
        database=resolved["database"],
        user=resolved["user"],
        password=resolved["password"],
        autocommit=True,
    )
    try:
        result = MigrationService(
            connection, MIGRATIONS, database_errors=(mariadb.Error,),
            before_apply=before_migration, after_apply=after_migration,
        ).run(apply=args.apply, notify=print)
        if result.pending and not args.apply:
            print("No changes made. Re-run with --apply.")
            return 2
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
