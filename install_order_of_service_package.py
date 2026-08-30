"""Validate or install an Order of Service package into local ChurchDBTest."""

from __future__ import annotations

import argparse
import getpass
import json
from pathlib import Path

import mariadb

from churchmanager_mode import resolve_database
from order_of_service_packages import (
    OrderOfServicePackageImporter,
    OrderOfServicePackageValidator,
    load_order_of_service_package,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_PACKAGE = ROOT / "packages" / "order_of_service" / "lsb-services-1.0.0.json"


def settings():
    """Resolve only the isolated local test database, prompting when necessary."""
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    database = config["database_settings"]
    arguments = {
        "server": database["host"], "database": database["database"],
        "user": database["user"], "password": None, "test_mode": True,
    }
    try:
        resolved = resolve_database(arguments, config)
    except KeyError:
        arguments["password"] = getpass.getpass(f"MariaDB password for {database['user']}: ")
        resolved = resolve_database(arguments, config)
    if str(resolved["server"]).casefold() not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("Safety stop: package installation is restricted to local MariaDB.")
    if str(resolved["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: package installation is restricted to ChurchDBTest.")
    return config, resolved


def lsb_hymnal_id(cursor):
    """Return the one installed LSB hymnal identifier or fail closed."""
    cursor.execute("SELECT ID FROM tblHymnal WHERE UPPER(TRIM(Hymnal))='LSB'")
    rows = cursor.fetchall()
    if len(rows) != 1:
        raise RuntimeError("Exactly one installed LSB hymnal record is required.")
    return rows[0][0]


def main():
    """Validate by default; install atomically only when ``--apply`` is supplied."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", nargs="?", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--apply", action="store_true", help="Install or upgrade the validated package")
    args = parser.parse_args()
    package, checksum = load_order_of_service_package(args.package)
    summary = OrderOfServicePackageValidator({"lsb"}).validate(package, checksum)
    print(f"package={summary.package_code} version={summary.package_version}")
    print(f"templates={summary.template_count} lines={summary.line_count} roles={summary.role_count}")
    if not args.apply:
        print("Package is valid. No database changes made; re-run with --apply to install it.")
        return 0

    config, resolved = settings()
    connection = mariadb.connect(
        host=resolved["server"], port=int(config["testing"].get("port", 3306)),
        database=resolved["database"], user=resolved["user"],
        password=resolved["password"], autocommit=False,
    )
    cursor = connection.cursor()
    try:
        hymnal_id = lsb_hymnal_id(cursor)
    finally:
        cursor.close()
    try:
        installed = OrderOfServicePackageImporter(
            connection, installed_hymnals={"lsb"}, hymnal_ids={"lsb": hymnal_id},
        ).install(package, checksum)
    finally:
        connection.close()
    print(f"installed={installed.package_code} templates={installed.template_count} lines={installed.line_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
