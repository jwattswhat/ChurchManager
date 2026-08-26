"""Exercise a guarded database upgrade in disposable local resources."""

from __future__ import annotations

import argparse
import getpass
import secrets
import shutil
from datetime import datetime
from pathlib import Path

import mariadb

from accept_setup_services import plan_for, remove_disposable
from installation_executor import FreshInstallationExecutor
from installation_readiness import find_mariadb_tool, inspect_readiness
from upgrade_service import DatabaseUpgradeService


ROOT = Path(__file__).resolve().parent
PROBE_MIGRATION = "999_acceptance_upgrade_probe.sql"


def acceptance_names(now=None):
    """Return unique, bounded names for one isolated upgrade rehearsal."""

    stamp = (now or datetime.now()).strftime("%Y%m%d%H%M%S")
    return f"CMUpgradeAcceptance_{stamp}", f"cm_upgrade_{stamp}"


def prepare_migrations(folder):
    """Copy release migrations and append one harmless acceptance-only change."""

    folder.mkdir(parents=True, exist_ok=True)
    for source in sorted((ROOT / "migrations").glob("[0-9][0-9][0-9]_*.sql")):
        shutil.copy2(source, folder / source.name)
    (folder / PROBE_MIGRATION).write_text(
        "CREATE TABLE cm_upgrade_acceptance_probe (\n"
        "    ID INT NOT NULL PRIMARY KEY,\n"
        "    AcceptedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP\n"
        ") ENGINE=InnoDB;\n",
        encoding="utf-8",
    )


def probe_exists(connection):
    """Return whether the acceptance-only upgrade table exists."""

    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='cm_upgrade_acceptance_probe'"
        )
        return int(cursor.fetchone()[0]) == 1
    finally:
        cursor.close()


def accept(admin_password, *, keep=False, notify=print):
    """Install a disposable current database, upgrade it, verify, and remove it."""

    readiness = inspect_readiness(ROOT)
    database_name, account_name = acceptance_names()
    plan = plan_for(database_name, readiness)
    application_password = secrets.token_urlsafe(24)
    master_password = secrets.token_urlsafe(24)
    work = ROOT / "tmp" / "upgrade-acceptance"
    migration_folder = work / "migrations"
    first_backup_folder = work / "installation-backups"
    upgrade_backup_folder = work / "upgrade-backups"
    shutil.rmtree(migration_folder, ignore_errors=True)
    prepare_migrations(migration_folder)
    admin = None
    application = None
    installation = None
    upgrade = None
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
            dump_directory=find_mariadb_tool("mariadb-dump.exe").parent,
            backup_folder=first_backup_folder,
        )
        application = mariadb.connect(
            host="127.0.0.1", port=3306, database=database_name,
            user=account_name, password=application_password,
        )
        service = DatabaseUpgradeService(
            application, migration_folder, database_errors=(mariadb.Error,),
        )
        preview = service.preview()
        if preview.pending != (PROBE_MIGRATION,):
            raise RuntimeError(
                "The isolated database did not expose exactly one acceptance upgrade."
            )
        notify(f"verified pending upgrade {PROBE_MIGRATION}")
        settings = {
            "server": "127.0.0.1", "port": 3306,
            "database": database_name, "user": account_name,
            "password": application_password,
        }
        upgrade = service.apply(
            settings, find_mariadb_tool("mariadb-dump.exe").parent,
            upgrade_backup_folder, notify,
        )
        if upgrade.newly_applied != (PROBE_MIGRATION,) or not probe_exists(application):
            raise RuntimeError("The isolated upgrade did not verify.")
        if service.preview().pending:
            raise RuntimeError("The isolated database still has pending upgrades.")
        succeeded = True
        notify(f"verified pre-upgrade backup {upgrade.backup.path}")
        notify(f"backup size {upgrade.backup.size_bytes:,} bytes")
        notify(f"backup SHA-256 {upgrade.backup.sha256}")
        notify("isolated_upgrade_services_accepted=true")
        return upgrade
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
                if upgrade is not None and upgrade.backup is not None:
                    upgrade.backup.path.unlink(missing_ok=True)
                notify("removed isolated acceptance backups")
            admin.close()
        shutil.rmtree(migration_folder, ignore_errors=True)


def main(argv=None):
    """Preview by default; use --apply for the interactive disposable test."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args(argv)
    database_name, account_name = acceptance_names()
    print("release_upgrade_rehearsal=true")
    print(f"temporary_database_pattern={database_name}")
    print(f"temporary_account_pattern={account_name}")
    print(f"acceptance_only_migration={PROBE_MIGRATION}")
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
