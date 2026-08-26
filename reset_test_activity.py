"""Preview or reset dated activity in the guarded local ChurchDBTest database.

The reset preserves congregation, membership, security, catalogs, choices,
reports, screens, and accounting setup. A verified SQL dump is created before
any activity is deleted. Running without ``--apply`` is read-only.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import subprocess
from pathlib import Path

import mariadb

from backup_service import BackupService
from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}

COUNT_QUERIES = {
    "worship_services": "SELECT COUNT(*) FROM tblService",
    "service_attendance_events": "SELECT COUNT(*) FROM tblAttendanceEvent WHERE ServiceID IS NOT NULL",
    "service_attendance_records": (
        "SELECT COUNT(*) FROM tblAttendance a JOIN tblAttendanceEvent e "
        "ON e.ID=a.AttendanceEventID WHERE e.ServiceID IS NOT NULL"
    ),
    "hymn_usage": "SELECT COUNT(*) FROM tblHymnUsage",
    "service_participant_assignments": "SELECT COUNT(*) FROM tblServiceRole",
    "service_checklist_items": "SELECT COUNT(*) FROM tblServiceChecklistItem",
    "service_reading_snapshots": "SELECT COUNT(*) FROM tblServiceReadingSnapshot",
    "accounting_transactions": "SELECT COUNT(*) FROM tblAccountingTransaction",
    "accounting_transaction_lines": "SELECT COUNT(*) FROM tblAccountingTransactionLine",
    "accounting_attachments": "SELECT COUNT(*) FROM tblAccountingAttachment",
    "bank_import_batches": "SELECT COUNT(*) FROM tblAccountingBankImportBatch",
    "bank_import_rows": "SELECT COUNT(*) FROM tblAccountingBankImportRow",
    "reconciliations": "SELECT COUNT(*) FROM tblAccountingReconciliation",
    "reconciliation_items": "SELECT COUNT(*) FROM tblAccountingReconciliationItem",
    "budgets": "SELECT COUNT(*) FROM tblAccountingBudget",
    "budget_lines": "SELECT COUNT(*) FROM tblAccountingBudgetLine",
    "accounting_audit_events": "SELECT COUNT(*) FROM tblAccountingAuditEvent",
}


def settings():
    """Resolve credentials only for the exact local ChurchDBTest target."""
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    try:
        username, password = read_credential(testing["credential_target"])
    except KeyError:
        username = str(testing.get("user") or "church")
        password = getpass.getpass(f"MariaDB password for {username}: ")
    resolved = {
        "server": testing["host"], "database": testing["database"],
        "user": username, "password": password,
    }
    if str(resolved["server"]).casefold() not in LOCAL_HOSTS:
        raise RuntimeError("Safety stop: reset is restricted to local MariaDB.")
    if str(resolved["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: reset is restricted to ChurchDBTest.")
    return config, resolved


def counts(cursor):
    """Return the activity counts covered by this reset contract."""
    result = {}
    for name, sql in COUNT_QUERIES.items():
        cursor.execute(sql)
        result[name] = cursor.fetchone()[0]
    return result


def create_backup(resolved):
    """Create and independently verify the pre-reset SQL dump."""
    def non_ssl_dump(command, **kwargs):
        return subprocess.run(command[:2] + ["--skip-ssl"] + command[2:], **kwargs)

    result = BackupService(runner=non_ssl_dump).create(
        resolved, Path(r"C:\Program Files\MariaDB 12.1\bin"),
        ROOT / "BackupDB" / "ChurchDBTest.pre-activity-reset",
    )
    size = result.path.stat().st_size
    digest = hashlib.sha256(result.path.read_bytes()).hexdigest()
    if size < 1024:
        raise RuntimeError("Backup verification failed: output is unexpectedly small.")
    return result.path, size, digest


def reset_activity(cursor):
    """Delete test activity in foreign-key-safe order and reopen periods."""
    cursor.execute(
        "DELETE a FROM tblAttendance a JOIN tblAttendanceEvent e "
        "ON e.ID=a.AttendanceEventID WHERE e.ServiceID IS NOT NULL"
    )
    cursor.execute("DELETE FROM tblAttendanceEvent WHERE ServiceID IS NOT NULL")
    for table in (
        "tblServiceChecklistItem", "tblServiceReadingSnapshot", "tblServiceRole",
        "tblHymnUsage", "tblServiceBulletinOrderLine", "tblServiceBulletinOrder",
    ):
        cursor.execute(f"DELETE FROM {table}")
    cursor.execute(
        "DELETE FROM tblSecurityAuditEvent WHERE EntityType='WORSHIP_SERVICE' "
        "OR Action LIKE 'WORSHIP_SERVICE_%'"
    )
    cursor.execute("DELETE FROM tblService")

    cursor.execute("DELETE FROM tblAccountingReconciliationItem")
    cursor.execute("DELETE FROM tblAccountingReconciliation")
    cursor.execute("DELETE FROM tblAccountingBankImportRow")
    cursor.execute("DELETE FROM tblAccountingBankImportBatch")
    cursor.execute("UPDATE tblAccountingBudget SET BasedOnBudgetID=NULL")
    cursor.execute("DELETE FROM tblAccountingBudgetLine")
    cursor.execute("DELETE FROM tblAccountingBudget")
    cursor.execute("UPDATE tblAccountingFiscalYear SET ClosingTransactionID=NULL,Status='OPEN'")
    cursor.execute("UPDATE tblAccountingFiscalPeriod SET Status='OPEN'")
    cursor.execute("UPDATE tblAccountingTransaction SET OriginalTransactionID=NULL,ReversalTransactionID=NULL")
    cursor.execute("DELETE FROM tblAccountingAttachment")
    cursor.execute("DELETE FROM tblAccountingTransactionLine")
    cursor.execute("DELETE FROM tblAccountingTransaction")
    cursor.execute("DELETE FROM tblAccountingAuditEvent")


def main():
    """Preview counts or back up and reset ChurchDBTest activity."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="back up and perform the reset")
    args = parser.parse_args()
    config, resolved = settings()
    connection = mariadb.connect(
        host=resolved["server"], port=int(config["testing"].get("port", 3306)),
        database=resolved["database"], user=resolved["user"],
        password=resolved["password"], autocommit=False,
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
        path, size, digest = create_backup(resolved)
        print(f"backup={path}")
        print(f"backup_bytes={size}")
        print(f"backup_sha256={digest}")
        reset_activity(cursor)
        connection.commit()
        after = counts(cursor)
        for name, count in after.items():
            print(f"after_{name}={count}")
        if any(after.values()):
            raise RuntimeError("Activity reset verification failed: covered rows remain.")
        print("activity_reset_verified=true")
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
