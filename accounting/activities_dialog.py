"""Read-only statement of activities."""
from datetime import date
from decimal import Decimal
import wx
import wx.adv
from .activities_service import ActivitiesService
from .formatting import money

def _date(control):
    value=control.GetValue();return date(value.GetYear(),value.GetMonth()+1,value.GetDay())
class ActivitiesDialog(wx.Dialog):
    def __init__(self,parent,service):
        super().__init__(parent,title="Statement of Activities",size=(900,650));self.service=service
        self.organization=wx.Choice(self)
        for key,name in service.organizations():self.organization.Append(name,key)
        if self.organization.GetCount():self.organization.SetSelection(0)
        self.start=wx.adv.DatePickerCtrl(self);self.end=wx.adv.DatePickerCtrl(self)
        run=wx.Button(self,label="Run Statement");run.Bind(wx.EVT_BUTTON,self.refresh)
        header=wx.BoxSizer(wx.HORIZONTAL)
        for label,control in (("Organization",self.organization),("From",self.start),("Through",self.end)):
            header.Add(wx.StaticText(self,label=label),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,5);header.Add(control,0,wx.RIGHT,12)
        header.Add(run)
        self.list=wx.ListCtrl(self,style=wx.LC_REPORT)
        for index,(label,width) in enumerate((("Section",105),("Code",70),("Account",250),("Without restrictions",145),("With restrictions",135),("Total",105))):self.list.InsertColumn(index,label,format=wx.LIST_FORMAT_RIGHT if index>=3 else wx.LIST_FORMAT_LEFT,width=width)
        self.status=wx.StaticText(self,label="")
        close=wx.Button(self,wx.ID_CLOSE,"Close");close.Bind(wx.EVT_BUTTON,lambda event:self.EndModal(wx.ID_CLOSE))
        footer=wx.BoxSizer(wx.HORIZONTAL);footer.Add(self.status,0,wx.ALIGN_CENTER_VERTICAL);footer.AddStretchSpacer();footer.Add(close)
        root=wx.BoxSizer(wx.VERTICAL);root.Add(header,0,wx.ALL|wx.EXPAND,10);root.Add(self.list,1,wx.LEFT|wx.RIGHT|wx.EXPAND,10);root.Add(footer,0,wx.ALL|wx.EXPAND,10)
        self.SetSizer(root)
    def _add(self,section,code,name,without,with_restrictions):
        row=self.list.InsertItem(self.list.GetItemCount(),section)
        for column,value in enumerate((code,name,money(without),money(with_restrictions),money(without+with_restrictions)),1):self.list.SetItem(row,column,str(value))
    def refresh(self,event=None):
        self.list.DeleteAllItems()
        if self.organization.GetSelection()==wx.NOT_FOUND:return
        try:rows=self.service.rows(self.organization.GetClientData(self.organization.GetSelection()),_date(self.start),_date(self.end))
        except ValueError as error:wx.MessageBox(str(error),"Statement not run",wx.OK|wx.ICON_WARNING);return
        revenue=[Decimal("0"),Decimal("0")];expense=[Decimal("0"),Decimal("0")];transfer=[Decimal("0"),Decimal("0")]
        labels={"REVENUE":"Revenue","EXPENSE":"Expenses","TRANSFER":"Transfers"}
        for code,name,kind,without,with_restrictions in rows:
            self._add(labels[kind],code,name,without,with_restrictions)
            target={"REVENUE":revenue,"EXPENSE":expense,"TRANSFER":transfer}[kind];target[0]+=without;target[1]+=with_restrictions
        change=[revenue[i]-expense[i]+transfer[i] for i in (0,1)]
        self._add("Change","","Change in net assets",*change)
        self.status.SetLabel("Change in net assets: {}".format(money(sum(change),True)))

def show_activities(parent,connection,session,authorization):
    authorization.require("accounting.reports.run","run accounting reports");dialog=ActivitiesDialog(parent,ActivitiesService(connection))
    try:dialog.ShowModal()
    finally:dialog.Destroy()
