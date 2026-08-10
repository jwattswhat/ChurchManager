"""Read-only trial balance queries over the posted ledger."""
from decimal import Decimal

class TrialBalanceService:
    def __init__(self, connection):
        self.connection = connection
        self.marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"
    def _execute(self, cursor, sql, values=()): return cursor.execute(sql.replace("?", self.marker), values)
    def organizations(self):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT ID, LegalName FROM tblAccountingOrganization WHERE Active=1 ORDER BY LegalName")
            return cursor.fetchall()
        finally: cursor.close()
    def rows(self, organization_id, as_of_date):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT a.Code, a.Name, a.AccountType, a.NormalBalance, "
                "COALESCE(SUM(CASE WHEN t.ID IS NOT NULL THEN l.Debit ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN t.ID IS NOT NULL THEN l.Credit ELSE 0 END),0) "
                "FROM tblAccountingAccount a "
                "LEFT JOIN tblAccountingTransactionLine l ON l.AccountID=a.ID "
                "LEFT JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
                "AND t.Status IN ('POSTED','REVERSED') AND t.TransactionDate<=? "
                "WHERE a.OrganizationID=? AND a.PostingAllowed=1 "
                "GROUP BY a.ID, a.Code, a.Name, a.AccountType, a.NormalBalance "
                "HAVING COALESCE(SUM(CASE WHEN t.ID IS NOT NULL THEN l.Debit ELSE 0 END),0)<>0 "
                "OR COALESCE(SUM(CASE WHEN t.ID IS NOT NULL THEN l.Credit ELSE 0 END),0)<>0 "
                "ORDER BY a.DisplayOrder, a.Code", (as_of_date, organization_id))
            result = []
            for code, name, account_type, normal, debit, credit in cursor.fetchall():
                debit, credit = Decimal(debit), Decimal(credit)
                net = debit - credit
                result.append((code, name, account_type, normal, debit, credit,
                               net if net > 0 else Decimal("0"),
                               -net if net < 0 else Decimal("0")))
            return result
        finally: cursor.close()
