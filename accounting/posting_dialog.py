"""Read-only selection and confirmation screen for transaction posting."""

import wx

from .posting_service import AccountingPostingService
from .formatting import money


class AccountingPostingDialog(wx.Dialog):
    def __init__(self, parent, service):
        super().__init__(parent, title="Accounting Transaction Posting", size=(950, 620))
        self.service = service
        self.rows = []
        self.transactions = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("ID", 55), ("Organization", 170), ("Date", 90), ("Status", 85),
            ("Description", 255), ("Reference", 125), ("Total", 90),
        )):
            self.transactions.InsertColumn(index, label, width=width)
        self.lines = wx.ListCtrl(self, style=wx.LC_REPORT)
        for index, (label, width) in enumerate((
            ("#", 40), ("Account", 245), ("Fund", 180), ("Description", 240),
            ("Debit", 90), ("Credit", 90),
        )):
            self.lines.InsertColumn(index, label, width=width)
        self.transactions.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)
        refresh = wx.Button(self, label="Refresh")
        post = wx.Button(self, label="Post Transaction")
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        refresh.Bind(wx.EVT_BUTTON, self.refresh)
        post.Bind(wx.EVT_BUTTON, self.on_post)
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(refresh)
        buttons.AddStretchSpacer()
        buttons.Add(post, 0, wx.RIGHT, 6)
        buttons.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(wx.StaticText(self, label="Transactions eligible for posting"), 0, wx.ALL, 10)
        root.Add(self.transactions, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(wx.StaticText(self, label="Transaction lines (read only)"), 0, wx.ALL, 10)
        root.Add(self.lines, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(buttons, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(root)
        self.refresh()

    def refresh(self, event=None):
        try:
            self.rows = self.service.list_postable()
        except ValueError as error:
            wx.MessageBox(str(error), "Transactions not available", wx.OK | wx.ICON_WARNING)
            return
        self.transactions.DeleteAllItems()
        self.lines.DeleteAllItems()
        for item in self.rows:
            row = self.transactions.InsertItem(self.transactions.GetItemCount(), str(item[0]))
            values = (item[1], str(item[2]), item[3], item[4] or "", item[5] or "",
                      money(item[7]))
            for column, value in enumerate(values, 1):
                self.transactions.SetItem(row, column, str(value))

    def on_select(self, event):
        self.lines.DeleteAllItems()
        for item in self.service.lines(self.rows[event.GetIndex()][0]):
            row = self.lines.InsertItem(self.lines.GetItemCount(), str(item[0]))
            values = (item[1], item[2], item[3] or "", money(item[4]), money(item[5]))
            for column, value in enumerate(values, 1):
                self.lines.SetItem(row, column, str(value))

    def on_post(self, event):
        index = self.transactions.GetFirstSelected()
        if index == -1:
            wx.MessageBox("Select a transaction to post.", "Transaction Posting")
            return
        item = self.rows[index]
        warning = ("Post transaction {}? Posting is permanent; corrections require "
                   "a reversing transaction.").format(item[0])
        if wx.MessageBox(warning, "Post Transaction",
                         wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING) != wx.YES:
            return
        try:
            number = self.service.post(item[0], item[6])
        except ValueError as error:
            wx.MessageBox(str(error), "Transaction not posted", wx.OK | wx.ICON_WARNING)
            return
        wx.MessageBox("Transaction {} was posted as number {}.".format(item[0], number),
                      "Transaction Posted", wx.OK | wx.ICON_INFORMATION)
        self.refresh()


def show_accounting_posting(parent, connection, session, authorization):
    authorization.require("accounting.transactions.post", "post accounting transactions")
    dialog = AccountingPostingDialog(
        parent, AccountingPostingService(connection, session.user_id)
    )
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
