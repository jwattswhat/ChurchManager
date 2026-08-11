"""Read-only accounting period close checklist."""

import wx

from .close_checklist_service import CloseChecklistService
from .period_close_service import PeriodCloseService


class CloseChecklistDialog(wx.Dialog):
    def __init__(self, parent, service, period_close=None):
        super().__init__(parent, title="Accounting Close Checklist", size=(900, 570))
        self.service = service
        self.period_close = period_close
        self.organization = wx.Choice(self); self.period = wx.Choice(self)
        for item_id, label in service.organizations(): self.organization.Append(str(label), item_id)
        if self.organization.GetCount(): self.organization.SetSelection(0)
        self.organization.Bind(wx.EVT_CHOICE, self.on_organization)
        run = wx.Button(self, label="Run Close Checklist"); run.Bind(wx.EVT_BUTTON, self.on_run)
        filters = wx.BoxSizer(wx.HORIZONTAL)
        for label, control in (("Organization",self.organization),("Fiscal period",self.period)):
            filters.Add(wx.StaticText(self,label=label),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,4)
            filters.Add(control,1,wx.RIGHT,12)
        filters.Add(run)
        self.status=wx.StaticText(self,label="Select a period and run the checklist.")
        self.list=wx.ListCtrl(self,style=wx.LC_REPORT)
        for index,(label,width) in enumerate((("Check",190),("Status",85),("Detail",570))):
            self.list.InsertColumn(index,label,width=width)
        close_period=wx.Button(self,label="Close Period")
        reopen_period=wx.Button(self,label="Reopen Period")
        close_period.Enable(period_close is not None);reopen_period.Enable(period_close is not None)
        close_period.Bind(wx.EVT_BUTTON,self.on_close_period)
        reopen_period.Bind(wx.EVT_BUTTON,self.on_reopen_period)
        close=wx.Button(self,wx.ID_CLOSE,"Close")
        close.Bind(wx.EVT_BUTTON,lambda event:self.EndModal(wx.ID_CLOSE))
        buttons=wx.BoxSizer(wx.HORIZONTAL);buttons.Add(close_period,0,wx.RIGHT,8)
        buttons.Add(reopen_period);buttons.AddStretchSpacer();buttons.Add(close)
        root=wx.BoxSizer(wx.VERTICAL);root.Add(filters,0,wx.ALL|wx.EXPAND,10)
        root.Add(self.status,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        root.Add(self.list,1,wx.LEFT|wx.RIGHT|wx.EXPAND,10)
        root.Add(buttons,0,wx.ALL|wx.EXPAND,10);self.SetSizer(root);self.on_organization()

    def on_organization(self,event=None):
        self.period.Clear(); index=self.organization.GetSelection()
        if index==wx.NOT_FOUND:return
        for item_id,label in self.service.periods(self.organization.GetClientData(index)):
            self.period.Append(str(label),item_id)
        if self.period.GetCount():self.period.SetSelection(0)

    def on_run(self,event):
        oi=self.organization.GetSelection();pi=self.period.GetSelection()
        if oi==wx.NOT_FOUND or pi==wx.NOT_FOUND:
            wx.MessageBox("Select an organization and fiscal period.","Close Checklist");return
        try:result=self.service.run(self.organization.GetClientData(oi),self.period.GetClientData(pi))
        except ValueError as error:
            wx.MessageBox(str(error),"Close Checklist",wx.OK|wx.ICON_WARNING);return
        self.list.DeleteAllItems()
        for item in result["checks"]:
            row=self.list.InsertItem(self.list.GetItemCount(),item["check"])
            self.list.SetItem(row,1,item["status"]);self.list.SetItem(row,2,item["detail"])
        summary = ("PERIOD CLOSED" if result["status"] == "CLOSED" else
                   "READY TO CLOSE" if result["ready"] else "NOT READY TO CLOSE")
        self.status.SetLabel("{}: {}".format(result["period"],summary))

    def _selection(self):
        oi=self.organization.GetSelection();pi=self.period.GetSelection()
        if oi==wx.NOT_FOUND or pi==wx.NOT_FOUND:
            wx.MessageBox("Select an organization and fiscal period.","Close Checklist")
            return None
        return self.organization.GetClientData(oi),self.period.GetClientData(pi)

    def on_close_period(self,event):
        selected=self._selection()
        if selected is None:return
        if wx.MessageBox(
            "Close this fiscal period? New postings in the period will be blocked.",
            "Confirm Period Close",wx.YES_NO|wx.NO_DEFAULT|wx.ICON_WARNING)!=wx.YES:return
        try:self.period_close.close(*selected)
        except ValueError as error:
            wx.MessageBox(str(error),"Period not closed",wx.OK|wx.ICON_WARNING);return
        wx.MessageBox("The fiscal period was closed and the action was audited.","Period Closed")
        self.on_run(None)

    def on_reopen_period(self,event):
        selected=self._selection()
        if selected is None:return
        dialog=wx.TextEntryDialog(self,"Explain why this closed period must be reopened.",
                                  "Reopen Fiscal Period")
        try:
            if dialog.ShowModal()!=wx.ID_OK:return
            reason=dialog.GetValue()
        finally:dialog.Destroy()
        try:self.period_close.reopen(*selected,reason)
        except ValueError as error:
            wx.MessageBox(str(error),"Period not reopened",wx.OK|wx.ICON_WARNING);return
        wx.MessageBox("The fiscal period was reopened and the action was audited.","Period Reopened")
        self.on_run(None)


def show_close_checklist(parent,connection,session,authorization):
    authorization.require("accounting.reports.run","run the accounting close checklist")
    period_close = None
    if authorization.has_permission("accounting.periods.override"):
        period_close = PeriodCloseService(connection, session.user_id)
    dialog=CloseChecklistDialog(parent,CloseChecklistService(connection),period_close)
    try:dialog.ShowModal()
    finally:dialog.Destroy()
