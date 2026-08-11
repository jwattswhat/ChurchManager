"""Read-only validation and fund summary for a fiscal year close."""
from decimal import Decimal


class YearEndService:
    def __init__(self, connection):
        self.connection = connection
        self.marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def organizations(self):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT ID,LegalName FROM tblAccountingOrganization WHERE Active=1 ORDER BY LegalName")
            return cursor.fetchall()
        finally:
            cursor.close()

    def years(self, organization_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT ID,CONCAT(Name,' (',Status,')') FROM tblAccountingFiscalYear WHERE OrganizationID=? ORDER BY StartDate DESC", (organization_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    def preview(self, organization_id, year_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT Name,StartDate,EndDate,Status,ClosingTransactionID FROM tblAccountingFiscalYear WHERE ID=? AND OrganizationID=?", (year_id, organization_id))
            year = cursor.fetchone()
            if year is None:
                raise ValueError("Select a fiscal year for this organization.")
            blockers = []
            if year[3] != "OPEN":
                blockers.append("The fiscal year is already {}.".format(year[3].lower()))
            self._execute(cursor, "SELECT COUNT(*) FROM tblAccountingFiscalPeriod WHERE FiscalYearID=? AND Status<>'CLOSED'", (year_id,))
            open_periods = cursor.fetchone()[0]
            if open_periods:
                blockers.append("{} fiscal period(s) are not closed.".format(open_periods))
            self._execute(cursor, "SELECT COUNT(*) FROM tblAccountingTransaction WHERE OrganizationID=? AND TransactionDate BETWEEN ? AND ? AND Status IN ('DRAFT','READY','APPROVED')", (organization_id, year[1], year[2]))
            unposted = cursor.fetchone()[0]
            if unposted:
                blockers.append("{} unposted transaction(s) remain in the fiscal year.".format(unposted))
            self._execute(cursor, "SELECT COALESCE(SUM(l.Debit-l.Credit),0) FROM tblAccountingTransaction t JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID WHERE t.OrganizationID=? AND t.Status IN ('POSTED','REVERSED') AND t.TransactionDate<=?", (organization_id, year[2]))
            difference = Decimal(cursor.fetchone()[0])
            if difference != 0:
                blockers.append("The posted ledger is out of balance by {}.".format(difference))
            self._execute(cursor,
                "SELECT f.ID,f.Code,f.Name,f.NetAssetAccountID,COALESCE(na.Code,''),COALESCE(na.Name,''),"
                "COALESCE(SUM(CASE WHEN a.AccountType='REVENUE' THEN l.Credit-l.Debit ELSE 0 END),0),"
                "COALESCE(SUM(CASE WHEN a.AccountType='EXPENSE' THEN l.Debit-l.Credit ELSE 0 END),0),"
                "COALESCE(SUM(CASE WHEN a.AccountType='TRANSFER' THEN l.Credit-l.Debit ELSE 0 END),0) "
                "FROM tblAccountingFund f LEFT JOIN tblAccountingAccount na ON na.ID=f.NetAssetAccountID "
                "JOIN tblAccountingTransactionLine l ON l.FundID=f.ID JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
                "JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "WHERE f.OrganizationID=? AND t.Status IN ('POSTED','REVERSED') AND t.TransactionDate BETWEEN ? AND ? "
                "AND a.AccountType IN ('REVENUE','EXPENSE','TRANSFER') "
                "GROUP BY f.ID,f.Code,f.Name,f.NetAssetAccountID,na.Code,na.Name ORDER BY f.Code",
                (organization_id, year[1], year[2]))
            rows = []
            for fund_id, code, name, net_asset_id, account_code, account_name, revenue, expense, transfer in cursor.fetchall():
                revenue, expense, transfer = Decimal(revenue), Decimal(expense), Decimal(transfer)
                change = revenue - expense + transfer
                if net_asset_id is None:
                    blockers.append("Fund {} has activity but no net-asset account.".format(code))
                rows.append((fund_id, code, name, revenue, expense, transfer, change,
                             "{} - {}".format(account_code, account_name) if net_asset_id else "Not configured"))
            return {"year": year, "rows": rows, "blockers": blockers, "ready": not blockers}
        finally:
            cursor.close()
