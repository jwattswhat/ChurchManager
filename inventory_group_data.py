"""Read-only inventory of normalized Group data in ChurchDBTest."""

from __future__ import annotations

import mariadb

from run_churchdb_migrations import settings


def scalar(cursor, sql):
    """Return the first column from one aggregate query."""

    cursor.execute(sql)
    return cursor.fetchone()[0]


def main():
    """Print counts and validation findings without changing the database."""

    config, resolved = settings()
    connection = mariadb.connect(
        host=resolved["server"],
        port=int(config["database_settings"].get("port", 3306)),
        database=resolved["database"],
        user=resolved["user"],
        password=resolved["password"],
        autocommit=True,
    )
    cursor = connection.cursor()
    try:
        checks = (
            ("groups", "SELECT COUNT(*) FROM tblGroup"),
            ("memberships", "SELECT COUNT(*) FROM tblGroupMembership"),
            ("role_assignments", "SELECT COUNT(*) FROM tblGroupMembershipRole"),
            ("blank_group_names", "SELECT COUNT(*) FROM tblGroup WHERE TRIM(COALESCE(Name,''))=''"),
            ("orphaned_group_churches", "SELECT COUNT(*) FROM tblGroup g LEFT JOIN tblChurch c ON c.ID=g.ChurchID WHERE c.ID IS NULL"),
            ("orphaned_membership_groups", "SELECT COUNT(*) FROM tblGroupMembership m LEFT JOIN tblGroup g ON g.ID=m.GroupID WHERE g.ID IS NULL"),
            ("orphaned_membership_people", "SELECT COUNT(*) FROM tblGroupMembership m LEFT JOIN tblPerson p ON p.ID=m.PersonID WHERE p.ID IS NULL"),
            ("cross_church_memberships", "SELECT COUNT(*) FROM tblGroupMembership m JOIN tblGroup g ON g.ID=m.GroupID JOIN tblPerson p ON p.ID=m.PersonID WHERE g.ChurchID<>p.ChurchID"),
            ("invalid_membership_dates", "SELECT COUNT(*) FROM tblGroupMembership WHERE EndDate IS NOT NULL AND EndDate<StartDate"),
            ("missing_membership_start_dates", "SELECT COUNT(*) FROM tblGroupMembership WHERE StartDate IS NULL"),
        )
        print(f"target={resolved['server']}/{resolved['database']}")
        for label, sql in checks:
            print(f"{label}={scalar(cursor, sql)}")
        cursor.execute(
            "SELECT t.Label,COUNT(*) FROM tblGroup g JOIN tblGroupType t ON t.ID=g.GroupTypeID GROUP BY t.Label "
            "ORDER BY 1"
        )
        print("group_types=" + repr(cursor.fetchall()))
        cursor.execute(
            "SELECT r.Label,COUNT(*) FROM tblGroupMembershipRole mr "
            "JOIN tblGroupRole r ON r.ID=mr.GroupRoleID GROUP BY r.Label "
            "ORDER BY 1"
        )
        print("group_roles=" + repr(cursor.fetchall()))
        cursor.execute(
            "SELECT m.ID,g.Name,p.FirstName,p.LastName,g.StartDate "
            "FROM tblGroupMembership m JOIN tblGroup g ON g.ID=m.GroupID "
            "JOIN tblPerson p ON p.ID=m.PersonID WHERE m.StartDate IS NULL "
            "ORDER BY m.ID"
        )
        print("missing_start_date_rows=" + repr(cursor.fetchall()))
    finally:
        cursor.close()
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
