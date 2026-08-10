"""Apply versioned SQL migrations to the isolated ChurchDB test database."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import mariadb

from churchmanager_mode import resolve_database


ROOT = Path(__file__).resolve().parent
MIGRATIONS = ROOT / "migrations"


def migration_files():
    return sorted(MIGRATIONS.glob("[0-9][0-9][0-9]_*.sql"))


def statements(sql):
    lines = [line for line in sql.splitlines() if not line.lstrip().startswith("--")]
    return [statement.strip() for statement in "\n".join(lines).split(";") if statement.strip()]


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
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='schema_migrations'"
        )
        if cursor.fetchone()[0]:
            cursor.execute("SELECT version, checksum FROM schema_migrations")
            applied = dict(cursor.fetchall())
        else:
            applied = {}
        pending = []
        for path in migration_files():
            sql = path.read_text(encoding="utf-8-sig")
            checksum = hashlib.sha256(sql.encode("utf-8")).hexdigest()
            if path.name in applied:
                if applied[path.name] != checksum:
                    raise RuntimeError(f"Applied migration checksum changed: {path.name}")
                print(f"applied {path.name}")
            else:
                pending.append((path, sql, checksum))
                print(f"pending {path.name}")
        if pending and not args.apply:
            print("No changes made. Re-run with --apply.")
            return 2
        if pending:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations ("
                "version varchar(100) NOT NULL PRIMARY KEY, "
                "checksum char(64) NOT NULL, "
                "applied_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP"
                ") ENGINE=InnoDB"
            )
        for path, sql, checksum in pending:
            print(f"applying {path.name}")
            for statement in statements(sql):
                try:
                    cursor.execute(statement)
                except mariadb.Error as error:
                    first_line = statement.splitlines()[0][:120]
                    raise RuntimeError(
                        f"Migration {path.name} failed at: {first_line}"
                    ) from error
            cursor.execute(
                "INSERT INTO schema_migrations (version, checksum) VALUES (?, ?)",
                (path.name, checksum),
            )
        return 0
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
