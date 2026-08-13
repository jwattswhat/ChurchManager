"""Read-only, filterable accounting audit history."""

from datetime import date

import wx
import wx.adv

from ui_dimensions import DATE_PICKER_SIZE

from .audit_service import AccountingAuditService


def _date_value(control):
    value = control.GetValue()
    if not value.IsValid():
        return None
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


class AccountingAuditDialog(wx.Dialog):
    def __init__(self, parent, service, report_service=None):
        super().__init__(parent, title="Accounting Audit History", size=(1100, 680))
        self.service, self.report_service, self.rows, self.organization_ids = service, report_service, [], []
        self.organization = wx.Choice(self)
        self.organization.Append("All organizations")
        self.organization_ids.append(None)
        for organization_id, name in service.organizations():
            self.organization.Append(str(name))
            self.organization_ids.append(organization_id)
        self.organization.SetSelection(0)
        self.user = wx.TextCtrl(self, size=(130, -1))
        self.action = wx.TextCtrl(self, size=(130, -1))
        self.entity = wx.TextCtrl(self, size=(130, -1))
        self.date_from = wx.adv.DatePickerCtrl(
            self, size=DATE_PICKER_SIZE, style=wx.adv.DP_ALLOWNONE
        )
        self.date_to = wx.adv.DatePickerCtrl(
            self, size=DATE_PICKER_SIZE, style=wx.adv.DP_ALLOWNONE
        )
        self.date_from.SetValue(wx.DateTime())
        self.date_to.SetValue(wx.DateTime())
        filters = wx.FlexGridSizer(cols=6, hgap=8, vgap=8)
        filters.AddGrowableCol(1, 1)
        filters.AddGrowableCol(3, 1)
        for label, control in (("Organization", self.organization), ("User", self.user),
                               ("Action", self.action), ("Entity", self.entity),
                               ("From", self.date_from), ("Through", self.date_to)):
            filters.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            filters.Add(control, 1, wx.EXPAND)
        run = wx.Button(self, label="Apply Filters")
        run.Bind(wx.EVT_BUTTON, self.refresh)
        filter_area = wx.BoxSizer(wx.VERTICAL)
        filter_area.Add(filters, 0, wx.EXPAND)
        filter_area.Add(run, 0, wx.TOP | wx.ALIGN_RIGHT, 8)

        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Date and time", 145), ("Organization", 155),
                ("User", 130), ("Action", 170), ("Entity", 120), ("ID", 80),
                ("Reason", 260))):
            self.list.InsertColumn(index, label, width=width)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)
        self.details = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        close = wx.Button(self, wx.ID_CLOSE, "Close")
        pdf=wx.Button(self,label="Preview Confidential PDF");pdf.Bind(wx.EVT_BUTTON,self.on_pdf);pdf.Enable(report_service is not None)
        close.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE))
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(filter_area, 0, wx.ALL | wx.EXPAND, 10)
        root.Add(self.list, 2, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        root.Add(wx.StaticText(self, label="Selected event details (read only)"), 0, wx.ALL, 10)
        root.Add(self.details, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        actions=wx.BoxSizer(wx.HORIZONTAL);actions.AddStretchSpacer();actions.Add(pdf,0,wx.RIGHT,8);actions.Add(close)
        root.Add(actions, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(root)
        self.refresh()

    def refresh(self, event=None):
        selection = self.organization.GetSelection()
        organization_id = self.organization_ids[selection] if selection != wx.NOT_FOUND else None
        try:
            self.rows = self.service.events(
                organization_id, self.user.GetValue(), self.action.GetValue(),
                self.entity.GetValue(), _date_value(self.date_from), _date_value(self.date_to),
            )
        except ValueError as error:
            wx.MessageBox(str(error), "Audit History", wx.OK | wx.ICON_WARNING)
            return
        self.list.DeleteAllItems(); self.details.Clear()
        for item in self.rows:
            row = self.list.InsertItem(self.list.GetItemCount(), str(item[1]))
            values = (item[2], item[3], item[4], item[5], item[6], item[7] or "")
            for column, value in enumerate(values, 1):
                self.list.SetItem(row, column, str(value))

    def on_select(self, event):
        item = self.rows[event.GetIndex()]
        self.details.SetValue(
            "Reason:\n{}\n\nBefore:\n{}\n\nAfter:\n{}".format(
                item[7] or "", item[8] or "", item[9] or ""
            )
        )

    def on_pdf(self,event=None):
        selection=self.organization.GetSelection();organization_id=self.organization_ids[selection] if selection!=wx.NOT_FOUND else None
        try:self.report_service.run_audit(organization_id,self.user.GetValue(),self.action.GetValue(),self.entity.GetValue(),_date_value(self.date_from),_date_value(self.date_to))
        except Exception as error:wx.MessageBox(str(error),"Accounting Audit Report",wx.OK|wx.ICON_ERROR,self)


def show_accounting_audit(parent, connection, session, authorization):
    authorization.require("accounting.audit.view", "view accounting audit history")
    from .reporting import AccountingVisualReportService
    dialog = AccountingAuditDialog(parent, AccountingAuditService(connection),AccountingVisualReportService(connection,authorization,session))
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
