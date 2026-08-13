"""Bank-statement reconciliation worksheet."""

from datetime import date
from decimal import Decimal, InvalidOperation

import wx
import wx.adv

from ui_dimensions import DATE_PICKER_SIZE

from .formatting import money


class BankReconciliationDialog(wx.Dialog):
    def __init__(self, parent, service):
        super().__init__(parent, title="Bank Reconciliation", size=(980, 610))
        self.service = service
        self.accounts = service.bank_accounts()
        self.rows = []
        self.account = wx.Choice(self)
        self.account.SetItems([str(row[1]) for row in self.accounts])
        if self.accounts:
            self.account.SetSelection(0)
        self.statement_date = wx.adv.DatePickerCtrl(self, size=DATE_PICKER_SIZE)
        self.beginning = wx.TextCtrl(self, value="0.00")
        self.ending = wx.TextCtrl(self, value="0.00")
        create = wx.Button(self, label="Create Draft")
        create.Bind(wx.EVT_BUTTON, self.on_create)

        inputs = wx.FlexGridSizer(cols=4, hgap=8, vgap=8)
        inputs.AddGrowableCol(1, 1)
        for label, control in (
            ("Bank account", self.account),
            ("Statement date", self.statement_date),
            ("Beginning balance", self.beginning),
            ("Ending balance", self.ending),
        ):
            inputs.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            inputs.Add(control, 1, wx.EXPAND)
        inputs.Add((1, 1)); inputs.Add(create)

        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Bank account", 150), ("Statement date", 100),
            ("Beginning", 105), ("Activity", 105), ("Calculated", 105),
            ("Statement", 105), ("Difference", 105), ("Status", 90),
            ("Items", 60),
        )):
            self.list.InsertColumn(index, label, width=width)
        for index in range(2, 7):
            column = self.list.GetColumn(index)
            column.SetAlign(wx.LIST_FORMAT_RIGHT)
            self.list.SetColumn(index, column)
        refresh = wx.Button(self, label="Refresh")
        complete = wx.Button(self, label="Complete Selected")
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        refresh.Bind(wx.EVT_BUTTON, self.refresh)
        complete.Bind(wx.EVT_BUTTON, self.on_complete)
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(refresh)
        buttons.AddStretchSpacer()
        buttons.Add(complete, 0, wx.RIGHT, 8)
        buttons.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(
            wx.StaticText(
                self,
                label=(
                    "A draft automatically includes matched bank rows since the previous "
                    "completed statement. Completion requires zero difference and no "
                    "unmatched rows in the statement period."
                ),
            ),
            0, wx.ALL | wx.EXPAND, 10,
        )
        root.Add(inputs, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(self.list, 1, wx.ALL | wx.EXPAND, 10)
        root.Add(buttons, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(root)
        self.refresh()
    def _date(self):
        value = self.statement_date.GetValue()
        return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())

    def on_create(self, event=None):
        index = self.account.GetSelection()
        if index == wx.NOT_FOUND:
            wx.MessageBox("Select an active bank account.", "Bank account required")
            return
        try:
            beginning = Decimal(self.beginning.GetValue().replace(",", "").replace("$", ""))
            ending = Decimal(self.ending.GetValue().replace(",", "").replace("$", ""))
            self.service.create_draft(
                self.accounts[index][0], self._date(), beginning, ending
            )
        except (InvalidOperation, ValueError) as error:
            wx.MessageBox(str(error), "Reconciliation not created", wx.OK | wx.ICON_WARNING)
            return
        self.refresh()

    def refresh(self, event=None):
        self.rows = self.service.reconciliations()
        self.list.DeleteAllItems()
        for item in self.rows:
            row = self.list.InsertItem(self.list.GetItemCount(), str(item[1]))
            values = (
                item[2], money(item[3]), money(item[5]), money(item[6]),
                money(item[4]), money(item[7]), item[8], item[9],
            )
            for column, value in enumerate(values, 1):
                self.list.SetItem(row, column, str(value))

    def on_complete(self, event=None):
        index = self.list.GetFirstSelected()
        if index == -1:
            wx.MessageBox("Select a draft reconciliation.", "Reconciliation required")
            return
        if wx.MessageBox(
            "Complete this reconciliation? Completed reconciliations are final.",
            "Confirm Reconciliation", wx.YES_NO | wx.ICON_QUESTION,
        ) != wx.YES:
            return
        try:
            self.service.complete(self.rows[index][0])
        except ValueError as error:
            wx.MessageBox(str(error), "Reconciliation not completed", wx.OK | wx.ICON_WARNING)
            return
        self.refresh()
