"""Statement of functional expenses by natural account and ministry function."""
from datetime import date
import wx
import wx.adv

from .formatting import money
from .functional_expense_service import FunctionalExpenseService


def _date(control):
    value = control.GetValue()
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


class FunctionalExpenseDialog(wx.Dialog):
    def __init__(self, parent, service, report_service=None):
        super().__init__(parent, title="Functional Expense Report", size=(1050, 650))
        self.service = service
        self.report_service = report_service
        self.organization = wx.Choice(self)
        for key, name in service.organizations():
            self.organization.Append(name, key)
        if self.organization.GetCount():
            self.organization.SetSelection(0)
        self.start = wx.adv.DatePickerCtrl(self)
        self.end = wx.adv.DatePickerCtrl(self)
        run = wx.Button(self, label="Run Report")
        run.Bind(wx.EVT_BUTTON, self.refresh)
        header = wx.BoxSizer(wx.HORIZONTAL)
        for label, control in (("Organization", self.organization), ("From", self.start), ("Through", self.end)):
            header.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            header.Add(control, 0, wx.RIGHT, 12)
        header.Add(run)
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.status = wx.StaticText(self, label="")
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        footer = wx.BoxSizer(wx.HORIZONTAL)
        footer.Add(self.status, 0, wx.ALIGN_CENTER_VERTICAL)
        footer.AddStretchSpacer()
        preview=wx.Button(self,label="Preview PDF");preview.Bind(wx.EVT_BUTTON,self.preview_pdf);preview.Enable(report_service is not None)
        customize=wx.Button(self,label="Customize Layout");customize.Bind(wx.EVT_BUTTON,self.customize_layout)
        customize.Enable(report_service is not None and report_service.authorization.has_permission("accounting.reports.design"))
        footer.Add(preview,0,wx.RIGHT,8);footer.Add(customize,0,wx.RIGHT,8);footer.Add(close)
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(header, 0, wx.ALL | wx.EXPAND, 10)
        root.Add(self.list, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(footer, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(root)

    def refresh(self, event=None):
        if self.organization.GetSelection() == wx.NOT_FOUND:
            return
        try:
            report = self.service.report(self.organization.GetClientData(self.organization.GetSelection()),
                                         _date(self.start), _date(self.end))
        except ValueError as error:
            wx.MessageBox(str(error), "Report not run", wx.OK | wx.ICON_WARNING)
            return
        self.list.ClearAll()
        self.list.InsertColumn(0, "Code", width=75)
        self.list.InsertColumn(1, "Expense account", width=230)
        for index, (_, name) in enumerate(report["functions"], 2):
            self.list.InsertColumn(index, name, format=wx.LIST_FORMAT_RIGHT, width=120)
        total_column = 2 + len(report["functions"])
        self.list.InsertColumn(total_column, "Total", format=wx.LIST_FORMAT_RIGHT, width=120)
        for code, name, values, total in report["rows"]:
            row = self.list.InsertItem(self.list.GetItemCount(), str(code))
            self.list.SetItem(row, 1, str(name))
            for column, amount in enumerate(values, 2):
                self.list.SetItem(row, column, money(amount))
            self.list.SetItem(row, total_column, money(total))
        row = self.list.InsertItem(self.list.GetItemCount(), "")
        self.list.SetItem(row, 1, "Total expenses")
        for column, amount in enumerate(report["totals"], 2):
            self.list.SetItem(row, column, money(amount))
        self.list.SetItem(row, total_column, money(report["grand_total"]))
        self.status.SetLabel("Total expenses: {}".format(money(report["grand_total"], True)))

    def _selection(self):
        return (self.organization.GetClientData(self.organization.GetSelection()),_date(self.start),_date(self.end))

    def preview_pdf(self,event=None):
        try:self.report_service.run_functional_expenses(*self._selection())
        except Exception as error:wx.MessageBox(str(error),"Functional Expense Report",wx.OK|wx.ICON_ERROR,self)

    def customize_layout(self,event=None):
        try:self.report_service.design_functional_expenses(*self._selection())
        except Exception as error:wx.MessageBox(str(error),"Functional Expense Report Designer",wx.OK|wx.ICON_ERROR,self)


def show_functional_expenses(parent, connection, session, authorization):
    authorization.require("accounting.reports.run", "run accounting reports")
    from .reporting import AccountingVisualReportService
    dialog = FunctionalExpenseDialog(parent, FunctionalExpenseService(connection),AccountingVisualReportService(connection,authorization,session))
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
