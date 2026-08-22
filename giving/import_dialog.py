"""Visual mapping, validation, and confirmed draft import for contribution CSV files."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import wx
import wx.adv

from giving.import_parser import (
    ContributionCsvMapping, ContributionImportError, csv_headers, parse_csv,
)
from giving.import_preview import ContributionImportPreviewService
from giving.import_service import ContributionImportService


OPTIONAL_FIELDS = (
    ("Envelope", "envelope_column"), ("Contributor", "contributor_column"),
    ("Method", "method_column"), ("Reference", "reference_column"),
    ("Purpose", "purpose_column"), ("Description", "description_column"),
)


def _guess(headers, *names):
    normalized = {value.casefold().replace(" ", "").replace("_", ""): value for value in headers}
    for name in names:
        match = normalized.get(name.casefold().replace(" ", "").replace("_", ""))
        if match: return match
    return ""


class ContributionImportPreviewDialog(wx.Dialog):
    """Map one provider CSV and display validation results without saving it."""

    def __init__(self, parent, batch_service, test_mode=False):
        super().__init__(parent, title="Preview Contribution Import", size=(1080, 720),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.batch_service = batch_service; self.connection = batch_service.connection
        self.church_id = int(batch_service.church_id()); self.test_mode = bool(test_mode)
        self.organizations = tuple(batch_service.organizations()); self.content = None
        self.headers = (); self.preview_rows = (); self.banks = (); self.batch_id = None
        self.source_path = None
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        intro = wx.StaticText(panel, label=(
            "Choose a CSV and map its columns. Preview performs no database changes. "
            "Every row must be Ready before import can proceed."
        )); intro.SetForegroundColour(wx.Colour(0, 80, 170)); intro.Wrap(1030)
        outer.Add(intro, 0, wx.EXPAND | wx.ALL, 12)

        source_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Source and destination")
        source_grid = wx.FlexGridSizer(0, 3, 8, 8); source_grid.AddGrowableCol(1, 1)
        source_grid.Add(wx.StaticText(panel, label="CSV file"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.path = wx.TextCtrl(panel, style=wx.TE_READONLY)
        source_grid.Add(self.path, 1, wx.EXPAND)
        choose = wx.Button(panel, label="Choose CSV..."); choose.Bind(wx.EVT_BUTTON, self.on_choose)
        source_grid.Add(choose)
        source_grid.Add(wx.StaticText(panel, label="Organization"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.organization = wx.Choice(panel, choices=[str(row[1]) for row in self.organizations])
        if self.organizations: self.organization.SetSelection(0)
        self.organization.Bind(wx.EVT_CHOICE, self.on_organization)
        source_grid.Add(self.organization, 1, wx.EXPAND); source_grid.AddSpacer(1)
        source_grid.Add(wx.StaticText(panel, label="Batch description"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.description = wx.TextCtrl(panel); source_grid.Add(self.description, 1, wx.EXPAND); source_grid.AddSpacer(1)
        source_grid.Add(wx.StaticText(panel, label="Deposit date"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.deposit_date = wx.adv.DatePickerCtrl(panel); source_grid.Add(self.deposit_date, 0); source_grid.AddSpacer(1)
        source_grid.Add(wx.StaticText(panel, label="Receiving bank account"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.bank = wx.Choice(panel); source_grid.Add(self.bank, 1, wx.EXPAND); source_grid.AddSpacer(1)
        source_box.Add(source_grid, 1, wx.EXPAND | wx.ALL, 10); outer.Add(source_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        mapping_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "CSV column mapping")
        mapping_grid = wx.FlexGridSizer(3, 6, 6, 8)
        self.controls = {}
        for label, key in (("Date *", "date_column"), ("Amount *", "amount_column"), *OPTIONAL_FIELDS):
            mapping_grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            control = wx.Choice(panel, choices=["Not provided"])
            control.SetSelection(0); self.controls[key] = control
            mapping_grid.Add(control, 0, wx.EXPAND)
        mapping_grid.Add(wx.StaticText(panel, label="Date format"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.date_format = wx.Choice(panel, choices=["MM/DD/YYYY", "YYYY-MM-DD", "M/D/YYYY"])
        self.date_format.SetSelection(0); mapping_grid.Add(self.date_format, 0, wx.EXPAND)
        mapping_box.Add(mapping_grid, 0, wx.EXPAND | wx.ALL, 10)
        outer.Add(mapping_box, 0, wx.EXPAND | wx.ALL, 12)

        self.summary = wx.StaticText(panel, label="Choose a CSV to begin.")
        outer.Add(self.summary, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Row",55),("Date",95),("Contributor / Envelope",250),
                                                ("Amount",100),("Purpose",180),("Status",310))):
            self.list.InsertColumn(index, label, width=width)
        amount_column = self.list.GetColumn(3); amount_column.SetAlign(wx.LIST_FORMAT_RIGHT)
        self.list.SetColumn(3, amount_column); outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        preview = wx.Button(panel, label="Preview Rows"); preview.Bind(wx.EVT_BUTTON, self.on_preview)
        buttons.Add(preview)
        self.import_button = wx.Button(panel, label="Import Ready Rows to Draft Batch")
        self.import_button.Bind(wx.EVT_BUTTON, self.on_import); self.import_button.Enable(False)
        buttons.Add(self.import_button, 0, wx.LEFT, 8); buttons.AddStretchSpacer()
        close = wx.Button(panel, wx.ID_CLOSE); close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        buttons.Add(close); outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12)
        panel.SetSizer(outer); self.on_organization()

    def on_organization(self, _event=None):
        selection = self.organization.GetSelection(); self.bank.Clear(); self.banks = ()
        if selection < 0: return
        self.banks = tuple(self.batch_service.bank_accounts(self.organizations[selection][0]))
        self.bank.Set([str(row[1]) for row in self.banks])
        if self.banks: self.bank.SetSelection(0)
        self.preview_rows = (); self.import_button.Enable(False)

    def on_choose(self, _event=None):
        picker = wx.FileDialog(self, "Choose contribution CSV", wildcard="CSV files (*.csv)|*.csv",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        try:
            if picker.ShowModal() != wx.ID_OK: return
            selected = Path(picker.GetPath()); content = selected.read_bytes()
            headers = csv_headers(content)
            self.content = content; self.headers = headers; self.path.SetValue(str(selected))
            self.source_path = selected; self.description.SetValue(f"Imported contributions - {selected.stem}"[:255])
            self._load_headings(headers); self.preview_rows = (); self.list.DeleteAllItems()
            self.summary.SetLabel(f"{len(headers)} column(s) found. Confirm the mapping, then preview rows.")
        except (OSError, ContributionImportError) as error:
            wx.MessageBox(str(error), "Unable to Read Contribution CSV", wx.OK | wx.ICON_ERROR, self)
        finally:
            picker.Destroy()

    def _load_headings(self, headers):
        guesses = {
            "date_column": _guess(headers, "Date", "Gift Date", "Received Date", "Transaction Date"),
            "amount_column": _guess(headers, "Amount", "Gift Amount", "Gross Amount"),
            "envelope_column": _guess(headers, "Envelope", "Envelope Number", "Envelope #"),
            "contributor_column": _guess(headers, "Contributor", "Contributor Name", "Donor", "Name"),
            "method_column": _guess(headers, "Method", "Payment Method", "Gift Method"),
            "reference_column": _guess(headers, "Reference", "Transaction ID", "External ID", "Check Number"),
            "purpose_column": _guess(headers, "Purpose", "Fund", "Designation"),
            "description_column": _guess(headers, "Description", "Memo", "Source Description"),
        }
        choices = ["Not provided", *headers]
        for key, control in self.controls.items():
            control.Set(choices); guess = guesses[key]
            control.SetSelection(choices.index(guess) if guess in choices else 0)

    def _selected(self, key, required=False):
        control = self.controls[key]; value = control.GetStringSelection()
        if value == "Not provided":
            if required: raise ContributionImportError(f"Map the {key.split('_')[0]} column.")
            return None
        return value

    def mapping(self):
        formats = ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%Y")
        values = {key: self._selected(key) for _label, key in OPTIONAL_FIELDS}
        return ContributionCsvMapping(
            date_column=self._selected("date_column", True),
            amount_column=self._selected("amount_column", True),
            date_format=formats[self.date_format.GetSelection()], **values,
        )

    def on_preview(self, _event=None):
        try:
            if self.content is None: raise ContributionImportError("Choose a contribution CSV first.")
            if self.organization.GetSelection() < 0:
                raise ContributionImportError("Select an accounting organization.")
            parsed = parse_csv(self.content, self.mapping())
            organization_id = self.organizations[self.organization.GetSelection()][0]
            self.preview_rows = ContributionImportPreviewService(
                self.connection, self.church_id, organization_id).preview(parsed)
            self._display_preview()
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Preview Contributions", wx.OK | wx.ICON_ERROR, self)

    def _display_preview(self):
        self.list.DeleteAllItems(); ready = 0; total = 0
        for item in self.preview_rows:
            source = item.source; total += source.amount; ready += int(item.ready)
            identity = source.contributor or (f"Envelope {source.envelope_number}" if source.envelope_number else "")
            index = self.list.InsertItem(self.list.GetItemCount(), str(source.row_number))
            values = (source.received_date, identity, f"${source.amount:,.2f}", source.purpose,
                      "Ready" if item.ready else "; ".join(item.issues))
            for column, value in enumerate(values, 1): self.list.SetItem(index, column, str(value))
            if not item.ready: self.list.SetItemTextColour(index, wx.RED)
        self.summary.SetLabel(
            f"{len(self.preview_rows)} row(s) · {ready} Ready · "
            f"{len(self.preview_rows)-ready} need attention · Total ${total:,.2f}"
        )
        self.import_button.Enable(bool(self.preview_rows) and all(item.ready for item in self.preview_rows))

    def on_import(self, _event=None):
        if not self.preview_rows or not all(item.ready for item in self.preview_rows): return
        if self.bank.GetSelection() < 0:
            wx.MessageBox("Select the bank account receiving this deposit.", "Contribution Import",
                          wx.OK | wx.ICON_WARNING, self); return
        if wx.MessageBox(
                f"Import {len(self.preview_rows)} contribution row(s) into one new Draft batch?\n\n"
                "The original CSV will be copied into protected ChurchManager storage.",
                "Confirm Contribution Import", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION, self) != wx.YES: return
        try:
            organization_id = self.organizations[self.organization.GetSelection()][0]
            bank_id = self.banks[self.bank.GetSelection()][0]
            selected_date = self.deposit_date.GetValue()
            deposit_date = date(
                selected_date.GetYear(), selected_date.GetMonth() + 1, selected_date.GetDay())
            self.batch_id = ContributionImportService(
                self.connection, self.batch_service.user_id, self.test_mode).import_draft(
                    source_path=self.source_path, content=self.content, mapping=self.mapping(),
                    preview_rows=self.preview_rows, church_id=self.church_id,
                    organization_id=organization_id, bank_account_id=bank_id,
                    deposit_date=deposit_date, description=self.description.GetValue())
            wx.MessageBox(f"Draft contribution batch {self.batch_id} was created.",
                          "Contribution Import Complete", wx.OK | wx.ICON_INFORMATION, self)
            self.EndModal(wx.ID_OK)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Import Contributions", wx.OK | wx.ICON_ERROR, self)


def show_contribution_import_preview(parent, batch_service, test_mode=False):
    """Open contribution CSV mapping and return the created Draft batch ID."""
    dialog = ContributionImportPreviewDialog(parent, batch_service, test_mode)
    try:
        return dialog.batch_id if dialog.ShowModal() == wx.ID_OK else None
    finally: dialog.Destroy()
