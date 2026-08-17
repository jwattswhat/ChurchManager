"""Exercise protected backup restoration in disposable local resources."""

from __future__ import annotations

import argparse
import getpass
import secrets
from datetime import datetime
from pathlib import Path

import mariadb

from accept_setup_services import plan_for, remove_disposable
from backup_service import BackupService
from installation_executor import FreshInstallationExecutor
from installation_readiness import find_mariadb_tool, inspect_readiness


ROOT = Path(__file__).resolve().parent
ORIGINAL_CHURCH_NAME = "ChurchManager Installation Acceptance"
DAMAGED_CHURCH_NAME = "Restore Acceptance - Replace Me"


def acceptance_names(now=None):
    """Return unique, bounded names for one isolated restore rehearsal."""

    stamp = (now or datetime.now()).strftime("%Y%m%d%H%M%S")
    return f"CMRestoreAcceptance_{stamp}", f"cm_restore_{stamp}"


def church_name(connection):
    """Return the single congregation name from the acceptance database."""

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT Church FROM tblChurch ORDER BY ID LIMIT 1")
        row = cursor.fetchone()
        return None if row is None else str(row[0])
    finally:
        cursor.close()


def migration_count(connection):
    """Return the represented migration count after restore."""

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM schema_migrations")
        return int(cursor.fetchone()[0])
    finally:
        cursor.close()


def accept(admin_password, *, keep=False, notify=print):
    """Install, alter, restore, verify, and remove an isolated database."""

    readiness = inspect_readiness(ROOT)
    database_name, account_name = acceptance_names()
    plan = plan_for(database_name, readiness)
    application_password = secrets.token_urlsafe(24)
    master_password = secrets.token_urlsafe(24)
    work = ROOT / "tmp" / "restore-acceptance"
    backup_folder = work / "backups"
    tools = find_mariadb_tool("mariadb-dump.exe").parent
    admin = None
    application = None
    installation = None
    safety = None
    succeeded = False
    try:
        admin = mariadb.connect(
            host="127.0.0.1", port=3306, user="root",
            password=admin_password, autocommit=True,
        )
        installation = FreshInstallationExecutor(
            admin, mariadb.connect, root=ROOT,
            database_errors=(mariadb.Error,), progress=notify,
        ).install(
            plan, account_name, application_password,
            master_password, master_password,
            dump_directory=tools, backup_folder=backup_folder,
        )
        settings = {
            "server": "127.0.0.1", "port": 3306,
            "database": database_name, "user": account_name,
            "password": application_password,
        }
        application = mariadb.connect(**{
            "host": settings["server"], "port": settings["port"],
            "database": database_name, "user": account_name,
            "password": application_password,
        })
        cursor = application.cursor()
        try:
            cursor.execute(
                "UPDATE tblChurch SET Church=? WHERE Church=?",
                (DAMAGED_CHURCH_NAME, ORIGINAL_CHURCH_NAME),
            )
            if cursor.rowcount != 1:
                raise RuntimeError("The restore acceptance congregation was not found.")
            application.commit()
        finally:
            cursor.close()
        if church_name(application) != DAMAGED_CHURCH_NAME:
            raise RuntimeError("The pre-restore change did not verify.")
        notify("verified disposable post-backup change")
        application.close()
        application = None
        safety = BackupService().restore(
            settings, tools, installation.backup_path, backup_folder,
        )
        application = mariadb.connect(
            host="127.0.0.1", port=3306, database=database_name,
            user=account_name, password=application_password,
        )
        if church_name(application) != ORIGINAL_CHURCH_NAME:
            raise RuntimeError("The restored congregation record did not verify.")
        represented = migration_count(application)
        if represented != 84:
            raise RuntimeError(
                f"The restored migration ledger has {represented} records instead of 84."
            )
        if BackupService.inspect_dump(safety.path).casefold() != database_name.casefold():
            raise RuntimeError("The pre-restore safety backup did not verify.")
        succeeded = True
        notify(f"verified restored congregation {ORIGINAL_CHURCH_NAME}")
        notify(f"verified {represented} represented migrations")
        notify(f"verified pre-restore safety backup {safety.path}")
        notify("isolated_restore_services_accepted=true")
        return safety
    finally:
        application_password = ""
        master_password = ""
        if application is not None:
            application.close()
        if admin is not None:
            if not keep or not succeeded:
                remove_disposable(admin, database_name, account_name)
                notify(f"removed isolated database {database_name}")
                if installation is not None:
                    installation.backup_path.unlink(missing_ok=True)
                if safety is not None:
                    safety.path.unlink(missing_ok=True)
                notify("removed isolated acceptance backups")
            admin.close()


def main(argv=None):
    """Preview by default; use --apply for the interactive disposable test."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args(argv)
    database_name, account_name = acceptance_names()
    print("release_restore_rehearsal=true")
    print(f"temporary_database_pattern={database_name}")
    print(f"temporary_account_pattern={account_name}")
    print("restore_source=verified_first_installation_backup")
    if not args.apply:
        print("preview_only=true")
        return 0
    password = getpass.getpass("Local MariaDB administrative password for root: ")
    try:
        accept(password, keep=args.keep)
        return 0
    finally:
        password = ""


if __name__ == "__main__":
    raise SystemExit(main())
