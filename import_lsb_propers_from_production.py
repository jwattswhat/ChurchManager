"""Safely merge legacy production LSB Propers and readings into ChurchDBTest."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from import_lsb_from_production import connect, rows_as_dicts


ROOT = Path(__file__).resolve().parent
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
SYSTEM_MAP = {
    "LCMS-A": ("Lutheran Service Book Three-Year Lectionary", "ABC", "A"),
    "LCMS-B": ("Lutheran Service Book Three-Year Lectionary", "ABC", "B"),
    "LCMS-C": ("Lutheran Service Book Three-Year Lectionary", "ABC", "C"),
    "LCMS-1": ("Lutheran Service Book One-Year Lectionary", "None", None),
    "LCMS-F": ("Lutheran Service Book Feasts and Festivals", "None", None),
    "LCMS-O": ("Lutheran Service Book Occasions", "Custom", None),
}
SYSTEM_DEFINITIONS = {
    name: cycle_type for name, cycle_type, _cycle in SYSTEM_MAP.values()
}
PROPER_FIELDS = (
    "Sort", "Season", "LiturgicalDate", "Color", "AltColor", "Theme",
    "HymnSug", "Introit", "Note",
)
READING_FIELDS = ("Reading", "Reference", "Note", "OldID")


def fetch_all(connection, sql, values=()):
    cursor = connection.cursor()
    try:
        cursor.execute(sql, values)
        return rows_as_dicts(cursor)
    finally:
        cursor.close()


def proper_key(system_name, cycle, liturgical_date):
    """Use the displayed Proper name because legacy festival Sort values repeat."""
    return (
        system_name.casefold(),
        (cycle or "").casefold(),
        str(liturgical_date or "").strip().casefold(),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write the reviewed merge")
    args = parser.parse_args()
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    production = config["database_settings"]
    testing = config["testing"]
    if str(testing["host"]).casefold() not in LOCAL_HOSTS:
        raise RuntimeError("Safety stop: the test target is not local.")
    if "test" not in str(testing["database"]).casefold():
        raise RuntimeError("Safety stop: the target is not a test database.")

    source = connect(production, production["credential_target"], production["database"])
    target = connect(testing, testing["credential_target"], testing["database"])
    try:
        source_cursor = source.cursor()
        source_cursor.execute("SET SESSION TRANSACTION READ ONLY")
        source_cursor.execute("START TRANSACTION READ ONLY")
        source_propers = fetch_all(source, "SELECT * FROM tblPropers")
        source_readings = fetch_all(source, "SELECT * FROM tblReading")
        unknown = sorted({str(row.get("Lectionary")) for row in source_propers} - set(SYSTEM_MAP))
        if unknown:
            raise RuntimeError(f"Unmapped production lectionary codes: {unknown}")
        source_ids = {row["ID"] for row in source_propers}
        orphan_readings = [row["ID"] for row in source_readings if row["PropersID"] not in source_ids]
        if orphan_readings:
            raise RuntimeError(f"Production contains {len(orphan_readings)} orphan readings.")
        keys = [
            proper_key(
                SYSTEM_MAP[row["Lectionary"]][0],
                SYSTEM_MAP[row["Lectionary"]][2],
                row["LiturgicalDate"],
            )
            for row in source_propers
        ]
        duplicate_keys = [key for key, count in Counter(keys).items() if count > 1]
        if duplicate_keys:
            raise RuntimeError(f"Production contains duplicate normalized Proper keys: {duplicate_keys[:5]}")
        readings_by_proper = defaultdict(list)
        for reading in source_readings:
            readings_by_proper[reading["PropersID"]].append(reading)
        duplicate_readings = []
        for proper_id, readings in readings_by_proper.items():
            labels = [str(row.get("Reading") or "").strip().casefold() for row in readings]
            if "" in labels or len(labels) != len(set(labels)):
                duplicate_readings.append(proper_id)
        if duplicate_readings:
            raise RuntimeError(
                f"Production has blank or duplicate reading labels for Proper IDs {duplicate_readings[:10]}."
            )

        target_systems = fetch_all(target, "SELECT * FROM tblLectionarySystem")
        systems_by_name = {str(row["Name"]).casefold(): row for row in target_systems}
        target_propers = fetch_all(
            target,
            "SELECT p.*,ls.Name AS SystemName FROM tblPropers p "
            "JOIN tblLectionarySystem ls ON ls.ID=p.LectionarySystemID",
        )
        existing_by_key = {
            proper_key(row["SystemName"], row.get("Cycle"), row["LiturgicalDate"]): row
            for row in target_propers
        }
        insert_count = sum(key not in existing_by_key for key in keys)
        update_count = len(keys) - insert_count
        system_insert_count = sum(
            name.casefold() not in systems_by_name
            for name in SYSTEM_DEFINITIONS
        )
        print(f"source={production['host']}/{production['database']} (read only)")
        print(f"target={testing['host']}/{testing['database']}")
        for code, count in sorted(Counter(row["Lectionary"] for row in source_propers).items()):
            name, _cycle_type, cycle = SYSTEM_MAP[code]
            print(f"{code}: {count} -> {name}" + (f" / Cycle {cycle}" if cycle else ""))
        print(f"source_propers={len(source_propers)} source_readings={len(source_readings)}")
        print(f"would_insert_systems={system_insert_count}")
        print(f"would_insert_propers={insert_count} would_update_propers={update_count}")
        print(f"would_merge_readings={len(source_readings)} would_delete=0")
        print(
            "legacy_hymn_suggestions_preserved="
            + str(sum(bool(str(row.get("HymnSug") or "").strip()) for row in source_propers))
        )
        if not args.apply:
            print("No changes made. Re-run with --apply after reviewing these counts.")
            return 2

        cursor = target.cursor()
        system_ids = {}
        for name, cycle_type in SYSTEM_DEFINITIONS.items():
            existing = systems_by_name.get(name.casefold())
            if existing:
                system_ids[name] = existing["ID"]
                cursor.execute(
                    "UPDATE tblLectionarySystem SET CycleType=?,Active=1 WHERE ID=?",
                    (cycle_type, existing["ID"]),
                )
            else:
                cursor.execute(
                    "INSERT INTO tblLectionarySystem (Name,CycleType,Active,Note) "
                    "VALUES (?,?,1,?)",
                    (name, cycle_type, "Imported from the legacy production LSB Proper catalog."),
                )
                system_ids[name] = cursor.lastrowid

        proper_ids = {}
        for row in source_propers:
            system_name, _cycle_type, cycle = SYSTEM_MAP[row["Lectionary"]]
            key = proper_key(system_name, cycle, row["LiturgicalDate"])
            values = [row.get(field) for field in PROPER_FIELDS]
            if key in existing_by_key:
                proper_id = existing_by_key[key]["ID"]
                assignments = ",".join(f"{field}=?" for field in PROPER_FIELDS)
                cursor.execute(
                    f"UPDATE tblPropers SET LectionarySystemID=?,Cycle=?,{assignments} WHERE ID=?",
                    [system_ids[system_name], cycle] + values + [proper_id],
                )
            else:
                fields = ["LectionarySystemID", "Cycle"] + list(PROPER_FIELDS)
                placeholders = ",".join("?" for _ in fields)
                cursor.execute(
                    f"INSERT INTO tblPropers ({','.join(fields)}) VALUES ({placeholders})",
                    [system_ids[system_name], cycle] + values,
                )
                proper_id = cursor.lastrowid
            proper_ids[row["ID"]] = proper_id

        readings_merged = 0
        for source_proper_id, readings in readings_by_proper.items():
            target_proper_id = proper_ids[source_proper_id]
            existing_readings = fetch_all(
                target, "SELECT * FROM tblReading WHERE PropersID=?", (target_proper_id,)
            )
            existing_by_label = {
                str(row.get("Reading") or "").strip().casefold(): row
                for row in existing_readings
            }
            for row in readings:
                label = str(row.get("Reading") or "").strip().casefold()
                values = [row.get(field) for field in READING_FIELDS]
                if label in existing_by_label:
                    assignments = ",".join(f"{field}=?" for field in READING_FIELDS)
                    cursor.execute(
                        f"UPDATE tblReading SET {assignments} WHERE ID=?",
                        values + [existing_by_label[label]["ID"]],
                    )
                else:
                    fields = ["PropersID"] + list(READING_FIELDS)
                    placeholders = ",".join("?" for _ in fields)
                    cursor.execute(
                        f"INSERT INTO tblReading ({','.join(fields)}) VALUES ({placeholders})",
                        [target_proper_id] + values,
                    )
                readings_merged += 1
        target.commit()
        print(
            f"applied: systems={len(system_ids)} propers={len(proper_ids)} "
            f"readings={readings_merged}"
        )
        return 0
    except Exception:
        target.rollback()
        raise
    finally:
        source.rollback()
        source.close()
        target.close()


if __name__ == "__main__":
    raise SystemExit(main())
