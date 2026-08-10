"""Protected desktop workflow for creating accounting starter data."""

from __future__ import annotations

from datetime import date

import wx

from .setup_service import AccountingSetupService, FundClassification
from .starter_data import STARTER_FUNDS


CLASSIFICATION_CHOICES = (
    ("Donor-restricted — purpose", FundClassification("WITH_DONOR_RESTRICTIONS", "PURPOSE")),
    ("Donor-restricted — time", FundClassification("WITH_DONOR_RESTRICTIONS", "TIME")),
    ("Donor-restricted — purpose and time", FundClassification("WITH_DONOR_RESTRICTIONS", "PURPOSE_AND_TIME")),
    ("Board-designated", FundClassification("WITHOUT_DONOR_RESTRICTIONS", "NONE", True)),
    ("Unrestricted", FundClassification("WITHOUT_DONOR_RESTRICTIONS", "NONE")),
)


class StarterSetupDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Create Starter Accounting Setup")
        grid = wx.FlexGridSizer(2, 2, 8, 8)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Organization legal name"))
        self.legal_name = wx.TextCtrl(self, size=(360, -1))
        grid.Add(self.legal_name, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="First fiscal year"))
        self.fiscal_year = wx.SpinCtrl(
            self, min=2000, max=2200, initial=date.today().year
        )
        grid.Add(self.fiscal_year)
        self.classifications = {}
        labels = [choice[0] for choice in CLASSIFICATION_CHOICES]
        for fund in STARTER_FUNDS:
            if not fund.requires_classification:
                continue
            grid.Add(wx.StaticText(self, label=fund.name))
            choice = wx.Choice(self, choices=labels)
            choice.SetSelection(wx.NOT_FOUND)
            self.classifications[fund.code] = choice
            grid.Add(choice, 1, wx.EXPAND)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(
            wx.StaticText(
                self,
                label=(
                    "Classify every special-purpose fund. ChurchManager will not "
                    "infer donor restrictions from a fund name."
                ),
            ),
            0, wx.ALL, 12,
        )
        root.Add(grid, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)
        root.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizerAndFit(root)

    def values(self):
        classifications = {}
        for code, control in self.classifications.items():
            index = control.GetSelection()
            if index == wx.NOT_FOUND:
                raise ValueError("Every special-purpose fund must be classified.")
            classifications[code] = CLASSIFICATION_CHOICES[index][1]
        return self.legal_name.GetValue(), self.fiscal_year.GetValue(), classifications


class AccountingSetupDialog(wx.Dialog):
    def __init__(self, parent, service):
        super().__init__(parent, title="Accounting Setup", size=(850, 420))
        self.service = service
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Organization", 250), ("Basis", 120), ("Approval", 95),
            ("Attachment", 95), ("Accounts", 75), ("Funds", 65), ("Active", 65),
        )):
            self.list.InsertColumn(index, label, width=width)
        create = wx.Button(self, label="Create Starter Setup")
        create.Bind(wx.EVT_BUTTON, self.on_create)
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(create)
        buttons.AddStretchSpacer()
        buttons.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(self.list, 1, wx.ALL | wx.EXPAND, 10)
        root.Add(buttons, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(root)
        self.refresh()

    def refresh(self):
        self.list.DeleteAllItems()
        for organization in self.service.list_organizations():
            row = self.list.InsertItem(self.list.GetItemCount(), organization[1])
            values = (
                organization[2], "${:.2f}".format(organization[3]),
                "${:.2f}".format(organization[4]), str(organization[6]),
                str(organization[7]), "Yes" if organization[5] else "No",
            )
            for column, value in enumerate(values, start=1):
                self.list.SetItem(row, column, value)

    def on_create(self, event):
        dialog = StarterSetupDialog(self)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            legal_name, fiscal_year, classifications = dialog.values()
            self.service.create_starter_organization(
                legal_name, fiscal_year, classifications
            )
            self.refresh()
        except (ValueError, RuntimeError) as error:
            wx.MessageBox(str(error), "Accounting Setup", wx.OK | wx.ICON_ERROR)
        finally:
            dialog.Destroy()


def show_accounting_setup(parent, connection, session, authorization):
    authorization.require("accounting.master_data.manage", "manage accounting setup")
    dialog = AccountingSetupDialog(
        parent, AccountingSetupService(connection, session.user_id)
    )
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
