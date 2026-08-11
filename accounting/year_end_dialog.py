"""Read-only preview of the controlled fiscal-year close."""
import wx

from .formatting import money
from .year_end_service import YearEndService


class YearEndDialog(wx.Dialog):
    def __init__(self, parent, service):
        super().__init__(parent, title="Year-End Close Preview", size=(1050, 650))
        self.service = service
        self.organization = wx.Choice(self)
        self.year = wx.Choice(self)
        for key, name in service.organizations():
            self.organization.Append(name, key)
        if self.organization.GetCount():
            self.organization.SetSelection(0)
        self.organization.Bind(wx.EVT_CHOICE, self.load_years)
        self.load_years()
        preview = wx.Button(self, label="Preview Close")
        preview.Bind(wx.EVT_BUTTON, self.refresh)
        header = wx.BoxSizer(wx.HORIZONTAL)
        for label, control in (("Organization", self.organization), ("Fiscal year", self.year)):
            header.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            header.Add(control, 0, wx.RIGHT, 12)
        header.Add(preview)
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        for index, (label, width) in enumerate((("Fund", 185), ("Revenue", 115), ("Expenses", 115), ("Transfers", 115), ("Change", 115), ("Net-asset account", 250))):
            self.list.InsertColumn(index, label, format=wx.LIST_FORMAT_RIGHT if 1 <= index <= 4 else wx.LIST_FORMAT_LEFT, width=width)
        self.status = wx.StaticText(self, label="Select a fiscal year and preview the close.")
        self.blockers = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 110))
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        footer = wx.BoxSizer(wx.HORIZONTAL)
        footer.Add(self.status, 0, wx.ALIGN_CENTER_VERTICAL)
        footer.AddStretchSpacer()
        footer.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(header, 0, wx.ALL | wx.EXPAND, 10)
        root.Add(self.list, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(wx.StaticText(self, label="Close readiness"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        root.Add(self.blockers, 0, wx.ALL | wx.EXPAND, 10)
        root.Add(footer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(root)

    def load_years(self, event=None):
        self.year.Clear()
        index = self.organization.GetSelection()
        if index != wx.NOT_FOUND:
            for key, name in self.service.years(self.organization.GetClientData(index)):
                self.year.Append(name, key)
            if self.year.GetCount():
                self.year.SetSelection(0)

    def refresh(self, event=None):
        if self.organization.GetSelection() == wx.NOT_FOUND or self.year.GetSelection() == wx.NOT_FOUND:
            return
        report = self.service.preview(self.organization.GetClientData(self.organization.GetSelection()), self.year.GetClientData(self.year.GetSelection()))
        self.list.DeleteAllItems()
        for _, code, name, revenue, expense, transfer, change, net_asset in report["rows"]:
            row = self.list.InsertItem(self.list.GetItemCount(), "{} - {}".format(code, name))
            for column, value in enumerate((money(revenue), money(expense), money(transfer), money(change), net_asset), 1):
                self.list.SetItem(row, column, str(value))
        if report["ready"]:
            self.status.SetLabel("Ready for year-end close")
            self.blockers.SetValue("All periods are closed, all transactions are posted, the ledger balances, and affected funds have net-asset accounts.")
        else:
            self.status.SetLabel("Not ready for year-end close")
            self.blockers.SetValue("\r\n".join("- " + item for item in report["blockers"]))


def show_year_end(parent, connection, session, authorization):
    authorization.require("accounting.periods.override", "preview and manage year-end close")
    dialog = YearEndDialog(parent, YearEndService(connection))
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
