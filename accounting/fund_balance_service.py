"""Read-only fund activity and balance reporting."""

from decimal import Decimal


class FundBalanceService:
    def __init__(self, connection):
        self.connection = connection
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def organizations(self):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT ID,LegalName FROM tblAccountingOrganization "
                                  "WHERE Active=1 ORDER BY LegalName")
            return cursor.fetchall()
        finally:
            cursor.close()

    def report(self, organization_id, date_from, date_to):
        if date_to < date_from:
            raise ValueError("The Through date cannot be before the From date.")
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT f.Code,f.Name,f.NetAssetClass,"
                "COALESCE(SUM(CASE WHEN t.TransactionDate<? AND a.AccountType='ASSET' "
                "THEN l.Debit-l.Credit WHEN t.TransactionDate<? AND a.AccountType='LIABILITY' "
                "THEN l.Credit-l.Debit ELSE 0 END),0) AS BeginningBalance,"
                "COALESCE(SUM(CASE WHEN t.TransactionDate<=? AND a.AccountType='ASSET' "
                "THEN l.Debit-l.Credit WHEN t.TransactionDate<=? AND a.AccountType='LIABILITY' "
                "THEN l.Credit-l.Debit ELSE 0 END),0) AS EndingBalance,"
                "COALESCE(SUM(CASE WHEN t.TransactionDate BETWEEN ? AND ? "
                "AND a.AccountType='REVENUE' THEN l.Credit-l.Debit ELSE 0 END),0),"
                "COALESCE(SUM(CASE WHEN t.TransactionDate BETWEEN ? AND ? "
                "AND a.AccountType='EXPENSE' THEN l.Debit-l.Credit ELSE 0 END),0),"
                "COALESCE(SUM(CASE WHEN t.TransactionDate BETWEEN ? AND ? "
                "AND a.AccountType='TRANSFER' THEN l.Credit-l.Debit ELSE 0 END),0) "
                "FROM tblAccountingFund f "
                "LEFT JOIN tblAccountingTransactionLine l ON l.FundID=f.ID "
                "LEFT JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
                "AND t.Status IN ('POSTED','REVERSED') "
                "LEFT JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "WHERE f.OrganizationID=? "
                "GROUP BY f.ID,f.Code,f.Name,f.NetAssetClass ORDER BY f.Code",
                (date_from, date_from, date_to, date_to,
                 date_from, date_to, date_from, date_to, date_from, date_to,
                 organization_id))
            result = []
            for row in cursor.fetchall():
                beginning, ending = Decimal(row[3]), Decimal(row[4])
                revenue, expense, transfers = map(Decimal, row[5:8])
                other = ending - beginning - (revenue - expense + transfers)
                result.append((*row[:3], beginning, revenue, expense, transfers,
                               other, ending))
            return result
        finally:
            cursor.close()
