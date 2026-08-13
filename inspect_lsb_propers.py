"""Read-only comparison of production and test lectionary/Proper structures."""

import json
from collections import defaultdict
from pathlib import Path

from import_lsb_from_production import connect, rows_as_dicts, table_columns


ROOT = Path(__file__).resolve().parent


def table_rows(connection, table):
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT * FROM `{table}`")
        return rows_as_dicts(cursor)
    finally:
        cursor.close()


def main():
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    production = config["database_settings"]
    testing = config["testing"]
    source = connect(production, production["credential_target"], production["database"])
    target = connect(testing, testing["credential_target"], testing["database"])
    try:
        source_cursor = source.cursor()
        source_cursor.execute("SET SESSION TRANSACTION READ ONLY")
        source_cursor.execute("START TRANSACTION READ ONLY")
        for label, connection in (("production", source), ("test", target)):
            print(label)
            for table in ("tblLectionarySystem", "tblPropers", "tblReading"):
                try:
                    columns = sorted(table_columns(connection, table))
                    rows = table_rows(connection, table)
                    print(f"  {table}: rows={len(rows)} columns={','.join(columns)}")
                    if table == "tblLectionarySystem":
                        for row in rows:
                            print(f"    system: {row}")
                    if table == "tblPropers":
                        legacy = {}
                        samples = {}
                        for row in rows:
                            key = str(row.get("Lectionary") or row.get("LectionarySystemID") or "")
                            legacy[key] = legacy.get(key, 0) + 1
                            samples.setdefault(key, []).append(
                                (row.get("Sort"), row.get("LiturgicalDate"), row.get("Season"))
                            )
                        print(f"    proper_groups: {legacy}")
                        for key, values in samples.items():
                            ordered = sorted(values, key=lambda item: (item[0] is None, item[0]))
                            print(f"    {key} first={ordered[:3]} last={ordered[-3:]}")
                        hymn_suggestions = [
                            (row.get("Lectionary"), row.get("LiturgicalDate"), row.get("HymnSug"))
                            for row in rows if str(row.get("HymnSug") or "").strip()
                        ]
                        print(f"    hymn_suggestions={len(hymn_suggestions)} samples={hymn_suggestions[:8]}")
                        if label == "production":
                            by_group_sort = defaultdict(list)
                            for row in rows:
                                by_group_sort[(row.get("Lectionary"), row.get("Sort"))].append(row)
                            for key, duplicates in by_group_sort.items():
                                if len(duplicates) > 1:
                                    print(
                                        f"    duplicate {key}: "
                                        + repr([(row.get('ID'), row.get('LiturgicalDate')) for row in duplicates])
                                    )
                except Exception as error:
                    print(f"  {table}: unavailable ({error})")
        return 0
    finally:
        source.rollback()
        source.close()
        target.close()


if __name__ == "__main__":
    raise SystemExit(main())
