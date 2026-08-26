"""Seed a sample document and fictional congregational journal entries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mariadb

from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
CHURCH_NAME = "Reformation Lutheran Church"
MARKER = "CMTEST: document-journal sample"
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def settings():
    """Return guarded ChurchDBTest connection settings and credentials."""
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    host = str(testing["host"])
    database = str(testing["database"])
    if host not in LOCAL_HOSTS or database.casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: seeding is restricted to local ChurchDBTest.")
    username, password = read_credential(testing["credential_target"])
    return testing, username, password


def scalar(cursor, sql, values=()):
    """Return the first column from a one-row query."""
    cursor.execute(sql, values)
    row = cursor.fetchone()
    return row[0] if row else None


def main():
    """Preview or apply the idempotent fictional document and journal fixture."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="commit the sample records")
    args = parser.parse_args()
    testing, username, password = settings()
    connection = mariadb.connect(
        host=testing["host"], port=int(testing.get("port", 3306)),
        database=testing["database"], user=username, password=password,
        autocommit=False,
    )
    password = ""
    cursor = connection.cursor()
    try:
        church_id = scalar(cursor, "SELECT ID FROM tblChurch WHERE Church=?", (CHURCH_NAME,))
        if not church_id:
            raise RuntimeError("The Reformation Lutheran Church test record is missing.")
        sample_path = ROOT / "Documents" / "Sample Congregational Document.txt"
        if not sample_path.is_file():
            raise RuntimeError("The sample congregational document is missing.")

        print("target", testing["database"])
        print("church", CHURCH_NAME, church_id)
        print("document", sample_path)
        print("journal_entries", 3)
        if not args.apply:
            connection.rollback()
            print("No changes made. Re-run with --apply after reviewing this preview.")
            return 2

        cursor.execute("DELETE FROM tblDocument WHERE Note=?", (MARKER,))
        cursor.execute(
            "INSERT INTO tblDocument "
            "(ChurchID,Title,Document,Date,DocumentType,Description,Note) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                church_id, "Sample Congregational Planning Note",
                str(sample_path.relative_to(ROOT)), "2026-08-26", "Planning",
                "Fictional sample file for testing the congregational document catalog.",
                MARKER,
            ),
        )
        cursor.execute("DELETE FROM tblJournal WHERE Note LIKE ?", (MARKER + "%",))
        entries = (
            ("Council approved the autumn ministry calendar", "2026-08-04 19:00:00", "2026-08-04 20:30:00"),
            ("Property committee reviewed seasonal maintenance", "2026-08-11 18:30:00", "2026-08-11 19:15:00"),
            ("Congregational fellowship planning follow-up", "2026-08-18 10:00:00", "2026-08-18 10:45:00"),
        )
        for number, (event, start, end) in enumerate(entries, 1):
            cursor.execute(
                "INSERT INTO tblJournal (ChurchID,Event,Complete,StartDate,EndDate,Note) "
                "VALUES (?,?,1,?,?,?)",
                (church_id, event, start, end, f"{MARKER} {number}"),
            )
        connection.commit()
        print("applied", True)
        print("documents", 1)
        print("journal_entries", len(entries))
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
