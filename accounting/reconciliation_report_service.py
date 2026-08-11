"""Read-only proof and item detail for completed bank reconciliations."""

from decimal import Decimal


class ReconciliationReportService:
    def __init__(self, connection):
        self.connection = connection
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def completed(self):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT r.ID,b.Name,r.StatementDate,r.BeginningBalance,r.EndingBalance,"
                "COALESCE(SUM(i.ClearedAmount),0),u.DisplayName,r.CompletedAt "
                "FROM tblAccountingReconciliation r "
                "JOIN tblAccountingBankAccount b ON b.ID=r.BankAccountID "
                "JOIN tblUser u ON u.ID=r.PreparedByUserID "
                "LEFT JOIN tblAccountingReconciliationItem i ON i.ReconciliationID=r.ID "
                "WHERE r.Status='COMPLETED' "
                "GROUP BY r.ID,b.Name,r.StatementDate,r.BeginningBalance,r.EndingBalance,"
                "u.DisplayName,r.CompletedAt ORDER BY r.StatementDate DESC,r.ID DESC")
            return cursor.fetchall()
        finally:
            cursor.close()

    def detail(self, reconciliation_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT r.BankAccountID,b.AccountID,r.StatementDate,r.BeginningBalance,"
                "r.EndingBalance,b.Name FROM tblAccountingReconciliation r "
                "JOIN tblAccountingBankAccount b ON b.ID=r.BankAccountID "
                "WHERE r.ID=? AND r.Status='COMPLETED'", (reconciliation_id,))
            header = cursor.fetchone()
            if header is None:
                raise ValueError("Select a completed reconciliation.")
            self._execute(cursor,
                "SELECT 'Cleared',t.TransactionDate,t.TransactionNumber,"
                "COALESCE(ir.Description,t.Description),COALESCE(ir.Reference,t.Reference),"
                "i.ClearedAmount,i.ClearedDate "
                "FROM tblAccountingReconciliationItem i "
                "JOIN tblAccountingTransactionLine l ON l.ID=i.TransactionLineID "
                "JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
                "LEFT JOIN tblAccountingBankImportRow ir ON ir.ID=i.ImportRowID "
                "WHERE i.ReconciliationID=? ORDER BY i.ClearedDate,t.TransactionNumber",
                (reconciliation_id,))
            cleared = cursor.fetchall()
            self._execute(cursor,
                "SELECT 'Outstanding',t.TransactionDate,t.TransactionNumber,t.Description,"
                "t.Reference,l.Debit-l.Credit,NULL "
                "FROM tblAccountingTransactionLine l "
                "JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
                "WHERE l.AccountID=? AND t.Status IN ('POSTED','REVERSED') "
                "AND t.TransactionDate<=? AND NOT EXISTS ("
                "SELECT 1 FROM tblAccountingReconciliationItem used "
                "JOIN tblAccountingReconciliation prior ON prior.ID=used.ReconciliationID "
                "WHERE used.TransactionLineID=l.ID AND prior.StatementDate<=?) "
                "ORDER BY t.TransactionDate,t.TransactionNumber,l.LineNumber",
                (header[1], header[2], header[2]))
            outstanding = cursor.fetchall()
            cleared_total = sum((Decimal(row[5]) for row in cleared), Decimal("0"))
            difference = Decimal(header[4]) - (Decimal(header[3]) + cleared_total)
            outstanding_total = sum((Decimal(row[5]) for row in outstanding), Decimal("0"))
            return {
                "bank_account": header[5], "statement_date": header[2],
                "beginning": Decimal(header[3]), "ending": Decimal(header[4]),
                "cleared_total": cleared_total, "difference": difference,
                "outstanding_total": outstanding_total,
                "items": list(cleared) + list(outstanding),
            }
        finally:
            cursor.close()
