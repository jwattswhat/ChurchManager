"""Read-only preview of the controlled fiscal-year close."""
import wx

from .formatting import money
from .year_end_service import YearEndService


class YearEndDialog(wx.Dialog):
    def __init__(self, parent, service, can_override=False):
        super().__init__(parent, title="Year-End Close Preview", size=(1050, 650))
        self.service = service
        self.can_override = can_override
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
        self.close_year = wx.Button(self, label="Close Fiscal Year")
        self.close_year.Enable(False)
        self.close_year.Bind(wx.EVT_BUTTON, self.on_close_year)
        self.reopen_year = wx.Button(self, label="Reopen Fiscal Year")
        self.reopen_year.Enable(False)
        self.reopen_year.Bind(wx.EVT_BUTTON, self.on_reopen_year)
        header = wx.BoxSizer(wx.HORIZONTAL)
        for label, control in (("Organization", self.organization), ("Fiscal year", self.year)):
            header.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            header.Add(control, 0, wx.RIGHT, 12)
        header.Add(preview, 0, wx.RIGHT, 8)
        header.Add(self.close_year)
        header.Add(self.reopen_year, 0, wx.LEFT, 8)
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
            self.close_year.Enable(self.can_override)
            self.reopen_year.Enable(False)
        else:
            self.status.SetLabel("Not ready for year-end close")
            self.blockers.SetValue("\r\n".join("- " + item for item in report["blockers"]))
            self.close_year.Enable(False)
            self.reopen_year.Enable(report["year"][3] == "CLOSED" and report["year"][4] is not None and self.can_override)

    def on_close_year(self, event):
        if self.organization.GetSelection() == wx.NOT_FOUND or self.year.GetSelection() == wx.NOT_FOUND:
            return
        reason_dialog = wx.TextEntryDialog(self, "Explain why this fiscal year is ready to close.", "Close Fiscal Year")
        try:
            if reason_dialog.ShowModal() != wx.ID_OK:
                return
            if wx.MessageBox("Post the year-end closing transaction and permanently close this fiscal year?", "Confirm Year-End Close", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING) != wx.YES:
                return
            number = self.service.close(self.organization.GetClientData(self.organization.GetSelection()), self.year.GetClientData(self.year.GetSelection()), reason_dialog.GetValue(), self.can_override)
            wx.MessageBox("Fiscal year closed with transaction {}.".format(number), "Year-End Close", wx.OK | wx.ICON_INFORMATION)
            self.load_years(); self.list.DeleteAllItems(); self.close_year.Enable(False)
        except ValueError as error:
            wx.MessageBox(str(error), "Fiscal year not closed", wx.OK | wx.ICON_WARNING)
        finally:
            reason_dialog.Destroy()

    def on_reopen_year(self, event):
        if self.organization.GetSelection() == wx.NOT_FOUND or self.year.GetSelection() == wx.NOT_FOUND:
            return
        reason_dialog = wx.TextEntryDialog(self, "Explain why this fiscal year must be reopened.", "Reopen Fiscal Year")
        try:
            if reason_dialog.ShowModal() != wx.ID_OK:
                return
            if wx.MessageBox("Reverse the closing transaction and reopen the final fiscal period for adjustments?", "Confirm Fiscal-Year Reopen", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING) != wx.YES:
                return
            number = self.service.reopen(self.organization.GetClientData(self.organization.GetSelection()), self.year.GetClientData(self.year.GetSelection()), reason_dialog.GetValue(), self.can_override)
            wx.MessageBox("Fiscal year reopened with reversal transaction {}.".format(number), "Fiscal Year Reopened", wx.OK | wx.ICON_INFORMATION)
            self.load_years(); self.list.DeleteAllItems(); self.close_year.Enable(False); self.reopen_year.Enable(False)
        except ValueError as error:
            wx.MessageBox(str(error), "Fiscal year not reopened", wx.OK | wx.ICON_WARNING)
        finally:
            reason_dialog.Destroy()


def show_year_end(parent, connection, session, authorization):
    authorization.require("accounting.periods.override", "preview and manage year-end close")
    dialog = YearEndDialog(parent, YearEndService(connection, session.user_id), authorization.has_permission("accounting.approval.override"))
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
