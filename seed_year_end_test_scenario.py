"""Preview or install an isolated fiscal-year-close scenario in local ChurchDBTest."""
from __future__ import annotations

import argparse
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import mariadb

from credential_store import read_credential
from accounting.year_end_service import YearEndService


ROOT = Path(__file__).resolve().parent
SCENARIO_NAME = "Year-End Close Test Congregation"


def settings():
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    host = str(testing["host"])
    database = str(testing["database"])
    if host not in {"127.0.0.1", "localhost", "::1"} or database.casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: year-end test data is restricted to local ChurchDBTest.")
    username, password = read_credential(testing["credential_target"])
    return testing, username, password


def add_transaction(cursor, organization_id, period_id, user_id, number, reference, description, lines):
    cursor.execute(
        "INSERT INTO tblAccountingTransaction "
        "(OrganizationID,TransactionNumber,TransactionDate,FiscalPeriodID,TransactionType,Status,Description,Reference,Version,CreatedByUserID,ReviewedByUserID,ReviewedAt,PostedByUserID,PostedAt) "
        "VALUES (?,?,?,?, 'JOURNAL','POSTED',?,?,1,?,?,CURRENT_TIMESTAMP(6),?,CURRENT_TIMESTAMP(6))",
        (organization_id, number, date(2026, 12, 15), period_id, description, reference,
         user_id, user_id, user_id),
    )
    transaction_id = cursor.lastrowid
    for line_number, (account_id, fund_id, function_id, debit, credit) in enumerate(lines, 1):
        cursor.execute(
            "INSERT INTO tblAccountingTransactionLine "
            "(TransactionID,LineNumber,AccountID,FundID,FunctionID,Description,Debit,Credit) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (transaction_id, line_number, account_id, fund_id, function_id, description,
             Decimal(str(debit)), Decimal(str(credit))),
        )
    cursor.execute(
        "INSERT INTO tblAccountingAuditEvent "
        "(OrganizationID,EntityType,EntityID,Action,AfterJSON,Reason,UserID) "
        "VALUES (?,'TRANSACTION',?,'SYNTHETIC_YEAR_END_POSTED',?,'Isolated year-end close test scenario',?)",
        (organization_id, str(transaction_id), json.dumps({"reference": reference, "transaction_number": number}), user_id),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    testing, username, password = settings()
    connection = mariadb.connect(host=testing["host"], port=int(testing.get("port", 3306)),
                                 database=testing["database"], user=username, password=password,
                                 autocommit=False)
    password = ""
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT ID FROM tblAccountingOrganization WHERE LegalName=?", (SCENARIO_NAME,))
        existing = cursor.fetchone()
        print("target", testing["database"])
        print("scenario", SCENARIO_NAME)
        print("existing", bool(existing))
        print("expected_revenue", "12500.00")
        print("expected_expenses", "4500.00")
        print("expected_change_in_net_assets", "8000.00")
        if existing:
            cursor.execute("SELECT ID FROM tblAccountingFiscalYear WHERE OrganizationID=? AND Name='Year-End Test 2026'", (existing[0],))
            year = cursor.fetchone()
            if year is None:
                raise RuntimeError("The scenario organization exists without its expected fiscal year.")
            report = YearEndService(connection).preview(existing[0], year[0])
            print("organization_id", existing[0])
            print("fiscal_year_id", year[0])
            print("preview_ready", report["ready"])
            print("preview_blockers", len(report["blockers"]))
            print("funds", len(report["rows"]))
            print("change_in_net_assets", sum((row[6] for row in report["rows"]), Decimal("0")))
            cursor.execute("SELECT Status,ClosingTransactionID FROM tblAccountingFiscalYear WHERE ID=?", (year[0],))
            year_status, closing_transaction_id = cursor.fetchone()
            print("year_status", year_status)
            print("closing_transaction_id", closing_transaction_id)
            if closing_transaction_id is not None:
                cursor.execute("SELECT TransactionNumber,Status FROM tblAccountingTransaction WHERE ID=?", (closing_transaction_id,))
                closing_number, closing_status = cursor.fetchone()
                cursor.execute("SELECT COALESCE(SUM(Debit),0),COALESCE(SUM(Credit),0) FROM tblAccountingTransactionLine WHERE TransactionID=?", (closing_transaction_id,))
                closing_debit, closing_credit = cursor.fetchone()
                cursor.execute("SELECT COALESCE(SUM(CASE WHEN a.AccountType IN ('REVENUE','EXPENSE','TRANSFER') THEN l.Debit-l.Credit ELSE 0 END),0) FROM tblAccountingTransaction t JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID JOIN tblAccountingAccount a ON a.ID=l.AccountID WHERE t.OrganizationID=? AND t.TransactionDate BETWEEN '2026-01-01' AND '2026-12-31' AND t.Status IN ('POSTED','REVERSED')", (existing[0],))
                nominal_balance = cursor.fetchone()[0]
                print("closing_transaction_number", closing_number)
                print("closing_transaction_status", closing_status)
                print("closing_debits", closing_debit)
                print("closing_credits", closing_credit)
                print("nominal_accounts_net_balance", nominal_balance)
            print("No changes made: the isolated scenario already exists.")
            return 0
        if not args.apply:
            print("No changes made. Re-run with --apply.")
            return 2
        cursor.execute("SELECT ID FROM tblUser WHERE Active=1 AND MasterAdministrator=1 ORDER BY ID LIMIT 1")
        user = cursor.fetchone()
        if user is None:
            raise RuntimeError("No active master administrator is available for test-data ownership.")
        user_id = user[0]
        cursor.execute(
            "INSERT INTO tblAccountingOrganization "
            "(LegalName,FiscalYearStartMonth,ReportingBasis,NextTransactionNumber,ApprovalThreshold,ApprovalPolicy,AttachmentThreshold,Active) "
            "VALUES (?,1,'MODIFIED_CASH',5,500.00,'INDEPENDENT_PREFERRED',250.00,1)",
            (SCENARIO_NAME,),
        )
        organization_id = cursor.lastrowid
        accounts = {}
        for code, name, account_type, normal, function_rule, order in (
            ("1000", "Checking", "ASSET", "DEBIT", "PROHIBITED", 10),
            ("3000", "Net Assets Without Donor Restrictions", "NET_ASSET", "CREDIT", "PROHIBITED", 20),
            ("3200", "Net Assets With Donor Restrictions", "NET_ASSET", "CREDIT", "PROHIBITED", 30),
            ("4000", "General Contributions", "REVENUE", "CREDIT", "OPTIONAL", 40),
            ("4100", "Restricted Contributions", "REVENUE", "CREDIT", "OPTIONAL", 50),
            ("5300", "Worship", "EXPENSE", "DEBIT", "REQUIRED", 60),
            ("5600", "Property and Utilities", "EXPENSE", "DEBIT", "REQUIRED", 70),
        ):
            cursor.execute(
                "INSERT INTO tblAccountingAccount "
                "(OrganizationID,Code,Name,AccountType,NormalBalance,PostingAllowed,FunctionRequirement,DisplayOrder,Active) "
                "VALUES (?,?,?,?,?,1,?,?,1)",
                (organization_id, code, name, account_type, normal, function_rule, order),
            )
            accounts[code] = cursor.lastrowid
        funds = {}
        for code, name, net_class, restriction, net_account in (
            ("GENERAL", "General Operating", "WITHOUT_DONOR_RESTRICTIONS", "NONE", accounts["3000"]),
            ("BUILDING", "Building Project", "WITH_DONOR_RESTRICTIONS", "PURPOSE", accounts["3200"]),
        ):
            cursor.execute(
                "INSERT INTO tblAccountingFund "
                "(OrganizationID,Code,Name,NetAssetClass,RestrictionType,NetAssetAccountID,Active) VALUES (?,?,?,?,?,?,1)",
                (organization_id, code, name, net_class, restriction, net_account),
            )
            funds[code] = cursor.lastrowid
        cursor.execute("INSERT INTO tblAccountingFunction (OrganizationID,Code,Name,FunctionClass,DisplayOrder,Active) VALUES (?,'WORSHIP','Worship','PROGRAM',10,1)", (organization_id,))
        worship = cursor.lastrowid
        cursor.execute("INSERT INTO tblAccountingFunction (OrganizationID,Code,Name,FunctionClass,DisplayOrder,Active) VALUES (?,'MGMT','Management and General','MANAGEMENT_GENERAL',20,1)", (organization_id,))
        management = cursor.lastrowid
        cursor.execute("INSERT INTO tblAccountingFiscalYear (OrganizationID,Name,StartDate,EndDate,Status) VALUES (?,'Year-End Test 2026','2026-01-01','2026-12-31','OPEN')", (organization_id,))
        year_id = cursor.lastrowid
        cursor.execute("INSERT INTO tblAccountingFiscalPeriod (FiscalYearID,PeriodNumber,Name,StartDate,EndDate,Status) VALUES (?,1,'Full Year 2026','2026-01-01','2026-12-31','CLOSED')", (year_id,))
        period_id = cursor.lastrowid
        add_transaction(cursor, organization_id, period_id, user_id, 1, "YE-TEST-GENERAL-GIFTS", "General contributions", ((accounts["1000"], funds["GENERAL"], None, 10000, 0), (accounts["4000"], funds["GENERAL"], None, 0, 10000)))
        add_transaction(cursor, organization_id, period_id, user_id, 2, "YE-TEST-GENERAL-EXPENSE", "General operating expenses", ((accounts["5600"], funds["GENERAL"], management, 3500, 0), (accounts["1000"], funds["GENERAL"], None, 0, 3500)))
        add_transaction(cursor, organization_id, period_id, user_id, 3, "YE-TEST-RESTRICTED-GIFT", "Restricted building contributions", ((accounts["1000"], funds["BUILDING"], None, 2500, 0), (accounts["4100"], funds["BUILDING"], None, 0, 2500)))
        add_transaction(cursor, organization_id, period_id, user_id, 4, "YE-TEST-RESTRICTED-EXPENSE", "Restricted worship improvements", ((accounts["5300"], funds["BUILDING"], worship, 1000, 0), (accounts["1000"], funds["BUILDING"], None, 0, 1000)))
        connection.commit()
        print("organization_id", organization_id)
        print("fiscal_year_id", year_id)
        print("posted_transactions", 4)
        print("closed_periods", 1)
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
