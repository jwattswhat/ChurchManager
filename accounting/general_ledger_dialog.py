"""Filterable, read-only general-ledger report."""

from datetime import date

import wx
import wx.adv

from ui_dimensions import DATE_PICKER_SIZE

from .formatting import money
from .general_ledger_service import GeneralLedgerService


def _date(control):
    value = control.GetValue()
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


class GeneralLedgerDialog(wx.Dialog):
    def __init__(self, parent, service, report_service=None):
        super().__init__(parent, title="General Ledger", size=(1180, 680))
        self.service = service
        self.report_service = report_service
        self.organization = wx.Choice(self)
        self.account = wx.Choice(self)
        self.fund = wx.Choice(self)
        for item_id, label in service.organizations():
            self.organization.Append(str(label), item_id)
        if self.organization.GetCount():
            self.organization.SetSelection(0)
        today = date.today()
        self.date_from = wx.adv.DatePickerCtrl(self, size=DATE_PICKER_SIZE)
        self.date_to = wx.adv.DatePickerCtrl(self, size=DATE_PICKER_SIZE)
        self.date_from.SetValue(wx.DateTime.FromDMY(1, 0, today.year))
        self.organization.Bind(wx.EVT_CHOICE, self.on_organization)
        filters = wx.FlexGridSizer(cols=4, hgap=8, vgap=8)
        filters.AddGrowableCol(1, 1); filters.AddGrowableCol(3, 1)
        for label, control in (("Organization", self.organization), ("Account", self.account),
                               ("Fund", self.fund), ("From", self.date_from),
                               ("Through", self.date_to)):
            filters.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            filters.Add(control, 1, wx.EXPAND)
        filters.AddSpacer(1); filters.AddSpacer(1)
        run = wx.Button(self, label="Run General Ledger")
        run.Bind(wx.EVT_BUTTON, self.on_run)
        self.heading = wx.StaticText(self, label="Select an account and run the report.")
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        columns = (("Date", 90), ("Number", 70), ("Type", 105),
                   ("Transaction", 190), ("Reference", 100), ("Fund", 140),
                   ("Line description", 155), ("Debit", 90), ("Credit", 90),
                   ("Balance", 100))
        for index, (label, width) in enumerate(columns):
            self.list.InsertColumn(index, label, width=width)
        for index in (7, 8, 9):
            column = self.list.GetColumn(index)
            column.SetAlign(wx.LIST_FORMAT_RIGHT)
            self.list.SetColumn(index, column)
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        preview=wx.Button(self,label="Preview PDF");preview.Bind(wx.EVT_BUTTON,self.preview_pdf);preview.Enable(report_service is not None)
        customize=wx.Button(self,label="Customize Layout");customize.Bind(wx.EVT_BUTTON,self.customize_layout)
        customize.Enable(report_service is not None and report_service.authorization.has_permission("accounting.reports.design"))
        top = wx.BoxSizer(wx.VERTICAL)
        top.Add(filters, 0, wx.ALL | wx.EXPAND, 10)
        top.Add(run, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT, 10)
        top.Add(self.heading, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        top.Add(self.list, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        actions=wx.BoxSizer(wx.HORIZONTAL);actions.AddStretchSpacer();actions.Add(preview,0,wx.RIGHT,8);actions.Add(customize,0,wx.RIGHT,8);actions.Add(close)
        top.Add(actions, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(top)
        self.on_organization()

    def on_organization(self, event=None):
        self.account.Clear(); self.fund.Clear()
        index = self.organization.GetSelection()
        if index == wx.NOT_FOUND:
            return
        accounts, funds = self.service.choices(self.organization.GetClientData(index))
        for item_id, label in accounts:
            self.account.Append(str(label), item_id)
        self.fund.Append("All funds", None)
        for item_id, label in funds:
            self.fund.Append(str(label), item_id)
        if self.account.GetCount(): self.account.SetSelection(0)
        self.fund.SetSelection(0)

    def on_run(self, event):
        org_index = self.organization.GetSelection()
        account_index = self.account.GetSelection()
        if org_index == wx.NOT_FOUND or account_index == wx.NOT_FOUND:
            wx.MessageBox("Select an organization and account.", "General Ledger")
            return
        fund_index = self.fund.GetSelection()
        fund_id = None if fund_index == wx.NOT_FOUND else self.fund.GetClientData(fund_index)
        try:
            result = self.service.report(
                self.organization.GetClientData(org_index),
                self.account.GetClientData(account_index),
                _date(self.date_from), _date(self.date_to), fund_id,
            )
        except ValueError as error:
            wx.MessageBox(str(error), "General Ledger", wx.OK | wx.ICON_WARNING)
            return
        self.list.DeleteAllItems()
        self.heading.SetLabel(
            "{}    Opening balance: {}    {} transaction line(s)".format(
                result["account"], money(result["opening_balance"], True),
                len(result["rows"]),
            )
        )
        for item in result["rows"]:
            row = self.list.InsertItem(self.list.GetItemCount(), str(item[0]))
            values = (item[1], item[2], item[3] or "", item[4] or "", item[5],
                      item[6] or "", money(item[7]), money(item[8]), money(item[9]))
            for column, value in enumerate(values, 1):
                self.list.SetItem(row, column, str(value))

    def _selection(self):
        oi=self.organization.GetSelection();ai=self.account.GetSelection();fi=self.fund.GetSelection()
        if oi==wx.NOT_FOUND or ai==wx.NOT_FOUND:raise ValueError("Select an organization and account.")
        fund_id=None if fi==wx.NOT_FOUND else self.fund.GetClientData(fi)
        return (self.organization.GetClientData(oi),self.account.GetClientData(ai),
                _date(self.date_from),_date(self.date_to),fund_id)

    def preview_pdf(self,event=None):
        try:self.report_service.run_general_ledger(*self._selection())
        except Exception as error:wx.MessageBox(str(error),"General Ledger Report",wx.OK|wx.ICON_ERROR,self)

    def customize_layout(self,event=None):
        try:self.report_service.design_general_ledger(*self._selection())
        except Exception as error:wx.MessageBox(str(error),"General Ledger Designer",wx.OK|wx.ICON_ERROR,self)


def show_general_ledger(parent, connection, session, authorization):
    authorization.require("accounting.reports.run", "run the general ledger")
    from .reporting import AccountingVisualReportService
    dialog = GeneralLedgerDialog(parent, GeneralLedgerService(connection),AccountingVisualReportService(connection,authorization,session))
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
