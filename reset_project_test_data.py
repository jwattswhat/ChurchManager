"""Replace local ChurchDBTest project work with a repeatable fictional dataset.

This guarded utility operates only on local ``ChurchDBTest``. Applying it first
creates a verified SQL backup, then replaces only project-planning records.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path

import mariadb

from backup_service import BackupService
from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
TABLES = ("tblMinistryProjectDocument", "tblMinistryProjectStepDependency",
          "tblMinistryProjectStep", "tblMinistryProject")
COUNT_SQL = {
    "tblMinistryProjectDocument": "SELECT COUNT(*) FROM tblMinistryProjectDocument",
    "tblMinistryProjectStepDependency": "SELECT COUNT(*) FROM tblMinistryProjectStepDependency",
    "tblMinistryProjectStep": "SELECT COUNT(*) FROM tblMinistryProjectStep",
    "tblMinistryProject": "SELECT COUNT(*) FROM tblMinistryProject",
}
DELETE_SQL = {
    "tblMinistryProjectDocument": "DELETE FROM tblMinistryProjectDocument",
    "tblMinistryProjectStepDependency": "DELETE FROM tblMinistryProjectStepDependency",
    "tblMinistryProjectStep": "DELETE FROM tblMinistryProjectStep",
    "tblMinistryProject": "DELETE FROM tblMinistryProject",
}


def settings():
    """Return credential-backed settings for the exact local test database."""
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    if str(testing["host"]).casefold() not in LOCAL_HOSTS:
        raise RuntimeError("Safety stop: project reset requires local MariaDB.")
    if str(testing["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: project reset requires ChurchDBTest.")
    try:
        username, password = read_credential(testing["credential_target"])
    except KeyError:
        username = str(testing.get("user") or config["database_settings"].get("user") or "church")
        password = getpass.getpass(f"MariaDB password for {username}: ")
    return testing, username, password


def scalar(cursor, sql, values=()):
    cursor.execute(sql, values); row = cursor.fetchone(); return row[0] if row else None


def create_backup(testing, username, password):
    """Create and verify a pre-reset database backup."""
    def non_ssl_dump(command, **kwargs):
        return subprocess.run(command[:2] + ["--skip-ssl"] + command[2:], **kwargs)
    resolved = {"server": testing["host"], "database": testing["database"],
                "user": username, "password": password}
    result = BackupService(runner=non_ssl_dump).create(
        resolved, Path(r"C:\Program Files\MariaDB 12.1\bin"),
        ROOT / "BackupDB" / "ChurchDBTest.pre-project-reset",
    )
    size = result.path.stat().st_size; digest = hashlib.sha256(result.path.read_bytes()).hexdigest()
    if size < 1024: raise RuntimeError("Project reset backup is unexpectedly small.")
    return result.path, size, digest


def seed(cursor):
    """Insert active, blocked, overdue, planned, and completed project work."""
    church_id = scalar(cursor, "SELECT ID FROM tblChurch WHERE ID>0 ORDER BY ID LIMIT 1")
    user_id = scalar(cursor, "SELECT ID FROM tblUser WHERE Active=1 ORDER BY ID LIMIT 1")
    person_id = scalar(cursor, "SELECT ID FROM tblPerson WHERE ChurchID=? ORDER BY ID LIMIT 1", (church_id,))
    group_id = scalar(cursor, "SELECT ID FROM tblGroup WHERE ChurchID=? AND Status='ACTIVE' ORDER BY ID LIMIT 1", (church_id,))
    if not church_id or not user_id: raise RuntimeError("Project fixtures require one church and active user.")

    projects = (
        ("PRJ-0001", "Fellowship Hall Painting", "Refresh the fellowship hall before fall activities.", "User", user_id, "Active", "High", date(2026, 8, 1), date(2026, 9, 15), None, 1, "Fictional acceptance project."),
        ("PRJ-0002", "Community Meal Planning", "Prepare a welcoming community meal.", "Group" if group_id else "User", group_id or user_id, "Active", "Normal", date(2026, 7, 15), date(2026, 8, 20), None, 1, "Includes deliberately overdue work."),
        ("PRJ-0003", "Annual Meeting Preparation", "Prepare reports and logistics for the annual meeting.", "Person" if person_id else "User", person_id or user_id, "Planned", "Normal", date(2026, 11, 1), date(2027, 1, 17), None, 1, None),
        ("PRJ-0004", "Office Records Reorganization", "Create a clear filing plan for ordinary office records.", "User", user_id, "Completed", "Low", date(2026, 2, 1), date(2026, 3, 31), date(2026, 3, 25), 0, "Completed fictional example."),
    )
    project_ids = {}
    for row in projects:
        cursor.execute("INSERT INTO tblMinistryProject (ChurchID,ProjectNumber,Name,Purpose,OwnerType,OwnerID,Status,Priority,PlannedStartDate,TargetDate,CompletedDate,CalendarEligible,Note,CreatedByUserID,UpdatedByUserID) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (church_id,) + row + (user_id, user_id))
        project_ids[row[0]] = cursor.lastrowid

    steps = (
        ("PRJ-0001", 1, "Choose paint colors", "Complete", date(2026, 8, 8), date(2026, 8, 7), 0, None),
        ("PRJ-0001", 2, "Purchase supplies", "In Progress", date(2026, 8, 29), None, 1, None),
        ("PRJ-0001", 3, "Schedule volunteer workday", "Blocked", date(2026, 9, 5), None, 1, "Waiting for volunteer availability."),
        ("PRJ-0002", 1, "Confirm serving volunteers", "In Progress", date(2026, 8, 15), None, 1, None),
        ("PRJ-0002", 2, "Prepare grocery list", "Not Started", date(2026, 8, 18), None, 0, None),
        ("PRJ-0003", 1, "Collect ministry reports", "Not Started", date(2026, 12, 15), None, 1, None),
        ("PRJ-0004", 1, "Inventory filing cabinets", "Complete", date(2026, 2, 15), date(2026, 2, 12), 0, None),
        ("PRJ-0004", 2, "Publish filing guide", "Complete", date(2026, 3, 31), date(2026, 3, 25), 0, None),
    )
    step_ids = {}
    for number, sequence, title, status, due, completed, calendar, note in steps:
        cursor.execute("INSERT INTO tblMinistryProjectStep (ProjectID,Sequence,Title,AssigneeType,AssigneeID,Status,DueDate,CompletedDate,CalendarEligible,Note,CreatedByUserID,UpdatedByUserID) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (project_ids[number], sequence, title, "User", user_id, status, due, completed, calendar, note, user_id, user_id))
        step_ids[(number, sequence)] = cursor.lastrowid
    cursor.execute("INSERT INTO tblMinistryProjectStepDependency (StepID,PredecessorStepID,CreatedByUserID) VALUES (?,?,?)", (step_ids[("PRJ-0001", 3)], step_ids[("PRJ-0001", 2)], user_id))


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--apply", action="store_true"); args = parser.parse_args()
    testing, username, password = settings()
    connection = mariadb.connect(host=testing["host"], port=int(testing.get("port", 3306)), database=testing["database"], user=username, password=password, autocommit=False)
    cursor = connection.cursor()
    try:
        print(f"target={testing['host']}/{testing['database']}")
        before = {table: int(scalar(cursor, COUNT_SQL[table]) or 0) for table in TABLES}
        for table, count in before.items(): print(f"before_{table}={count}")
        if not args.apply: print("No changes made. Re-run with --apply after reviewing the counts."); return 2
        path, size, digest = create_backup(testing, username, password); print(f"backup={path}"); print(f"backup_bytes={size}"); print(f"backup_sha256={digest}")
        for table in TABLES: cursor.execute(DELETE_SQL[table])
        seed(cursor)
        after = {table: int(scalar(cursor, COUNT_SQL[table]) or 0) for table in TABLES}
        for table, count in after.items(): print(f"after_{table}={count}")
        if after["tblMinistryProject"] != 4 or after["tblMinistryProjectStep"] != 8 or after["tblMinistryProjectStepDependency"] != 1: raise RuntimeError("Project test dataset verification failed.")
        connection.commit(); print("project_test_dataset_verified=true"); return 0
    except Exception: connection.rollback(); raise
    finally: cursor.close(); connection.close()


if __name__ == "__main__": raise SystemExit(main())
