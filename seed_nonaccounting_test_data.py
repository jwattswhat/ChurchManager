"""Preview or install connected fictional non-accounting data in local ChurchDBTest."""

from __future__ import annotations

import argparse
import getpass
import json
from pathlib import Path

import mariadb

from authentication import PasswordService
from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
MARKER = "CMTEST: non-accounting baseline"
CHURCH_NAME = "Reformation Lutheran Church"
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def settings():
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    host = str(testing["host"])
    database = str(testing["database"])
    if host not in LOCAL_HOSTS or database.casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: seeding is restricted to local ChurchDBTest.")
    username, password = read_credential(testing["credential_target"])
    return testing, username, password


def scalar(cursor, sql, values=()):
    cursor.execute(sql, values)
    row = cursor.fetchone()
    return row[0] if row else None


def ensure_user(cursor, password_hash, username, display_name, role_name, assigner_id):
    cursor.execute("SELECT ID FROM tblUser WHERE Username=?", (username,))
    row = cursor.fetchone()
    if row:
        user_id = row[0]
    else:
        cursor.execute(
            "INSERT INTO tblUser "
            "(Username,DisplayName,PasswordHash,Active,MasterAdministrator,MustChangePassword) "
            "VALUES (?,?,?,1,0,0)",
            (username, display_name, password_hash),
        )
        user_id = cursor.lastrowid
    role_id = scalar(cursor, "SELECT ID FROM tblRole WHERE Name=?", (role_name,))
    if role_id is None:
        raise RuntimeError("Required test role is missing: {}".format(role_name))
    cursor.execute(
        "INSERT IGNORE INTO tblUserRole (UserID,RoleID,AssignedByUserID) VALUES (?,?,?)",
        (user_id, role_id, assigner_id),
    )
    return user_id


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="commit the previewed dataset")
    args = parser.parse_args()
    testing, username, database_password = settings()
    connection = mariadb.connect(
        host=testing["host"], port=int(testing.get("port", 3306)),
        database=testing["database"], user=username, password=database_password,
        autocommit=False,
    )
    database_password = ""
    cursor = connection.cursor()
    try:
        database = scalar(cursor, "SELECT DATABASE()")
        if str(database).casefold() != "churchdbtest":
            raise RuntimeError("Safety stop: connected database is not ChurchDBTest.")
        church_id = scalar(cursor, "SELECT ID FROM tblChurch WHERE Church=?", (CHURCH_NAME,))
        if church_id is None:
            raise RuntimeError("The Reformation Lutheran Church test record is missing.")
        master_id = scalar(
            cursor,
            "SELECT ID FROM tblUser WHERE Active=1 AND MasterAdministrator=1 ORDER BY ID LIMIT 1",
        )
        if master_id is None:
            raise RuntimeError("An active test master administrator is required.")

        targets = (
            "tblAsset", "tblChurchInfo", "tblConfig", "tblDocuments", "tblFamilyDate",
            "tblGroup", "tblGroupMember", "tblHymnal", "tblJournal",
            "tblLectionarySystem", "tblPastor", "tblPersonAddress",
        )
        print("target", database)
        print("church", CHURCH_NAME, church_id)
        for table in targets:
            print("before", table, scalar(cursor, "SELECT COUNT(*) FROM `{}`".format(table)))
        for account in ("pastor.test", "volunteer.test", "auditor.test"):
            print("user", account, bool(scalar(cursor, "SELECT COUNT(*) FROM tblUser WHERE Username=?", (account,))))
        if not args.apply:
            print("No changes made. Re-run with --apply after reviewing this preview.")
            connection.rollback()
            return 2

        password = getpass.getpass("Password for the three fictional test users: ")
        confirmation = getpass.getpass("Confirm test-user password: ")
        if password != confirmation:
            raise RuntimeError("The test-user passwords did not match.")
        password_hash = PasswordService(minimum_length=4).hash(password)
        password = confirmation = ""

        logo_path = ROOT / "TestData" / "Reformation-Lutheran-Church-Test-Logo.png"
        if not logo_path.is_file():
            raise RuntimeError("The Reformation Lutheran Church test logo is missing.")
        cursor.execute("UPDATE tblChurch SET Logo=? WHERE ID=?", (logo_path.read_bytes(), church_id))

        family_id = scalar(cursor, "SELECT ID FROM tblFamily ORDER BY ID LIMIT 1")
        person_ids = []
        cursor.execute("SELECT ID FROM tblPerson ORDER BY ID LIMIT 3")
        person_ids = [row[0] for row in cursor.fetchall()]
        if family_id is None or not person_ids:
            raise RuntimeError("Membership seed data is required before adding connected fixtures.")

        if not scalar(cursor, "SELECT COUNT(*) FROM tblAsset WHERE Note=?", (MARKER,)):
            cursor.execute(
                "INSERT INTO tblAsset (ChurchID,AssetID,Description,Reserve,PurchaseDate,Depreciate,Note) "
                "VALUES (?,'TEST-PIANO','Sanctuary piano',0,'2024-06-01',0,?)",
                (church_id, MARKER),
            )
        if not scalar(cursor, "SELECT COUNT(*) FROM tblChurchInfo WHERE Note=?", (MARKER,)):
            cursor.execute(
                "INSERT INTO tblChurchInfo (ChurchID,InfoType,InfoValue,Note) "
                "VALUES (?,'Website','https://example.invalid/reformation',?)",
                (church_id, MARKER),
            )
        if not scalar(cursor, "SELECT COUNT(*) FROM tblConfig WHERE Note=?", (MARKER,)):
            cursor.execute(
                "INSERT INTO tblConfig (ConfigFamily,ConfigType,ConfigValue,Note) "
                "VALUES ('Testing','Dataset','Reformation Lutheran Church',?)", (MARKER,)
            )
        if not scalar(cursor, "SELECT COUNT(*) FROM tblDocuments WHERE Note=?", (MARKER,)):
            cursor.execute(
                "INSERT INTO tblDocuments (ChurchID,Description,FileName,Date,DocumentType,Note) "
                "VALUES (?,'Fictional test council minutes','test-council-minutes.pdf','2026-07-14','Minutes',?)",
                (church_id, MARKER),
            )
        if not scalar(cursor, "SELECT COUNT(*) FROM tblFamilyDate WHERE Note=?", (MARKER,)):
            cursor.execute(
                "INSERT INTO tblFamilyDate (FamilyID,DateType,Date,Note) VALUES (?,'Joined','2025-01-12',?)",
                (family_id, MARKER),
            )
        group_id = scalar(cursor, "SELECT id FROM tblGroup WHERE Notes=?", (MARKER,))
        if group_id is None:
            cursor.execute(
                "INSERT INTO tblGroup (ChurchID,Description,Number,GroupType,DateStarted,Notes) "
                "VALUES (?,'Test Altar Guild',1,'Service','2025-01-01',?)",
                (church_id, MARKER),
            )
            group_id = cursor.lastrowid
        if not scalar(cursor, "SELECT COUNT(*) FROM tblGroupMember WHERE Notes=?", (MARKER,)):
            for role, person_id in zip(("Coordinator", "Member", "Member"), person_ids):
                cursor.execute(
                    "INSERT INTO tblGroupMember (GroupID,GroupRole,PersonID,StartDate,Notes) "
                    "VALUES (?,?,?,'2025-01-01',?)", (group_id, role, person_id, MARKER)
                )
        if not scalar(cursor, "SELECT COUNT(*) FROM tblHymnal WHERE Note=?", (MARKER,)):
            cursor.execute(
                "INSERT INTO tblHymnal (Hymnal,Title,Publisher,Note) "
                "VALUES ('TEST','Synthetic Test Hymnal','ChurchManager Test Data',?)", (MARKER,)
            )
        if not scalar(cursor, "SELECT COUNT(*) FROM tblJournal WHERE Note=?", (MARKER,)):
            cursor.execute(
                "INSERT INTO tblJournal (ChurchID,Event,Complete,StartDate,EndDate,Note) "
                "VALUES (?,'Test Reformation service planning',0,'2026-10-25 09:00:00','2026-10-25 10:00:00',?)",
                (church_id, MARKER),
            )
        if not scalar(cursor, "SELECT COUNT(*) FROM tblLectionarySystem WHERE Name='Revised Common Lectionary'"):
            cursor.execute(
                "INSERT INTO tblLectionarySystem (Name,CycleType,Active,Note) "
                "VALUES ('Revised Common Lectionary','ABC',1,?)", (MARKER,)
            )
        if not scalar(cursor, "SELECT COUNT(*) FROM tblPastor WHERE ChurchID=?", (church_id,)):
            cursor.execute(
                "INSERT INTO tblPastor (ChurchID,Date,Pastor,Reported,Note) "
                "VALUES (?,'2024-01-01','Rev. Martin Keller',0,?)", (church_id, MARKER)
            )
        if not scalar(cursor, "SELECT COUNT(*) FROM tblPersonAddress WHERE Note=?", (MARKER,)):
            cursor.execute(
                "INSERT INTO tblPersonAddress "
                "(PersonID,AddressLabel,Address,City,State,Zip,Unlisted,StartDate,Note) "
                "VALUES (?,'Seasonal','404 Luther Lane','Wittenberg','MN','55555',0,'2025-01-01',?)",
                (person_ids[0], MARKER),
            )

        users = (
            ("pastor.test", "Rev. Martin Keller", "Pastor/Staff"),
            ("volunteer.test", "Anna Schmidt", "Volunteer"),
            ("auditor.test", "David Fischer", "Auditor"),
        )
        user_ids = [
            ensure_user(cursor, password_hash, login, display, role, master_id)
            for login, display, role in users
        ]
        for user_id in user_ids:
            cursor.execute(
                "INSERT INTO tblSecurityAuditEvent (UserID,Action,EntityType,EntityID,Reason) "
                "SELECT ?, 'TEST_USER_SEEDED', 'User', ?, ? FROM DUAL "
                "WHERE NOT EXISTS (SELECT 1 FROM tblSecurityAuditEvent "
                "WHERE UserID=? AND Action='TEST_USER_SEEDED')",
                (user_id, str(user_id), MARKER, user_id),
            )

        connection.commit()
        print("applied", True)
        print("fictional_users", len(user_ids))
        print("logo_bytes", logo_path.stat().st_size)
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
