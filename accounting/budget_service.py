"""Draft budget creation and line maintenance."""

import json
from decimal import Decimal, InvalidOperation


class BudgetService:
    def __init__(self, connection, acting_user_id):
        self.connection=connection;self.acting_user_id=int(acting_user_id)
        self.marker="%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"
    def _execute(self,cursor,sql,values=()):return cursor.execute(sql.replace("?",self.marker),values)
    def organizations(self):
        c=self.connection.cursor()
        try:self._execute(c,"SELECT ID,LegalName FROM tblAccountingOrganization WHERE Active=1 ORDER BY LegalName");return c.fetchall()
        finally:c.close()
    def years(self,organization_id):
        c=self.connection.cursor()
        try:self._execute(c,"SELECT ID,Name FROM tblAccountingFiscalYear WHERE OrganizationID=? ORDER BY StartDate DESC",(organization_id,));return c.fetchall()
        finally:c.close()
    def budgets(self):
        c=self.connection.cursor()
        try:
            self._execute(c,"SELECT b.ID,o.LegalName,y.Name,b.Name,b.VersionNumber,b.DetailMode,b.Status "
                "FROM tblAccountingBudget b JOIN tblAccountingOrganization o ON o.ID=b.OrganizationID "
                "JOIN tblAccountingFiscalYear y ON y.ID=b.FiscalYearID ORDER BY y.StartDate DESC,b.Name,b.VersionNumber DESC")
            return c.fetchall()
        finally:c.close()
    def create(self,organization_id,year_id,name,detail_mode):
        name=(name or "").strip();detail_mode=str(detail_mode)
        if not name:raise ValueError("Enter a budget name.")
        if detail_mode not in {"ACCOUNT_ONLY","DETAILED"}:raise ValueError("Select a budget detail mode.")
        c=self.connection.cursor()
        try:
            self._execute(c,"SELECT ID FROM tblAccountingFiscalYear WHERE ID=? AND OrganizationID=?",(year_id,organization_id))
            if c.fetchone() is None:raise ValueError("Select a fiscal year for this organization.")
            self._execute(c,"INSERT INTO tblAccountingBudget (OrganizationID,FiscalYearID,Name,DetailMode,CreatedByUserID) VALUES (?,?,?,?,?)",(organization_id,year_id,name,detail_mode,self.acting_user_id))
            budget_id=c.lastrowid
            after=json.dumps({"name":name,"detail_mode":detail_mode,"status":"DRAFT"},separators=(",",":"))
            self._execute(c,"INSERT INTO tblAccountingAuditEvent (OrganizationID,EntityType,EntityID,Action,AfterJSON,UserID) VALUES (?,'BUDGET',?,'BUDGET_CREATED',?,?)",(organization_id,str(budget_id),after,self.acting_user_id))
            self.connection.commit();return budget_id
        except Exception:self.connection.rollback();raise
        finally:c.close()
    def context(self,budget_id):
        c=self.connection.cursor()
        try:
            self._execute(c,"SELECT OrganizationID,FiscalYearID,Name,DetailMode,Status FROM tblAccountingBudget WHERE ID=?",(budget_id,));header=c.fetchone()
            if header is None:raise ValueError("The budget is no longer available.")
            queries={
              "periods":("SELECT p.ID,p.Name FROM tblAccountingFiscalPeriod p WHERE p.FiscalYearID=? ORDER BY p.PeriodNumber",header[1]),
              "accounts":("SELECT ID,CONCAT(Code,' - ',Name) FROM tblAccountingAccount WHERE OrganizationID=? AND Active=1 AND PostingAllowed=1 AND AccountType IN ('REVENUE','EXPENSE','TRANSFER') ORDER BY Code",header[0]),
              "funds":("SELECT ID,CONCAT(Code,' - ',Name) FROM tblAccountingFund WHERE OrganizationID=? AND Active=1 ORDER BY Code",header[0]),
              "functions":("SELECT ID,CONCAT(Code,' - ',Name) FROM tblAccountingFunction WHERE OrganizationID=? AND Active=1 ORDER BY DisplayOrder,Code",header[0])}
            result={"header":header}
            for key,(sql,value) in queries.items():self._execute(c,sql,(value,));result[key]=c.fetchall()
            return result
        finally:c.close()
    def lines(self,budget_id):
        c=self.connection.cursor()
        try:
            self._execute(c,"SELECT l.ID,p.Name,CONCAT(a.Code,' - ',a.Name),CONCAT(f.Code,' - ',f.Name),COALESCE(fn.Name,''),l.LineItemName,l.Amount,l.Note,l.FiscalPeriodID,l.AccountID,l.FundID,l.FunctionID "
                "FROM tblAccountingBudgetLine l JOIN tblAccountingFiscalPeriod p ON p.ID=l.FiscalPeriodID JOIN tblAccountingAccount a ON a.ID=l.AccountID JOIN tblAccountingFund f ON f.ID=l.FundID LEFT JOIN tblAccountingFunction fn ON fn.ID=l.FunctionID WHERE l.BudgetID=? ORDER BY p.PeriodNumber,l.DisplayOrder,l.ID",(budget_id,));return c.fetchall()
        finally:c.close()
    def save_line(self,budget_id,values,line_id=None):
        try:amount=Decimal(str(values["amount"])).quantize(Decimal("0.01"))
        except (InvalidOperation,KeyError) as error:raise ValueError("Enter a valid budget amount.") from error
        if amount<0:raise ValueError("Budget amounts cannot be negative.")
        c=self.connection.cursor()
        try:
            self._execute(c,"SELECT OrganizationID,FiscalYearID,DetailMode,Status FROM tblAccountingBudget WHERE ID=? FOR UPDATE",(budget_id,));header=c.fetchone()
            if header is None or header[3]!="DRAFT":raise ValueError("Only a draft budget can be edited.")
            line_name=(values.get("line_item") or "").strip() or None
            if header[2]=="DETAILED" and not line_name:raise ValueError("Enter a detailed budget line item.")
            if header[2]=="ACCOUNT_ONLY":line_name=None
            params=(values["period_id"],values["account_id"],values["fund_id"],values.get("function_id"),line_name,amount,(values.get("note") or "").strip() or None)
            if line_id is None:self._execute(c,"INSERT INTO tblAccountingBudgetLine (BudgetID,FiscalPeriodID,AccountID,FundID,FunctionID,LineItemName,Amount,Note) VALUES (?,?,?,?,?,?,?,?)",(budget_id,*params))
            else:self._execute(c,"UPDATE tblAccountingBudgetLine SET FiscalPeriodID=?,AccountID=?,FundID=?,FunctionID=?,LineItemName=?,Amount=?,Note=? WHERE ID=? AND BudgetID=?",(*params,line_id,budget_id))
            self.connection.commit()
        except Exception:self.connection.rollback();raise
        finally:c.close()

    def propose(self,budget_id):
        c=self.connection.cursor()
        try:
            self._execute(c,"SELECT OrganizationID,Status FROM tblAccountingBudget WHERE ID=? FOR UPDATE",(budget_id,));row=c.fetchone()
            if row is None or row[1]!="DRAFT":raise ValueError("Only a draft budget can be proposed.")
            self._execute(c,"SELECT COUNT(*) FROM tblAccountingBudgetLine WHERE BudgetID=? AND Amount>0",(budget_id,))
            if c.fetchone()[0]<1:raise ValueError("Add at least one positive budget line before proposing the budget.")
            self._execute(c,"UPDATE tblAccountingBudget SET Status='PROPOSED',ProposedByUserID=?,ProposedAt=CURRENT_TIMESTAMP(6) WHERE ID=? AND Status='DRAFT'",(self.acting_user_id,budget_id))
            self._execute(c,"INSERT INTO tblAccountingAuditEvent (OrganizationID,EntityType,EntityID,Action,AfterJSON,UserID) VALUES (?,'BUDGET',?,'BUDGET_PROPOSED','{\"status\":\"PROPOSED\"}',?)",(row[0],str(budget_id),self.acting_user_id));self.connection.commit()
        except Exception:self.connection.rollback();raise
        finally:c.close()

    def adopt(self,budget_id,reason=None,can_override=False):
        c=self.connection.cursor();reason=(reason or "").strip()
        try:
            self._execute(c,"SELECT b.OrganizationID,b.FiscalYearID,b.Status,b.CreatedByUserID,o.ApprovalPolicy FROM tblAccountingBudget b JOIN tblAccountingOrganization o ON o.ID=b.OrganizationID WHERE b.ID=? FOR UPDATE",(budget_id,));row=c.fetchone()
            if row is None or row[2]!="PROPOSED":raise ValueError("Only a proposed budget can be adopted.")
            same=row[3]==self.acting_user_id
            if same:
                if row[4]!="INDEPENDENT_PREFERRED" or not can_override:raise ValueError("A different authorized user must adopt this budget under the current policy.")
                if not reason:raise ValueError("Enter a reason for the solo budget-adoption override.")
            self._execute(c,"UPDATE tblAccountingBudget SET Status='SUPERSEDED' WHERE FiscalYearID=? AND Status='ADOPTED' AND ID<>?",(row[1],budget_id))
            self._execute(c,"UPDATE tblAccountingBudget SET Status='ADOPTED',AdoptedByUserID=?,AdoptedAt=CURRENT_TIMESTAMP(6) WHERE ID=? AND Status='PROPOSED'",(self.acting_user_id,budget_id))
            action="BUDGET_ADOPTED_OVERRIDE" if same else "BUDGET_ADOPTED"
            self._execute(c,"INSERT INTO tblAccountingAuditEvent (OrganizationID,EntityType,EntityID,Action,AfterJSON,Reason,UserID) VALUES (?,'BUDGET',?,?,'{\"status\":\"ADOPTED\"}',?,?)",(row[0],str(budget_id),action,reason or None,self.acting_user_id));self.connection.commit()
        except Exception:self.connection.rollback();raise
        finally:c.close()
