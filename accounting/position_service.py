"""Statement of financial position derived from the posted ledger."""
from decimal import Decimal

class FinancialPositionService:
    def __init__(self, connection):
        self.connection = connection
        self.marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"
    def _execute(self, cursor, sql, values=()): return cursor.execute(sql.replace("?", self.marker), values)
    def organizations(self):
        cursor=self.connection.cursor()
        try:
            self._execute(cursor,"SELECT ID, LegalName FROM tblAccountingOrganization WHERE Active=1 ORDER BY LegalName")
            return cursor.fetchall()
        finally: cursor.close()
    def rows(self, organization_id, as_of_date):
        cursor=self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT a.Code, a.Name, a.AccountType, f.NetAssetClass, "
                "COALESCE(SUM(l.Debit),0), COALESCE(SUM(l.Credit),0) "
                "FROM tblAccountingTransaction t "
                "JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID "
                "JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "JOIN tblAccountingFund f ON f.ID=l.FundID "
                "WHERE t.OrganizationID=? AND t.Status IN ('POSTED','REVERSED') "
                "AND t.TransactionDate<=? "
                "GROUP BY a.ID, a.Code, a.Name, a.AccountType, f.NetAssetClass "
                "ORDER BY a.DisplayOrder, a.Code, f.NetAssetClass",
                (organization_id, as_of_date))
            assets=[]; liabilities=[]; net_accounts=[]
            activity={"WITHOUT_DONOR_RESTRICTIONS":Decimal("0"),
                      "WITH_DONOR_RESTRICTIONS":Decimal("0")}
            for code,name,kind,net_class,debit,credit in cursor.fetchall():
                debit,credit=Decimal(debit),Decimal(credit)
                if kind=="ASSET": assets.append((code,name,debit-credit))
                elif kind=="LIABILITY": liabilities.append((code,name,credit-debit))
                elif kind=="NET_ASSET": net_accounts.append((code,name,net_class,credit-debit))
                elif kind in ("REVENUE","EXPENSE","TRANSFER","OTHER"):
                    activity[net_class]+=credit-debit
            return assets, liabilities, net_accounts, activity
        finally: cursor.close()
