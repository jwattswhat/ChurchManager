"""Read-only diagnostic for local staged bank matching."""

import json

import mariadb

from churchmanager_mode import resolve_database


config = json.load(open("churchmanager.json", encoding="utf-8"))
database = config["database_settings"]
settings = resolve_database(
    {
        "server": database["host"], "database": database["database"],
        "user": database["user"], "password": None, "test_mode": True,
        "jsform_database": None,
    }, config,
)
connection = mariadb.connect(
    host=settings["server"], port=settings["port"], database=settings["database"],
    user=settings["user"], password=settings["password"],
)
try:
    cursor = connection.cursor()
    cursor.execute(
        "SELECT r.ID,r.TransactionDate,r.Amount,r.MatchStatus,b.Name,a.ID,a.Code,a.Name "
        "FROM tblAccountingBankImportRow r "
        "JOIN tblAccountingBankImportBatch i ON i.ID=r.ImportBatchID "
        "JOIN tblAccountingBankAccount b ON b.ID=i.BankAccountID "
        "JOIN tblAccountingAccount a ON a.ID=b.AccountID "
        "ORDER BY r.ID DESC LIMIT 10"
    )
    print("STAGED")
    for row in cursor.fetchall():
        print(row)
    cursor.execute(
        "SELECT l.ID,t.TransactionNumber,t.TransactionDate,l.Debit-l.Credit,a.ID,a.Code,a.Name "
        "FROM tblAccountingTransactionLine l "
        "JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
        "JOIN tblAccountingAccount a ON a.ID=l.AccountID "
        "WHERE t.Status='POSTED' ORDER BY t.TransactionDate,t.TransactionNumber,l.LineNumber"
    )
    print("POSTED")
    for row in cursor.fetchall():
        print(row)
finally:
    connection.close()
