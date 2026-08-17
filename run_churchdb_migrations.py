"""Apply versioned SQL migrations to the isolated ChurchDB test database."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mariadb

from churchmanager_mode import resolve_database
from hymn_titles import title_case
from migration_service import MigrationService, split_sql_statements


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
    try:
        def before_apply(cursor, record):
            if record.version == OBSOLETE_STRUCTURE_CLEANUP:
                verify_obsolete_structure_conversion(cursor)

        def after_apply(cursor, record):
            if record.version == PERMANENT_HYMN_CATALOG:
                normalize_hymn_catalog_titles(cursor)

        result = MigrationService(
            connection, MIGRATIONS, database_errors=(mariadb.Error,),
            before_apply=before_apply, after_apply=after_apply,
        ).run(apply=args.apply, notify=print)
        if result.pending and not args.apply:
            print("No changes made. Re-run with --apply.")
            return 2
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
