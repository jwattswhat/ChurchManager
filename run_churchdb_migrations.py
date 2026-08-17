"""Apply versioned SQL migrations to the isolated ChurchDB test database."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import mariadb

from churchmanager_mode import resolve_database
from hymn_titles import title_case


ROOT = Path(__file__).resolve().parent
MIGRATIONS = ROOT / "migrations"
OBSOLETE_STRUCTURE_CLEANUP = "053_remove_obsolete_jsform_database_structures.sql"
PERMANENT_HYMN_CATALOG = "074_add_permanent_hymn_catalog.sql"


def normalize_hymn_catalog_titles(cursor):
    """Apply the approved title-case conversion to hymnal and hymn titles."""
    for table in ("tblHymnal", "tblHymn"):
        cursor.execute(f"SELECT ID,Title FROM {table}")
        changes = [
            (title_case(title), record_id)
            for record_id, title in cursor.fetchall()
            if title_case(title) != str(title or "")
        ]
        if changes:
            cursor.executemany(f"UPDATE {table} SET Title=? WHERE ID=?", changes)


def migration_files():
    return sorted(MIGRATIONS.glob("[0-9][0-9][0-9]_*.sql"))


def statements(sql):
    delimiter = ";"
    buffer = []
    result = []
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        if stripped.upper().startswith("DELIMITER "):
            delimiter = stripped.split(None, 1)[1]
            continue
        buffer.append(line)
        joined = "\n".join(buffer).rstrip()
        if joined.endswith(delimiter):
            statement = joined[:-len(delimiter)].strip()
            if statement:
                result.append(statement)
            buffer = []
    if buffer:
        statement = "\n".join(buffer).strip()
        if statement:
            result.append(statement)
    return result


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


def verify_obsolete_structure_conversion(cursor):
    """Refuse destructive cleanup while old data lacks a normalized replacement."""
    cursor.execute(
        "SELECT TABLE_NAME,COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA=DATABASE()"
    )
    columns = {}
    for table, column in cursor.fetchall():
        columns.setdefault(str(table).casefold(), set()).add(str(column).casefold())

    def has(table, *required_columns):
        available = columns.get(table.casefold())
        return available is not None and all(
            column.casefold() in available for column in required_columns
        )

    checks = (
        (
            has("tblOrderofService", "OrderofService")
            and has("tblBulletinOrderTemplate", "SourceLegacyName"),
            "Order of Service templates",
            "SELECT COUNT(*) FROM (SELECT DISTINCT o.OrderofService "
            "FROM tblOrderofService o LEFT JOIN tblBulletinOrderTemplate t "
            "ON t.SourceLegacyName=o.OrderofService WHERE t.ID IS NULL) missing",
        ),
        (
            has("tblSchedule", "ID")
            and has("tblWorshipSchedulePattern", "SourceLegacyScheduleID"),
            "worship schedule patterns",
            "SELECT COUNT(*) FROM tblSchedule old "
            "LEFT JOIN tblWorshipSchedulePattern current "
            "ON current.SourceLegacyScheduleID=old.ID WHERE current.ID IS NULL",
        ),
        (
            has("tblParticipant", "Roles"),
            "participant roles",
            "SELECT COUNT(*) FROM tblParticipant p WHERE TRIM(COALESCE(p.Roles,''))<>'' "
            "AND NOT EXISTS (SELECT 1 FROM tblParticipantRole r WHERE r.ParticipantID=p.ID)",
        ),
        (
            has("tblParticipant", "Schedule"),
            "participant availability",
            "SELECT COUNT(*) FROM tblParticipant p WHERE TRIM(COALESCE(p.Schedule,''))<>'' "
            "AND NOT EXISTS (SELECT 1 FROM tblParticipantAvailability a "
            "WHERE a.ParticipantID=p.ID)",
        ),
        (
            has("tblService", "CheckListID"),
            "service checklist selections",
            "SELECT COUNT(*) FROM tblService s WHERE s.CheckListID IS NOT NULL "
            "AND s.CheckListID<>0 AND s.WorshipChecklistTemplateID IS NULL",
        ),
        (
            has("tblService", "CheckList"),
            "service checklist results",
            "SELECT COUNT(*) FROM tblService s WHERE TRIM(COALESCE(s.CheckList,'')) "
            "NOT IN ('','{}') AND NOT EXISTS (SELECT 1 FROM tblServiceChecklistItem i "
            "WHERE i.ServiceID=s.ID)",
        ),
        (
            has("tblServiceRole", "WorshipRoleID"),
            "service participant roles",
            "SELECT COUNT(*) FROM tblServiceRole WHERE WorshipRoleID IS NULL",
        ),
    )
    failures = []
    for applicable, description, sql in checks:
        if not applicable:
            continue
        cursor.execute(sql)
        count = int(cursor.fetchone()[0])
        if count:
            failures.append(f"{description}: {count} unconverted record(s)")
    if failures:
        raise RuntimeError(
            "Safety stop: obsolete database structures were not removed because "
            "conversion verification failed:\n- " + "\n- ".join(failures)
        )


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
            if path.name == OBSOLETE_STRUCTURE_CLEANUP:
                verify_obsolete_structure_conversion(cursor)
            for statement in statements(sql):
                try:
                    cursor.execute(statement)
                except mariadb.Error as error:
                    first_line = statement.splitlines()[0][:120]
                    raise RuntimeError(
                        f"Migration {path.name} failed at: {first_line}"
                    ) from error
            if path.name == PERMANENT_HYMN_CATALOG:
                normalize_hymn_catalog_titles(cursor)
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
