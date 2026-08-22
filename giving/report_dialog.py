"""Permission-separated operational Giving report screens."""

from __future__ import annotations

from datetime import date, datetime, timedelta
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


def quarter_bounds(year, quarter):
    """Return inclusive dates for a calendar-year quarter."""
    if quarter not in (1, 2, 3, 4):
        raise ValueError("Select Quarter 1 through Quarter 4.")
    first_month = ((quarter - 1) * 3) + 1
    first = date(int(year), first_month, 1)
    following = date(int(year) + (1 if quarter == 4 else 0), 1 if quarter == 4 else first_month + 3, 1)
    return first, following - timedelta(days=1)


def statement_period_bounds(mode, year, quarter, custom_first=None, custom_last=None):
    """Return inclusive statement dates and a filename-safe period label."""
    if mode == "Quarterly":
        first, last = quarter_bounds(year, quarter)
        return first, last, f"{year}-Q{quarter}", f"Quarter {quarter} of {year}"
    if mode == "Calendar Year":
        return date(int(year), 1, 1), date(int(year), 12, 31), str(year), f"calendar year {year}"
    if mode == "Custom Date Range":
        if custom_first is None or custom_last is None:
            raise ValueError("Select both custom statement dates.")
        if custom_last < custom_first:
            raise ValueError("The custom Through date cannot be before the From date.")
        suffix = f"{custom_first:%Y%m%d}-{custom_last:%Y%m%d}"
        return custom_first, custom_last, suffix, f"{custom_first} through {custom_last}"
    raise ValueError("Select Quarterly, Calendar Year, or Custom Date Range.")


class GivingReportsDialog(wx.Dialog):
    """Show donor-free controls and separately authorized donor history."""

    def __init__(self, parent, connection, authorization, session):
        super().__init__(parent, title="Giving Reports", size=(1120, 700),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = GivingReportService(connection, authorization)
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
        if authorization.has_permission("giving.statements.generate"):
            self._build_statement_tab()
            self._build_statement_history_tab()
        if authorization.has_permission("giving.reports.confidential"):
            self._build_tribute_tab()
            self._build_directed_gifts_tab()
            self._build_envelope_boxes_tab()
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

    def _build_statement_tab(self):
        panel = wx.Panel(self.notebook); root = wx.BoxSizer(wx.VERTICAL)
        guidance = wx.StaticText(
            panel,
            label="Preview or issue statements for one contributor or all statement-enabled contributors.",
        )
        guidance.SetForegroundColour(wx.Colour(0, 75, 150))
        root.Add(guidance, 0, wx.ALL, 10)
        self.statement_contributors = self.service.statement_contributors()
        names = ["All eligible contributors"] + [row[1] for row in self.statement_contributors]
        self.statement_contributor = wx.Choice(panel, choices=names)
        self.statement_contributor.SetSelection(0)
        years = self.service.statement_years() or [date.today().year]
        self.statement_year = wx.Choice(panel, choices=[str(value) for value in years])
        self.statement_year.SetSelection(0)
        self.statement_period = wx.Choice(
            panel, choices=["Quarterly", "Calendar Year", "Custom Date Range"],
        )
        self.statement_period.SetSelection(0)
        self.statement_period.Bind(wx.EVT_CHOICE, self.on_statement_period)
        self.statement_quarter = wx.Choice(panel, choices=["Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"])
        current_quarter = min(3, (date.today().month - 1) // 3)
        self.statement_quarter.SetSelection(current_quarter)
        self.statement_start, self.statement_end = self._date_controls(panel)
        preview = wx.Button(panel, label="Preview Statement(s)")
        preview.Bind(wx.EVT_BUTTON, self.on_statement_pdf)
        issue = wx.Button(panel, label="Issue and Record Statement(s)")
        issue.Bind(wx.EVT_BUTTON, self.on_statement_issue)
        filters = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
        filters.AddGrowableCol(1, 1)
        for label, control in (
            ("Contributor", self.statement_contributor),
            ("Period", self.statement_period),
            ("Year", self.statement_year),
            ("Quarter", self.statement_quarter),
            ("From", self.statement_start),
            ("Through", self.statement_end),
        ):
            filters.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            filters.Add(control, 1, wx.EXPAND)
        root.Add(filters, 0, wx.ALL | wx.EXPAND, 10)
        actions = wx.BoxSizer(wx.HORIZONTAL)
        actions.Add(preview, 0, wx.RIGHT, 8); actions.Add(issue)
        root.Add(actions, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        note = wx.StaticText(
            panel,
            label=("Preview does not record issuance or delivery. Only Posted, statement-eligible "
                   "contributions are included."),
        )
        root.Add(note, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(root)
        self.notebook.AddPage(panel, "Contribution Statements")
        self.on_statement_period()

    def _build_statement_history_tab(self):
        panel = wx.Panel(self.notebook); root = wx.BoxSizer(wx.VERTICAL)
        refresh = wx.Button(panel, label="Refresh Issuance History")
        refresh.Bind(wx.EVT_BUTTON, self.on_statement_history)
        root.Add(refresh, 0, wx.ALL, 10)
        self.statement_history = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((
            ("Generated",145),("Contributor",210),("From",95),("Through",95),
            ("Revision",70),("File",185),("SHA-256",180),
        )):
            self.statement_history.InsertColumn(index, label, width=width)
        root.Add(self.statement_history, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(root); self.notebook.AddPage(panel, "Statement Issuance History")
        self.on_statement_history()

    def _build_envelope_boxes_tab(self):
        """Build protected annual label and assignment-register controls."""
        panel = wx.Panel(self.notebook); root = wx.BoxSizer(wx.VERTICAL)
        guidance = wx.StaticText(
            panel,
            label=("Print 30-up envelope-box labels or a verification register. "
                   "No contribution amounts are included."),
        )
        guidance.SetForegroundColour(wx.Colour(0, 75, 150))
        root.Add(guidance, 0, wx.ALL, 10)
        years = self.service.envelope_assignment_years()
        self.envelope_year = wx.Choice(panel, choices=[str(value) for value in years])
        if years:
            self.envelope_year.SetSelection(0)
        self.envelope_format = wx.Choice(
            panel, choices=["Avery 5160 or compatible (30 labels, US Letter)"],
        )
        self.envelope_format.SetSelection(0)
        self.envelope_inactive = wx.CheckBox(panel, label="Include inactive contributors")
        self.envelope_outside = wx.CheckBox(panel, label="Include outside contributors")
        self.envelope_outside.SetValue(True)
        self.envelope_church = wx.CheckBox(panel, label="Include congregation name on labels")
        self.envelope_church.SetValue(True)
        form = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
        form.AddGrowableCol(1, 1)
        for label, control in (("Assignment year", self.envelope_year),
                               ("Label sheet", self.envelope_format),
                               ("", self.envelope_inactive), ("", self.envelope_outside),
                               ("", self.envelope_church)):
            form.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            form.Add(control, 1, wx.EXPAND)
        root.Add(form, 0, wx.EXPAND | wx.ALL, 10)
        actions = wx.BoxSizer(wx.HORIZONTAL)
        self.envelope_labels_button = wx.Button(panel, label="Preview Box Labels")
        self.envelope_labels_button.Bind(wx.EVT_BUTTON, self.on_envelope_labels)
        self.envelope_register_button = wx.Button(panel, label="Preview Assignment Register")
        self.envelope_register_button.Bind(wx.EVT_BUTTON, self.on_envelope_register)
        actions.Add(self.envelope_labels_button, 0, wx.RIGHT, 8)
        actions.Add(self.envelope_register_button)
        root.Add(actions, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.envelope_status = wx.StaticText(panel, label="")
        self.envelope_status.SetForegroundColour(wx.Colour(0, 75, 150))
        root.Add(self.envelope_status, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        note = wx.StaticText(
            panel,
            label=("Print label PDFs at Actual Size / 100%. The assignment register should be "
                   "retained for box-distribution verification."),
        )
        root.Add(note, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(root)
        self.notebook.AddPage(panel, "Envelope Boxes")

    def _build_tribute_tab(self):
        """Build the consent-limited memorial and honor report controls."""
        panel = wx.Panel(self.notebook); root = wx.BoxSizer(wx.VERTICAL)
        guidance = wx.StaticText(
            panel,
            label=("Create a protected acknowledgment list for Posted memorial and honor gifts. "
                   "Donor names and gift amounts appear only when each disclosure was separately authorized."),
        )
        guidance.SetForegroundColour(wx.Colour(0, 75, 150))
        guidance.Wrap(920)
        root.Add(guidance, 0, wx.ALL, 10)
        self.tribute_start, self.tribute_end = self._date_controls(panel)
        preview = wx.Button(panel, label="Preview Memorial / Honor List")
        preview.Bind(wx.EVT_BUTTON, self.on_tribute_pdf)
        filters = wx.BoxSizer(wx.HORIZONTAL)
        for label, control in (("From", self.tribute_start), ("Through", self.tribute_end)):
            filters.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            filters.Add(control, 0, wx.RIGHT, 12)
        filters.Add(preview)
        root.Add(filters, 0, wx.ALL, 10)
        note = wx.StaticText(
            panel,
            label=("This list is for acknowledgment work. It is confidential and includes no Draft or Ready gifts."),
        )
        root.Add(note, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(root)
        self.notebook.AddPage(panel, "Memorial / Honor Gifts")

    def _build_directed_gifts_tab(self):
        """Build the restricted donor-direction review controls."""
        panel = wx.Panel(self.notebook); root = wx.BoxSizer(wx.VERTICAL)
        guidance = wx.StaticText(panel, label=(
            "Review pending and completed donor directions. This report documents the congregation's "
            "disposition and does not determine deductibility."
        ))
        guidance.SetForegroundColour(wx.Colour(0, 75, 150)); guidance.Wrap(920)
        root.Add(guidance, 0, wx.ALL, 10)
        self.directed_start, self.directed_end = self._date_controls(panel)
        preview = wx.Button(panel, label="Preview Directed Gift Review List")
        preview.Bind(wx.EVT_BUTTON, self.on_directed_gifts_pdf)
        filters = wx.BoxSizer(wx.HORIZONTAL)
        for label, control in (("From", self.directed_start), ("Through", self.directed_end)):
            filters.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            filters.Add(control, 0, wx.RIGHT, 12)
        filters.Add(preview); root.Add(filters, 0, wx.ALL, 10)
        panel.SetSizer(root); self.notebook.AddPage(panel, "Directed Gift Review")

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

    def on_statement_pdf(self, _event=None):
        """Preview the selected statement period without recording issuance."""
        try:
            first, last, suffix, _display, contributor_ids = self._statement_selection()
            self.report_service.run_statements(
                contributor_ids, first, last, output_name=f"GIVE-STMT-{suffix}",
            )
        except Exception as error:
            wx.MessageBox(str(error), "Contribution Statements", wx.OK | wx.ICON_ERROR, self)

    def _statement_selection(self):
        year = int(self.statement_year.GetStringSelection())
        quarter = self.statement_quarter.GetSelection() + 1
        mode = self.statement_period.GetStringSelection()
        custom_first = date.fromisoformat(_python_date(self.statement_start))
        custom_last = date.fromisoformat(_python_date(self.statement_end))
        first, last, suffix, display = statement_period_bounds(
            mode, year, quarter, custom_first, custom_last,
        )
        selected = self.statement_contributor.GetSelection()
        if selected <= 0:
            contributor_ids = [row[0] for row in self.service.statement_contributors_for_period(first, last)]
            if not contributor_ids:
                raise ValueError(
                    f"No statement-enabled contributors have eligible Posted contributions "
                    f"in {display}."
                )
        else:
            contributor_ids = [self.statement_contributors[selected - 1][0]]
        return first, last, suffix, display, contributor_ids

    def on_statement_period(self, _event=None):
        """Enable only the controls used by the selected statement period."""
        mode = self.statement_period.GetStringSelection()
        self.statement_year.Enable(mode in {"Quarterly", "Calendar Year"})
        self.statement_quarter.Enable(mode == "Quarterly")
        self.statement_start.Enable(mode == "Custom Date Range")
        self.statement_end.Enable(mode == "Custom Date Range")

    def on_statement_issue(self, _event=None):
        """Generate statements and record their hashes as officially issued."""
        try:
            first, last, suffix, display, contributor_ids = self._statement_selection()
            answer = wx.MessageBox(
                f"Issue and record {len(contributor_ids)} statement(s) for {display}?\n\n"
                "This records issuance, but it does not record printing, mailing, or delivery.",
                "Issue Contribution Statements", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self,
            )
            if answer != wx.YES:
                return
            self.report_service.run_statements(
                contributor_ids, first, last,
                output_name=f"GIVE-STMT-ISSUED-{suffix}", issue=True,
            )
            self.on_statement_history()
        except Exception as error:
            wx.MessageBox(str(error), "Contribution Statements", wx.OK | wx.ICON_ERROR, self)

    def on_statement_history(self, _event=None):
        """Refresh confidential statement issuance identifiers."""
        rows = self.service.statement_issuance_history()
        self.statement_history.DeleteAllItems()
        for index, row in enumerate(rows):
            self.statement_history.InsertItem(index, str(row[0]))
            values = (row[1], str(row[2]), str(row[3]), str(row[4]), row[5], str(row[6])[:16] + "...")
            for column, value in enumerate(values, 1):
                self.statement_history.SetItem(index, column, value)

    def _envelope_selection(self):
        selected = self.envelope_year.GetStringSelection()
        if not selected:
            raise ValueError("Select an envelope assignment year.")
        return int(selected), self.envelope_inactive.GetValue(), self.envelope_outside.GetValue()

    def on_envelope_labels(self, _event=None):
        """Render the selected 30-up envelope-box label sheet."""
        self._begin_envelope_preview(self.envelope_labels_button, "Creating box labels...")
        try:
            year, inactive, outside = self._envelope_selection()
            output = self.report_service.run_envelope_labels(
                year, inactive, outside, self.envelope_church.GetValue(),
            )
            self._finish_envelope_preview(output)
        except Exception as error:
            self.envelope_status.SetLabel("Box labels were not created.")
            wx.MessageBox(str(error), "Envelope Box Labels", wx.OK | wx.ICON_ERROR, self)
        finally:
            self.envelope_labels_button.Enable()

    def on_tribute_pdf(self, _event=None):
        """Render the protected memorial and honor acknowledgment list."""
        try:
            first, last = self._dates(self.tribute_start, self.tribute_end)
            self.report_service.run_tribute_acknowledgments(
                date.fromisoformat(first), date.fromisoformat(last),
            )
        except Exception as error:
            wx.MessageBox(
                str(error), "Memorial and Honor Gifts", wx.OK | wx.ICON_ERROR, self,
            )

    def on_directed_gifts_pdf(self, _event=None):
        """Render the restricted directed-gift review and disposition list."""
        try:
            first, last = self._dates(self.directed_start, self.directed_end)
            self.report_service.run_directed_gift_reviews(
                date.fromisoformat(first), date.fromisoformat(last),
            )
        except Exception as error:
            wx.MessageBox(str(error), "Directed Gift Review", wx.OK | wx.ICON_ERROR, self)

    def on_envelope_register(self, _event=None):
        """Render the selected confidential envelope assignment register."""
        self._begin_envelope_preview(
            self.envelope_register_button, "Creating assignment register...",
        )
        try:
            year, inactive, outside = self._envelope_selection()
            output = self.report_service.run_envelope_register(year, inactive, outside)
            self._finish_envelope_preview(output)
        except Exception as error:
            self.envelope_status.SetLabel("Assignment register was not created.")
            wx.MessageBox(str(error), "Envelope Assignment Register", wx.OK | wx.ICON_ERROR, self)
        finally:
            self.envelope_register_button.Enable()

    def _begin_envelope_preview(self, button, message):
        """Make PDF generation progress visible even when the viewer stays behind the app."""
        button.Disable()
        self.envelope_status.SetLabel(message)
        self.envelope_status.GetParent().Layout()
        self.envelope_status.Update()
        wx.YieldIfNeeded()

    def _finish_envelope_preview(self, output):
        """Show where a completed PDF was saved after requesting viewer launch."""
        self.envelope_status.SetLabel(
            f"Created {output}. If the PDF viewer did not come forward, open this file directly."
        )
        self.envelope_status.GetParent().Layout()


def show_giving_reports(parent, connection, authorization, session):
    """Open Giving reports after enforcing the summary-report entry permission."""
    authorization.require("giving.reports.summary", "run Giving reports")
    dialog = GivingReportsDialog(parent, connection, authorization, session)
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
