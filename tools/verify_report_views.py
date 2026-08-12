"""Verify the local ChurchDBTest report-view surface without displaying data."""

import mariadb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_churchdb_migrations import settings


def main():
    config, resolved = settings()
    connection = mariadb.connect(
        host=resolved["server"],
        port=int(config["database_settings"].get("port", 3306)),
        database=resolved["database"],
        user=resolved["user"],
        password=resolved["password"],
    )
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT TABLE_NAME FROM information_schema.VIEWS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME LIKE 'rpt\\_%' ESCAPE '\\\\' "
            "ORDER BY TABLE_NAME"
        )
        views = [row[0] for row in cursor.fetchall()]
        for view in views:
            cursor.execute(f"SELECT COUNT(*) FROM `{view}`")
            cursor.fetchone()
        for view in (
            "rpt_person_contact",
            "rpt_person_address",
            "rpt_family_contact",
            "rpt_family_address",
        ):
            cursor.execute(f"SELECT COUNT(*) FROM `{view}` WHERE Unlisted<>0")
            if cursor.fetchone()[0]:
                raise RuntimeError(f"Privacy filter failed for {view}")
        cursor.execute("SELECT COUNT(*) FROM rpt_directory_family WHERE Directory<>1")
        if cursor.fetchone()[0]:
            raise RuntimeError("Directory filter failed for rpt_directory_family")
        print(f"Verified {len(views)} queryable report views in {resolved['database']}")
        print("Verified unlisted contact and directory privacy filters")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
