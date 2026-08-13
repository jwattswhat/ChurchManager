"""Interactive read-only trial balance."""
from datetime import date
from decimal import Decimal
import wx
import wx.adv
from ui_dimensions import DATE_PICKER_SIZE
from .trial_balance_service import TrialBalanceService
from .formatting import money

class TrialBalanceDialog(wx.Dialog):
    def __init__(self, parent, service, report_service=None):
        super().__init__(parent, title="Trial Balance", size=(900, 620))
        self.service = service
        self.organization = wx.Choice(self)
        for organization_id, name in service.organizations(): self.organization.Append(name, organization_id)
        if self.organization.GetCount(): self.organization.SetSelection(0)
        self.as_of = wx.adv.DatePickerCtrl(self, size=DATE_PICKER_SIZE)
        run = wx.Button(self, label="Run Trial Balance")
        run.Bind(wx.EVT_BUTTON, self.refresh)
        preview = wx.Button(self, label="Preview PDF")
        preview.Bind(wx.EVT_BUTTON, self.preview_pdf)
        preview.Enable(report_service is not None)
        customize = wx.Button(self, label="Customize Layout")
        customize.Bind(wx.EVT_BUTTON, self.customize_layout)
        can_design = (
            report_service is not None
            and report_service.authorization.has_permission("accounting.reports.design")
        )
        customize.Enable(can_design)
        self.report_service = report_service
        header = wx.BoxSizer(wx.HORIZONTAL)
        for label, control in (("Organization", self.organization), ("As of", self.as_of)):
            header.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            header.Add(control, 0, wx.RIGHT, 15)
        header.Add(run, 0, wx.RIGHT, 8)
        header.Add(preview, 0, wx.RIGHT, 8)
        header.Add(customize)
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        for index, (label, width) in enumerate((
            ("Code",75), ("Account",180), ("Type",90), ("Normal",70),
            ("Debits",85), ("Credits",85), ("Debit Balance",95), ("Credit Balance",95),
        )): self.list.InsertColumn(
            index, label,
            format=wx.LIST_FORMAT_RIGHT if index >= 4 else wx.LIST_FORMAT_LEFT,
            width=width,
        )
        self.totals = wx.StaticText(self, label="Debit balances $0.00    Credit balances $0.00    Difference $0.00")
        self.status = wx.StaticText(self, label="Choose an as-of date and run the report.")
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        footer = wx.BoxSizer(wx.HORIZONTAL); footer.Add(self.totals, 0, wx.ALIGN_CENTER_VERTICAL); footer.AddStretchSpacer(); footer.Add(close)
        root = wx.BoxSizer(wx.VERTICAL); root.Add(header, 0, wx.ALL | wx.EXPAND, 10)
        root.Add(self.list, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(self.status, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        root.Add(footer, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(root); self.refresh()
    def refresh(self, event=None):
        self.list.DeleteAllItems()
        if self.organization.GetSelection() == wx.NOT_FOUND: return
        value = self.as_of.GetValue(); as_of = date(value.GetYear(), value.GetMonth()+1, value.GetDay())
        rows = self.service.rows(self.organization.GetClientData(self.organization.GetSelection()), as_of)
        debit_balances = credit_balances = Decimal("0")
        for item in rows:
            row = self.list.InsertItem(self.list.GetItemCount(), str(item[0]))
            values = (item[1], item[2], item[3], *[money(value) for value in item[4:]])
            for column, text in enumerate(values, 1): self.list.SetItem(row, column, str(text))
            debit_balances += item[6]; credit_balances += item[7]
        self.totals.SetLabel("Debit balances {}    Credit balances {}    Difference {}".format(money(debit_balances,True),money(credit_balances,True),money(debit_balances-credit_balances,True)))
        if rows:
            self.status.SetLabel(
                "Trial balance completed through {}: {} account(s).".format(as_of, len(rows))
            )
        else:
            self.status.SetLabel(
                "Trial balance completed through {}. All posted activity nets to zero, or no transactions have been posted.".format(as_of)
            )
    def preview_pdf(self, event=None):
        if self.report_service is None or self.organization.GetSelection() == wx.NOT_FOUND:
            return
        value = self.as_of.GetValue()
        as_of = date(value.GetYear(), value.GetMonth()+1, value.GetDay())
        try:
            self.report_service.run_trial_balance(
                self.organization.GetClientData(self.organization.GetSelection()), as_of,
            )
            self.status.SetLabel("The Trial Balance PDF opened in your default viewer.")
        except Exception as error:
            wx.MessageBox(str(error), "Trial Balance Report", wx.OK | wx.ICON_ERROR, self)
    def customize_layout(self, event=None):
        if self.report_service is None or self.organization.GetSelection() == wx.NOT_FOUND:
            return
        value = self.as_of.GetValue()
        as_of = date(value.GetYear(), value.GetMonth()+1, value.GetDay())
        try:
            self.report_service.design_trial_balance(
                self.organization.GetClientData(self.organization.GetSelection()), as_of,
            )
        except Exception as error:
            wx.MessageBox(str(error), "Trial Balance Report Designer", wx.OK | wx.ICON_ERROR, self)

def show_trial_balance(parent, connection, session, authorization):
    authorization.require("accounting.reports.run", "run accounting reports")
    from .reporting import AccountingVisualReportService
    dialog = TrialBalanceDialog(
        parent, TrialBalanceService(connection),
        AccountingVisualReportService(connection, authorization, session),
    )
    try: dialog.ShowModal()
    finally: dialog.Destroy()
