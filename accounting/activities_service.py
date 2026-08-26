"""Statement of activities from posted revenue, expense, and transfer lines."""
from decimal import Decimal

class ActivitiesService:
    def __init__(self,connection):
        self.connection=connection; self.marker="%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"
    def _execute(self,cursor,sql,values=()):return cursor.execute(sql.replace("?",self.marker),values)
    def organizations(self):
        cursor=self.connection.cursor()
        try:self._execute(cursor,"SELECT ID,LegalName FROM tblAccountingOrganization WHERE Active=1 ORDER BY LegalName");return cursor.fetchall()
        finally:cursor.close()
    def rows(self,organization_id,start_date,end_date):
        if start_date>end_date:raise ValueError("The statement start date cannot be after the end date.")
        cursor=self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT a.Code,a.Name,a.AccountType,f.NetAssetClass,COALESCE(SUM(l.Debit),0),COALESCE(SUM(l.Credit),0) "
                "FROM tblAccountingTransaction t JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID "
                "JOIN tblAccountingAccount a ON a.ID=l.AccountID JOIN tblAccountingFund f ON f.ID=l.FundID "
                "WHERE t.OrganizationID=? AND t.Status IN ('POSTED','REVERSED') AND t.TransactionDate BETWEEN ? AND ? "
                "AND a.AccountType IN ('REVENUE','EXPENSE','TRANSFER') "
                "GROUP BY a.ID,a.Code,a.Name,a.AccountType,f.NetAssetClass ORDER BY a.DisplayOrder,a.Code,f.NetAssetClass",
                (organization_id,start_date,end_date))
            combined={}
            for code,name,kind,net_class,debit,credit in cursor.fetchall():
                key=(code,name,kind); combined.setdefault(key,{"WITHOUT_DONOR_RESTRICTIONS":Decimal("0"),"WITH_DONOR_RESTRICTIONS":Decimal("0")})
                debit,credit=Decimal(debit),Decimal(credit)
                combined[key][net_class]+=(debit-credit if kind=="EXPENSE" else credit-debit)
            return [(code,name,kind,values["WITHOUT_DONOR_RESTRICTIONS"],values["WITH_DONOR_RESTRICTIONS"]) for (code,name,kind),values in combined.items()]
        finally:cursor.close()
