"""Read-only posted accounting transaction register."""

import wx

from .register_service import AccountingRegisterService


class AccountingRegisterDialog(wx.Dialog):
    def __init__(self, parent, service):
        super().__init__(parent, title="Posted Transaction Register", size=(1000, 650))
        self.service, self.rows = service, []
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
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        refresh.Bind(wx.EVT_BUTTON, self.refresh)
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.Add(refresh); buttons.AddStretchSpacer(); buttons.Add(close)
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


def show_accounting_register(parent, connection, session, authorization):
    authorization.require("accounting.transactions.view", "view posted accounting transactions")
    dialog = AccountingRegisterDialog(parent, AccountingRegisterService(connection))
    try: dialog.ShowModal()
    finally: dialog.Destroy()
