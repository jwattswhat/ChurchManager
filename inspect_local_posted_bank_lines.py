"""Read-only development diagnostic for posted bank-account ledger lines."""

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
    },
    config,
)
connection = mariadb.connect(
    host=settings["server"], port=settings["port"],
    database=settings["database"], user=settings["user"],
    password=settings["password"],
)
try:
    cursor = connection.cursor()
    cursor.execute(
        "SELECT t.TransactionNumber,t.TransactionDate,a.Code,a.Name,"
        "l.Debit,l.Credit,t.Description "
        "FROM tblAccountingTransactionLine l "
        "JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
        "JOIN tblAccountingAccount a ON a.ID=l.AccountID "
        "JOIN tblAccountingBankAccount b ON b.AccountID=l.AccountID "
        "WHERE t.Status='POSTED' "
        "ORDER BY t.TransactionDate,t.TransactionNumber"
    )
    for row in cursor.fetchall():
        print(row)
finally:
    connection.close()
