"""Preview or create one fictional duplicate pair in local ChurchDBTest.

This fixture exists because the normal membership importer correctly blocks the
very duplicates needed to exercise the human duplicate-review workflow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mariadb

from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
CHURCH_NAME = "Reformation Lutheran Church"
MARKER = "CMTEST: duplicate review fixture"


def settings():
    """Return the guarded local test connection settings and stored credential."""
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    if str(testing["host"]).casefold() not in LOCAL_HOSTS:
        raise RuntimeError("Safety stop: fixture is restricted to local MariaDB.")
    if str(testing["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: fixture is restricted to ChurchDBTest.")
    username, password = read_credential(testing["credential_target"])
    return testing, username, password


def main():
    """Preview or idempotently install the duplicate-review fixture."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="create the fictional pair")
    args = parser.parse_args()
    testing, username, password = settings()
    connection = mariadb.connect(
        host=testing["host"], port=int(testing.get("port", 3306)),
        database=testing["database"], user=username, password=password, autocommit=False,
    )
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT ID FROM tblChurch WHERE ID>0 AND Church=?", (CHURCH_NAME,))
        church = cursor.fetchone()
        if not church:
            raise RuntimeError("The Reformation Lutheran Church test record is missing.")
        cursor.execute("SELECT COUNT(*) FROM tblPerson WHERE Note=?", (MARKER,))
        existing = int(cursor.fetchone()[0])
        print("target=127.0.0.1/ChurchDBTest")
        print("church={}".format(CHURCH_NAME))
        print("existing_fixture_records={}".format(existing))
        if not args.apply:
            print("No changes made. Re-run with --apply to create the fictional pair.")
            connection.rollback()
            return 2
        while existing < 2:
            cursor.execute(
                "INSERT INTO tblPerson "
                "(ChurchID,FirstName,LastName,Status,Member,Note) "
                "VALUES (?,'Pat','Duplicate','Active',0,?)",
                (church[0], MARKER),
            )
            existing += 1
        connection.commit()
        print("fixture_records={}".format(existing))
        print("duplicate_name=Pat Duplicate")
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
