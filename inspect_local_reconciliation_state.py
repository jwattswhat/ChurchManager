"""Read-only development diagnostic for bank reconciliation test state."""

import json
import mariadb
from churchmanager_mode import resolve_database

config = json.load(open("churchmanager.json", encoding="utf-8"))
database = config["database_settings"]
settings = resolve_database({
    "server": database["host"], "database": database["database"],
    "user": database["user"], "password": None, "test_mode": True,
    "jsform_database": None,
}, config)
connection = mariadb.connect(
    host=settings["server"], port=settings["port"], database=settings["database"],
    user=settings["user"], password=settings["password"],
)
try:
    cursor = connection.cursor()
    cursor.execute(
        "SELECT i.OriginalName,r.RowNumber,r.TransactionDate,r.Amount,r.MatchStatus "
        "FROM tblAccountingBankImportRow r "
        "JOIN tblAccountingBankImportBatch i ON i.ID=r.ImportBatchID "
        "ORDER BY i.ID,r.RowNumber"
    )
    for row in cursor.fetchall():
        print(row)
finally:
    connection.close()
