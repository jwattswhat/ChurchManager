"""Create the first master administrator in ChurchDBTest.

This command deliberately refuses every database whose name does not contain
"test". It prompts for the temporary password without echoing it.
"""

from __future__ import annotations

import argparse
from getpass import getpass

import mariadb

from authentication import PasswordService
from run_churchdb_migrations import settings


def create_master(connection, username, display_name, password_hash):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM tblUser WHERE MasterAdministrator=1 AND Active=1")
        if cursor.fetchone()[0]:
            raise RuntimeError("An active master administrator already exists.")
        cursor.execute("SELECT COUNT(*) FROM tblUser WHERE Username=?", (username,))
        if cursor.fetchone()[0]:
            raise RuntimeError("That username already exists.")
        cursor.execute(
            "INSERT INTO tblUser "
            "(Username, DisplayName, PasswordHash, Active, MasterAdministrator, MustChangePassword) "
            "VALUES (?, ?, ?, 1, 1, 1)",
            (username, display_name, password_hash),
        )
        user_id = cursor.lastrowid
        cursor.execute("SELECT ID FROM tblRole WHERE Name='Master Administrator'")
        role = cursor.fetchone()
        if not role:
            raise RuntimeError("The Master Administrator role is not installed.")
        cursor.execute(
            "INSERT INTO tblUserRole (UserID, RoleID, AssignedByUserID) VALUES (?, ?, ?)",
            (user_id, role[0], user_id),
        )
        cursor.execute(
            "INSERT INTO tblSecurityAuditEvent "
            "(UserID, Action, EntityType, EntityID, Reason) "
            "VALUES (?, 'MASTER_BOOTSTRAPPED', 'User', ?, 'Initial test deployment')",
            (user_id, str(user_id)),
        )
        connection.commit()
        return user_id
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="jonathan")
    parser.add_argument("--display-name", default="Rev. Jonathan C. Watt")
    args = parser.parse_args()
    config, resolved = settings()
    if "test" not in resolved["database"].casefold():
        raise RuntimeError("Safety stop: this command operates only on a test database.")
    password = getpass("Temporary master password: ")
    confirmation = getpass("Confirm temporary master password: ")
    if password != confirmation:
        raise RuntimeError("The passwords do not match.")
    password_hash = PasswordService().hash(password)
    connection = mariadb.connect(
        host=resolved["server"],
        port=int(config["database_settings"].get("port", 3306)),
        database=resolved["database"],
        user=resolved["user"],
        password=resolved["password"],
    )
    try:
        user_id = create_master(
            connection, args.username.strip(), args.display_name.strip(), password_hash
        )
        print("Created test master administrator ID {}.".format(user_id))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
