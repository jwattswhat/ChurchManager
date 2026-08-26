"""Create the neutral accounting foundation required by beta fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mariadb

from accounting.setup_service import AccountingSetupService, FundClassification
from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    if str(testing["host"]).casefold() not in LOCAL_HOSTS or str(testing["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: beta accounting setup requires local ChurchDBTest.")
    if not args.apply:
        print("No changes made. Re-run with --apply."); return 2
    username, password = read_credential(testing["credential_target"])
    connection = mariadb.connect(host=testing["host"], port=int(testing.get("port", 3306)),
                                 database=testing["database"], user=username,
                                 password=password, autocommit=False)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT ID FROM tblChurch WHERE ID>0 AND Church='Reformation Lutheran Church'")
        church_id = int(cursor.fetchone()[0])
        cursor.execute("SELECT ID FROM tblUser WHERE Active=1 AND MasterAdministrator=1 ORDER BY ID LIMIT 1")
        user_id = int(cursor.fetchone()[0])
        cursor.execute("SELECT ID FROM tblAccountingOrganization WHERE Active=1 ORDER BY ID LIMIT 1")
        row = cursor.fetchone()
        if row is None:
            restricted = FundClassification("WITH_DONOR_RESTRICTIONS", "PURPOSE")
            organization_id = AccountingSetupService(connection, user_id).create_starter_organization(
                "ChurchManager Sample Congregation", 2027,
                {code: restricted for code in ("BUILDING", "MISSIONS", "BENEVOLENCE", "MEMORIALS", "ENDOWMENT")},
                church_id,
            )
        else:
            organization_id = int(row[0])
        cursor.execute("SELECT ID FROM tblAccountingBankAccount WHERE OrganizationID=? AND Active=1", (organization_id,))
        if cursor.fetchone() is None:
            cursor.execute("SELECT ID FROM tblAccountingAccount WHERE OrganizationID=? AND Code='1000'", (organization_id,))
            account_id = int(cursor.fetchone()[0])
            cursor.execute(
                "INSERT INTO tblAccountingBankAccount (OrganizationID,AccountID,Name,InstitutionName,AccountLastFour,Active) "
                "VALUES (?,?,'Main Checking','Fictional Community Bank','0001',1)",
                (organization_id, account_id),
            )
        connection.commit()
        print(f"accounting_organization_id={organization_id}")
        print("beta_accounting_setup_verified=true")
        return 0
    except Exception:
        connection.rollback(); raise
    finally:
        cursor.close(); connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
