"""Complete read-only journal-entry report data for a posted transaction."""


class JournalEntryService:
    def __init__(self, connection):
        self.connection = connection
        self.marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def report(self, transaction_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT t.ID,t.TransactionNumber,o.LegalName,t.TransactionDate,t.TransactionType,t.Status,"
                "t.Description,COALESCE(t.Reference,''),t.CreatedAt,creator.DisplayName,t.ReviewedAt,"
                "COALESCE(reviewer.DisplayName,''),t.PostedAt,COALESCE(poster.DisplayName,''),"
                "original.TransactionNumber,reversal.TransactionNumber "
                "FROM tblAccountingTransaction t JOIN tblAccountingOrganization o ON o.ID=t.OrganizationID "
                "JOIN tblUser creator ON creator.ID=t.CreatedByUserID "
                "LEFT JOIN tblUser reviewer ON reviewer.ID=t.ReviewedByUserID "
                "LEFT JOIN tblUser poster ON poster.ID=t.PostedByUserID "
                "LEFT JOIN tblAccountingTransaction original ON original.ID=t.OriginalTransactionID "
                "LEFT JOIN tblAccountingTransaction reversal ON reversal.ID=t.ReversalTransactionID "
                "WHERE t.ID=? AND t.Status IN ('POSTED','REVERSED')", (transaction_id,))
            header = cursor.fetchone()
            if header is None:
                raise ValueError("Select a posted or reversed transaction.")
            self._execute(cursor,
                "SELECT l.LineNumber,CONCAT(a.Code,' - ',a.Name),CONCAT(f.Code,' - ',f.Name),"
                "COALESCE(fn.Name,''),COALESCE(p.Name,''),COALESCE(l.Description,''),l.Debit,l.Credit "
                "FROM tblAccountingTransactionLine l JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "JOIN tblAccountingFund f ON f.ID=l.FundID LEFT JOIN tblAccountingFunction fn ON fn.ID=l.FunctionID "
                "LEFT JOIN tblAccountingPayee p ON p.ID=l.PayeeID WHERE l.TransactionID=? ORDER BY l.LineNumber",
                (transaction_id,))
            lines = cursor.fetchall()
            self._execute(cursor,
                "SELECT OriginalName,COALESCE(DocumentType,''),FileHash,AddedAt FROM tblAccountingAttachment "
                "WHERE TransactionID=? ORDER BY AddedAt,ID", (transaction_id,))
            attachments = cursor.fetchall()
            return {"header": header, "lines": lines, "attachments": attachments}
        finally:
            cursor.close()
