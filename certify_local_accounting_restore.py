"""Certify a fresh ChurchDBTest backup by restoring and validating a temporary clone."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import mariadb

from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
BACKUP_ROOT = ROOT / "LocalTestMigrationBackups"
CLIENT_EXE = Path(r"C:\Program Files\MariaDB 12.1\bin\mariadb.exe")
REQUIRED_TABLES = {
    "tblAccountingOrganization", "tblAccountingAccount", "tblAccountingFund",
    "tblAccountingFiscalYear", "tblAccountingFiscalPeriod",
    "tblAccountingTransaction", "tblAccountingTransactionLine",
    "tblAccountingAuditEvent",
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def latest_backup():
    candidates = sorted(
        (folder for folder in BACKUP_ROOT.iterdir() if folder.is_dir() and (folder / "manifest.json").is_file()),
        reverse=True,
    )
    if not candidates:
        raise RuntimeError("No local test backup with a manifest is available.")
    return candidates[0]


def validate_target(name):
    if not re.fullmatch(r"ChurchDBTestRestoreVerify_[0-9]{14}", name):
        raise RuntimeError("Safety stop: invalid temporary restore database name.")


def main():
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    if str(testing["host"]) not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("Safety stop: restore certification is restricted to localhost.")
    if str(testing["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: source database must be ChurchDBTest.")
    backup = latest_backup()
    manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    entries = {item["database"]: item for item in manifest}
    entry = entries.get("ChurchDBTest")
    if entry is None:
        raise RuntimeError("The backup manifest does not contain ChurchDBTest.")
    dump = backup / entry["file"]
    actual_hash = sha256(dump)
    if actual_hash != entry["sha256"]:
        raise RuntimeError("Checksum mismatch for ChurchDBTest backup.")
    target = "ChurchDBTestRestoreVerify_" + datetime.now().strftime("%Y%m%d%H%M%S")
    validate_target(target)
    restore_file = backup / (target + ".sql")
    source = dump.read_bytes()
    restored, replacements = re.subn(rb"`churchdbtest`", ("`" + target + "`").encode("ascii"), source, flags=re.IGNORECASE)
    if replacements < 2:
        raise RuntimeError("The dump did not contain the expected ChurchDBTest database declarations.")
    restored = re.sub(rb"DEFINER=`[^`]+`@`[^`]+`", b"DEFINER=CURRENT_USER", restored)
    restore_file.write_bytes(restored)
    username, password = read_credential(testing["credential_target"])
    admin_username, admin_password = read_credential("ChurchManager/LocalRestoreAdmin")
    if admin_username != "root":
        raise RuntimeError("The local restore administrator must be the root account.")
    environment = os.environ.copy()
    environment["MYSQL_PWD"] = password
    connection = None
    admin = None
    try:
        admin = mariadb.connect(host=testing["host"], port=int(testing.get("port", 3306)), user=admin_username, password=admin_password, autocommit=True)
        cursor = admin.cursor()
        cursor.execute("SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=?", (target,))
        if cursor.fetchone() is not None:
            raise RuntimeError("Safety stop: temporary certification database already exists.")
        cursor.execute("CREATE DATABASE `" + target + "` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        cursor.execute("GRANT ALL PRIVILEGES ON `" + target + "`.* TO 'church'@'127.0.0.1'")
        cursor.close()
        # The administrator created the exact target; the limited account only loads objects into it.
        restored = re.sub(rb"CREATE DATABASE[^;]+;", b"", restored, count=1, flags=re.IGNORECASE)
        restore_file.write_bytes(restored)
        connection = mariadb.connect(host=testing["host"], port=int(testing.get("port", 3306)), user=username, password=password, autocommit=True)
        with restore_file.open("rb") as stream:
            subprocess.run([str(CLIENT_EXE), "--host", str(testing["host"]), "--port", str(testing.get("port", 3306)), "--user", username, "--skip-ssl"], stdin=stream, check=True, env=environment)
        verified = mariadb.connect(host=testing["host"], port=int(testing.get("port", 3306)), database=target, user=username, password=password)
        try:
            cursor = verified.cursor()
            cursor.execute("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=?", (target,))
            tables = {row[0] for row in cursor.fetchall()}
            table_names = {name.casefold() for name in tables}
            missing = sorted(name for name in REQUIRED_TABLES if name.casefold() not in table_names)
            if missing:
                raise RuntimeError("Restored database is missing accounting tables: " + ", ".join(missing))
            cursor.execute("SELECT COUNT(*) FROM tblAccountingTransaction")
            transactions = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM tblAccountingTransactionLine")
            lines = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM tblAccountingAuditEvent")
            audits = cursor.fetchone()[0]
            cursor.execute("SELECT COALESCE(SUM(l.Debit-l.Credit),0) FROM tblAccountingTransaction t JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID WHERE t.Status IN ('POSTED','REVERSED')")
            ledger_difference = Decimal(cursor.fetchone()[0])
            if transactions < 1 or lines < 2 or audits < 1:
                raise RuntimeError("Restored accounting data is unexpectedly empty.")
            if ledger_difference != 0:
                raise RuntimeError("Restored posted ledger is out of balance: {}".format(ledger_difference))
            cursor.execute("SELECT COUNT(*) FROM tblAccountingFiscalYear y LEFT JOIN tblAccountingTransaction t ON t.ID=y.ClosingTransactionID WHERE y.ClosingTransactionID IS NOT NULL AND (t.ID IS NULL OR t.Status NOT IN ('POSTED','REVERSED'))")
            broken_closes = cursor.fetchone()[0]
            if broken_closes:
                raise RuntimeError("Restored fiscal-year closing references are invalid.")
            print("backup", backup)
            print("backup_sha256", actual_hash)
            print("temporary_database", target)
            print("tables_views", len(tables))
            print("accounting_transactions", transactions)
            print("accounting_lines", lines)
            print("audit_events", audits)
            print("posted_ledger_difference", ledger_difference)
            print("fiscal_year_close_reference_errors", broken_closes)
            print("certification", "PASS")
        finally:
            verified.close()
    finally:
        environment.pop("MYSQL_PWD", None)
        password = ""
        admin_password = ""
        if admin is not None:
            cursor = admin.cursor()
            try:
                validate_target(target)
                cursor.execute("DROP DATABASE IF EXISTS `" + target + "`")
                print("temporary_database_removed", target)
            finally:
                cursor.close()
                admin.close()
        if connection is not None:
            connection.close()
        if restore_file.exists():
            restore_file.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
