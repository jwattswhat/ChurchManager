"""Desktop editor for balanced accounting drafts."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

import wx
import wx.adv

from .draft_service import AccountingDraftService
from .models import JournalLine, JournalTransaction, ZERO
from .formatting import money


def _date_value(control):
    value = control.GetValue()
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


class LineDialog(wx.Dialog):
    def __init__(self, parent, choices, initial=None):
        super().__init__(parent, title="Transaction Line")
        self.choices = choices
        self.account = wx.Choice(self)
        self.fund = wx.Choice(self)
        self.function = wx.Choice(self)
        self.payee = wx.Choice(self)
        self.description = wx.TextCtrl(self)
        self.amount = wx.TextCtrl(self)
        self.side = wx.Choice(self, choices=["Debit", "Credit"])
        self.side.SetSelection(0)
        self._load_choice(self.account, choices["accounts"], required=True)
        self._load_choice(self.fund, choices["funds"], required=True)
        self._load_choice(self.function, choices["functions"])
        self._load_choice(self.payee, choices["payees"])
        grid = wx.FlexGridSizer(cols=2, hgap=8, vgap=8)
        grid.AddGrowableCol(1, 1)
        for label, control in (
            ("Account", self.account), ("Fund", self.fund),
            ("Function", self.function), ("Payee", self.payee),
            ("Line description", self.description),
            ("Amount", self.amount), ("Entry side", self.side),
        ):
            grid.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(
            wx.StaticText(
                self,
                label=(
                    "Enter one positive amount and designate the line as Debit or Credit."
                ),
            ),
            0, wx.LEFT | wx.RIGHT | wx.TOP, 12,
        )
        root.Add(grid, 1, wx.ALL | wx.EXPAND, 12)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizerAndFit(root)
        self.SetMinSize((560, self.GetSize().height))
        if initial:
            self._set_initial(initial)

    @staticmethod
    def _load_choice(control, rows, required=False):
        if not required:
            control.Append("(none)", None)
        for row in rows:
            control.Append(str(row[1]), row[0])
        control.SetSelection(0 if control.GetCount() else wx.NOT_FOUND)

    @staticmethod
    def _select_id(control, value):
        for index in range(control.GetCount()):
            if control.GetClientData(index) == value:
                control.SetSelection(index)
                return

    def _set_initial(self, initial):
        self._select_id(self.account, initial["account_id"])
        self._select_id(self.fund, initial["fund_id"])
        self._select_id(self.function, initial["function_id"])
        self._select_id(self.payee, initial["payee_id"])
        self.description.SetValue(initial["description"])
        debit = initial["debit"] or ZERO
        credit = initial["credit"] or ZERO
        self.side.SetSelection(0 if debit > ZERO else 1)
        self.amount.SetValue(str(debit if debit > ZERO else credit))

    @staticmethod
    def _money(control):
        text = control.GetValue().strip().replace(",", "").replace("$", "")
        return ZERO if not text else Decimal(text).quantize(Decimal("0.01"))

    def values(self):
        if self.account.GetSelection() == wx.NOT_FOUND:
            raise ValueError("Select an account.")
        if self.fund.GetSelection() == wx.NOT_FOUND:
            raise ValueError("Select a fund.")
        try:
            amount = self._money(self.amount)
        except InvalidOperation as error:
            raise ValueError("Amount must be a valid dollar amount.") from error
        if amount <= ZERO:
            raise ValueError("Enter a positive amount.")
        debit = amount if self.side.GetSelection() == 0 else ZERO
        credit = amount if self.side.GetSelection() == 1 else ZERO
        return {
            "account_id": self.account.GetClientData(self.account.GetSelection()),
            "account": self.account.GetStringSelection(),
            "fund_id": self.fund.GetClientData(self.fund.GetSelection()),
            "fund": self.fund.GetStringSelection(),
            "function_id": self.function.GetClientData(self.function.GetSelection()),
            "function": self.function.GetStringSelection(),
            "payee_id": self.payee.GetClientData(self.payee.GetSelection()),
            "payee": self.payee.GetStringSelection(),
            "description": self.description.GetValue().strip(),
            "debit": debit, "credit": credit,
        }


class DraftListDialog(wx.Dialog):
    def __init__(self, parent, rows):
        super().__init__(parent, title="Open Accounting Draft", size=(850, 430))
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("ID", 60), ("Organization", 170), ("Date", 95), ("Type", 125),
            ("Description", 230), ("Reference", 130),
        )):
            self.list.InsertColumn(index, label, width=width)
        self.ids = []
        type_labels = {
            "CASH_DISBURSEMENT": "Cash disbursement",
            "CASH_RECEIPT": "Cash receipt",
            "JOURNAL": "General journal",
        }
        for item in rows:
            self.ids.append(item[0])
            row = self.list.InsertItem(self.list.GetItemCount(), str(item[0]))
            values = (item[1], str(item[2]), type_labels.get(item[3], item[3]),
                      item[4] or "", item[5] or "")
            for column, value in enumerate(values, start=1):
                self.list.SetItem(row, column, str(value))
        if self.ids:
            self.list.Select(0)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, lambda event: self.EndModal(wx.ID_OK))
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(self.list, 1, wx.ALL | wx.EXPAND, 10)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(root)

    def selected_id(self):
        index = self.list.GetFirstSelected()
        return None if index == -1 else self.ids[index]


class AccountingDraftDialog(wx.Dialog):
    def __init__(self, parent, service, can_edit_any=False, can_mark_ready=False):
        super().__init__(parent, title="Accounting Transaction Entry", size=(980, 650))
        self.service = service
        self.can_edit_any = can_edit_any
        self.can_mark_ready = can_mark_ready
        self.current_id = None
        self.current_version = None
        self.lines = []
        self.master_choices = None
        self.organization = wx.Choice(self)
        for organization_id, name in service.list_organizations():
            self.organization.Append(name, organization_id)
        if self.organization.GetCount():
            self.organization.SetSelection(0)
        self.organization.Bind(wx.EVT_CHOICE, self.on_organization)
        self.transaction_date = wx.adv.DatePickerCtrl(self)
        self.transaction_type = wx.Choice(
            self, choices=["Cash disbursement", "Cash receipt", "General journal"]
        )
        self.transaction_type.SetSelection(0)
        self.description = wx.TextCtrl(self)
        self.reference = wx.TextCtrl(self)
        header = wx.FlexGridSizer(cols=4, hgap=8, vgap=8)
        header.AddGrowableCol(1, 1)
        header.AddGrowableCol(3, 1)
        for label, control in (
            ("Organization", self.organization), ("Date", self.transaction_date),
            ("Type", self.transaction_type), ("Source/reference", self.reference),
        ):
            header.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            header.Add(control, 1, wx.EXPAND)
        header.Add(wx.StaticText(self, label="Description"), 0, wx.ALIGN_CENTER_VERTICAL)
        header.Add(self.description, 1, wx.EXPAND)
        header.AddSpacer(1)
        header.AddSpacer(1)

        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("#", 35), ("Account", 175), ("Fund", 135), ("Function", 120),
            ("Payee", 110), ("Description", 150), ("Debit", 80), ("Credit", 80),
        )):
            self.list.InsertColumn(index, label, width=width)
        add = wx.Button(self, label="Add Line")
        edit = wx.Button(self, label="Edit Line")
        remove = wx.Button(self, label="Remove Line")
        add.Bind(wx.EVT_BUTTON, self.on_add)
        edit.Bind(wx.EVT_BUTTON, self.on_edit)
        remove.Bind(wx.EVT_BUTTON, self.on_remove)
        self.totals = wx.StaticText(self, label="Debits $0.00    Credits $0.00    Difference $0.00")
        new = wx.Button(self, label="New Draft")
        open_draft = wx.Button(self, label="Open Draft")
        self.save = wx.Button(self, label="Save Draft")
        self.submit = wx.Button(self, label="Submit for Review")
        self.submit.Enable(False)
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        new.Bind(wx.EVT_BUTTON, self.on_new)
        open_draft.Bind(wx.EVT_BUTTON, self.on_open)
        self.save.Bind(wx.EVT_BUTTON, self.on_save)
        self.submit.Bind(wx.EVT_BUTTON, self.on_submit)
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        for button in (add, edit, remove):
            buttons.Add(button, 0, wx.RIGHT, 6)
        buttons.AddStretchSpacer()
        buttons.Add(self.totals, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 16)
        buttons.Add(new, 0, wx.RIGHT, 6)
        buttons.Add(open_draft, 0, wx.RIGHT, 6)
        buttons.Add(self.save, 0, wx.RIGHT, 6)
        buttons.Add(self.submit, 0, wx.RIGHT, 6)
        buttons.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(header, 0, wx.ALL | wx.EXPAND, 12)
        root.Add(self.list, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 12)
        root.Add(buttons, 0, wx.ALL | wx.EXPAND, 12)
        self.SetSizer(root)
        self.on_organization()

    def on_organization(self, event=None):
        index = self.organization.GetSelection()
        if index != wx.NOT_FOUND:
            self.master_choices = self.service.choices(self.organization.GetClientData(index))
            self.lines = []
            self.refresh()

    @staticmethod
    def _select_id(control, value):
        for index in range(control.GetCount()):
            if control.GetClientData(index) == value:
                control.SetSelection(index)
                return True
        return False

    def _label(self, group, value):
        if value is None:
            return "(none)"
        for row in self.master_choices[group]:
            if row[0] == value:
                return str(row[1])
        return "(inactive or unavailable)"

    def on_new(self, event=None):
        self.current_id = None
        self.current_version = None
        self.lines = []
        self.description.SetValue("")
        self.reference.SetValue("")
        self.save.SetLabel("Save Draft")
        self.submit.Enable(False)
        self.refresh()

    def on_open(self, event=None):
        try:
            rows = self.service.list_drafts(self.can_edit_any)
        except ValueError as error:
            wx.MessageBox(str(error), "Drafts not available", wx.OK | wx.ICON_WARNING)
            return
        if not rows:
            wx.MessageBox("There are no editable drafts.", "Open Draft")
            return
        dialog = DraftListDialog(self, rows)
        selected_id = None
        try:
            if dialog.ShowModal() != wx.ID_OK or dialog.selected_id() is None:
                return
            selected_id = dialog.selected_id()
            transaction, version, _creator = self.service.load(
                selected_id, self.can_edit_any
            )
        except ValueError as error:
            wx.MessageBox(str(error), "Draft not opened", wx.OK | wx.ICON_WARNING)
            return
        finally:
            dialog.Destroy()
        if not self._select_id(self.organization, transaction.organization_id):
            wx.MessageBox("The draft's organization is not active.", "Draft not opened")
            return
        self.master_choices = self.service.choices(transaction.organization_id)
        self.transaction_date.SetValue(wx.DateTime.FromDMY(
            transaction.transaction_date.day, transaction.transaction_date.month - 1,
            transaction.transaction_date.year,
        ))
        type_codes = ("CASH_DISBURSEMENT", "CASH_RECEIPT", "JOURNAL")
        self.transaction_type.SetSelection(type_codes.index(transaction.transaction_type))
        self.description.SetValue(transaction.description)
        self.reference.SetValue(transaction.reference)
        self.lines = [{
            "account_id": line.account_id, "account": self._label("accounts", line.account_id),
            "fund_id": line.fund_id, "fund": self._label("funds", line.fund_id),
            "function_id": line.function_id, "function": self._label("functions", line.function_id),
            "payee_id": line.payee_id, "payee": self._label("payees", line.payee_id),
            "description": line.description, "debit": line.debit, "credit": line.credit,
        } for line in transaction.lines]
        self.current_id = selected_id
        self.current_version = version
        self.save.SetLabel("Update Draft")
        self.submit.Enable(self.can_mark_ready)
        self.refresh()

    def on_submit(self, event=None):
        if self.current_id is None:
            return
        answer = wx.MessageBox(
            "Submit this draft for review? Its lines will be locked.",
            "Submit for Review", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        )
        if answer != wx.YES:
            return
        try:
            self.service.submit(
                self.current_id, self.current_version, self.can_edit_any
            )
        except ValueError as error:
            wx.MessageBox(str(error), "Draft not submitted", wx.OK | wx.ICON_WARNING)
            return
        wx.MessageBox(
            "Draft {} is ready for review.".format(self.current_id),
            "Submitted", wx.OK | wx.ICON_INFORMATION,
        )
        self.on_new()

    def _line_dialog(self, initial=None):
        if not self.master_choices or not self.master_choices["accounts"]:
            wx.MessageBox("No active posting accounts are available.", "Transaction Entry")
            return None
        dialog = LineDialog(self, self.master_choices, initial)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return None
            return dialog.values()
        except ValueError as error:
            wx.MessageBox(str(error), "Line not added", wx.OK | wx.ICON_WARNING)
            return None
        finally:
            dialog.Destroy()

    def on_add(self, event):
        value = self._line_dialog()
        if value:
            self.lines.append(value)
            self.refresh()

    def on_edit(self, event):
        index = self.list.GetFirstSelected()
        if index == -1:
            return
        value = self._line_dialog(self.lines[index])
        if value:
            self.lines[index] = value
            self.refresh()

    def on_remove(self, event):
        index = self.list.GetFirstSelected()
        if index != -1:
            self.lines.pop(index)
            self.refresh()

    def refresh(self):
        self.list.DeleteAllItems()
        debit_total = ZERO
        credit_total = ZERO
        for number, line in enumerate(self.lines, start=1):
            row = self.list.InsertItem(self.list.GetItemCount(), str(number))
            values = (
                line["account"], line["fund"], line["function"], line["payee"],
                line["description"], money(line["debit"] or ZERO),
                money(line["credit"] or ZERO),
            )
            for column, value in enumerate(values, start=1):
                self.list.SetItem(row, column, value)
            debit_total += line["debit"]
            credit_total += line["credit"]
        self.totals.SetLabel(
            "Debits {}    Credits {}    Difference {}".format(
                money(debit_total, True), money(credit_total, True),
                money(debit_total - credit_total, True))
        )

    def transaction(self):
        type_codes = ("CASH_DISBURSEMENT", "CASH_RECEIPT", "JOURNAL")
        lines = tuple(
            JournalLine(
                number, line["account_id"], line["fund_id"], line["debit"],
                line["credit"], line["function_id"], line["payee_id"],
                line["description"],
            )
            for number, line in enumerate(self.lines, start=1)
        )
        return JournalTransaction(
            self.organization.GetClientData(self.organization.GetSelection()),
            _date_value(self.transaction_date), self.description.GetValue(), lines,
            self.reference.GetValue(), type_codes[self.transaction_type.GetSelection()],
        )

    def on_save(self, event):
        try:
            if self.current_id is None:
                transaction_id = self.service.create(self.transaction())
                message = "Draft {} was saved. It has not been posted.".format(transaction_id)
            else:
                self.current_version = self.service.update(
                    self.current_id, self.current_version, self.transaction(), self.can_edit_any
                )
                transaction_id = self.current_id
                message = "Draft {} was updated. It has not been posted.".format(transaction_id)
        except ValueError as error:
            wx.MessageBox(str(error), "Draft not saved", wx.OK | wx.ICON_WARNING)
            return
        wx.MessageBox(
            message,
            "Draft saved", wx.OK | wx.ICON_INFORMATION,
        )
        self.on_new()


def show_accounting_draft_entry(parent, connection, session, authorization):
    authorization.require("accounting.transactions.create", "create accounting drafts")
    dialog = AccountingDraftDialog(
        parent, AccountingDraftService(connection, session.user_id),
        can_edit_any=authorization.has_permission(
            "accounting.transactions.edit_any_draft"
        ),
        can_mark_ready=authorization.has_permission(
            "accounting.transactions.mark_ready"
        ),
    )
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
