"""Replace local ChurchDBTest assets with a repeatable fictional dataset.

The utility is hard-limited to local ``ChurchDBTest``. Applying the reset first
creates a verified SQL backup, then replaces only asset locations, assets, and
asset activities. Running without ``--apply`` is a read-only preview.
"""

from __future__ import annotations

import argparse
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
TABLES = ("tblAssetActivity", "tblAsset", "tblAssetLocation")


def settings():
    """Return credential-backed settings for the exact local test database."""
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    if str(testing["host"]).casefold() not in LOCAL_HOSTS:
        raise RuntimeError("Safety stop: asset reset requires local MariaDB.")
    if str(testing["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: asset reset requires ChurchDBTest.")
    username, password = read_credential(testing["credential_target"])
    return testing, username, password


def scalar(cursor, sql, values=()):
    cursor.execute(sql, values)
    row = cursor.fetchone()
    return row[0] if row else None


def counts(cursor):
    return {table: int(scalar(cursor, f"SELECT COUNT(*) FROM {table}") or 0) for table in TABLES}


def create_backup(testing, username, password):
    """Create and verify a pre-reset SQL dump."""
    def non_ssl_dump(command, **kwargs):
        return subprocess.run(command[:2] + ["--skip-ssl"] + command[2:], **kwargs)

    resolved = {"server": testing["host"], "database": testing["database"],
                "user": username, "password": password}
    result = BackupService(runner=non_ssl_dump).create(
        resolved, Path(r"C:\Program Files\MariaDB 12.1\bin"),
        ROOT / "BackupDB" / "ChurchDBTest.pre-asset-reset",
    )
    size = result.path.stat().st_size
    digest = hashlib.sha256(result.path.read_bytes()).hexdigest()
    if size < 1024:
        raise RuntimeError("Asset reset backup is unexpectedly small.")
    return result.path, size, digest


def seed(cursor):
    """Insert locations, assets, and representative append-only history."""
    church_id = scalar(cursor, "SELECT ID FROM tblChurch ORDER BY ID LIMIT 1")
    user_id = scalar(cursor, "SELECT ID FROM tblUser WHERE Active=1 ORDER BY ID LIMIT 1")
    if not church_id or not user_id:
        raise RuntimeError("The asset fixture requires one church and one active user.")

    locations = {}
    for name, address, note in (
        ("Sanctuary", None, "Primary worship space"),
        ("Church Office", None, "Administrative office"),
        ("Fellowship Hall", None, "Congregational gathering space"),
        ("Storage Room", None, "Secured equipment storage"),
    ):
        cursor.execute(
            "INSERT INTO tblAssetLocation (ChurchID,LocationName,Address,Note) VALUES (?,?,?,?)",
            (church_id, name, address, note),
        )
        locations[name] = cursor.lastrowid

    assets = {}
    rows = (
        ("AV-001", "Sanctuary Sound Mixer", "Audio/Visual", "Digital mixer used for worship audio.", 1,
         "Yamaha", "TF1", "TEST-TF1-001", "Sanctuary", "Purchased", date(2022, 5, 15),
         2800, "Good", "Active", date(2027, 1, 15), date(2028, 1, 15), None),
        ("MUS-001", "Sanctuary Piano", "Musical Instrument", "Upright piano.", 1,
         "Fictional Piano Company", "Upright", "TEST-PIANO-001", "Sanctuary", "Donated",
         date(2018, 9, 1), 4500, "Good", "Active", date(2026, 7, 1), date(2027, 7, 1), None),
        ("KIT-001", "Commercial Refrigerator", "Kitchen Equipment", "Fellowship kitchen refrigerator.", 1,
         "Sample Appliance", "ColdBox 40", "TEST-COLD-040", "Fellowship Hall", "Purchased",
         date(2020, 3, 12), 3200, "Fair", "Active", date(2026, 9, 15), date(2027, 3, 15), None),
        ("OFF-001", "Office Laptop", "Technology", "Retired administrative laptop.", 1,
         "Example Computer", "OfficeBook", "TEST-LAPTOP-001", "Church Office", "Purchased",
         date(2017, 6, 10), 900, "Poor", "Retired", None, None, date(2025, 12, 31)),
        ("FUR-001", "Folding Tables", "Furniture", "Eight-foot folding tables.", 12,
         None, None, None, "Storage Room", "Purchased", date(2021, 2, 20), 1440,
         "Good", "Active", None, date(2028, 1, 1), None),
    )
    for row in rows:
        (number, name, category, description, quantity, manufacturer, model, serial, location,
         method, acquired, value, condition, status, maintenance, replacement, retired) = row
        cursor.execute(
            "INSERT INTO tblAsset (ChurchID,AssetNumber,AssetName,Category,Description,Quantity,"
            "Manufacturer,Model,SerialNumber,LocationID,AcquisitionMethod,AcquisitionDate,"
            "ReferenceValue,`Condition`,Status,NextMaintenanceDate,ReplacementReviewDate,RetiredDate) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (church_id, number, name, category, description, quantity, manufacturer, model, serial,
             locations[location], method, acquired, value, condition, status, maintenance,
             replacement, retired),
        )
        assets[number] = cursor.lastrowid

    activities = (
        ("AV-001", date(2026, 1, 15), "Inspection", "Annual sound-system inspection completed.", 0,
         "Sanctuary", date(2027, 1, 15)),
        ("MUS-001", date(2026, 1, 10), "Maintenance", "Piano tuned and action inspected.", 180,
         "Sanctuary", date(2026, 7, 1)),
        ("KIT-001", date(2026, 3, 15), "Repair", "Door gasket replaced.", 145,
         "Fellowship Hall", date(2026, 9, 15)),
        ("OFF-001", date(2025, 12, 31), "Retirement", "Removed from congregational service.", 0,
         "Church Office", None),
    )
    for number, activity_date, activity_type, summary, cost, location, next_action in activities:
        cursor.execute(
            "INSERT INTO tblAssetActivity (AssetID,ActivityDate,ActivityType,Summary,Cost,LocationID,"
            "NextActionDate,RecordedByUserID) VALUES (?,?,?,?,?,?,?,?)",
            (assets[number], activity_date, activity_type, summary, cost, locations[location],
             next_action, user_id),
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="back up, replace, and verify asset test data")
    args = parser.parse_args()
    testing, username, password = settings()
    connection = mariadb.connect(host=testing["host"], port=int(testing.get("port", 3306)),
                                 database=testing["database"], user=username,
                                 password=password, autocommit=False)
    cursor = connection.cursor()
    try:
        print(f"target={testing['host']}/{testing['database']}")
        for table, count in counts(cursor).items():
            print(f"before_{table}={count}")
        if not args.apply:
            print("No changes made. Re-run with --apply after reviewing the counts.")
            return 2
        path, size, digest = create_backup(testing, username, password)
        print(f"backup={path}")
        print(f"backup_bytes={size}")
        print(f"backup_sha256={digest}")
        cursor.execute("DELETE FROM tblAssetActivity")
        cursor.execute("DELETE FROM tblAsset")
        cursor.execute("DELETE FROM tblAssetLocation")
        seed(cursor)
        after = counts(cursor)
        for table, count in after.items():
            print(f"after_{table}={count}")
        if after != {"tblAssetActivity": 4, "tblAsset": 5, "tblAssetLocation": 4}:
            raise RuntimeError("Asset test dataset verification failed.")
        connection.commit()
        print("asset_test_dataset_verified=true")
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
