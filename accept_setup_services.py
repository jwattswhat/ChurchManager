"""Exercise the complete fresh-install service in disposable local resources."""

from __future__ import annotations

import argparse
import getpass
import secrets
from datetime import datetime
from pathlib import Path

import mariadb

from authentication import MariaDBUserRepository, PasswordService
from database_provisioning import quote_identifier
from installation_executor import FreshInstallationExecutor
from installation_plan import InstallationRequest, build_installation_plan
from installation_readiness import find_mariadb_tool, inspect_readiness


ROOT = Path(__file__).resolve().parent


def acceptance_names(now=None):
    """Return unique, bounded database and account names for one rehearsal."""
    stamp = (now or datetime.now()).strftime("%Y%m%d%H%M%S")
    return f"CMSetupAcceptance_{stamp}", f"cm_setup_{stamp}"


def plan_for(database_name, readiness):
    """Build a realistic plan using the bundled distributable lectionary."""
    lectionaries = tuple(
        item.code for item in readiness.packages
        if item.family == "lectionary" and item.valid and item.installable
    )
    default = lectionaries[0] if lectionaries else None
    return build_installation_plan(InstallationRequest(
        church_name="ChurchManager Installation Acceptance",
        database_name=database_name,
        master_username="acceptance_admin",
        master_display_name="Acceptance Administrator",
        master_email="acceptance@example.invalid",
        hymnal_packages=(),
        lectionary_packages=lectionaries[:1],
        order_of_service_packages=(),
        primary_hymnal=None,
        default_lectionary=default,
    ), readiness)


def remove_disposable(admin, database_name, account_name):
    """Remove only the exact acceptance database and local account."""
    cursor = admin.cursor()
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {quote_identifier(database_name)}")
        cursor.execute(f"DROP USER IF EXISTS '{account_name}'@'127.0.0.1'")
    finally:
        cursor.close()


def accept(admin_password, *, keep=False, notify=print):
    """Run the full isolated rehearsal and return its password-free result."""
    readiness = inspect_readiness(ROOT)
    database_name, account_name = acceptance_names()
    plan = plan_for(database_name, readiness)
    application_password = secrets.token_urlsafe(24)
    master_password = secrets.token_urlsafe(24)
    backup_folder = ROOT / "tmp" / "installation-acceptance" / "backups"
    admin = None
    result = None
    succeeded = False
    try:
        admin = mariadb.connect(
            host="127.0.0.1", port=3306, user="root",
            password=admin_password, autocommit=True,
        )
        result = FreshInstallationExecutor(
            admin, mariadb.connect, root=ROOT,
            database_errors=(mariadb.Error,), progress=notify,
        ).install(
            plan, account_name, application_password,
            master_password, master_password,
            dump_directory=find_mariadb_tool("mariadb-dump.exe").parent,
            backup_folder=backup_folder,
        )
        check = mariadb.connect(
            host="127.0.0.1", port=3306, database=database_name,
            user=account_name, password=application_password,
        )
        try:
            account = MariaDBUserRepository(check).find_by_username("acceptance_admin")
            if not account or not account.is_master or not account.must_change_password:
                raise RuntimeError("The acceptance Master Administrator did not verify.")
            if not PasswordService().verify(account.password_hash, master_password):
                raise RuntimeError("The acceptance password did not verify.")
        finally:
            check.close()
        succeeded = True
        notify(result.completion_report())
        notify("isolated_setup_services_accepted=true")
        return result
    finally:
        application_password = ""
        master_password = ""
        if admin is not None:
            if not keep or not succeeded:
                remove_disposable(admin, database_name, account_name)
                notify(f"removed isolated database {database_name}")
                if result is not None:
                    result.backup_path.unlink(missing_ok=True)
                    notify("removed isolated acceptance backup")
            admin.close()


def main(argv=None):
    """Preview by default; use --apply for the interactive disposable test."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args(argv)
    readiness = inspect_readiness(ROOT)
    database_name, account_name = acceptance_names()
    plan = plan_for(database_name, readiness)
    print("release_fresh_setup_rehearsal=true")
    print(f"temporary_database_pattern={database_name}")
    print(f"temporary_account_pattern={account_name}")
    print("selected_packages=" + ",".join(item.code for item in plan.selected_packages))
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
