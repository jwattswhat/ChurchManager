"""Approved giving-purpose maintenance and accounting mapping."""

from datetime import date

import wx
import wx.adv

from bulletin_orders import portable_connection
from giving.validation import GivingValidationError


def _date_value(control):
    value = control.GetValue()
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


class PurposeRepository:
    """Persist congregation-approved purposes without donor information."""

    def __init__(self, connection, authorization):
        self.connection = portable_connection(connection)
        self.authorization = authorization

    def all(self, sql, values=()):
        self.authorization.require(
            "giving.purposes.manage", "access approved Giving purposes"
        )
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def church_id(self):
        rows = self.all("SELECT ID FROM tblChurch ORDER BY ID LIMIT 1")
        if not rows:
            raise GivingValidationError("Church information must be created first.")
        return rows[0][0]

    def organizations(self):
        return self.all(
            "SELECT ID,LegalName FROM tblAccountingOrganization "
            "WHERE ChurchID=? AND Active=1 ORDER BY LegalName", (self.church_id(),)
        )

    def destinations(self, organization_id):
        funds = self.all(
            "SELECT f.ID,CONCAT(f.Code,' - ',f.Name) FROM tblAccountingFund f "
            "JOIN tblAccountingOrganization o ON o.ID=f.OrganizationID "
            "WHERE f.OrganizationID=? AND o.ChurchID=? AND f.Active=1 ORDER BY f.Code",
            (organization_id, self.church_id()),
        )
        accounts = self.all(
            "SELECT a.ID,CONCAT(a.Code,' - ',a.Name),a.FunctionRequirement FROM tblAccountingAccount a "
            "JOIN tblAccountingOrganization o ON o.ID=a.OrganizationID "
            "WHERE a.OrganizationID=? AND o.ChurchID=? AND a.Active=1 AND a.PostingAllowed=1 "
            "AND a.AccountType='REVENUE' ORDER BY a.Code", (organization_id, self.church_id()),
        )
        functions = self.all(
            "SELECT fn.ID,CONCAT(fn.Code,' - ',fn.Name) FROM tblAccountingFunction fn "
            "JOIN tblAccountingOrganization o ON o.ID=fn.OrganizationID "
            "WHERE fn.OrganizationID=? AND o.ChurchID=? AND fn.Active=1 ORDER BY fn.Code",
            (organization_id, self.church_id()),
        )
        return funds, accounts, functions

    def purposes(self):
        return self.all(
            "SELECT p.ID,p.Name,p.ApprovalDate,p.ApprovingAuthority,p.IsActive,"
            "p.StatementTreatment,o.LegalName FROM tblContributionPurpose p "
            "JOIN tblAccountingOrganization o ON o.ID=p.OrganizationID "
            "WHERE p.ChurchID=? ORDER BY p.IsActive DESC,p.Name,p.ID", (self.church_id(),),
        )

    def purpose(self, purpose_id):
        rows = self.all(
            "SELECT ID,Name,COALESCE(Description,''),ApprovalDate,ApprovingAuthority,"
            "EffectiveFrom,EffectiveThrough,IsActive,OrganizationID,FundID,RevenueAccountID,FunctionID,"
            "ControlAndDiscretionConfirmed,StatementTreatment,COALESCE(Note,'') "
            "FROM tblContributionPurpose WHERE ID=? AND ChurchID=?",
            (purpose_id, self.church_id()),
        )
        return rows[0] if rows else None

    def save(self, purpose_id, values):
        (name, description, approval_date, authority, effective_from, effective_through,
         active, organization_id, fund_id, account_id, function_id, confirmed, treatment, note) = values
        if not name:
            raise GivingValidationError("Purpose name is required.")
        if not authority:
            raise GivingValidationError("Approving authority is required.")
        if effective_through and effective_through < effective_from:
            raise GivingValidationError("The ending date cannot precede the starting date.")
        if not confirmed:
            raise GivingValidationError(
                "Confirm that the congregation retains control and discretion over this purpose."
            )
        if None in (organization_id, fund_id, account_id):
            raise GivingValidationError("Organization, fund, and revenue account are required.")
        account = next((row for row in self.destinations(organization_id)[1] if row[0] == account_id), None)
        if not account:
            raise GivingValidationError("Select an active revenue account for this organization.")
        if account[2] == "REQUIRED" and function_id is None:
            raise GivingValidationError("The selected revenue account requires a functional classification.")
        if account[2] == "PROHIBITED" and function_id is not None:
            raise GivingValidationError("The selected revenue account does not allow a functional classification.")
        if function_id is not None and not any(row[0] == function_id for row in self.destinations(organization_id)[2]):
            raise GivingValidationError("Select an active functional classification for this organization.")
        cursor = self.connection.cursor()
        try:
            if purpose_id is None:
                cursor.execute(
                    "INSERT INTO tblContributionPurpose "
                    "(ChurchID,Name,Description,ApprovalDate,ApprovingAuthority,EffectiveFrom,"
                    "EffectiveThrough,IsActive,OrganizationID,FundID,RevenueAccountID,FunctionID,"
                    "ControlAndDiscretionConfirmed,StatementTreatment,Note) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (self.church_id(),) + values,
                )
                purpose_id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE tblContributionPurpose SET Name=?,Description=?,ApprovalDate=?,"
                    "ApprovingAuthority=?,EffectiveFrom=?,EffectiveThrough=?,IsActive=?,"
                    "OrganizationID=?,FundID=?,RevenueAccountID=?,FunctionID=?,ControlAndDiscretionConfirmed=?,"
                    "StatementTreatment=?,Note=? WHERE ID=? AND ChurchID=?",
                    values + (purpose_id, self.church_id()),
                )
            self.connection.commit()
            return purpose_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()


class PurposeDialog(wx.Dialog):
    """Maintain approved purposes and their accounting destinations."""

    TREATMENTS = (("Eligible", "ELIGIBLE"), ("Needs review", "REVIEW"),
                  ("Not eligible", "INELIGIBLE"))

    def __init__(self, parent, connection, authorization):
        super().__init__(parent, title="Approved Giving Purposes", size=(1050, 680),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = PurposeRepository(connection, authorization); self.rows = []; self.current_id = None
        self.organizations = self.repository.organizations(); self.funds = []; self.accounts = []; self.functions = []
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        heading = wx.StaticText(panel, label="Approved Giving Purposes")
        heading.SetFont(heading.GetFont().Bold().Larger()); outer.Add(heading, 0, wx.ALL, 12)
        body = wx.BoxSizer(wx.HORIZONTAL); left = wx.BoxSizer(wx.VERTICAL)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Purpose",220),("Approved",95),("Authority",170),("Status",70))): self.list.InsertColumn(index,label,width=width)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select); left.Add(self.list,1,wx.EXPAND)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (("New",self.on_new),("Save",self.on_save)):
            button=wx.Button(panel,label=label); button.Bind(wx.EVT_BUTTON,handler); buttons.Add(button,0,wx.RIGHT,6)
        left.Add(buttons,0,wx.TOP,8); body.Add(left,0,wx.EXPAND|wx.RIGHT,14)
        form=wx.FlexGridSizer(0,2,7,10); form.AddGrowableCol(1,1)
        self.name=wx.TextCtrl(panel); self.description=wx.TextCtrl(panel,style=wx.TE_MULTILINE)
        self.approval=wx.adv.DatePickerCtrl(panel); self.authority=wx.TextCtrl(panel)
        self.effective=wx.adv.DatePickerCtrl(panel); self.has_end=wx.CheckBox(panel,label="Purpose has an ending date")
        self.through=wx.adv.DatePickerCtrl(panel); self.active=wx.CheckBox(panel,label="Active")
        self.organization=wx.Choice(panel,choices=[row[1] for row in self.organizations])
        self.fund=wx.Choice(panel); self.account=wx.Choice(panel); self.function=wx.Choice(panel)
        self.confirmed=wx.CheckBox(panel,label="Congregation retains control and discretion")
        self.treatment=wx.Choice(panel,choices=[row[0] for row in self.TREATMENTS]); self.treatment.SetSelection(0)
        self.note=wx.TextCtrl(panel,style=wx.TE_MULTILINE)
        for label,control in (("Purpose name",self.name),("Description",self.description),
            ("Approval date",self.approval),("Approving authority",self.authority),
            ("Effective from",self.effective),("",self.has_end),("Effective through",self.through),
            ("",self.active),("Accounting organization",self.organization),("Fund",self.fund),
            ("Revenue account",self.account),("Functional classification",self.function),
            ("",self.confirmed),("Statement treatment",self.treatment),
            ("Note",self.note)):
            form.Add(wx.StaticText(panel,label=label),0,wx.ALIGN_CENTER_VERTICAL); form.Add(control,1,wx.EXPAND)
        body.Add(form,1,wx.EXPAND); outer.Add(body,1,wx.EXPAND|wx.LEFT|wx.RIGHT,12)
        close=wx.Button(panel,wx.ID_CLOSE); close.Bind(wx.EVT_BUTTON,lambda _e:self.EndModal(wx.ID_CLOSE)); outer.Add(close,0,wx.ALIGN_RIGHT|wx.ALL,12); panel.SetSizer(outer)
        self.organization.Bind(wx.EVT_CHOICE,self.on_organization)
        self.account.Bind(wx.EVT_CHOICE,self.on_account)
        self.has_end.Bind(wx.EVT_CHECKBOX,lambda _e:self.through.Enable(self.has_end.GetValue()))
        self.on_new(); self.refresh()

    def on_organization(self,_event=None):
        selected=self.organization.GetSelection()
        self.funds,self.accounts,self.functions=self.repository.destinations(self.organizations[selected][0]) if selected>=0 else ([],[],[])
        self.fund.Set([row[1] for row in self.funds]); self.account.Set([row[1] for row in self.accounts])
        self.function.Set(["No functional classification"] + [row[1] for row in self.functions])
        self.fund.SetSelection(0 if self.funds else wx.NOT_FOUND); self.account.SetSelection(0 if self.accounts else wx.NOT_FOUND)
        self.function.SetSelection(0); self.on_account()

    def on_account(self,_event=None):
        selected=self.account.GetSelection(); requirement=self.accounts[selected][2] if selected>=0 else "OPTIONAL"
        self.function.Enable(requirement != "PROHIBITED")
        if requirement == "PROHIBITED": self.function.SetSelection(0)

    def on_new(self,_event=None):
        self.current_id=None
        for control in (self.name,self.description,self.authority,self.note): control.SetValue("")
        self.has_end.SetValue(False); self.through.Enable(False); self.active.SetValue(True); self.confirmed.SetValue(False); self.treatment.SetSelection(0)
        self.organization.SetSelection(0 if self.organizations else wx.NOT_FOUND); self.on_organization()

    def refresh(self):
        self.rows=self.repository.purposes(); self.list.DeleteAllItems()
        for index,row in enumerate(self.rows):
            self.list.InsertItem(index,row[1]); self.list.SetItem(index,1,str(row[2])); self.list.SetItem(index,2,row[3]); self.list.SetItem(index,3,"Active" if row[4] else "Inactive")

    def _choose_id(self, rows, choice):
        selected=choice.GetSelection(); return rows[selected][0] if selected>=0 else None

    def values(self):
        return (self.name.GetValue().strip(),self.description.GetValue().strip() or None,
            _date_value(self.approval),self.authority.GetValue().strip(),_date_value(self.effective),
            _date_value(self.through) if self.has_end.GetValue() else None,int(self.active.GetValue()),
            self._choose_id(self.organizations,self.organization),self._choose_id(self.funds,self.fund),
            self._choose_id(self.accounts,self.account),
            self.functions[self.function.GetSelection()-1][0] if self.function.GetSelection()>0 else None,
            int(self.confirmed.GetValue()),
            self.TREATMENTS[self.treatment.GetSelection()][1],self.note.GetValue().strip() or None)

    def on_save(self,_event=None):
        try:
            self.current_id=self.repository.save(self.current_id,self.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error),"Unable to Save Purpose",wx.OK|wx.ICON_ERROR,self)

    def on_select(self,_event=None):
        selected=self.list.GetFirstSelected()
        if selected<0:return
        row=self.repository.purpose(self.rows[selected][0]); self.current_id=row[0]
        self.name.SetValue(row[1]); self.description.SetValue(row[2]); self.authority.SetValue(row[4])
        for control,value in ((self.approval,row[3]),(self.effective,row[5])): control.SetValue(wx.DateTime.FromDMY(value.day,value.month-1,value.year))
        self.has_end.SetValue(row[6] is not None); self.through.Enable(row[6] is not None)
        if row[6]:self.through.SetValue(wx.DateTime.FromDMY(row[6].day,row[6].month-1,row[6].year))
        self.active.SetValue(bool(row[7])); self.confirmed.SetValue(bool(row[12])); self.note.SetValue(row[14])
        for index,item in enumerate(self.organizations):
            if item[0]==row[8]:self.organization.SetSelection(index);break
        self.on_organization()
        for rows,choice,wanted in ((self.funds,self.fund,row[9]),(self.accounts,self.account,row[10])):
            for index,item in enumerate(rows):
                if item[0]==wanted:choice.SetSelection(index);break
        self.on_account(); self.function.SetSelection(0)
        for index,item in enumerate(self.functions):
            if item[0]==row[11]: self.function.SetSelection(index+1); break
        self.treatment.SetSelection([item[1] for item in self.TREATMENTS].index(row[13]))


def show_giving_purposes(parent, connection, authorization):
    """Open approved-purpose maintenance."""
    authorization.require("giving.purposes.manage", "maintain approved Giving purposes")
    dialog=PurposeDialog(parent,connection,authorization)
    try:dialog.ShowModal()
    finally:dialog.Destroy()
