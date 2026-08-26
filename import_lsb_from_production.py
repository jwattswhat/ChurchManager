"""Safely merge the production LSB hymnal catalog into ChurchDBTest."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import mariadb

from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "churchmanager.json"
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
HYMN_ALIASES = {"HymnalCategory": "Category", "Notes": "Note"}


def rows_as_dicts(cursor):
    columns = [item[0] for item in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def table_columns(connection, table):
    cursor = connection.cursor()
    try:
        cursor.execute(f"SHOW COLUMNS FROM `{table}`")
        return {row[0] for row in cursor.fetchall()}
    finally:
        cursor.close()


def is_lsb_hymnal(row):
    abbreviation = str(row.get("Hymnal") or "").strip().casefold()
    title = str(row.get("Title") or "").strip().casefold()
    return abbreviation == "lsb" or "lutheran service book" in title


def is_lsb_hymn(row, source_hymnal_id, has_hymnal_id):
    if has_hymnal_id:
        return row.get("HymnalID") == source_hymnal_id
    return bool(re.match(r"^\s*LSB(?:\s|$)", str(row.get("Hymn") or ""), re.I))


def mapped_value(row, target_column):
    if target_column in row:
        return row[target_column]
    for source, target in HYMN_ALIASES.items():
        if target == target_column and source in row:
            return row[source]
    return None


def connect(settings, credential_target, database):
    username, password = read_credential(credential_target)
    try:
        return mariadb.connect(
            host=str(settings["host"]),
            port=int(settings.get("port", 3306)),
            database=str(database),
            user=username,
            password=password,
            autocommit=False,
        )
    finally:
        password = ""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write the reviewed merge")
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    production = config["database_settings"]
    testing = config["testing"]
    if str(testing["host"]).casefold() not in LOCAL_HOSTS:
        raise RuntimeError("Safety stop: the test target is not local.")
    if "test" not in str(testing["database"]).casefold():
        raise RuntimeError("Safety stop: the target database is not a test database.")
    if str(production["database"]).casefold() == str(testing["database"]).casefold():
        raise RuntimeError("Safety stop: production and test database names match.")

    source = connect(
        production,
        production.get("credential_target", "ChurchManager/Production"),
        production["database"],
    )
    target = connect(testing, testing["credential_target"], testing["database"])
    try:
        source_cursor = source.cursor()
        source_cursor.execute("SET SESSION TRANSACTION READ ONLY")
        source_cursor.execute("START TRANSACTION READ ONLY")
        source_cursor.execute("SELECT * FROM tblHymnal")
        hymnals = rows_as_dicts(source_cursor)
        matches = [row for row in hymnals if is_lsb_hymnal(row)]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one production LSB hymnal; found {len(matches)}.")
        source_hymnal = matches[0]
        source_cursor.execute("SELECT * FROM tblHymn")
        all_hymns = rows_as_dicts(source_cursor)
        has_hymnal_id = "HymnalID" in table_columns(source, "tblHymn")
        source_hymns = [
            row for row in all_hymns
            if is_lsb_hymn(row, source_hymnal["ID"], has_hymnal_id)
        ]
        if not source_hymns:
            raise RuntimeError("No production LSB hymns were found.")
        source_keys = [str(row.get("Hymn") or "").strip().casefold() for row in source_hymns]
        if "" in source_keys or len(source_keys) != len(set(source_keys)):
            raise RuntimeError("Production LSB hymn identifiers are blank or duplicated.")

        target_cursor = target.cursor()
        target_cursor.execute("SELECT * FROM tblHymnal")
        target_hymnals = rows_as_dicts(target_cursor)
        target_matches = [row for row in target_hymnals if is_lsb_hymnal(row)]
        if len(target_matches) > 1:
            raise RuntimeError("ChurchDBTest contains more than one LSB hymnal record.")
        target_hymnal_id = target_matches[0]["ID"] if target_matches else None
        existing = []
        if target_hymnal_id is not None:
            target_cursor.execute("SELECT * FROM tblHymn WHERE HymnalID=?", (target_hymnal_id,))
            existing = rows_as_dicts(target_cursor)
        existing_by_key = {str(row["Hymn"]).strip().casefold(): row for row in existing}
        insert_count = sum(key not in existing_by_key for key in source_keys)
        update_count = len(source_hymns) - insert_count
        print(f"source={production['host']}/{production['database']} (read only)")
        print(f"target={testing['host']}/{testing['database']}")
        print(f"hymnal={source_hymnal.get('Hymnal')} - {source_hymnal.get('Title')}")
        print(f"source_hymns={len(source_hymns)} existing={len(existing)}")
        print(f"would_insert={insert_count} would_update={update_count} would_delete=0")
        if not args.apply:
            print("No changes made. Re-run with --apply after reviewing these counts.")
            return 2

        hymnal_columns = table_columns(target, "tblHymnal") - {"ID"}
        if target_hymnal_id is None:
            fields = [name for name in ("Hymnal", "Title", "Publisher", "Note") if name in hymnal_columns]
            values = [source_hymnal.get(name) for name in fields]
            placeholders = ",".join("?" for _ in fields)
            target_cursor.execute(
                f"INSERT INTO tblHymnal ({','.join(fields)}) VALUES ({placeholders})", values
            )
            target_hymnal_id = target_cursor.lastrowid
        else:
            fields = [name for name in ("Hymnal", "Title", "Publisher", "Note") if name in hymnal_columns]
            assignments = ",".join(f"{name}=?" for name in fields)
            target_cursor.execute(
                f"UPDATE tblHymnal SET {assignments} WHERE ID=?",
                [source_hymnal.get(name) for name in fields] + [target_hymnal_id],
            )

        hymn_columns = table_columns(target, "tblHymn")
        data_fields = [
            name for name in ("Title", "BibleText", "Category", "Note") if name in hymn_columns
        ]
        for source_hymn, key in zip(source_hymns, source_keys):
            values = [mapped_value(source_hymn, name) for name in data_fields]
            if key in existing_by_key:
                assignments = ",".join(f"{name}=?" for name in data_fields)
                target_cursor.execute(
                    f"UPDATE tblHymn SET {assignments} WHERE ID=?",
                    values + [existing_by_key[key]["ID"]],
                )
            else:
                fields = ["HymnalID", "Hymn"] + data_fields
                insert_values = [target_hymnal_id, str(source_hymn["Hymn"]).strip()] + values
                placeholders = ",".join("?" for _ in fields)
                target_cursor.execute(
                    f"INSERT INTO tblHymn ({','.join(fields)}) VALUES ({placeholders})",
                    insert_values,
                )
        target.commit()
        target_cursor.execute("SELECT COUNT(*) FROM tblHymn WHERE HymnalID=?", (target_hymnal_id,))
        final_count = target_cursor.fetchone()[0]
        print(f"applied: hymnal_id={target_hymnal_id} final_lsb_hymns={final_count}")
        return 0
    except Exception:
        target.rollback()
        raise
    finally:
        try:
            source.rollback()
        finally:
            source.close()
            target.close()


if __name__ == "__main__":
    raise SystemExit(main())
