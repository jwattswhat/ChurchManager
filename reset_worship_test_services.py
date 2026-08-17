"""Preview or remove all Worship Services and dependent data from local ChurchDBTest."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import subprocess
from pathlib import Path

import mariadb

from backup_service import BackupService
from churchmanager_mode import resolve_database


ROOT = Path(__file__).resolve().parent
TABLES = (
    "tblAttendance",
    "tblAttendanceEvent",
    "tblServiceRole",
    "tblHymnUsage",
    "tblServiceBulletinOrderLine",
    "tblServiceBulletinOrder",
    "tblService",
)


def settings():
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    database = config["database_settings"]
    arguments = {
        "server": database["host"],
        "database": database["database"],
        "user": database["user"],
        "password": None,
        "test_mode": True,
        "jsform_database": None,
    }
    try:
        resolved = resolve_database(arguments, config)
    except KeyError:
        arguments["password"] = getpass.getpass(
            f"MariaDB password for {database['user']}: "
        )
        resolved = resolve_database(arguments, config)
    if str(resolved["server"]).casefold() not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("Safety stop: worship cleanup is restricted to local MariaDB.")
    if str(resolved["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: worship cleanup is restricted to ChurchDBTest.")
    return config, resolved


def counts(cursor):
    result = {}
    cursor.execute(
        "SELECT COUNT(*) FROM tblAttendance a JOIN tblAttendanceEvent e "
        "ON e.ID=a.AttendanceEventID WHERE e.ServiceID IS NOT NULL"
    )
    result["service_attendance_records"] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tblAttendanceEvent WHERE ServiceID IS NOT NULL")
    result["service_attendance_events"] = cursor.fetchone()[0]
    for table in TABLES[2:]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        result[table] = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM tblSecurityAuditEvent "
        "WHERE EntityType='WORSHIP_SERVICE' OR Action='WORSHIP_SERVICE_DELETED'"
    )
    result["worship_service_audit_events"] = cursor.fetchone()[0]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Create a backup and perform cleanup")
    args = parser.parse_args()
    config, resolved = settings()
    connection = mariadb.connect(
        host=resolved["server"],
        port=int(config["testing"].get("port", 3306)),
        database=resolved["database"],
        user=resolved["user"],
        password=resolved["password"],
        autocommit=False,
    )
    cursor = connection.cursor()
    try:
        before = counts(cursor)
        print(f"target={resolved['server']}/{resolved['database']}")
        for name, count in before.items():
            print(f"before_{name}={count}")
        if not args.apply:
            print("No changes made. Re-run with --apply after reviewing these counts.")
            return 2

        def non_ssl_dump(command, **kwargs):
            return subprocess.run(command[:2] + ["--skip-ssl"] + command[2:], **kwargs)

        backup = BackupService(runner=non_ssl_dump).create(
            resolved,
            Path(r"C:\Program Files\MariaDB 12.1\bin"),
            ROOT / "BackupDB" / "ChurchDBTest.pre-worship-reset",
        )
        size = backup.path.stat().st_size
        digest = hashlib.sha256(backup.path.read_bytes()).hexdigest()
        if size < 1024:
            raise RuntimeError("Backup verification failed: output is unexpectedly small.")
        print(f"backup={backup.path}")
        print(f"backup_bytes={size}")
        print(f"backup_sha256={digest}")

        cursor.execute(
            "DELETE a FROM tblAttendance a JOIN tblAttendanceEvent e "
            "ON e.ID=a.AttendanceEventID WHERE e.ServiceID IS NOT NULL"
        )
        cursor.execute("DELETE FROM tblAttendanceEvent WHERE ServiceID IS NOT NULL")
        cursor.execute("DELETE FROM tblServiceRole")
        cursor.execute("DELETE FROM tblHymnUsage")
        cursor.execute("DELETE FROM tblServiceBulletinOrderLine")
        cursor.execute("DELETE FROM tblServiceBulletinOrder")
        cursor.execute(
            "DELETE FROM tblSecurityAuditEvent "
            "WHERE EntityType='WORSHIP_SERVICE' OR Action='WORSHIP_SERVICE_DELETED'"
        )
        cursor.execute("DELETE FROM tblService")
        connection.commit()

        after = counts(cursor)
        for name, count in after.items():
            print(f"after_{name}={count}")
        if any(after.values()):
            raise RuntimeError("Worship cleanup verification failed: dependent rows remain.")
        print("cleanup_verified=true")
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
