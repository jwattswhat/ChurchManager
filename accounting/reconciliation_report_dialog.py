"""Completed bank-reconciliation proof report."""

import wx

from .formatting import money
from .reconciliation_report_service import ReconciliationReportService


class ReconciliationReportDialog(wx.Dialog):
    def __init__(self, parent, service, report_service=None):
        super().__init__(parent, title="Bank Reconciliation Report", size=(1050, 680))
        self.service, self.report_service, self.rows = service, report_service, []
        self.reconciliations = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Bank account", 180), ("Statement date", 100), ("Beginning", 100),
            ("Cleared activity", 110), ("Ending", 100), ("Difference", 100),
            ("Prepared by", 140), ("Completed", 145),
        )): self.reconciliations.InsertColumn(index, label, width=width)
        for index in range(2, 6):
            column = self.reconciliations.GetColumn(index)
            column.SetAlign(wx.LIST_FORMAT_RIGHT); self.reconciliations.SetColumn(index, column)
        self.reconciliations.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)
        self.reconciliations.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_select)
        self.proof = wx.StaticText(self, label="Select a completed reconciliation.")
        self.items = wx.ListCtrl(self, style=wx.LC_REPORT)
        for index, (label, width) in enumerate((
            ("Status", 90), ("Transaction date", 105), ("Number", 70),
            ("Description", 260), ("Reference", 140), ("Amount", 110),
            ("Cleared date", 105),
        )): self.items.InsertColumn(index, label, width=width)
        amount_column = self.items.GetColumn(5); amount_column.SetAlign(wx.LIST_FORMAT_RIGHT)
        self.items.SetColumn(5, amount_column)
        refresh = wx.Button(self, label="Refresh")
        refresh.Bind(wx.EVT_BUTTON, self.refresh)
        preview=wx.Button(self,label="Preview PDF");preview.Bind(wx.EVT_BUTTON,self.on_preview);preview.Enable(report_service is not None)
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.Add(refresh)
        buttons.AddStretchSpacer();buttons.Add(preview,0,wx.RIGHT,8); buttons.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(wx.StaticText(self, label="Completed reconciliations"), 0, wx.ALL, 10)
        root.Add(self.reconciliations, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(self.proof, 0, wx.ALL, 10)
        root.Add(self.items, 2, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(buttons, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(root); self.refresh()

    def refresh(self, event=None):
        self.rows = self.service.completed()
        self.reconciliations.DeleteAllItems(); self.items.DeleteAllItems()
        for item in self.rows:
            difference = item[4] - (item[3] + item[5])
            row = self.reconciliations.InsertItem(self.reconciliations.GetItemCount(), str(item[1]))
            values = (item[2], money(item[3]), money(item[5]), money(item[4]),
                      money(difference), item[6], item[7])
            for column, value in enumerate(values, 1): self.reconciliations.SetItem(row, column, str(value))
        self.proof.SetLabel("{} completed reconciliation(s).".format(len(self.rows)))

    def on_select(self, event):
        result = self.service.detail(self.rows[event.GetIndex()][0])
        self.proof.SetLabel(
            "Beginning {} + cleared activity {} = statement ending {}    "
            "Difference {}    Outstanding {}".format(
                money(result["beginning"], True), money(result["cleared_total"], True),
                money(result["ending"], True), money(result["difference"], True),
                money(result["outstanding_total"], True)))
        self.items.DeleteAllItems()
        for item in result["items"]:
            row = self.items.InsertItem(self.items.GetItemCount(), str(item[0]))
            values = (item[1], item[2] or "", item[3] or "", item[4] or "",
                      money(item[5]), item[6] or "")
            for column, value in enumerate(values, 1): self.items.SetItem(row, column, str(value))

    def on_preview(self,event=None):
        index=self.reconciliations.GetFirstSelected()
        if index<0:wx.MessageBox("Select a completed reconciliation.","Reconciliation Report");return
        try:self.report_service.run_reconciliation(self.rows[index][0])
        except Exception as error:wx.MessageBox(str(error),"Reconciliation Report",wx.OK|wx.ICON_ERROR,self)


def show_reconciliation_report(parent, connection, session, authorization):
    authorization.require("accounting.reports.run", "run bank reconciliation reports")
    from .reporting import AccountingVisualReportService
    dialog = ReconciliationReportDialog(parent, ReconciliationReportService(connection),
                                        AccountingVisualReportService(connection,authorization,session))
    try: dialog.ShowModal()
    finally: dialog.Destroy()
