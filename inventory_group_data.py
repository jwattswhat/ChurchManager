"""Read-only inventory of pre-normalization Group data in ChurchDBTest."""

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
            ("memberships", "SELECT COUNT(*) FROM tblGroupMember"),
            ("blank_group_names", "SELECT COUNT(*) FROM tblGroup WHERE TRIM(COALESCE(Description,''))=''"),
            ("orphaned_group_churches", "SELECT COUNT(*) FROM tblGroup g LEFT JOIN tblChurch c ON c.ID=g.ChurchID WHERE c.ID IS NULL"),
            ("orphaned_membership_groups", "SELECT COUNT(*) FROM tblGroupMember m LEFT JOIN tblGroup g ON g.ID=m.GroupID WHERE g.ID IS NULL"),
            ("orphaned_membership_people", "SELECT COUNT(*) FROM tblGroupMember m LEFT JOIN tblPerson p ON p.ID=m.PersonID WHERE p.ID IS NULL"),
            ("cross_church_memberships", "SELECT COUNT(*) FROM tblGroupMember m JOIN tblGroup g ON g.ID=m.GroupID JOIN tblPerson p ON p.ID=m.PersonID WHERE g.ChurchID<>p.ChurchID"),
            ("invalid_membership_dates", "SELECT COUNT(*) FROM tblGroupMember WHERE EndDate IS NOT NULL AND StartDate IS NOT NULL AND EndDate<StartDate"),
            ("missing_membership_start_dates", "SELECT COUNT(*) FROM tblGroupMember WHERE StartDate IS NULL"),
        )
        print(f"target={resolved['server']}/{resolved['database']}")
        for label, sql in checks:
            print(f"{label}={scalar(cursor, sql)}")
        cursor.execute(
            "SELECT COALESCE(NULLIF(TRIM(GroupType),''),'(blank)'),COUNT(*) "
            "FROM tblGroup GROUP BY COALESCE(NULLIF(TRIM(GroupType),''),'(blank)') "
            "ORDER BY 1"
        )
        print("group_types=" + repr(cursor.fetchall()))
        cursor.execute(
            "SELECT COALESCE(NULLIF(TRIM(GroupRole),''),'(blank)'),COUNT(*) "
            "FROM tblGroupMember GROUP BY COALESCE(NULLIF(TRIM(GroupRole),''),'(blank)') "
            "ORDER BY 1"
        )
        print("group_roles=" + repr(cursor.fetchall()))
        cursor.execute(
            "SELECT m.ID,g.Description,p.FirstName,p.LastName,g.DateStarted "
            "FROM tblGroupMember m JOIN tblGroup g ON g.ID=m.GroupID "
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
