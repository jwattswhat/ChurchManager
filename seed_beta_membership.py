"""Install the small fictional membership foundation used by beta fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mariadb

from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
CHURCH_NAME = "Reformation Lutheran Church"
MARKER = "CMTEST: beta membership 1.1.0"
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _settings():
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    if str(testing["host"]).casefold() not in LOCAL_HOSTS:
        raise RuntimeError("Safety stop: beta membership requires local MariaDB.")
    if str(testing["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: beta membership requires ChurchDBTest.")
    username, password = read_credential(testing["credential_target"])
    return testing, username, password


def install(cursor):
    """Idempotently add fictional households, contacts, and people."""
    cursor.execute("SELECT ID FROM tblChurch WHERE ID>0 AND Church=?", (CHURCH_NAME,))
    row = cursor.fetchone()
    if not row:
        raise RuntimeError("Reformation Lutheran Church must exist before beta data is installed.")
    church_id = int(row[0])
    households = (
        ("Agricola, Wilhelm & Agnes", "Wilhelm", "Agricola", "Agnes", "Agricola", 0),
        ("Bach, Johann & Anna", "Johann", "Bach", "Anna", "Bach", 0),
        ("Schmidt Family", "Anna", "Schmidt", "David", "Schmidt", 1),
    )
    for index, (family_name, first_a, last_a, first_b, last_b, unlisted) in enumerate(households, 1):
        cursor.execute("SELECT ID FROM tblFamily WHERE ChurchID=? AND FamilyName=?", (church_id, family_name))
        family = cursor.fetchone()
        if family:
            family_id = int(family[0])
        else:
            cursor.execute(
                "INSERT INTO tblFamily (ChurchID,FamilyName,Directory,Note) VALUES (?,?,1,?)",
                (church_id, family_name, MARKER),
            )
            family_id = int(cursor.lastrowid)
            cursor.execute(
                "INSERT INTO tblFamilyAddress (FamilyID,AddressLabel,Address,City,State,Zip,Unlisted,StartDate,Note) "
                "VALUES (?,'Main',?,'Wittenberg','MN','55555',?,'2026-01-01',?)",
                (family_id, f"{100 + index} Reformation Way", unlisted, MARKER),
            )
            cursor.execute(
                "INSERT INTO tblFamilyContact (FamilyID,ContactLabel,Type,Contact,Unlisted,Note) "
                "VALUES (?,'Household email','Email',?,?,?)",
                (family_id, f"household{index}@example.invalid", unlisted, MARKER),
            )
        for first, last in ((first_a, last_a), (first_b, last_b)):
            cursor.execute(
                "SELECT ID FROM tblPerson WHERE ChurchID=? AND FirstName=? AND LastName=?",
                (church_id, first, last),
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO tblPerson (ChurchID,FamilyID,FirstName,LastName,Status,Baptized,Confirmed,Member,Voter,Note) "
                    "VALUES (?,?,?,?,'Member',1,1,1,1,?)",
                    (church_id, family_id, first, last, MARKER),
                )
    cursor.execute("SELECT COUNT(*) FROM tblFamily WHERE ChurchID=?", (church_id,))
    families = int(cursor.fetchone()[0])
    cursor.execute("SELECT COUNT(*) FROM tblPerson WHERE ChurchID=?", (church_id,))
    people = int(cursor.fetchone()[0])
    if families < 3 or people < 6:
        raise RuntimeError("Beta membership verification failed.")
    return {"families": families, "people": people}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        print("No changes made. Re-run with --apply to install fictional membership data.")
        return 2
    settings, username, password = _settings()
    connection = mariadb.connect(host=settings["host"], port=int(settings.get("port", 3306)),
                                 database=settings["database"], user=username,
                                 password=password, autocommit=False)
    cursor = connection.cursor()
    try:
        evidence = install(cursor)
        connection.commit()
        print("beta_membership_verified=true")
        for key, value in evidence.items():
            print(f"{key}={value}")
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close(); connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
