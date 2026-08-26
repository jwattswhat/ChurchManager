"""Adopted budget versus posted actual reporting."""
from collections import defaultdict
from decimal import Decimal

def variance(budget,actual):return Decimal(budget)-Decimal(actual)
def percent(actual,budget):
    budget=Decimal(budget)
    return None if budget==0 else (Decimal(actual)/budget*Decimal("100")).quantize(Decimal("0.1"))

class BudgetActualService:
    def __init__(self,connection):
        self.connection=connection;self.marker="%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"
    def _execute(self,c,s,v=()):return c.execute(s.replace("?",self.marker),v)
    def budgets(self):
        c=self.connection.cursor()
        try:self._execute(c,"SELECT b.ID,CONCAT(o.LegalName,' - ',y.Name,' - ',b.Name),b.DetailMode FROM tblAccountingBudget b JOIN tblAccountingOrganization o ON o.ID=b.OrganizationID JOIN tblAccountingFiscalYear y ON y.ID=b.FiscalYearID WHERE b.Status='ADOPTED' ORDER BY y.StartDate DESC,b.Name");return c.fetchall()
        finally:c.close()
    def periods(self,budget_id):
        c=self.connection.cursor()
        try:self._execute(c,"SELECT p.ID,p.Name FROM tblAccountingFiscalPeriod p JOIN tblAccountingBudget b ON b.FiscalYearID=p.FiscalYearID WHERE b.ID=? ORDER BY p.PeriodNumber",(budget_id,));return c.fetchall()
        finally:c.close()
    def report(self,budget_id,period_id):
        c=self.connection.cursor()
        try:
            self._execute(c,"SELECT b.OrganizationID,b.FiscalYearID,b.DetailMode,p.PeriodNumber,p.StartDate,p.EndDate,y.StartDate FROM tblAccountingBudget b JOIN tblAccountingFiscalPeriod p ON p.FiscalYearID=b.FiscalYearID JOIN tblAccountingFiscalYear y ON y.ID=b.FiscalYearID WHERE b.ID=? AND b.Status='ADOPTED' AND p.ID=?",(budget_id,period_id));h=c.fetchone()
            if h is None:raise ValueError("Select a period from an adopted budget.")
            self._execute(c,"SELECT l.AccountID,l.FundID,COALESCE(l.FunctionID,0),CONCAT(a.Code,' - ',a.Name),CONCAT(f.Code,' - ',f.Name),COALESCE(fn.Name,''),SUM(CASE WHEN l.FiscalPeriodID=? THEN l.Amount ELSE 0 END),SUM(CASE WHEN p.PeriodNumber<=? THEN l.Amount ELSE 0 END) FROM tblAccountingBudgetLine l JOIN tblAccountingAccount a ON a.ID=l.AccountID JOIN tblAccountingFund f ON f.ID=l.FundID LEFT JOIN tblAccountingFunction fn ON fn.ID=l.FunctionID JOIN tblAccountingFiscalPeriod p ON p.ID=l.FiscalPeriodID WHERE l.BudgetID=? GROUP BY l.AccountID,l.FundID,COALESCE(l.FunctionID,0),a.Code,a.Name,f.Code,f.Name,fn.Name ORDER BY a.Code,f.Code,fn.Name",(period_id,h[3],budget_id));budget_rows=c.fetchall()
            self._execute(c,"SELECT l.AccountID,l.FundID,COALESCE(l.FunctionID,0),SUM(CASE WHEN t.TransactionDate BETWEEN ? AND ? THEN CASE WHEN a.NormalBalance='CREDIT' THEN l.Credit-l.Debit ELSE l.Debit-l.Credit END ELSE 0 END),SUM(CASE WHEN t.TransactionDate BETWEEN ? AND ? THEN CASE WHEN a.NormalBalance='CREDIT' THEN l.Credit-l.Debit ELSE l.Debit-l.Credit END ELSE 0 END) FROM tblAccountingTransactionLine l JOIN tblAccountingTransaction t ON t.ID=l.TransactionID JOIN tblAccountingAccount a ON a.ID=l.AccountID WHERE t.OrganizationID=? AND t.Status IN ('POSTED','REVERSED') AND a.AccountType IN ('REVENUE','EXPENSE','TRANSFER') AND t.TransactionDate BETWEEN ? AND ? GROUP BY l.AccountID,l.FundID,COALESCE(l.FunctionID,0)",(h[4],h[5],h[6],h[5],h[0],h[6],h[5]));actual={(r[0],r[1],r[2]):(Decimal(r[3]),Decimal(r[4])) for r in c.fetchall()}
            rows=[]
            for r in budget_rows:
                ac,ay=actual.get((r[0],r[1],r[2]),(Decimal("0"),Decimal("0")));bc,by=Decimal(r[6]),Decimal(r[7])
                rows.append((*r[3:6],bc,ac,variance(bc,ac),percent(ac,bc),by,ay,variance(by,ay),percent(ay,by)))
            details=[]
            if h[2]=="DETAILED":
                self._execute(c,"SELECT p.Name,CONCAT(a.Code,' - ',a.Name),CONCAT(f.Code,' - ',f.Name),COALESCE(fn.Name,''),l.LineItemName,l.Amount,l.Note FROM tblAccountingBudgetLine l JOIN tblAccountingFiscalPeriod p ON p.ID=l.FiscalPeriodID JOIN tblAccountingAccount a ON a.ID=l.AccountID JOIN tblAccountingFund f ON f.ID=l.FundID LEFT JOIN tblAccountingFunction fn ON fn.ID=l.FunctionID WHERE l.BudgetID=? AND p.PeriodNumber<=? ORDER BY a.Code,f.Code,l.DisplayOrder,l.ID",(budget_id,h[3]));details=c.fetchall()
            return {"mode":h[2],"rows":rows,"details":details}
        finally:c.close()
