import datetime
import JSForm


def fnposttogl(dbconnection,record):
    """
    Args:
        record:{
            "LedgerID:rec["LedgerID"],
            "ChurchID":rec["ChurchID"],
            "DebitAccountID": rec["DebitAccountID"],
            "CreditAccountID": rec["CreditAccountID"],
            "Description": "Check #" + rec["CheckNumber"],
            "Amount": rec["Amount"],
            "Note": rec["Note"],
        }
    Returns:
        lid: LedgerID
    """

    if record["LedgerID"] != None:
        return False
    postdate = datetime.datetime.now().strftime("%m/%d/%Y")
    fiscalyear = JSForm.CONFIG.get_Config_Value("Financial", "FiscalYear")
    tblgl = {"name": "tblLedger", "fields": ["*"]}
    SQL = JSForm.clsSQL(dbconnection, tblgl)
    ledgerrec = {
        "ChurchID": record["ChurchID"],
        "Date": postdate,
        "FiscalYear": fiscalyear,
        "DebitAccountID": record["DebitAccountID"],
        "CreditAccountID": record["CreditAccountID"],
        "Description": record["Description"],
        "Amount": record["Amount"],
        "Note": record["Note"],
    }
    sql = SQL.insert(ledgerrec)
    cursor = dbconnection.cursor()
    try:
        cursor.execute(sql)
    except Exception as ex:
        print("sql error {err}:{sql} ".format(err=ex, sql=sql))
    dbconnection.commit()

    # Get the ID (autoincrement field) from the last Insert

    sql = "SELECT Last_Insert_ID();"
    try:
        cursor.execute(sql)
    except Exception as ex:
        print("sql error {err}:{sql} ".format(err=ex, sql=sql))
    lid = cursor.fetchone()
    cursor.close()
    return lid[0]

