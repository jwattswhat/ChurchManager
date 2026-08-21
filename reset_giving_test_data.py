"""Replace local ChurchDBTest giving records with a repeatable fictional dataset.

The script is hard-limited to local ``ChurchDBTest``. It creates and verifies a
database backup before deleting any giving records. Running without ``--apply``
is a read-only preview.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import mariadb

from backup_service import BackupService
from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
GIVING_TABLES = (
    "tblContributionAuditEvent", "tblContributionAllocation", "tblContribution",
    "tblContributionBatch", "tblContributionEnvelopeAssignment",
    "tblContributionPurpose", "tblContributionContributor",
)


def settings():
    """Return credential-backed settings for the exact local test database."""
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    if str(testing["host"]).casefold() not in LOCAL_HOSTS:
        raise RuntimeError("Safety stop: giving reset requires local MariaDB.")
    if str(testing["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: giving reset requires ChurchDBTest.")
    username, password = read_credential(testing["credential_target"])
    return config, testing, username, password


def scalar(cursor, sql, values=()):
    cursor.execute(sql, values); row = cursor.fetchone()
    return row[0] if row else None


def counts(cursor):
    return {table: scalar(cursor, f"SELECT COUNT(*) FROM {table}") for table in GIVING_TABLES}


def create_backup(testing, username, password):
    """Create a verified pre-reset SQL dump."""
    def non_ssl_dump(command, **kwargs):
        return subprocess.run(command[:2] + ["--skip-ssl"] + command[2:], **kwargs)

    resolved = {"server": testing["host"], "database": testing["database"],
                "user": username, "password": password}
    result = BackupService(runner=non_ssl_dump).create(
        resolved, Path(r"C:\Program Files\MariaDB 12.1\bin"),
        ROOT / "BackupDB" / "ChurchDBTest.pre-giving-reset",
    )
    size = result.path.stat().st_size
    digest = hashlib.sha256(result.path.read_bytes()).hexdigest()
    if size < 1024:
        raise RuntimeError("Giving reset backup is unexpectedly small.")
    return result.path, size, digest


def remove_existing(cursor):
    """Remove giving rows and only accounting transactions linked from them."""
    cursor.execute("SELECT AccountingTransactionID FROM tblContributionBatch "
                   "WHERE AccountingTransactionID IS NOT NULL")
    transaction_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("UPDATE tblContributionBatch SET CorrectsBatchID=NULL,CorrectionBatchID=NULL")
    cursor.execute("UPDATE tblContributionBatch SET AccountingTransactionID=NULL")
    for table in ("tblContributionAuditEvent", "tblContributionAllocation", "tblContribution",
                  "tblContributionEnvelopeAssignment", "tblContributionBatch",
                  "tblContributionPurpose", "tblContributionContributor"):
        cursor.execute(f"DELETE FROM {table}")
    for transaction_id in transaction_ids:
        cursor.execute("DELETE FROM tblAccountingAuditEvent WHERE EntityType='TRANSACTION' AND EntityID=?",
                       (str(transaction_id),))
        cursor.execute("DELETE FROM tblAccountingAttachment WHERE TransactionID=?", (transaction_id,))
        cursor.execute("DELETE FROM tblAccountingTransactionLine WHERE TransactionID=?", (transaction_id,))
        cursor.execute("DELETE FROM tblAccountingTransaction WHERE ID=?", (transaction_id,))


def accounting_setup(cursor):
    organization = scalar(cursor, "SELECT ID FROM tblAccountingOrganization WHERE Active=1 ORDER BY ID LIMIT 1")
    if organization is None:
        raise RuntimeError("An active accounting organization is required for giving test data.")
    cursor.execute("SELECT ID FROM tblAccountingBankAccount WHERE OrganizationID=? AND Active=1 ORDER BY ID LIMIT 1",
                   (organization,)); bank = cursor.fetchone()
    cursor.execute("SELECT ID,NetAssetClass FROM tblAccountingFund WHERE OrganizationID=? AND Active=1 ORDER BY Code,ID",
                   (organization,)); funds = cursor.fetchall()
    cursor.execute("SELECT ID,FunctionRequirement FROM tblAccountingAccount WHERE OrganizationID=? "
                   "AND Active=1 AND PostingAllowed=1 AND AccountType='REVENUE' ORDER BY Code,ID",
                   (organization,)); accounts = cursor.fetchall()
    function_id = scalar(cursor, "SELECT ID FROM tblAccountingFunction WHERE OrganizationID=? AND Active=1 ORDER BY DisplayOrder,ID LIMIT 1",
                         (organization,))
    cursor.execute(
        "SELECT p.ID,p.StartDate,p.EndDate FROM tblAccountingFiscalPeriod p "
        "JOIN tblAccountingFiscalYear y ON y.ID=p.FiscalYearID "
        "WHERE y.OrganizationID=? AND y.Status='OPEN' AND p.Status='OPEN' "
        "ORDER BY p.StartDate,p.ID",
        (organization,),
    )
    open_periods = cursor.fetchall()
    if not bank or not funds or not accounts:
        raise RuntimeError("Active bank, fund, and revenue-account setup is required.")
    if not open_periods:
        raise RuntimeError("An open fiscal period is required for giving test batches.")
    if any(row[1] == "REQUIRED" for row in accounts) and function_id is None:
        raise RuntimeError("A functional classification is required by the revenue setup.")
    unrestricted = next((row[0] for row in funds if row[1] == "WITHOUT_DONOR_RESTRICTIONS"), funds[0][0])
    restricted = next((row[0] for row in funds if row[1] == "WITH_DONOR_RESTRICTIONS"), funds[-1][0])
    bank_account = scalar(cursor, "SELECT AccountID FROM tblAccountingBankAccount WHERE ID=?", (bank[0],))
    if bank_account is None:
        raise RuntimeError("The giving bank account must be linked to a ledger account.")
    latest_period = open_periods[-1]
    ready_date = latest_period[2]
    draft_date = max(latest_period[1], ready_date - timedelta(days=7))
    return (organization, bank[0], bank_account, unrestricted, restricted, accounts,
            function_id, draft_date, ready_date, open_periods)


def seed(cursor):
    """Install the canonical fictional giving acceptance dataset."""
    church_id = scalar(cursor, "SELECT ID FROM tblChurch ORDER BY ID LIMIT 1")
    user_id = scalar(cursor, "SELECT ID FROM tblUser WHERE Active=1 AND MasterAdministrator=1 ORDER BY ID LIMIT 1")
    if church_id is None or user_id is None:
        raise RuntimeError("Church information and an active Master Administrator are required.")
    (organization, bank, bank_account, unrestricted, restricted, accounts, function_id,
     draft_date, ready_date, open_periods) = accounting_setup(cursor)
    cursor.execute("SELECT ID,TRIM(CONCAT_WS(' ',NULLIF(Title,''),FirstName,MiddleName,LastName)) "
                   "FROM tblPerson ORDER BY LastName,FirstName,ID LIMIT 3")
    people = cursor.fetchall()
    family = cursor.execute("SELECT ID,FamilyName FROM tblFamily ORDER BY FamilyName,ID LIMIT 1")
    family = cursor.fetchone()
    if len(people) < 3 or family is None:
        raise RuntimeError("At least three people and one family are required in the fictional directory.")

    contributors = []
    for person_id, name in people:
        cursor.execute("INSERT INTO tblContributionContributor "
                       "(ChurchID,ContributorType,PersonID,DisplayName,StatementName,IsActive,StatementEnabled,Note) "
                       "VALUES (?,'PERSON',?,?,?,1,1,'Fictional giving test contributor')",
                       (church_id, person_id, name, name)); contributors.append(cursor.lastrowid)
    cursor.execute("INSERT INTO tblContributionContributor "
                   "(ChurchID,ContributorType,FamilyID,DisplayName,StatementName,IsActive,StatementEnabled,Note) "
                   "VALUES (?,'FAMILY',?,?,?,1,1,'Fictional giving test family')",
                   (church_id, family[0], family[1], family[1])); contributors.append(cursor.lastrowid)
    cursor.execute("INSERT INTO tblContributionContributor "
                   "(ChurchID,ContributorType,DisplayName,StatementName,Address,City,State,PostalCode,Email,IsActive,StatementEnabled,Note) "
                   "VALUES (?,'EXTERNAL','Jordan Community','Jordan Community','25 Sample Street','Wittenberg','MN','55000',"
                   "'jordan.community@example.invalid',1,1,'Fictional outside contributor')", (church_id,))
    contributors.append(cursor.lastrowid)
    for contributor, envelope in zip(contributors[:4], (101, 102, 103, 201)):
        cursor.execute("INSERT INTO tblContributionEnvelopeAssignment "
                       "(ChurchID,ContributorID,EnvelopeNumber,EffectiveFrom,Note) "
                       "VALUES (?,?,?,'2026-01-01','Fictional annual assignment')",
                       (church_id, contributor, str(envelope)))

    def account(index):
        row = accounts[min(index, len(accounts) - 1)]
        return row[0], function_id if row[1] == "REQUIRED" else None

    purpose_specs = (
        ("General Ministry", unrestricted, *account(0), "Congregational operating ministry"),
        ("Building and Property", restricted, *account(1), "Approved property improvements"),
        ("Student Support", restricted, *account(1), "Congregation-controlled student support"),
    )
    purposes = []
    for name, fund_id, account_id, purpose_function, description in purpose_specs:
        cursor.execute("INSERT INTO tblContributionPurpose "
                       "(ChurchID,Name,Description,ApprovalDate,ApprovingAuthority,EffectiveFrom,IsActive,"
                       "OrganizationID,FundID,RevenueAccountID,FunctionID,ControlAndDiscretionConfirmed,StatementTreatment,Note) "
                       "VALUES (?,?,?,'2026-01-01','Church Council','2026-01-01',1,?,?,?,?,1,'ELIGIBLE',"
                       "'Fictional approved purpose for testing')",
                       (church_id, name, description, organization, fund_id, account_id, purpose_function))
        purposes.append((cursor.lastrowid, fund_id, account_id, purpose_function))

    def post_batch(batch_id, batch_date, description, total):
        """Create the privacy-safe summarized ledger receipt for a test batch."""
        period_id = next((row[0] for row in open_periods if row[1] <= batch_date <= row[2]), None)
        if period_id is None:
            raise RuntimeError(f"No open fiscal period contains statement test date {batch_date}.")
        transaction_number = scalar(
            cursor, "SELECT NextTransactionNumber FROM tblAccountingOrganization WHERE ID=? FOR UPDATE",
            (organization,),
        )
        cursor.execute(
            "UPDATE tblAccountingOrganization SET NextTransactionNumber=? WHERE ID=?",
            (transaction_number + 1, organization),
        )
        cursor.execute(
            "INSERT INTO tblAccountingTransaction "
            "(OrganizationID,TransactionNumber,TransactionDate,FiscalPeriodID,TransactionType,Status,"
            "Description,Reference,CreatedByUserID,ReviewedByUserID,ReviewedAt,PostedByUserID,PostedAt) "
            "VALUES (?,?,?,?,'CASH_RECEIPT','POSTED',?,?,?,?,CURRENT_TIMESTAMP(6),?,CURRENT_TIMESTAMP(6))",
            (organization, transaction_number, batch_date, period_id,
             f"Contribution deposit - {description}", f"Giving batch {batch_id}",
             user_id, user_id, user_id),
        )
        transaction_id = cursor.lastrowid
        cursor.execute(
            "SELECT a.FundID,a.RevenueAccountID,a.FunctionID,SUM(a.Amount) "
            "FROM tblContributionAllocation a JOIN tblContribution g ON g.ID=a.ContributionID "
            "WHERE g.BatchID=? GROUP BY a.FundID,a.RevenueAccountID,a.FunctionID "
            "ORDER BY a.FundID,a.RevenueAccountID,a.FunctionID",
            (batch_id,),
        )
        credits = cursor.fetchall()
        debits = {}
        for fund_id, _account_id, _function_id, amount in credits:
            debits[fund_id] = debits.get(fund_id, Decimal("0.00")) + Decimal(amount)
        line_number = 1
        for fund_id, amount in sorted(debits.items()):
            cursor.execute(
                "INSERT INTO tblAccountingTransactionLine "
                "(TransactionID,LineNumber,AccountID,FundID,Description,Debit,Credit) "
                "VALUES (?,?,?,?,'Contribution deposit',?,0.00)",
                (transaction_id, line_number, bank_account, fund_id, amount),
            )
            line_number += 1
        for fund_id, account_id, allocation_function, amount in credits:
            cursor.execute(
                "INSERT INTO tblAccountingTransactionLine "
                "(TransactionID,LineNumber,AccountID,FundID,FunctionID,Description,Debit,Credit) "
                "VALUES (?,?,?,?,?,'Contribution revenue',0.00,?)",
                (transaction_id, line_number, account_id, fund_id, allocation_function, amount),
            )
            line_number += 1
        cursor.execute(
            "UPDATE tblContributionBatch SET AccountingTransactionID=?,Status='POSTED',"
            "ReviewedByUserID=?,ReviewedAt=CURRENT_TIMESTAMP(6),PostedByUserID=?,"
            "PostedAt=CURRENT_TIMESTAMP(6),Version=Version+1 WHERE ID=?",
            (transaction_id, user_id, user_id, batch_id),
        )
        safe = json.dumps({"status": "POSTED", "transaction_number": transaction_number,
                           "total": str(total)}, separators=(",", ":"))
        cursor.execute(
            "INSERT INTO tblAccountingAuditEvent "
            "(OrganizationID,EntityType,EntityID,Action,AfterJSON,UserID) "
            "VALUES (?,'TRANSACTION',?,'TRANSACTION_POSTED',?,?)",
            (organization, str(transaction_id), safe, user_id),
        )

    def create_batch(batch_date, description, status, gifts):
        total = sum((gift[3] for gift in gifts), Decimal("0.00"))
        cursor.execute("INSERT INTO tblContributionBatch "
                       "(ChurchID,BatchDate,Description,DepositDate,OrganizationID,BankAccountID,Status,"
                       "ControlTotal,CalculatedTotal,EnteredByUserID,ReviewedByUserID,ReviewedAt) "
                       "VALUES (?,?,?,?,?,?,?,?,?,?,?,CASE WHEN ?='READY' THEN CURRENT_TIMESTAMP(6) ELSE NULL END)",
                       (church_id, batch_date, description, batch_date, organization, bank, status,
                        total, total, user_id, user_id if status == "READY" else None, status))
        batch_id = cursor.lastrowid
        for gift in gifts:
            contributor_id, envelope, method, amount, reference, splits = gift[:6]
            eligibility = gift[6] if len(gift) > 6 else "ELIGIBLE"
            cursor.execute("INSERT INTO tblContribution "
                           "(BatchID,ContributorID,EnteredEnvelopeNumber,ContributionMethod,ReferenceValue,"
                           "ReceivedDate,Amount,StatementEligibility,Note) VALUES (?,?,?,?,?,?,?,? ,"
                           "'Fictional giving acceptance data')",
                           (batch_id, contributor_id, envelope, method, reference, batch_date, amount,
                            eligibility))
            contribution_id = cursor.lastrowid
            for purpose_index, split_amount in splits:
                purpose_id, fund_id, account_id, allocation_function = purposes[purpose_index]
                cursor.execute("INSERT INTO tblContributionAllocation "
                               "(ContributionID,PurposeID,OrganizationID,FundID,RevenueAccountID,FunctionID,Amount) "
                               "VALUES (?,?,?,?,?,?,?)",
                               (contribution_id, purpose_id, organization, fund_id, account_id,
                                allocation_function, split_amount))
        if status == "POSTED":
            post_batch(batch_id, batch_date, description, total)
        cursor.execute("INSERT INTO tblContributionAuditEvent "
                       "(ChurchID,UserID,Action,EntityType,EntityID,SafeReference) "
                       "VALUES (?,?,?,'BATCH',?,?)",
                       (church_id, user_id, "BATCH_POSTED" if status == "POSTED" else
                        ("BATCH_MARKED_READY" if status == "READY" else "BATCH_CREATED"),
                        batch_id, f"Fictional {status.lower()} batch {batch_id}"))

    create_batch(draft_date, "TEST - Sunday Offering Entry", "DRAFT", (
        (contributors[0], "101", "CHECK", Decimal("500.00"), "TEST-1001", ((0, Decimal("500.00")),)),
        (contributors[1], "102", "CHECK", Decimal("250.00"), "TEST-1002", ((0, Decimal("150.00")), (1, Decimal("100.00")))),
        (contributors[4], None, "ELECTRONIC", Decimal("400.00"), "TEST-EGIVE-1", ((2, Decimal("400.00")),)),
        (None, None, "CASH", Decimal("125.00"), None, ((0, Decimal("125.00")),)),
    ))
    create_batch(ready_date, "TEST - Ready Deposit", "READY", (
        (contributors[0], "101", "CHECK", Decimal("300.00"), "TEST-2001", ((0, Decimal("300.00")),)),
        (contributors[3], "201", "CHECK", Decimal("300.00"), "TEST-2002", ((1, Decimal("300.00")),)),
        (None, None, "CASH", Decimal("200.00"), None, ((0, Decimal("200.00")),)),
    ))

    # One posted deposit in each open quarter gives the statement screen a
    # useful year of history while keeping the familiar Draft and Ready batches.
    quarterly_periods = {}
    for period_id, start_date, end_date in open_periods:
        representative = start_date + ((end_date - start_date) // 2)
        quarterly_periods.setdefault((representative.year, (representative.month - 1) // 3 + 1),
                                     (period_id, representative))
    years = {}
    for (year, quarter), row in quarterly_periods.items():
        years.setdefault(year, {})[quarter] = row
    statement_year, statement_quarters = max(years.items(), key=lambda item: (len(item[1]), item[0]))
    if len(statement_quarters) < 4:
        raise RuntimeError("Four open fiscal quarters are required for contribution statement test data.")
    posted_specs = (
        (1, "TEST - First Quarter Posted", (
            (contributors[0], "101", "CHECK", Decimal("120.00"), "TEST-Q1-101", ((0, Decimal("120.00")),)),
            (contributors[1], "102", "CHECK", Decimal("75.00"), "TEST-Q1-102", ((1, Decimal("75.00")),)),
        )),
        (2, "TEST - Second Quarter Posted", (
            (contributors[0], "101", "ELECTRONIC", Decimal("140.00"), "TEST-Q2-101", ((0, Decimal("140.00")),)),
            (contributors[2], "103", "CHECK", Decimal("90.00"), "TEST-Q2-103", ((2, Decimal("90.00")),)),
        )),
        (3, "TEST - Third Quarter Posted", (
            (contributors[1], "102", "CHECK", Decimal("160.00"), "TEST-Q3-102", ((0, Decimal("160.00")),)),
            (contributors[3], "201", "CHECK", Decimal("110.00"), "TEST-Q3-201", ((1, Decimal("110.00")),)),
        )),
        (4, "TEST - Fourth Quarter Posted", (
            (contributors[0], "101", "CHECK", Decimal("180.00"), "TEST-Q4-101", ((0, Decimal("180.00")),)),
            (contributors[4], None, "ELECTRONIC", Decimal("130.00"), "TEST-Q4-EXT", ((2, Decimal("130.00")),)),
            (contributors[2], "103", "OTHER", Decimal("50.00"), "TEST-Q4-INELIGIBLE",
             ((0, Decimal("50.00")),), "INELIGIBLE"),
        )),
    )
    for quarter, description, gifts in posted_specs:
        create_batch(statement_quarters[quarter][1], description, "POSTED", gifts)
    print(f"statement_test_year={statement_year}")
    return statement_year


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="back up, replace, and verify giving test data")
    args = parser.parse_args()
    config, testing, username, password = settings()
    connection = mariadb.connect(host=testing["host"], port=int(testing.get("port", 3306)),
                                 database=testing["database"], user=username,
                                 password=password, autocommit=False)
    cursor = connection.cursor()
    try:
        print(f"target={testing['host']}/{testing['database']}")
        for table, count in counts(cursor).items(): print(f"before_{table}={count}")
        if not args.apply:
            print("No changes made. Re-run with --apply after reviewing the counts.")
            return 2
        path, size, digest = create_backup(testing, username, password)
        print(f"backup={path}"); print(f"backup_bytes={size}"); print(f"backup_sha256={digest}")
        remove_existing(cursor); statement_year = seed(cursor)
        after = counts(cursor)
        for table, count in after.items(): print(f"after_{table}={count}")
        expected = {"tblContributionContributor": 5, "tblContributionEnvelopeAssignment": 4,
                    "tblContributionPurpose": 3, "tblContributionBatch": 6,
                    "tblContribution": 16, "tblContributionAllocation": 17,
                    "tblContributionAuditEvent": 6}
        if any(after[name] != count for name, count in expected.items()):
            raise RuntimeError("Giving test dataset verification failed.")
        cursor.execute(
            "SELECT QUARTER(g.ReceivedDate),COUNT(DISTINCT g.ContributorID) "
            "FROM tblContribution g JOIN tblContributionBatch b ON b.ID=g.BatchID "
            "JOIN tblContributionAllocation a ON a.ContributionID=g.ID "
            "LEFT JOIN tblContributionPurpose p ON p.ID=a.PurposeID "
            "JOIN tblContributionContributor c ON c.ID=g.ContributorID "
            "WHERE YEAR(g.ReceivedDate)=? AND b.Status='POSTED' "
            "AND c.StatementEnabled=1 AND g.StatementEligibility='ELIGIBLE' "
            "AND (p.ID IS NULL OR p.StatementTreatment='ELIGIBLE') "
            "GROUP BY QUARTER(g.ReceivedDate) ORDER BY QUARTER(g.ReceivedDate)",
            (statement_year,),
        )
        quarterly_statement_counts = {int(row[0]): int(row[1]) for row in cursor.fetchall()}
        for quarter in range(1, 5):
            print(f"statement_q{quarter}_contributors={quarterly_statement_counts.get(quarter, 0)}")
        if quarterly_statement_counts != {1: 2, 2: 2, 3: 2, 4: 2}:
            raise RuntimeError("Quarterly contribution statement test data verification failed.")
        connection.commit()
        print("giving_test_dataset_verified=true")
        return 0
    except Exception:
        connection.rollback(); raise
    finally:
        cursor.close(); connection.close()


if __name__ == "__main__": raise SystemExit(main())
