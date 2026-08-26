"""Budget-to-Actual report with optional supporting detail."""
import wx
from .budget_actual_service import BudgetActualService
from .formatting import money

class BudgetActualDialog(wx.Dialog):
    def __init__(self,parent,service,report_service=None):
        super().__init__(parent,title="Budget to Actual",size=(1200,700));self.service=service;self.budget=wx.Choice(self);self.period=wx.Choice(self)
        for i,label,mode in service.budgets():self.budget.Append(str(label),i)
        if self.budget.GetCount():self.budget.SetSelection(0)
        self.budget.Bind(wx.EVT_CHOICE,self.load_periods);self.load_periods();run=wx.Button(self,label="Run Budget to Actual");run.Bind(wx.EVT_BUTTON,self.on_run)
        filters=wx.BoxSizer(wx.HORIZONTAL);filters.Add(wx.StaticText(self,label="Adopted budget"),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,4);filters.Add(self.budget,1,wx.RIGHT,12);filters.Add(wx.StaticText(self,label="Through period"),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,4);filters.Add(self.period,0,wx.RIGHT,12);filters.Add(run)
        self.summary=wx.ListCtrl(self,style=wx.LC_REPORT)
        cols=(("General account",175),("Fund",125),("Function",100),("Period budget",95),("Period actual",95),("Variance",90),("%",55),("YTD budget",95),("YTD actual",95),("Variance",90),("%",55))
        for i,(label,width) in enumerate(cols):self.summary.InsertColumn(i,label,width=width)
        for i in range(3,11):col=self.summary.GetColumn(i);col.SetAlign(wx.LIST_FORMAT_RIGHT);self.summary.SetColumn(i,col)
        self.detail=wx.ListCtrl(self,style=wx.LC_REPORT)
        for i,(label,width) in enumerate((("Period",80),("General account",180),("Fund",130),("Function",100),("Detailed line item",220),("Budget",95),("Note",180))):self.detail.InsertColumn(i,label,width=width)
        col=self.detail.GetColumn(5);col.SetAlign(wx.LIST_FORMAT_RIGHT);self.detail.SetColumn(5,col)
        self.report_service=report_service;preview=wx.Button(self,label="Preview PDF");preview.Bind(wx.EVT_BUTTON,self.preview_pdf);preview.Enable(report_service is not None)
        customize=wx.Button(self,label="Customize Layout");customize.Bind(wx.EVT_BUTTON,self.customize_layout);customize.Enable(report_service is not None and report_service.authorization.has_permission("accounting.reports.design"))
        close=wx.Button(self,wx.ID_CLOSE,"Close");close.Bind(wx.EVT_BUTTON,lambda e:self.EndModal(wx.ID_CLOSE));root=wx.BoxSizer(wx.VERTICAL);root.Add(filters,0,wx.ALL|wx.EXPAND,10);root.Add(self.summary,2,wx.LEFT|wx.RIGHT|wx.EXPAND,10);root.Add(wx.StaticText(self,label="Supporting detailed budget lines (actuals remain at the general-account level)"),0,wx.ALL,10);root.Add(self.detail,1,wx.LEFT|wx.RIGHT|wx.EXPAND,10);actions=wx.BoxSizer(wx.HORIZONTAL);actions.AddStretchSpacer();actions.Add(preview,0,wx.RIGHT,8);actions.Add(customize,0,wx.RIGHT,8);actions.Add(close);root.Add(actions,0,wx.ALL|wx.EXPAND,10);self.SetSizer(root)
    def load_periods(self,event=None):
        self.period.Clear();i=self.budget.GetSelection()
        if i!=wx.NOT_FOUND:
            for pid,label in self.service.periods(self.budget.GetClientData(i)):self.period.Append(str(label),pid)
            if self.period.GetCount():self.period.SetSelection(self.period.GetCount()-1)
    def on_run(self,event):
        bi=self.budget.GetSelection();pi=self.period.GetSelection()
        if bi==wx.NOT_FOUND or pi==wx.NOT_FOUND:wx.MessageBox("Select an adopted budget and period.","Budget to Actual");return
        result=self.service.report(self.budget.GetClientData(bi),self.period.GetClientData(pi));self.summary.DeleteAllItems();self.detail.DeleteAllItems()
        for r in result["rows"]:
            row=self.summary.InsertItem(self.summary.GetItemCount(),str(r[0]));vals=(*r[1:3],money(r[3]),money(r[4]),money(r[5]),"" if r[6] is None else str(r[6]),money(r[7]),money(r[8]),money(r[9]),"" if r[10] is None else str(r[10]))
            for c,v in enumerate(vals,1):self.summary.SetItem(row,c,str(v))
        for r in result["details"]:
            row=self.detail.InsertItem(self.detail.GetItemCount(),str(r[0]));vals=(*r[1:5],money(r[5]),r[6] or "")
            for c,v in enumerate(vals,1):self.detail.SetItem(row,c,str(v))
    def _selection(self):
        bi=self.budget.GetSelection();pi=self.period.GetSelection()
        if bi==wx.NOT_FOUND or pi==wx.NOT_FOUND:raise ValueError("Select an adopted budget and period.")
        return self.budget.GetClientData(bi),self.period.GetClientData(pi)
    def preview_pdf(self,event=None):
        try:self.report_service.run_budget_actual(*self._selection())
        except Exception as error:wx.MessageBox(str(error),"Budget to Actual Report",wx.OK|wx.ICON_ERROR,self)
    def customize_layout(self,event=None):
        try:self.report_service.design_budget_actual(*self._selection())
        except Exception as error:wx.MessageBox(str(error),"Budget to Actual Designer",wx.OK|wx.ICON_ERROR,self)

def show_budget_actual(parent,connection,session,authorization):
    authorization.require("accounting.reports.run","run budget-to-actual reports")
    from .reporting import AccountingVisualReportService
    d=BudgetActualDialog(parent,BudgetActualService(connection),AccountingVisualReportService(connection,authorization,session))
    try:d.ShowModal()
    finally:d.Destroy()
