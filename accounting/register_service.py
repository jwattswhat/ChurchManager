"""Read-only queries for the posted accounting transaction register."""

class AccountingRegisterService:
    def __init__(self, connection):
        self.connection = connection
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def transactions(self):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT t.ID, t.TransactionNumber, o.LegalName, t.TransactionDate, "
                "t.TransactionType, t.Status, t.Description, t.Reference, "
                "COALESCE(SUM(l.Debit),0) FROM tblAccountingTransaction t "
                "JOIN tblAccountingOrganization o ON o.ID=t.OrganizationID "
                "JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID "
                "WHERE t.Status IN ('POSTED','REVERSED') "
                "GROUP BY t.ID, t.TransactionNumber, o.LegalName, t.TransactionDate, "
                "t.TransactionType, t.Status, t.Description, t.Reference "
                "ORDER BY t.TransactionDate DESC, t.TransactionNumber DESC")
            return cursor.fetchall()
        finally:
            cursor.close()

    def lines(self, transaction_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT l.LineNumber, CONCAT(a.Code, ' - ', a.Name), "
                "CONCAT(f.Code, ' - ', f.Name), COALESCE(fn.Name,''), "
                "COALESCE(p.Name,''), l.Description, l.Debit, l.Credit "
                "FROM tblAccountingTransactionLine l "
                "JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "JOIN tblAccountingFund f ON f.ID=l.FundID "
                "LEFT JOIN tblAccountingFunction fn ON fn.ID=l.FunctionID "
                "LEFT JOIN tblAccountingPayee p ON p.ID=l.PayeeID "
                "WHERE l.TransactionID=? ORDER BY l.LineNumber", (transaction_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
