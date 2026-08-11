"""User-confirmed, non-posting CSV bank import staging."""

from decimal import Decimal
from pathlib import Path

import wx

from .bank_import import BankImportError, CsvMapping, csv_headers, parse_csv
from .bank_import_service import BankImportService
from .formatting import money


class BankImportDialog(wx.Dialog):
    def __init__(self, parent, service):
        super().__init__(parent, title="Bank File Import", size=(690, 520))
        self.service = service
        self.accounts = service.bank_accounts()

        self.account = wx.Choice(self)
        self.account.SetItems([str(row[1]) for row in self.accounts])
        if self.accounts:
            self.account.SetSelection(0)
        self.file = wx.FilePickerCtrl(
            self,
            wildcard="CSV files (*.csv)|*.csv|All files (*.*)|*.*",
            style=wx.FLP_OPEN | wx.FLP_FILE_MUST_EXIST,
        )
        self.date_column = wx.Choice(self)
        self.description_column = wx.Choice(self)
        self.amount_column = wx.Choice(self)
        self.debit_column = wx.Choice(self)
        self.credit_column = wx.Choice(self)
        self.reference_column = wx.Choice(self)
        self.external_id_column = wx.Choice(self)
        self.date_format = wx.TextCtrl(self, value="%m/%d/%Y")
        self.status = wx.StaticText(
            self,
            label="Choose a CSV file. Its column headings will appear below.",
        )

        grid = wx.FlexGridSizer(cols=2, hgap=10, vgap=8)
        grid.AddGrowableCol(1, 1)
        for label, control in (
            ("Bank account", self.account),
            ("CSV file", self.file),
            ("Date column", self.date_column),
            ("Description column", self.description_column),
            ("Single amount column", self.amount_column),
            ("Debit column", self.debit_column),
            ("Credit column", self.credit_column),
            ("Reference column", self.reference_column),
            ("External ID column", self.external_id_column),
            ("Date format", self.date_format),
        ):
            grid.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 1, wx.EXPAND)

        explanation = wx.StaticText(
            self,
            label=(
                "Map either one signed Amount column, or both Debit and Credit "
                "columns. Imported rows are staged for review and are never posted automatically."
            ),
        )
        explanation.Wrap(640)
        stage = wx.Button(self, label="Preview and Stage")
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        stage.Bind(wx.EVT_BUTTON, self.on_stage)
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        self.file.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_file_selected)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.AddStretchSpacer()
        buttons.Add(stage, 0, wx.RIGHT, 8)
        buttons.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(explanation, 0, wx.ALL | wx.EXPAND, 12)
        root.Add(grid, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 12)
        root.Add(self.status, 0, wx.ALL | wx.EXPAND, 12)
        root.AddStretchSpacer()
        root.Add(buttons, 0, wx.ALL | wx.EXPAND, 12)
        self.SetSizer(root)

    def on_file_selected(self, event=None):
        try:
            headings = csv_headers(Path(self.file.GetPath()).read_bytes())
        except (OSError, BankImportError) as error:
            wx.MessageBox(str(error), "Cannot read bank file", wx.OK | wx.ICON_WARNING)
            return
        required = [self.date_column, self.description_column]
        optional = [
            self.amount_column, self.debit_column, self.credit_column,
            self.reference_column, self.external_id_column,
        ]
        for control in required:
            control.SetItems(list(headings))
            control.SetSelection(0)
        for control in optional:
            control.SetItems([""] + list(headings))
            control.SetSelection(0)
        self.status.SetLabel(
            "Loaded {} column headings. Select the mappings, then preview.".format(
                len(headings)
            )
        )

    @staticmethod
    def _value(control):
        return control.GetStringSelection() or None

    def mapping(self):
        date_column = self._value(self.date_column)
        description_column = self._value(self.description_column)
        if not date_column or not description_column:
            raise BankImportError("Select the date and description columns.")
        amount = self._value(self.amount_column)
        debit = self._value(self.debit_column)
        credit = self._value(self.credit_column)
        if bool(amount) == bool(debit or credit):
            raise BankImportError(
                "Map either one Amount column or both Debit and Credit columns."
            )
        if not amount and not (debit and credit):
            raise BankImportError("Select both the Debit and Credit columns.")
        return CsvMapping(
            date_column=date_column,
            description_column=description_column,
            date_format=self.date_format.GetValue().strip() or "%m/%d/%Y",
            amount_column=amount,
            debit_column=debit,
            credit_column=credit,
            reference_column=self._value(self.reference_column),
            external_id_column=self._value(self.external_id_column),
        )

    def on_stage(self, event=None):
        account_index = self.account.GetSelection()
        if account_index == wx.NOT_FOUND:
            wx.MessageBox(
                "Configure and select an active bank account first.",
                "Bank account required", wx.OK | wx.ICON_WARNING,
            )
            return
        path = Path(self.file.GetPath())
        if not path.is_file():
            wx.MessageBox("Choose a CSV bank file.", "Bank file required", wx.OK | wx.ICON_WARNING)
            return
        try:
            mapping = self.mapping()
            rows = parse_csv(path.read_bytes(), mapping)
        except (OSError, BankImportError) as error:
            wx.MessageBox(str(error), "Bank file not staged", wx.OK | wx.ICON_WARNING)
            return
        total = sum((row.amount for row in rows), Decimal("0"))
        dates = [row.transaction_date for row in rows]
        message = (
            "Stage this bank file for review?\n\n"
            "Rows: {}\nDate range: {} through {}\nNet amount: {}\n\n"
            "No accounting transactions will be created or posted."
        ).format(len(rows), min(dates), max(dates), money(total))
        if wx.MessageBox(
            message, "Confirm Bank File Staging", wx.YES_NO | wx.ICON_QUESTION
        ) != wx.YES:
            return
        try:
            batch_id, row_count = self.service.stage_csv(
                self.accounts[account_index][0], path, mapping
            )
        except (OSError, ValueError) as error:
            wx.MessageBox(str(error), "Bank file not staged", wx.OK | wx.ICON_WARNING)
            return
        self.status.SetLabel(
            "Staged batch {} with {} rows. No transactions were posted.".format(
                batch_id, row_count
            )
        )
        wx.MessageBox(self.status.GetLabel(), "Bank File Staged", wx.OK | wx.ICON_INFORMATION)


def show_bank_import(parent, connection, session, authorization):
    authorization.require(
        "accounting.reconciliation.manage", "import and reconcile bank activity"
    )
    dialog = BankImportDialog(
        parent, BankImportService(connection, session.user_id)
    )
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
