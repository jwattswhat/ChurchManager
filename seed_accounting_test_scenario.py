"""Preview or install the standard synthetic ledger in guarded ChurchDBTest."""
from __future__ import annotations
import argparse,json
from datetime import date
from decimal import Decimal
import mariadb
from churchmanager_mode import resolve_database

def settings():
    config=json.load(open("churchmanager.json",encoding="utf-8-sig")); db=config["database_settings"]
    resolved=resolve_database({"server":db["host"],"database":db["database"],"user":db["user"],"password":None,"test_mode":True},config)
    if resolved["database"].casefold()=="churchdb" or "test" not in resolved["database"].casefold(): raise RuntimeError("Safety stop: seeding is restricted to a test database.")
    return config,resolved

SCENARIO=(
 ("SYNTHETIC-OPENING","Opening unrestricted balances",(("1000","GENERAL",None,"10000",0),("3000","GENERAL",None,0,"10000"))),
 ("SYNTHETIC-OFFERING","Unrestricted offerings",(("1000","GENERAL",None,"1000",0),("4000","GENERAL",None,0,"1000"))),
 ("SYNTHETIC-BUILDING-GIFT","Restricted building gift",(("1000","BUILDING",None,"500",0),("4100","BUILDING",None,0,"500"))),
 ("SYNTHETIC-UTILITY","General property expense",(("5600","GENERAL","MGMT","250",0),("1000","GENERAL",None,0,"250"))),
 ("SYNTHETIC-BUILDING-EXPENSE","Restricted building expense",(("5600","BUILDING","MGMT","100",0),("1000","BUILDING",None,0,"100"))),
 ("SYNTHETIC-TRANSFER","Transfer to operating reserve",(("8000","GENERAL",None,"200",0),("1000","GENERAL",None,0,"200"),("1000","RESERVE",None,"200",0),("8100","RESERVE",None,0,"200"))),
)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--apply",action="store_true");args=parser.parse_args()
    config,resolved=settings();db=config["database_settings"]
    connection=mariadb.connect(host=resolved["server"],port=int(db.get("port",3306)),database=resolved["database"],user=resolved["user"],password=resolved["password"],autocommit=False);cursor=connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM tblAccountingTransaction");existing=cursor.fetchone()[0]
        print("target",resolved["database"]);print("existing_transactions",existing);print("scenario_transactions",len(SCENARIO))
        print("expected_trial_balance_debits",Decimal("11700.00"));print("expected_trial_balance_credits",Decimal("11700.00"));print("expected_assets",Decimal("11150.00"));print("expected_liabilities_plus_net_assets",Decimal("11150.00"))
        if existing: raise RuntimeError("Safety stop: accounting transactions already exist. Reset first.")
        if not args.apply: print("No changes made. Re-run with --apply.");return 2
        cursor.execute("SELECT ID FROM tblAccountingOrganization WHERE Active=1 ORDER BY ID LIMIT 1");org=cursor.fetchone()[0]
        cursor.execute("SELECT ID FROM tblAccountingFiscalPeriod WHERE StartDate<=? AND EndDate>=? AND Status='OPEN'",(date(2027,1,15),date(2027,1,15)));period=cursor.fetchone()[0]
        cursor.execute("SELECT ID FROM tblUser WHERE Active=1 AND MasterAdministrator=1 ORDER BY ID LIMIT 1");user=cursor.fetchone()[0]
        cursor.execute("SELECT Code,ID FROM tblAccountingAccount WHERE OrganizationID=?",(org,));accounts=dict(cursor.fetchall())
        cursor.execute("SELECT Code,ID FROM tblAccountingFund WHERE OrganizationID=?",(org,));funds=dict(cursor.fetchall())
        cursor.execute("SELECT Code,ID FROM tblAccountingFunction WHERE OrganizationID=?",(org,));functions=dict(cursor.fetchall())
        cursor.execute("UPDATE tblAccountingOrganization SET NextTransactionNumber=1 WHERE ID=?",(org,))
        for number,(reference,description,lines) in enumerate(SCENARIO,1):
            cursor.execute("INSERT INTO tblAccountingTransaction (OrganizationID,TransactionNumber,TransactionDate,FiscalPeriodID,TransactionType,Status,Description,Reference,Version,CreatedByUserID,ReviewedByUserID,ReviewedAt,PostedByUserID,PostedAt) VALUES (?,?,?,?,'JOURNAL','POSTED',?,?,1,?,?,CURRENT_TIMESTAMP(6),?,CURRENT_TIMESTAMP(6))",(org,number,date(2027,1,15),period,description,reference,user,user,user));transaction_id=cursor.lastrowid
            for line_number,(account,fund,function,debit,credit) in enumerate(lines,1): cursor.execute("INSERT INTO tblAccountingTransactionLine (TransactionID,LineNumber,AccountID,FundID,FunctionID,Description,Debit,Credit) VALUES (?,?,?,?,?,?,?,?)",(transaction_id,line_number,accounts[account],funds[fund],functions.get(function),description,Decimal(str(debit)),Decimal(str(credit))))
            cursor.execute("INSERT INTO tblAccountingAuditEvent (OrganizationID,EntityType,EntityID,Action,AfterJSON,Reason,UserID) VALUES (?,'TRANSACTION',?,'SYNTHETIC_TEST_POSTED',?,'Standard ChurchDBTest accounting scenario',?)",(org,str(transaction_id),json.dumps({"reference":reference,"transaction_number":number}),user))
        cursor.execute("UPDATE tblAccountingOrganization SET NextTransactionNumber=7 WHERE ID=?",(org,));connection.commit();print("installed_transactions",len(SCENARIO));return 0
    except Exception:connection.rollback();raise
    finally:cursor.close();connection.close()
if __name__=="__main__":raise SystemExit(main())
