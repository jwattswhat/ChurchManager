"""Read-only review and approval screen for accounting transactions."""

import wx

from .review_service import AccountingReviewService
from .formatting import money


class AccountingReviewDialog(wx.Dialog):
    def __init__(self, parent, service, can_override=False):
        super().__init__(parent, title="Accounting Transaction Review", size=(950, 620))
        self.service = service
        self.can_override = can_override
        self.rows = []
        self.transactions = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("ID", 55), ("Organization", 170), ("Date", 90), ("Type", 125),
            ("Description", 260), ("Reference", 130), ("Total", 85),
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
        approve = wx.Button(self, label="Approve")
        override = wx.Button(self, label="Solo Override")
        override.Enable(can_override)
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        refresh.Bind(wx.EVT_BUTTON, self.refresh)
        approve.Bind(wx.EVT_BUTTON, self.on_approve)
        override.Bind(wx.EVT_BUTTON, self.on_override)
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(refresh, 0, wx.RIGHT, 6)
        buttons.AddStretchSpacer()
        buttons.Add(approve, 0, wx.RIGHT, 6)
        buttons.Add(override, 0, wx.RIGHT, 6)
        buttons.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(wx.StaticText(self, label="Transactions awaiting review"), 0, wx.ALL, 10)
        root.Add(self.transactions, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(wx.StaticText(self, label="Transaction lines (read only)"), 0, wx.ALL, 10)
        root.Add(self.lines, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(buttons, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(root)
        self.refresh()

    def refresh(self, event=None):
        self.rows = self.service.list_ready()
        self.transactions.DeleteAllItems()
        self.lines.DeleteAllItems()
        type_labels = {"CASH_DISBURSEMENT": "Cash disbursement",
                       "CASH_RECEIPT": "Cash receipt", "JOURNAL": "General journal",
                       "RESTRICTION_RELEASE": "Restriction release"}
        for item in self.rows:
            row = self.transactions.InsertItem(self.transactions.GetItemCount(), str(item[0]))
            values = (item[1], str(item[2]), type_labels.get(item[3], item[3]),
                      item[4] or "", item[5] or "", money(item[8]))
            for column, value in enumerate(values, 1):
                self.transactions.SetItem(row, column, str(value))

    def on_select(self, event):
        self.lines.DeleteAllItems()
        for item in self.service.lines(self.rows[event.GetIndex()][0]):
            row = self.lines.InsertItem(self.lines.GetItemCount(), str(item[0]))
            values = (item[1], item[2], item[3] or "", money(item[4]), money(item[5]))
            for column, value in enumerate(values, 1):
                self.lines.SetItem(row, column, str(value))

    def on_approve(self, event):
        index = self.transactions.GetFirstSelected()
        if index == -1:
            wx.MessageBox("Select a transaction to approve.", "Accounting Review")
            return
        item = self.rows[index]
        if wx.MessageBox("Approve transaction {}?".format(item[0]), "Approve Transaction",
                         wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) != wx.YES:
            return
        try:
            self.service.approve(item[0], item[6])
        except ValueError as error:
            wx.MessageBox(str(error), "Transaction not approved", wx.OK | wx.ICON_WARNING)
            return
        wx.MessageBox("Transaction {} was approved.".format(item[0]), "Approved")
        self.refresh()

    def on_override(self, event):
        index = self.transactions.GetFirstSelected()
        if index == -1:
            wx.MessageBox("Select a transaction to approve.", "Solo Override"); return
        dialog = wx.TextEntryDialog(self, "Explain why independent approval is unavailable.", "Solo Approval Override")
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            reason = dialog.GetValue()
        finally: dialog.Destroy()
        item = self.rows[index]
        try: self.service.approve(item[0], item[6], reason, can_override=True)
        except ValueError as error:
            wx.MessageBox(str(error), "Transaction not approved", wx.OK | wx.ICON_WARNING); return
        wx.MessageBox("Transaction {} was approved with an audited override.".format(item[0]), "Override Recorded")
        self.refresh()


def show_accounting_review(parent, connection, session, authorization):
    authorization.require("accounting.transactions.approve", "approve accounting transactions")
    dialog = AccountingReviewDialog(
        parent, AccountingReviewService(connection, session.user_id),
        can_override=authorization.has_permission("accounting.approval.override")
    )
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
