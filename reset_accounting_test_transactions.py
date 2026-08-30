"""Preview or reset transaction-only accounting data in guarded ChurchDBTest."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
import mariadb
from backup_service import BackupService
from churchmanager_mode import resolve_database

ROOT=Path(__file__).resolve().parent
def settings():
    config=json.loads((ROOT/"churchmanager.json").read_text(encoding="utf-8-sig"))
    db=config["database_settings"]
    resolved=resolve_database({"server":db["host"],"database":db["database"],"user":db["user"],"password":None,"test_mode":True},config)
    if resolved["database"].casefold()=="churchdb" or "test" not in resolved["database"].casefold():
        raise RuntimeError("Safety stop: reset is restricted to a test database.")
    return config,resolved
def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--apply",action="store_true"); args=parser.parse_args()
    config,resolved=settings()
    connection=mariadb.connect(host=resolved["server"],port=int(config["database_settings"].get("port",3306)),database=resolved["database"],user=resolved["user"],password=resolved["password"],autocommit=False)
    cursor=connection.cursor()
    try:
        counts={}
        for table in ("tblAccountingTransaction","tblAccountingTransactionLine","tblAccountingAttachment"):
            cursor.execute("SELECT COUNT(*) FROM "+table); counts[table]=cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tblAccountingAuditEvent WHERE EntityType='TRANSACTION'"); counts["transaction_audit_events"]=cursor.fetchone()[0]
        print("target",resolved["database"]); [print(name,count) for name,count in counts.items()]
        if not args.apply: print("No changes made. Re-run with --apply."); return 2
        def non_ssl_dump(command, **kwargs):
            return subprocess.run(command[:2]+["--skip-ssl"]+command[2:], **kwargs)
        dump=BackupService(runner=non_ssl_dump).create(resolved,Path(r"C:\Program Files\MariaDB 12.1\bin"),ROOT/"BackupDB"/"ChurchDBTest.pre-accounting-reset")
        size=dump.path.stat().st_size; digest=hashlib.sha256(dump.path.read_bytes()).hexdigest()
        if size<1024: raise RuntimeError("Backup verification failed: output is unexpectedly small.")
        print("backup",dump.path); print("backup_bytes",size); print("backup_sha256",digest)
        cursor.execute("UPDATE tblAccountingFiscalYear SET ClosingTransactionID=NULL WHERE ClosingTransactionID IS NOT NULL")
        cursor.execute("UPDATE tblAccountingTransaction SET OriginalTransactionID=NULL, ReversalTransactionID=NULL")
        cursor.execute("DELETE FROM tblAccountingAttachment"); deleted_attachments=cursor.rowcount
        cursor.execute("DELETE FROM tblAccountingTransactionLine"); deleted_lines=cursor.rowcount
        cursor.execute("DELETE FROM tblAccountingAuditEvent WHERE EntityType='TRANSACTION'"); deleted_audit=cursor.rowcount
        cursor.execute("DELETE FROM tblAccountingTransaction"); deleted_transactions=cursor.rowcount
        connection.commit()
        print("deleted_transactions",deleted_transactions); print("deleted_lines",deleted_lines); print("deleted_attachments",deleted_attachments); print("deleted_audit_events",deleted_audit)
        return 0
    except Exception: connection.rollback(); raise
    finally: cursor.close(); connection.close()
if __name__=="__main__": raise SystemExit(main())
