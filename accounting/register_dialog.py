"""Read-only posted accounting transaction register."""

import wx
import wx.adv
from datetime import date

from .register_service import AccountingRegisterService


class ReversalDialog(wx.Dialog):
    def __init__(self, parent, transaction_number):
        super().__init__(parent, title="Create Reversal")
        self.reversal_date = wx.adv.DatePickerCtrl(self)
        self.reason = wx.TextCtrl(self, size=(420, 80), style=wx.TE_MULTILINE)
        grid = wx.FlexGridSizer(cols=2, hgap=8, vgap=8); grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Transaction")); grid.Add(wx.StaticText(self, label=str(transaction_number)))
        grid.Add(wx.StaticText(self, label="Reversal date")); grid.Add(self.reversal_date, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Reason")); grid.Add(self.reason, 1, wx.EXPAND)
        root = wx.BoxSizer(wx.VERTICAL); root.Add(grid, 1, wx.ALL | wx.EXPAND, 12)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizerAndFit(root)
    def values(self):
        value = self.reversal_date.GetValue()
        return date(value.GetYear(), value.GetMonth() + 1, value.GetDay()), self.reason.GetValue()


class AccountingRegisterDialog(wx.Dialog):
    def __init__(self, parent, service, reversal_service=None):
        super().__init__(parent, title="Posted Transaction Register", size=(1000, 650))
        self.service, self.reversal_service, self.rows = service, reversal_service, []
        self.transactions = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Number",70), ("Organization",150), ("Date",90), ("Type",115),
            ("Status",75), ("Description",230), ("Reference",120), ("Total",85),
        )): self.transactions.InsertColumn(index, label, width=width)
        self.lines = wx.ListCtrl(self, style=wx.LC_REPORT)
        for index, (label, width) in enumerate((
            ("#",35), ("Account",200), ("Fund",140), ("Function",115),
            ("Payee",100), ("Description",160), ("Debit",80), ("Credit",80),
        )): self.lines.InsertColumn(index, label, width=width)
        self.transactions.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)
        refresh = wx.Button(self, label="Refresh")
        reverse = wx.Button(self, label="Create Reversal")
        reverse.Enable(reversal_service is not None)
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        refresh.Bind(wx.EVT_BUTTON, self.refresh)
        reverse.Bind(wx.EVT_BUTTON, self.on_reverse)
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.Add(refresh); buttons.AddStretchSpacer(); buttons.Add(reverse, 0, wx.RIGHT, 6); buttons.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(wx.StaticText(self, label="Posted transactions"), 0, wx.ALL, 10)
        root.Add(self.transactions, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(wx.StaticText(self, label="Transaction lines (read only)"), 0, wx.ALL, 10)
        root.Add(self.lines, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(buttons, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(root); self.refresh()

    def refresh(self, event=None):
        self.rows = self.service.transactions(); self.transactions.DeleteAllItems(); self.lines.DeleteAllItems()
        for item in self.rows:
            row = self.transactions.InsertItem(self.transactions.GetItemCount(), str(item[1]))
            values = (item[2], str(item[3]), item[4], item[5], item[6] or "", item[7] or "", "{:.2f}".format(item[8]))
            for column, value in enumerate(values, 1): self.transactions.SetItem(row, column, str(value))

    def on_select(self, event):
        self.lines.DeleteAllItems()
        for item in self.service.lines(self.rows[event.GetIndex()][0]):
            row = self.lines.InsertItem(self.lines.GetItemCount(), str(item[0]))
            values = (*item[1:6], "{:.2f}".format(item[6]), "{:.2f}".format(item[7]))
            for column, value in enumerate(values, 1): self.lines.SetItem(row, column, str(value))

    def on_reverse(self, event):
        index = self.transactions.GetFirstSelected()
        if index == -1:
            wx.MessageBox("Select a posted transaction.", "Create Reversal"); return
        item = self.rows[index]
        dialog = ReversalDialog(self, item[1])
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            reversal_date, reason = dialog.values()
        finally: dialog.Destroy()
        try: reversal_id = self.reversal_service.create(item[0], reversal_date, reason)
        except ValueError as error:
            wx.MessageBox(str(error), "Reversal not created", wx.OK | wx.ICON_WARNING); return
        wx.MessageBox("Reversal {} is ready for independent review.".format(reversal_id),
                      "Reversal Created", wx.OK | wx.ICON_INFORMATION)


def show_accounting_register(parent, connection, session, authorization):
    authorization.require("accounting.transactions.view", "view posted accounting transactions")
    reversal_service = None
    if authorization.has_permission("accounting.transactions.reverse"):
        from .reversal_service import AccountingReversalService
        reversal_service = AccountingReversalService(connection, session.user_id)
    dialog = AccountingRegisterDialog(parent, AccountingRegisterService(connection), reversal_service)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
