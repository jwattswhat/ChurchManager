"""Permission-separated operational Giving report screens."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import wx
import wx.adv

from giving.report_service import GivingReportService
from giving.reporting import GivingVisualReportService


def _python_date(control):
    value = control.GetValue()
    return value.FormatISODate()


def _set_date(control, value):
    control.SetValue(wx.DateTime.FromDMY(value.day, value.month - 1, value.year))


def _money(value):
    return "" if value is None else f"${Decimal(value):,.2f}"


def _run_time():
    return datetime.now().strftime("%I:%M:%S %p").lstrip("0")


class GivingReportsDialog(wx.Dialog):
    """Show donor-free controls and separately authorized donor history."""

    def __init__(self, parent, connection, authorization, session):
        super().__init__(parent, title="Giving Reports", size=(1120, 700),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = GivingReportService(connection)
        self.authorization = authorization
        self.report_service = GivingVisualReportService(connection, authorization, session)
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        notice = wx.StaticText(
            panel,
            label="Giving reports are confidential. Summary reports never display donor identity.",
        )
        notice.SetForegroundColour(wx.Colour(0, 75, 150))
        outer.Add(notice, 0, wx.ALL, 12)
        self.notebook = wx.Notebook(panel)
        if authorization.has_permission("giving.reports.summary"):
            self._build_summary_tab()
        if authorization.has_permission("giving.history.view"):
            self._build_history_tab()
        if self.notebook.GetPageCount() == 0:
            raise PermissionError("You do not have permission to run Giving reports.")
        outer.Add(self.notebook, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        close = wx.Button(panel, wx.ID_CLOSE)
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer(); buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12); panel.SetSizer(outer)

    def _date_controls(self, parent):
        start, end = self.service.date_bounds()
        start_control = wx.adv.DatePickerCtrl(parent)
        end_control = wx.adv.DatePickerCtrl(parent)
        _set_date(start_control, start); _set_date(end_control, end)
        return start_control, end_control

    def _build_summary_tab(self):
        panel = wx.Panel(self.notebook); root = wx.BoxSizer(wx.VERTICAL)
        self.summary_start, self.summary_end = self._date_controls(panel)
        self.summary_run = wx.Button(panel, label="Refresh Batch Summary")
        self.summary_run.Bind(wx.EVT_BUTTON, self.on_summary)
        preview = wx.Button(panel, label="Preview PDF")
        preview.Bind(wx.EVT_BUTTON, self.on_summary_pdf)
        filters = wx.BoxSizer(wx.HORIZONTAL)
        for label, control in (("From", self.summary_start), ("Through", self.summary_end)):
            filters.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            filters.Add(control, 0, wx.RIGHT, 12)
        filters.Add(self.summary_run, 0, wx.RIGHT, 8)
        filters.Add(preview); root.Add(filters, 0, wx.ALL, 10)
        self.summary_list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        columns = (("Date",95),("Description",230),("Organization",200),("Status",80),
                   ("Control",100),("Entered",100),("Difference",100),("Accounting",100))
        for index, (label, width) in enumerate(columns):
            self.summary_list.InsertColumn(index, label, width=width)
        root.Add(self.summary_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        self.summary_total = wx.StaticText(panel, label="")
        self.summary_total.SetForegroundColour(wx.Colour(0, 75, 150))
        self.summary_total.SetFont(self.summary_total.GetFont().Bold())
        root.Add(self.summary_total, 0, wx.ALL, 10); panel.SetSizer(root)
        self.notebook.AddPage(panel, "Batch Control Summary"); self.on_summary()

    def _build_history_tab(self):
        panel = wx.Panel(self.notebook); root = wx.BoxSizer(wx.VERTICAL)
        self.contributors = self.service.contributors()
        self.contributor = wx.Choice(panel, choices=[row[1] for row in self.contributors])
        if self.contributors: self.contributor.SetSelection(0)
        self.history_start, self.history_end = self._date_controls(panel)
        self.history_run = wx.Button(panel, label="Refresh Contributor History")
        self.history_run.Bind(wx.EVT_BUTTON, self.on_history)
        filters = wx.BoxSizer(wx.HORIZONTAL)
        filters.Add(wx.StaticText(panel, label="Contributor"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        filters.Add(self.contributor, 1, wx.RIGHT, 12)
        for label, control in (("From", self.history_start), ("Through", self.history_end)):
            filters.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            filters.Add(control, 0, wx.RIGHT, 12)
        filters.Add(self.history_run); root.Add(filters, 0, wx.ALL | wx.EXPAND, 10)
        self.history_list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        columns = (("Date",95),("Batch",210),("Method",90),("Reference",130),
                   ("Purpose",180),("Amount",100),("Status",75),("Statement",90))
        for index, (label, width) in enumerate(columns):
            self.history_list.InsertColumn(index, label, width=width)
        root.Add(self.history_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        self.history_total = wx.StaticText(panel, label="")
        self.history_total.SetForegroundColour(wx.Colour(0, 75, 150))
        self.history_total.SetFont(self.history_total.GetFont().Bold())
        root.Add(self.history_total, 0, wx.ALL, 10); panel.SetSizer(root)
        self.notebook.AddPage(panel, "Contributor History"); self.on_history()

    def _dates(self, start, end):
        first, last = _python_date(start), _python_date(end)
        if first > last:
            raise ValueError("The Through date cannot be before the From date.")
        return first, last

    def on_summary(self, _event=None):
        self.summary_run.Disable()
        self.summary_run.SetLabel("Refreshing...")
        self.summary_run.Update()
        try:
            rows = self.service.batch_summary(*self._dates(self.summary_start, self.summary_end))
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Refresh Giving Summary", wx.OK | wx.ICON_ERROR, self)
            return
        finally:
            self.summary_run.SetLabel("Refresh Batch Summary")
            self.summary_run.Enable()
        self.summary_list.DeleteAllItems(); entered = Decimal("0.00")
        for index, row in enumerate(rows):
            self.summary_list.InsertItem(index, str(row[0]))
            values = (row[1], row[2], str(row[3]).title(), _money(row[4]), _money(row[5]),
                      _money(row[6]), "" if row[7] is None else str(row[7]))
            for column, value in enumerate(values, 1): self.summary_list.SetItem(index, column, value)
            entered += Decimal(row[5])
        if rows:
            result = f"{len(rows)} batch(es) · Entered total {_money(entered)}"
        else:
            result = "No contribution batches match the selected dates."
        self.summary_total.SetLabel(f"{result} - Refreshed {_run_time()}")
        self.summary_total.GetParent().Layout()
        self.summary_total.Refresh()

    def on_history(self, _event=None):
        selected = self.contributor.GetSelection()
        if selected < 0:
            self.history_total.SetLabel("Select a contributor before refreshing the history.")
            self.history_total.GetParent().Layout()
            return
        self.history_run.Disable()
        self.history_run.SetLabel("Refreshing...")
        self.history_run.Update()
        try:
            rows = self.service.contributor_history(
                self.contributors[selected][0], *self._dates(self.history_start, self.history_end),
            )
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Refresh Contributor History", wx.OK | wx.ICON_ERROR, self)
            return
        finally:
            self.history_run.SetLabel("Refresh Contributor History")
            self.history_run.Enable()
        self.history_list.DeleteAllItems(); total = Decimal("0.00")
        for index, row in enumerate(rows):
            self.history_list.InsertItem(index, str(row[0]))
            values = (row[1], str(row[2]).title(), row[3] or "", row[4], _money(row[5]),
                      str(row[6]).title(), str(row[7]).title())
            for column, value in enumerate(values, 1): self.history_list.SetItem(index, column, value)
            total += Decimal(row[5])
        if rows:
            result = f"{len(rows)} allocation line(s) · Total {_money(total)}"
        else:
            result = "No Ready or Posted contributions match this selection."
        self.history_total.SetLabel(f"{result} - Refreshed {_run_time()}")
        self.history_total.GetParent().Layout()
        self.history_total.Refresh()

    def on_summary_pdf(self, _event=None):
        """Render the selected donor-free batch controls as a protected PDF."""
        try:
            first, last = self._dates(self.summary_start, self.summary_end)
            self.report_service.run_batch_summary(
                date.fromisoformat(first), date.fromisoformat(last),
            )
        except Exception as error:
            wx.MessageBox(str(error), "Giving Batch Summary", wx.OK | wx.ICON_ERROR, self)


def show_giving_reports(parent, connection, authorization, session):
    """Open Giving reports after enforcing the summary-report entry permission."""
    authorization.require("giving.reports.summary", "run Giving reports")
    dialog = GivingReportsDialog(parent, connection, authorization, session)
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
