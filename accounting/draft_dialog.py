"""Desktop editor for balanced accounting drafts."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

import wx
import wx.adv

from .draft_service import AccountingDraftService
from .models import JournalLine, JournalTransaction, ZERO
from .formatting import money
from .attachment_service import (
    AccountingAttachmentService, AttachmentStore, load_attachment_policy,
)


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


class GuidedCashDialog(wx.Dialog):
    def __init__(self, parent, choices, receipt):
        title = "Guided Cash Receipt" if receipt else "Guided Cash Disbursement"
        super().__init__(parent, title=title)
        self.receipt = receipt
        self.cash = wx.Choice(self)
        self.offset = wx.Choice(self)
        self.fund = wx.Choice(self)
        self.function = wx.Choice(self)
        self.payee = wx.Choice(self)
        self.amount = wx.TextCtrl(self)
        self.description = wx.TextCtrl(self)
        self.reference = wx.TextCtrl(self)
        LineDialog._load_choice(self.cash, choices["cash_accounts"], required=True)
        LineDialog._load_choice(
            self.offset,
            choices["revenue_accounts" if receipt else "expense_accounts"],
            required=True,
        )
        self.offset_rows = choices["revenue_accounts" if receipt else "expense_accounts"]
        LineDialog._load_choice(self.fund, choices["funds"], required=True)
        LineDialog._load_choice(self.function, choices["functions"])
        LineDialog._load_choice(self.payee, choices["payees"])
        offset_label = "Revenue account" if receipt else "Expense account"
        grid = wx.FlexGridSizer(cols=2, hgap=8, vgap=8)
        grid.AddGrowableCol(1, 1)
        for label, control in (
            ("Bank account", self.cash), (offset_label, self.offset),
            ("Fund", self.fund), ("Function", self.function),
            ("Payee / payer", self.payee), ("Amount", self.amount),
            ("Description", self.description), ("Source/reference", self.reference),
        ):
            grid.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(wx.StaticText(self, label=(
            "This guide creates an ordinary balanced two-line journal entry for review."
        )), 0, wx.ALL, 12)
        root.Add(grid, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL),
                 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizerAndFit(root)
        self.SetMinSize((590, self.GetSize().height))

    @staticmethod
    def _selected(control, message):
        index = control.GetSelection()
        if index == wx.NOT_FOUND:
            raise ValueError(message)
        return control.GetClientData(index), control.GetStringSelection()

    def values(self):
        cash_id, cash_label = self._selected(self.cash, "Select a bank account.")
        offset_id, offset_label = self._selected(
            self.offset, "Select a revenue or expense account."
        )
        fund_id, fund_label = self._selected(self.fund, "Select a fund.")
        try:
            amount = LineDialog._money(self.amount)
        except InvalidOperation as error:
            raise ValueError("Amount must be a valid dollar amount.") from error
        if amount <= ZERO:
            raise ValueError("Enter a positive amount.")
        description = self.description.GetValue().strip()
        if not description:
            raise ValueError("Enter a description.")
        function_id, function_label = self._selected(self.function, "Select a function.")
        payee_id, payee_label = self._selected(self.payee, "Select a payee or payer.")
        requirement = self.offset_rows[self.offset.GetSelection()][2]
        if requirement == "REQUIRED" and function_id is None:
            raise ValueError("Select a functional classification for this account.")
        if requirement == "PROHIBITED" and function_id is not None:
            raise ValueError("This account does not allow a functional classification.")
        cash_line = {
            "account_id": cash_id, "account": cash_label,
            "fund_id": fund_id, "fund": fund_label,
            "function_id": None, "function": "(none)",
            "payee_id": payee_id, "payee": payee_label,
            "description": description,
            "debit": amount if self.receipt else ZERO,
            "credit": ZERO if self.receipt else amount,
        }
        offset_line = {
            "account_id": offset_id, "account": offset_label,
            "fund_id": fund_id, "fund": fund_label,
            "function_id": function_id, "function": function_label,
            "payee_id": payee_id, "payee": payee_label,
            "description": description,
            "debit": ZERO if self.receipt else amount,
            "credit": amount if self.receipt else ZERO,
        }
        reference = self.reference.GetValue().strip()
        if not self.receipt and not reference:
            raise ValueError("Enter the receipt, invoice, or voucher reference.")
        lines = [cash_line, offset_line] if self.receipt else [offset_line, cash_line]
        return lines, description, reference


class GuidedTransferDialog(wx.Dialog):
    def __init__(self, parent, choices, restriction_release=False):
        self.restriction_release = restriction_release
        super().__init__(
            parent,
            title=("Guided Restriction Release" if restriction_release
                   else "Guided Fund Transfer"),
        )
        self.cash = wx.Choice(self)
        self.from_fund = wx.Choice(self)
        self.to_fund = wx.Choice(self)
        self.transfer_out = wx.Choice(self)
        self.transfer_in = wx.Choice(self)
        self.amount = wx.TextCtrl(self)
        self.description = wx.TextCtrl(self)
        self.reference = wx.TextCtrl(self)
        for control, rows in (
            (self.cash, choices["cash_accounts"]),
            (self.from_fund, choices["restricted_funds"] if restriction_release
             else choices["funds"]),
            (self.to_fund, choices["unrestricted_funds"] if restriction_release
             else choices["funds"]),
            (self.transfer_out, choices["transfer_out_accounts"]),
            (self.transfer_in, choices["transfer_in_accounts"]),
        ):
            LineDialog._load_choice(control, rows, required=True)
        grid = wx.FlexGridSizer(cols=2, hgap=8, vgap=8)
        grid.AddGrowableCol(1, 1)
        for label, control in (
            ("Bank account", self.cash), ("From fund", self.from_fund),
            ("To fund", self.to_fund), ("Transfer-out account", self.transfer_out),
            ("Transfer-in account", self.transfer_in), ("Amount", self.amount),
            ("Description", self.description), ("Reference", self.reference),
        ):
            grid.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(wx.StaticText(self, label=(
            ("This records an explicit release from a donor-restricted fund into an "
             "unrestricted fund. Supporting authority must be attached."
             if restriction_release else
             "The guide creates four lines so both funds remain individually balanced.")
        )), 0, wx.ALL, 12)
        root.Add(grid, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL),
                 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizerAndFit(root)
        self.SetMinSize((590, self.GetSize().height))

    def values(self):
        cash_id, cash_label = GuidedCashDialog._selected(
            self.cash, "Select a bank account."
        )
        from_id, from_label = GuidedCashDialog._selected(
            self.from_fund, "Select the fund providing the money."
        )
        to_id, to_label = GuidedCashDialog._selected(
            self.to_fund, "Select the fund receiving the money."
        )
        if from_id == to_id:
            raise ValueError("The From fund and To fund must be different.")
        out_id, out_label = GuidedCashDialog._selected(
            self.transfer_out, "Select the transfer-out account."
        )
        in_id, in_label = GuidedCashDialog._selected(
            self.transfer_in, "Select the transfer-in account."
        )
        try:
            amount = LineDialog._money(self.amount)
        except InvalidOperation as error:
            raise ValueError("Amount must be a valid dollar amount.") from error
        if amount <= ZERO:
            raise ValueError("Enter a positive amount.")
        description = self.description.GetValue().strip()
        if not description:
            raise ValueError("Enter a description.")
        none = {"function_id": None, "function": "(none)",
                "payee_id": None, "payee": "(none)", "description": description}
        lines = [
            {**none, "account_id": out_id, "account": out_label,
             "fund_id": from_id, "fund": from_label, "debit": amount, "credit": ZERO},
            {**none, "account_id": cash_id, "account": cash_label,
             "fund_id": from_id, "fund": from_label, "debit": ZERO, "credit": amount},
            {**none, "account_id": cash_id, "account": cash_label,
             "fund_id": to_id, "fund": to_label, "debit": amount, "credit": ZERO},
            {**none, "account_id": in_id, "account": in_label,
             "fund_id": to_id, "fund": to_label, "debit": ZERO, "credit": amount},
        ]
        reference = self.reference.GetValue().strip()
        if self.restriction_release and not reference:
            raise ValueError("Enter the authority or source-document reference.")
        return lines, description, reference


class DepositReceiptDialog(wx.Dialog):
    def __init__(self, parent, choices, initial=None):
        super().__init__(parent, title="Deposit Receipt Component")
        self.revenue_rows = choices["revenue_accounts"]
        self.revenue = wx.Choice(self)
        self.fund = wx.Choice(self)
        self.function = wx.Choice(self)
        self.payer = wx.Choice(self)
        self.amount = wx.TextCtrl(self)
        self.description = wx.TextCtrl(self)
        LineDialog._load_choice(self.revenue, self.revenue_rows, required=True)
        LineDialog._load_choice(self.fund, choices["funds"], required=True)
        LineDialog._load_choice(self.function, choices["functions"])
        LineDialog._load_choice(self.payer, choices["payees"])
        grid = wx.FlexGridSizer(cols=2, hgap=8, vgap=8)
        grid.AddGrowableCol(1, 1)
        for label, control in (("Revenue account", self.revenue), ("Fund", self.fund),
                               ("Function", self.function), ("Payer", self.payer),
                               ("Amount", self.amount), ("Description", self.description)):
            grid.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(grid, 1, wx.ALL | wx.EXPAND, 12)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL),
                 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizerAndFit(root)
        self.SetMinSize((560, self.GetSize().height))
        if initial:
            LineDialog._select_id(self.revenue, initial["revenue_id"])
            LineDialog._select_id(self.fund, initial["fund_id"])
            LineDialog._select_id(self.function, initial["function_id"])
            LineDialog._select_id(self.payer, initial["payer_id"])
            self.amount.SetValue(str(initial["amount"]))
            self.description.SetValue(initial["description"])

    def values(self):
        revenue_id, revenue_label = GuidedCashDialog._selected(
            self.revenue, "Select a revenue account."
        )
        fund_id, fund_label = GuidedCashDialog._selected(self.fund, "Select a fund.")
        function_id, function_label = GuidedCashDialog._selected(
            self.function, "Select a function."
        )
        payer_id, payer_label = GuidedCashDialog._selected(self.payer, "Select a payer.")
        requirement = self.revenue_rows[self.revenue.GetSelection()][2]
        if requirement == "REQUIRED" and function_id is None:
            raise ValueError("Select a functional classification for this revenue account.")
        if requirement == "PROHIBITED" and function_id is not None:
            raise ValueError("This revenue account does not allow a functional classification.")
        try:
            amount = LineDialog._money(self.amount)
        except InvalidOperation as error:
            raise ValueError("Amount must be a valid dollar amount.") from error
        if amount <= ZERO:
            raise ValueError("Enter a positive amount.")
        description = self.description.GetValue().strip()
        if not description:
            raise ValueError("Enter a receipt description.")
        return {
            "revenue_id": revenue_id, "revenue": revenue_label,
            "fund_id": fund_id, "fund": fund_label,
            "function_id": function_id, "function": function_label,
            "payer_id": payer_id, "payer": payer_label,
            "amount": amount, "description": description,
        }


class GuidedDepositDialog(wx.Dialog):
    def __init__(self, parent, choices):
        super().__init__(parent, title="Guided Multi-Receipt Deposit", size=(820, 540))
        self.choices = choices
        self.items = []
        self.cash = wx.Choice(self)
        LineDialog._load_choice(self.cash, choices["cash_accounts"], required=True)
        self.description = wx.TextCtrl(self)
        self.reference = wx.TextCtrl(self)
        header = wx.FlexGridSizer(cols=2, hgap=8, vgap=8)
        header.AddGrowableCol(1, 1)
        for label, control in (("Bank account", self.cash),
                               ("Deposit description", self.description),
                               ("Deposit/reference number", self.reference)):
            header.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            header.Add(control, 1, wx.EXPAND)
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Fund", 145), ("Revenue account", 190), ("Payer", 120),
            ("Description", 190), ("Amount", 95),
        )):
            self.list.InsertColumn(index, label, width=width)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit)
        add = wx.Button(self, label="Add Receipt")
        remove = wx.Button(self, label="Remove Receipt")
        add.Bind(wx.EVT_BUTTON, self.on_add)
        remove.Bind(wx.EVT_BUTTON, self.on_remove)
        self.total = wx.StaticText(self, label="$0.00", size=(130, -1), style=wx.ALIGN_RIGHT)
        actions = wx.BoxSizer(wx.HORIZONTAL)
        actions.Add(add, 0, wx.RIGHT, 6); actions.Add(remove)
        actions.AddStretchSpacer(); actions.Add(wx.StaticText(self, label="Deposit total"),
                                                0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        actions.Add(self.total, 0, wx.ALIGN_CENTER_VERTICAL)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(header, 0, wx.ALL | wx.EXPAND, 12)
        root.Add(self.list, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 12)
        root.Add(actions, 0, wx.ALL | wx.EXPAND, 12)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL),
                 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)
        self.SetSizer(root)

    def refresh(self):
        self.list.DeleteAllItems()
        total = ZERO
        for item in self.items:
            row = self.list.InsertItem(self.list.GetItemCount(), item["fund"])
            for column, value in enumerate((item["revenue"], item["payer"],
                                             item["description"], money(item["amount"])), 1):
                self.list.SetItem(row, column, str(value))
            total += item["amount"]
        self.total.SetLabel(money(total, True))

    def on_add(self, event):
        dialog = DepositReceiptDialog(self, self.choices)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            self.items.append(dialog.values())
            self.refresh()
        except ValueError as error:
            wx.MessageBox(str(error), "Receipt not added", wx.OK | wx.ICON_WARNING)
        finally:
            dialog.Destroy()

    def on_remove(self, event):
        index = self.list.GetFirstSelected()
        if index != -1:
            self.items.pop(index)
            self.refresh()

    def on_edit(self, event):
        index = event.GetIndex() if event is not None else self.list.GetFirstSelected()
        if index < 0 or index >= len(self.items):
            return
        dialog = DepositReceiptDialog(self, self.choices, self.items[index])
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            self.items[index] = dialog.values()
            self.refresh()
        except ValueError as error:
            wx.MessageBox(str(error), "Receipt not updated", wx.OK | wx.ICON_WARNING)
        finally:
            dialog.Destroy()

    def values(self):
        cash_id, cash_label = GuidedCashDialog._selected(
            self.cash, "Select a bank account."
        )
        if len(self.items) < 2:
            raise ValueError("Add at least two receipt components to this deposit.")
        description = self.description.GetValue().strip()
        if not description:
            raise ValueError("Enter a deposit description.")
        lines = []
        for item in self.items:
            common = {
                "fund_id": item["fund_id"], "fund": item["fund"],
                "payee_id": item["payer_id"], "payee": item["payer"],
                "description": item["description"],
            }
            lines.append({**common, "account_id": cash_id, "account": cash_label,
                          "function_id": None, "function": "(none)",
                          "debit": item["amount"], "credit": ZERO})
            lines.append({**common, "account_id": item["revenue_id"],
                          "account": item["revenue"],
                          "function_id": item["function_id"],
                          "function": item["function"],
                          "debit": ZERO, "credit": item["amount"]})
        return lines, description, self.reference.GetValue().strip()


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
            "RESTRICTION_RELEASE": "Restriction release",
            "OPENING_BALANCE": "Opening balances",
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


class AttachmentDialog(wx.Dialog):
    def __init__(self, parent, service, transaction_id, can_edit_any=False):
        super().__init__(parent, title="Source Documents", size=(760, 440))
        self.service = service
        self.transaction_id = transaction_id
        self.can_edit_any = can_edit_any
        self.rows = []
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("File", 245), ("Document type", 120), ("Added", 145), ("Added by", 150),
        )):
            self.list.InsertColumn(index, label, width=width)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_verify)
        add = wx.Button(self, label="Add Document")
        verify = wx.Button(self, label="Verify / Open")
        remove = wx.Button(self, label="Remove")
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        add.Bind(wx.EVT_BUTTON, self.on_add)
        verify.Bind(wx.EVT_BUTTON, self.on_verify)
        remove.Bind(wx.EVT_BUTTON, self.on_remove)
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(add, 0, wx.RIGHT, 6)
        buttons.Add(verify, 0, wx.RIGHT, 6)
        buttons.Add(remove)
        buttons.AddStretchSpacer()
        buttons.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(wx.StaticText(self, label=(
            "Files are copied into protected ChurchManager storage and checked for later changes."
        )), 0, wx.ALL, 10)
        root.Add(self.list, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(buttons, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(root)
        self.refresh()

    def refresh(self):
        try:
            self.rows = self.service.list(self.transaction_id, self.can_edit_any)
        except ValueError as error:
            wx.MessageBox(str(error), "Source Documents", wx.OK | wx.ICON_WARNING)
            return
        self.list.DeleteAllItems()
        for item in self.rows:
            row = self.list.InsertItem(self.list.GetItemCount(), str(item[1]))
            values = (item[2] or "Other", str(item[5]), item[6])
            for column, value in enumerate(values, 1):
                self.list.SetItem(row, column, str(value))

    def _selected(self):
        index = self.list.GetFirstSelected()
        if index == -1:
            wx.MessageBox("Select a source document first.", "Source Documents")
            return None
        return self.rows[index]

    def on_add(self, event):
        picker = wx.FileDialog(
            self, "Select a receipt, invoice, or other source document",
            wildcard=("Supported documents|*.pdf;*.jpg;*.jpeg;*.png;*.tif;*.tiff;"
                      "*.doc;*.docx;*.xls;*.xlsx;*.csv;*.txt|All files|*.*"),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        )
        try:
            if picker.ShowModal() != wx.ID_OK:
                return
            choices = ["Receipt", "Invoice", "Voucher", "Bank document", "Other"]
            kind = wx.SingleChoiceDialog(self, "What kind of document is this?",
                                         "Document Type", choices)
            try:
                if kind.ShowModal() != wx.ID_OK:
                    return
                document_type = kind.GetStringSelection()
            finally:
                kind.Destroy()
            self.service.add(
                self.transaction_id, picker.GetPath(), document_type, self.can_edit_any
            )
            self.refresh()
        except ValueError as error:
            wx.MessageBox(str(error), "Document not added", wx.OK | wx.ICON_WARNING)
        finally:
            picker.Destroy()

    def on_verify(self, event):
        item = self._selected()
        if item is None:
            return
        try:
            path = self.service.verify(self.transaction_id, item[0], self.can_edit_any)
            wx.LaunchDefaultApplication(str(path))
        except ValueError as error:
            wx.MessageBox(str(error), "Document verification failed", wx.OK | wx.ICON_WARNING)

    def on_remove(self, event):
        item = self._selected()
        if item is None:
            return
        if wx.MessageBox(
            "Remove this source document from the draft? The action will be audited.",
            "Remove Source Document", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
        ) != wx.YES:
            return
        try:
            self.service.remove(self.transaction_id, item[0], self.can_edit_any)
            self.refresh()
        except ValueError as error:
            wx.MessageBox(str(error), "Document not removed", wx.OK | wx.ICON_WARNING)


class AccountingDraftDialog(wx.Dialog):
    def __init__(self, parent, service, can_edit_any=False, can_mark_ready=False,
                 can_delete=False, attachment_service=None):
        super().__init__(parent, title="Accounting Transaction Entry", size=(980, 650))
        self.service = service
        self.can_edit_any = can_edit_any
        self.can_mark_ready = can_mark_ready
        self.can_delete = can_delete
        self.attachment_service = attachment_service
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
            self, choices=["Cash disbursement", "Cash receipt", "General journal",
                           "Restriction release", "Opening balances"]
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
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit)
        add = wx.Button(self, label="Add Line")
        edit = wx.Button(self, label="Edit Line")
        remove = wx.Button(self, label="Remove Line")
        self.attachments = wx.Button(self, label="Source Documents")
        guided_receipt = wx.Button(self, label="Guided Receipt")
        guided_disbursement = wx.Button(self, label="Guided Disbursement")
        guided_transfer = wx.Button(self, label="Guided Transfer")
        guided_deposit = wx.Button(self, label="Guided Deposit")
        guided_release = wx.Button(self, label="Restriction Release")
        guided_opening = wx.Button(self, label="Opening Balances")
        self.attachments.Enable(False)
        add.Bind(wx.EVT_BUTTON, self.on_add)
        edit.Bind(wx.EVT_BUTTON, self.on_edit)
        remove.Bind(wx.EVT_BUTTON, self.on_remove)
        self.attachments.Bind(wx.EVT_BUTTON, self.on_attachments)
        guided_receipt.Bind(wx.EVT_BUTTON, lambda event: self.on_guided_cash(True))
        guided_disbursement.Bind(wx.EVT_BUTTON, lambda event: self.on_guided_cash(False))
        guided_transfer.Bind(wx.EVT_BUTTON, self.on_guided_transfer)
        guided_deposit.Bind(wx.EVT_BUTTON, self.on_guided_deposit)
        guided_release.Bind(wx.EVT_BUTTON, self.on_guided_release)
        guided_opening.Bind(wx.EVT_BUTTON, self.on_guided_opening)
        self.debit_total = wx.StaticText(
            self, label="$0.00", size=(135, -1), style=wx.ALIGN_RIGHT
        )
        self.credit_total = wx.StaticText(
            self, label="$0.00", size=(135, -1), style=wx.ALIGN_RIGHT
        )
        self.difference_total = wx.StaticText(
            self, label="$0.00", size=(135, -1), style=wx.ALIGN_RIGHT
        )
        new = wx.Button(self, label="New Draft")
        open_draft = wx.Button(self, label="Open Draft")
        self.save = wx.Button(self, label="Save Draft")
        self.submit = wx.Button(self, label="Submit for Review")
        self.delete = wx.Button(self, label="Delete Draft")
        self.submit.Enable(False)
        self.delete.Enable(False)
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        new.Bind(wx.EVT_BUTTON, self.on_new)
        open_draft.Bind(wx.EVT_BUTTON, self.on_open)
        self.save.Bind(wx.EVT_BUTTON, self.on_save)
        self.submit.Bind(wx.EVT_BUTTON, self.on_submit)
        self.delete.Bind(wx.EVT_BUTTON, self.on_delete)
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        line_buttons = wx.BoxSizer(wx.HORIZONTAL)
        for button in (add, edit, remove):
            line_buttons.Add(button, 0, wx.RIGHT, 6)
        line_buttons.AddStretchSpacer()
        guided_buttons = wx.GridSizer(cols=3, hgap=6, vgap=6)
        for button in (guided_receipt, guided_disbursement, guided_transfer,
                       guided_deposit, guided_release, guided_opening, self.attachments):
            guided_buttons.Add(button, 0, wx.EXPAND)
        totals_row = wx.BoxSizer(wx.HORIZONTAL)
        totals_row.AddStretchSpacer()
        for label, value in (("Debits", self.debit_total),
                             ("Credits", self.credit_total),
                             ("Difference", self.difference_total)):
            totals_row.Add(wx.StaticText(self, label=label), 0,
                           wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 12)
            totals_row.Add(value, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 4)
        workflow_buttons = wx.BoxSizer(wx.HORIZONTAL)
        workflow_buttons.AddStretchSpacer()
        workflow_buttons.Add(new, 0, wx.RIGHT, 6)
        workflow_buttons.Add(open_draft, 0, wx.RIGHT, 6)
        workflow_buttons.Add(self.save, 0, wx.RIGHT, 6)
        workflow_buttons.Add(self.submit, 0, wx.RIGHT, 6)
        workflow_buttons.Add(self.delete, 0, wx.RIGHT, 6)
        workflow_buttons.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(header, 0, wx.ALL | wx.EXPAND, 12)
        root.Add(self.list, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 12)
        root.Add(line_buttons, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 12)
        root.Add(totals_row, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 12)
        root.Add(guided_buttons, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 12)
        root.Add(workflow_buttons, 0, wx.ALL | wx.EXPAND, 12)
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
        self.delete.Enable(False)
        self.attachments.Enable(False)
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
            transaction, version, creator = self.service.load(
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
        type_codes = ("CASH_DISBURSEMENT", "CASH_RECEIPT", "JOURNAL", "RESTRICTION_RELEASE", "OPENING_BALANCE")
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
        self.delete.Enable(self.can_delete and creator == self.service.acting_user_id)
        self.attachments.Enable(self.attachment_service is not None)
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

    def on_delete(self, event=None):
        if self.current_id is None:
            return
        if wx.MessageBox(
            "Permanently delete this unposted draft? This cannot be undone.",
            "Confirm Draft Deletion",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
        ) != wx.YES:
            return
        try:
            self.service.delete(self.current_id, self.current_version)
        except ValueError as error:
            wx.MessageBox(str(error), "Draft not deleted", wx.OK | wx.ICON_WARNING)
            return
        wx.MessageBox(
            "Draft {} was deleted. The deletion was audited.".format(self.current_id),
            "Draft Deleted", wx.OK | wx.ICON_INFORMATION,
        )
        self.on_new()

    def _line_dialog(self, initial=None):
        if not self.master_choices or not self.master_choices["accounts"]:
            wx.MessageBox("No active posting accounts are available.", "Transaction Entry")
            return None
        choices = self.master_choices
        if self.transaction_type.GetSelection() == 4:
            choices = dict(self.master_choices)
            choices["accounts"] = self.master_choices["opening_accounts"]
        dialog = LineDialog(self, choices, initial)
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

    def on_attachments(self, event):
        if self.current_id is None or self.attachment_service is None:
            wx.MessageBox("Save the draft before adding source documents.", "Source Documents")
            return
        dialog = AttachmentDialog(
            self, self.attachment_service, self.current_id, self.can_edit_any
        )
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()

    def on_guided_cash(self, receipt):
        if self.current_id is not None or self.lines:
            if wx.MessageBox(
                "Start a new guided transaction and discard the current unsaved screen values?",
                "Guided Transaction", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
            ) != wx.YES:
                return
            self.on_new()
        if not self.master_choices or not self.master_choices["cash_accounts"]:
            wx.MessageBox(
                "Configure an active Bank Account before using a guided cash transaction.",
                "Guided Transaction", wx.OK | wx.ICON_WARNING,
            )
            return
        dialog = GuidedCashDialog(self, self.master_choices, receipt)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            lines, description, reference = dialog.values()
        except ValueError as error:
            wx.MessageBox(str(error), "Guided transaction not created",
                          wx.OK | wx.ICON_WARNING)
            return
        finally:
            dialog.Destroy()
        self.lines = lines
        self.description.SetValue(description)
        self.reference.SetValue(reference)
        self.transaction_type.SetSelection(1 if receipt else 0)
        self.refresh()

    def on_guided_transfer(self, event):
        if self.current_id is not None or self.lines:
            if wx.MessageBox(
                "Start a new guided transfer and discard the current unsaved screen values?",
                "Guided Transfer", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
            ) != wx.YES:
                return
            self.on_new()
        required = ("cash_accounts", "transfer_out_accounts", "transfer_in_accounts")
        if not self.master_choices or any(not self.master_choices[name] for name in required):
            wx.MessageBox(
                "A bank account and active transfer-in and transfer-out accounts are required.",
                "Guided Transfer", wx.OK | wx.ICON_WARNING,
            )
            return
        dialog = GuidedTransferDialog(self, self.master_choices)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            lines, description, reference = dialog.values()
        except ValueError as error:
            wx.MessageBox(str(error), "Guided transfer not created",
                          wx.OK | wx.ICON_WARNING)
            return
        finally:
            dialog.Destroy()
        self.lines = lines
        self.description.SetValue(description)
        self.reference.SetValue(reference)
        self.transaction_type.SetSelection(2)
        self.refresh()

    def on_guided_deposit(self, event):
        if self.current_id is not None or self.lines:
            if wx.MessageBox(
                "Start a new guided deposit and discard the current unsaved screen values?",
                "Guided Deposit", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
            ) != wx.YES:
                return
            self.on_new()
        if (not self.master_choices or not self.master_choices["cash_accounts"]
                or not self.master_choices["revenue_accounts"]):
            wx.MessageBox(
                "A bank account and active revenue accounts are required.",
                "Guided Deposit", wx.OK | wx.ICON_WARNING,
            )
            return
        dialog = GuidedDepositDialog(self, self.master_choices)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            lines, description, reference = dialog.values()
        except ValueError as error:
            wx.MessageBox(str(error), "Guided deposit not created",
                          wx.OK | wx.ICON_WARNING)
            return
        finally:
            dialog.Destroy()
        self.lines = lines
        self.description.SetValue(description)
        self.reference.SetValue(reference)
        self.transaction_type.SetSelection(1)
        self.refresh()

    def on_guided_release(self, event):
        if self.current_id is not None or self.lines:
            if wx.MessageBox(
                "Start a new restriction release and discard the current unsaved values?",
                "Restriction Release", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
            ) != wx.YES:
                return
            self.on_new()
        required = (
            "cash_accounts", "transfer_out_accounts", "transfer_in_accounts",
            "restricted_funds", "unrestricted_funds",
        )
        if not self.master_choices or any(not self.master_choices[name] for name in required):
            wx.MessageBox(
                "This guide requires a bank account, transfer accounts, and both "
                "restricted and unrestricted funds.",
                "Restriction Release", wx.OK | wx.ICON_WARNING,
            )
            return
        dialog = GuidedTransferDialog(self, self.master_choices, restriction_release=True)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            lines, description, reference = dialog.values()
        except ValueError as error:
            wx.MessageBox(str(error), "Restriction release not created",
                          wx.OK | wx.ICON_WARNING)
            return
        finally:
            dialog.Destroy()
        self.lines = lines
        self.description.SetValue(description)
        self.reference.SetValue(reference)
        self.transaction_type.SetSelection(3)
        self.refresh()

    def on_guided_opening(self, event):
        if self.current_id is not None or self.lines:
            if wx.MessageBox(
                "Start a new opening-balance transaction and discard the current unsaved values?",
                "Opening Balances", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
            ) != wx.YES:
                return
            self.on_new()
        if not self.master_choices or not self.master_choices["opening_accounts"]:
            wx.MessageBox("No active balance-sheet accounts are available.", "Opening Balances", wx.OK | wx.ICON_WARNING)
            return
        self.transaction_type.SetSelection(4)
        self.description.SetValue("Opening balances")
        wx.MessageBox(
            "Add each approved asset and liability balance by fund, then add the corresponding net-asset lines so total debits equal total credits. Save the draft before attaching the source balance report.",
            "Opening Balances", wx.OK | wx.ICON_INFORMATION,
        )
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
        self.debit_total.SetLabel(money(debit_total, True))
        self.credit_total.SetLabel(money(credit_total, True))
        self.difference_total.SetLabel(money(debit_total - credit_total, True))

    def transaction(self):
        type_codes = ("CASH_DISBURSEMENT", "CASH_RECEIPT", "JOURNAL", "RESTRICTION_RELEASE", "OPENING_BALANCE")
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
                self.current_id = transaction_id
                self.current_version = 1
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
        self.save.SetLabel("Update Draft")
        self.submit.Enable(self.can_mark_ready)
        self.delete.Enable(self.can_delete)
        self.attachments.Enable(self.attachment_service is not None)


def show_accounting_draft_entry(parent, connection, session, authorization,
                                test_mode=False, config=None):
    authorization.require("accounting.transactions.create", "create accounting drafts")
    if config is None:
        from churchmanager_mode import load_config
        config = load_config()
    attachment_service = AccountingAttachmentService(
        connection, session.user_id,
        AttachmentStore(load_attachment_policy(config, test_mode)),
    )
    dialog = AccountingDraftDialog(
        parent, AccountingDraftService(connection, session.user_id),
        can_edit_any=authorization.has_permission(
            "accounting.transactions.edit_any_draft"
        ),
        can_mark_ready=authorization.has_permission(
            "accounting.transactions.mark_ready"
        ),
        can_delete=authorization.has_permission(
            "accounting.transactions.delete_draft"
        ),
        attachment_service=attachment_service,
    )
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
