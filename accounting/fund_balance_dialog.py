"""Fund activity and balances report."""

from datetime import date
from decimal import Decimal

import wx
import wx.adv

from .formatting import money
from .fund_balance_service import FundBalanceService


def _date(control):
    value = control.GetValue()
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


class FundBalanceDialog(wx.Dialog):
    def __init__(self, parent, service):
        super().__init__(parent, title="Fund Activity and Balances", size=(1080, 620))
        self.service = service
        self.organization = wx.Choice(self)
        for item_id, label in service.organizations():
            self.organization.Append(str(label), item_id)
        if self.organization.GetCount(): self.organization.SetSelection(0)
        today = date.today()
        self.date_from = wx.adv.DatePickerCtrl(self, size=(125, -1))
        self.date_to = wx.adv.DatePickerCtrl(self, size=(125, -1))
        self.date_from.SetValue(wx.DateTime.FromDMY(1, 0, today.year))
        filters = wx.BoxSizer(wx.HORIZONTAL)
        for label, control in (("Organization", self.organization),
                               ("From", self.date_from), ("Through", self.date_to)):
            filters.Add(wx.StaticText(self, label=label), 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
            filters.Add(control, 0, wx.RIGHT, 12)
        run = wx.Button(self, label="Run Fund Balances")
        run.Bind(wx.EVT_BUTTON, self.on_run); filters.Add(run)
        self.status = wx.StaticText(self, label="Run the report to calculate fund balances.")
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        columns = (("Code", 65), ("Fund", 180), ("Restriction class", 150),
                   ("Beginning", 100), ("Revenue", 100), ("Expense", 100),
                   ("Transfers / releases", 125), ("Other", 90), ("Ending", 105))
        for index, (label, width) in enumerate(columns):
            self.list.InsertColumn(index, label, width=width)
        for index in range(3, 9):
            column = self.list.GetColumn(index); column.SetAlign(wx.LIST_FORMAT_RIGHT)
            self.list.SetColumn(index, column)
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(filters, 0, wx.ALL | wx.EXPAND, 10)
        root.Add(self.status, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        root.Add(self.list, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(close, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        self.SetSizer(root)

    def on_run(self, event):
        index = self.organization.GetSelection()
        if index == wx.NOT_FOUND:
            wx.MessageBox("Select an organization.", "Fund Balances"); return
        try:
            rows = self.service.report(self.organization.GetClientData(index),
                                       _date(self.date_from), _date(self.date_to))
        except ValueError as error:
            wx.MessageBox(str(error), "Fund Balances", wx.OK | wx.ICON_WARNING); return
        self.list.DeleteAllItems()
        totals = [Decimal("0") for _ in range(6)]
        labels = {"WITH_DONOR_RESTRICTIONS": "With donor restrictions",
                  "WITHOUT_DONOR_RESTRICTIONS": "Without donor restrictions"}
        for item in rows:
            row = self.list.InsertItem(self.list.GetItemCount(), str(item[0]))
            values = (item[1], labels.get(item[2], item[2]),
                      *(money(value) for value in item[3:9]))
            for column, value in enumerate(values, 1): self.list.SetItem(row, column, str(value))
            for offset, value in enumerate(item[3:9]): totals[offset] += value
        self.status.SetLabel(
            "{} fund(s)    Total beginning {}    Total ending {}".format(
                len(rows), money(totals[0], True), money(totals[5], True))
        )


def show_fund_balances(parent, connection, session, authorization):
    authorization.require("accounting.reports.run", "run fund activity and balances")
    dialog = FundBalanceDialog(parent, FundBalanceService(connection))
    try: dialog.ShowModal()
    finally: dialog.Destroy()
