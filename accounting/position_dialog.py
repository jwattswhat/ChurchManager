"""Read-only statement of financial position."""
from datetime import date
from decimal import Decimal
import wx
import wx.adv
from ui_dimensions import DATE_PICKER_SIZE
from .position_service import FinancialPositionService
from .formatting import money

class FinancialPositionDialog(wx.Dialog):
    def __init__(self,parent,service,report_service=None):
        super().__init__(parent,title="Statement of Financial Position",size=(760,620))
        self.service=service; self.organization=wx.Choice(self)
        for key,name in service.organizations(): self.organization.Append(name,key)
        if self.organization.GetCount(): self.organization.SetSelection(0)
        self.as_of=wx.adv.DatePickerCtrl(self,size=DATE_PICKER_SIZE); run=wx.Button(self,label="Run Statement")
        run.Bind(wx.EVT_BUTTON,self.refresh)
        header=wx.BoxSizer(wx.HORIZONTAL)
        for label,control in (("Organization",self.organization),("As of",self.as_of)):
            header.Add(wx.StaticText(self,label=label),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,5); header.Add(control,0,wx.RIGHT,15)
        header.Add(run)
        self.list=wx.ListCtrl(self,style=wx.LC_REPORT)
        for index,(label,width) in enumerate((("Section",190),("Code",80),("Account",300),("Amount",120))): self.list.InsertColumn(index,label,format=wx.LIST_FORMAT_RIGHT if index==3 else wx.LIST_FORMAT_LEFT,width=width)
        self.status=wx.StaticText(self,label=""); self.report_service=report_service
        preview=wx.Button(self,label="Preview PDF");preview.Bind(wx.EVT_BUTTON,self.preview_pdf);preview.Enable(report_service is not None)
        customize=wx.Button(self,label="Customize Layout");customize.Bind(wx.EVT_BUTTON,self.customize_layout)
        customize.Enable(report_service is not None and report_service.authorization.has_permission("accounting.reports.design"))
        close=wx.Button(self,wx.ID_CLOSE,"Close"); close.Bind(wx.EVT_BUTTON,lambda event:self.EndModal(wx.ID_CLOSE))
        footer=wx.BoxSizer(wx.HORIZONTAL); footer.Add(self.status,0,wx.ALIGN_CENTER_VERTICAL); footer.AddStretchSpacer();footer.Add(preview,0,wx.RIGHT,8);footer.Add(customize,0,wx.RIGHT,8); footer.Add(close)
        root=wx.BoxSizer(wx.VERTICAL); root.Add(header,0,wx.ALL|wx.EXPAND,10); root.Add(self.list,1,wx.LEFT|wx.RIGHT|wx.EXPAND,10); root.Add(footer,0,wx.ALL|wx.EXPAND,10)
        self.SetSizer(root); self.refresh()
    def _add(self,section,code,name,amount):
        row=self.list.InsertItem(self.list.GetItemCount(),section); self.list.SetItem(row,1,code); self.list.SetItem(row,2,name); self.list.SetItem(row,3,money(amount))
    def refresh(self,event=None):
        self.list.DeleteAllItems()
        if self.organization.GetSelection()==wx.NOT_FOUND:return
        value=self.as_of.GetValue(); as_of=date(value.GetYear(),value.GetMonth()+1,value.GetDay())
        assets,liabilities,net_accounts,activity=self.service.rows(self.organization.GetClientData(self.organization.GetSelection()),as_of)
        total_assets=sum((r[2] for r in assets),Decimal("0")); total_liabilities=sum((r[2] for r in liabilities),Decimal("0"))
        without=activity["WITHOUT_DONOR_RESTRICTIONS"]; with_restrictions=activity["WITH_DONOR_RESTRICTIONS"]
        for code,name,amount in assets:self._add("Assets",code,name,amount)
        for code,name,amount in liabilities:self._add("Liabilities",code,name,amount)
        for code,name,net_class,amount in net_accounts:
            self._add("Net assets - "+("with restrictions" if net_class=="WITH_DONOR_RESTRICTIONS" else "without restrictions"),code,name,amount)
            if net_class=="WITH_DONOR_RESTRICTIONS":with_restrictions+=amount
            else:without+=amount
        self._add("Current activity","","Without donor restrictions",activity["WITHOUT_DONOR_RESTRICTIONS"])
        self._add("Current activity","","With donor restrictions",activity["WITH_DONOR_RESTRICTIONS"])
        total_net=without+with_restrictions; difference=total_assets-total_liabilities-total_net
        self.status.SetLabel("Assets {}    Liabilities + net assets {}    Difference {}".format(money(total_assets,True),money(total_liabilities+total_net,True),money(difference,True)))
    def _selection(self):
        value=self.as_of.GetValue()
        return self.organization.GetClientData(self.organization.GetSelection()),date(value.GetYear(),value.GetMonth()+1,value.GetDay())
    def preview_pdf(self,event=None):
        try:self.report_service.run_financial_position(*self._selection())
        except Exception as error:wx.MessageBox(str(error),"Financial Position Report",wx.OK|wx.ICON_ERROR,self)
    def customize_layout(self,event=None):
        try:self.report_service.design_financial_position(*self._selection())
        except Exception as error:wx.MessageBox(str(error),"Financial Position Report Designer",wx.OK|wx.ICON_ERROR,self)

def show_financial_position(parent,connection,session,authorization):
    authorization.require("accounting.reports.run","run accounting reports")
    from .reporting import AccountingVisualReportService
    dialog=FinancialPositionDialog(parent,FinancialPositionService(connection),AccountingVisualReportService(connection,authorization,session))
    try:dialog.ShowModal()
    finally:dialog.Destroy()
