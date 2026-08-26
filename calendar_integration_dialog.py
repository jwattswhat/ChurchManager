"""Preview approved calendar sources and export them as iCalendar files."""

from __future__ import annotations

from datetime import date, timedelta

import wx
import wx.adv

from calendar_sources import CalendarSourceService, MariaDBCalendarSourceRepository
from calendar_publication import CalendarPublicationService, MariaDBCalendarPublicationRepository
from google_calendar_provider import connect_google_calendar
from icalendar_export import ICalendarExportService


SOURCE_OPTIONS = (
    ("CHURCH_EVENT", "Church Events", "calendar.view"),
    ("WORSHIP_SERVICE", "Worship Services", "worship.manage"),
    ("GROUP_MEETING", "Group Meetings", "groups.meetings.view"),
    ("PROJECT_MILESTONE", "Project Targets", "projects.calendar"),
    ("PROJECT_STEP", "Project Steps", "projects.calendar"),
)


def _date_value(control):
    value = control.GetValue()
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


class CalendarIntegrationDialog(wx.Dialog):
    """Present a bounded preview before creating a portable calendar file."""

    def __init__(self, parent, connection, authorization, test_mode=False):
        super().__init__(parent, title="Calendar Integration", size=(1040, 680))
        self.connection = connection
        self.authorization = authorization
        self.source_service = CalendarSourceService(
            MariaDBCalendarSourceRepository(connection), authorization,
        )
        self.export_service = ICalendarExportService(authorization)
        self.publication_service = CalendarPublicationService(
            MariaDBCalendarPublicationRepository(connection), authorization, test_mode,
        )
        self.test_mode = bool(test_mode)
        self.google_provider = None
        self.descriptors = []
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)

        heading = wx.StaticText(panel, label="Calendar Integration")
        font = heading.GetFont(); font.SetPointSize(font.GetPointSize() + 2); font.SetWeight(wx.FONTWEIGHT_BOLD)
        heading.SetFont(font); outer.Add(heading, 0, wx.ALL, 14)
        guidance = wx.StaticText(
            panel,
            label="Preview safe ChurchManager dates, then create a standard .ics file for your external calendar.",
        )
        guidance.SetForegroundColour(wx.Colour(0, 82, 165))
        outer.Add(guidance, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)

        filters = wx.FlexGridSizer(cols=4, hgap=10, vgap=8); filters.AddGrowableCol(1, 1)
        churches = self._churches()
        self.church = wx.Choice(panel, choices=[row[1] for row in churches]); self.church.rows = churches
        if churches: self.church.SetSelection(0)
        self.from_date = wx.adv.DatePickerCtrl(panel); self.through_date = wx.adv.DatePickerCtrl(panel)
        today = date.today(); through = today + timedelta(days=90)
        self.from_date.SetValue(wx.DateTime(today.day, today.month - 1, today.year))
        self.through_date.SetValue(wx.DateTime(through.day, through.month - 1, through.year))
        filters.Add(wx.StaticText(panel, label="Church"), 0, wx.ALIGN_CENTER_VERTICAL)
        filters.Add(self.church, 1, wx.EXPAND)
        filters.Add(wx.StaticText(panel, label="From"), 0, wx.ALIGN_CENTER_VERTICAL)
        filters.Add(self.from_date, 0)
        filters.AddSpacer(1); filters.AddSpacer(1)
        filters.Add(wx.StaticText(panel, label="Through"), 0, wx.ALIGN_CENTER_VERTICAL)
        filters.Add(self.through_date, 0)
        outer.Add(filters, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)

        source_row = wx.BoxSizer(wx.HORIZONTAL); source_row.Add(wx.StaticText(panel, label="Include"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        self.sources = {}
        for key, label, permission in SOURCE_OPTIONS:
            control = wx.CheckBox(panel, label=label); control.SetValue(self.authorization.has_permission(permission))
            control.Enable(self.authorization.has_permission(permission)); self.sources[key] = control
            source_row.Add(control, 0, wx.RIGHT, 18)
        outer.Add(source_row, 0, wx.ALL, 14)

        publish_row = wx.BoxSizer(wx.HORIZONTAL)
        publish_row.Add(wx.StaticText(panel, label="Google calendar"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        self.destination = wx.TextCtrl(panel, value="primary", size=(260, -1))
        self.destination.SetToolTip("Use primary, or enter the Google Calendar identifier supplied by Google.")
        publish_row.Add(self.destination, 0, wx.RIGHT, 10)
        self.connect = wx.Button(panel, label="Connect to Google")
        self.connect.Bind(wx.EVT_BUTTON, self.on_connect)
        publish_row.Add(self.connect, 0, wx.RIGHT, 8)
        self.publish = wx.Button(panel, label="Publish Preview")
        self.publish.Bind(wx.EVT_BUTTON, self.on_publish)
        publish_row.Add(self.publish, 0)
        live_allowed = not self.test_mode
        self.connect.Enable(live_allowed and self.authorization.has_permission("calendar.configure"))
        self.publish.Enable(False)
        outer.Add(publish_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        if self.test_mode:
            notice = wx.StaticText(panel, label="Google publishing is disabled in TEST MODE. Portable .ics export remains available.")
            notice.SetForegroundColour(wx.Colour(150, 80, 0))
            outer.Add(notice, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)

        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("When", 170), ("Source", 130), ("Event", 280), ("Location", 190), ("Status", 90))):
            self.list.InsertColumn(index, label, width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        self.summary = wx.StaticText(panel, label="Select Preview Calendar to review eligible dates.")
        outer.Add(self.summary, 0, wx.EXPAND | wx.ALL, 14)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        preview = wx.Button(panel, label="Preview Calendar"); preview.Bind(wx.EVT_BUTTON, self.on_preview); buttons.Add(preview, 0, wx.RIGHT, 8)
        self.export = wx.Button(panel, label="Export .ics..."); self.export.Bind(wx.EVT_BUTTON, self.on_export)
        self.export.Enable(False); buttons.Add(self.export, 0)
        buttons.AddStretchSpacer(); close = wx.Button(panel, wx.ID_CLOSE, "Close"); close.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE)); buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        panel.SetSizer(outer)

    def _churches(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT ID,Church FROM tblChurch WHERE ID>0 ORDER BY Church,ID")
            return cursor.fetchall()
        finally:
            cursor.close()

    def _selected_church_id(self):
        index = self.church.GetSelection()
        return self.church.rows[index][0] if 0 <= index < len(self.church.rows) else None

    def on_preview(self, _event):
        try:
            start, end = _date_value(self.from_date), _date_value(self.through_date)
            rows = []
            for source, control in self.sources.items():
                if control.GetValue():
                    rows.extend(self.source_service.descriptors(source, self._selected_church_id(), start, end))
            self.descriptors = sorted(rows, key=lambda row: (row.starts_at, row.title.casefold(), row.uid))
            self._fill_preview()
        except Exception as error:
            self.descriptors = []; self._fill_preview()
            wx.MessageBox(str(error), "Unable to Preview Calendar", wx.OK | wx.ICON_ERROR, self)

    def _fill_preview(self):
        self.list.DeleteAllItems()
        labels = {key: label for key, label, _permission in SOURCE_OPTIONS}
        for row in self.descriptors:
            when = row.starts_at.strftime("%m/%d/%Y") if row.all_day else row.starts_at.strftime("%m/%d/%Y %I:%M %p")
            index = self.list.InsertItem(self.list.GetItemCount(), when)
            for column, value in enumerate((labels[row.source_type], row.title, row.location, row.status.title()), 1):
                self.list.SetItem(index, column, str(value or ""))
        count = len(self.descriptors)
        self.summary.SetLabel(f"{count} eligible calendar item{'s' if count != 1 else ''} ready for export.")
        self.export.Enable(bool(count) and self.authorization.has_permission("calendar.export"))
        self.publish.Enable(
            bool(count) and not self.test_mode
            and self.authorization.has_permission("calendar.publish")
        )

    def on_connect(self, _event):
        """Authorize the separate production-only Google publishing token."""
        try:
            self.authorization.require("calendar.configure", "configure Google Calendar")
            self.publication_service.ensure_live_publish_allowed()
            self.google_provider = connect_google_calendar()
            wx.MessageBox("Google Calendar is connected for this Windows user.",
                          "Google Calendar Connected", wx.OK | wx.ICON_INFORMATION, self)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Connect to Google Calendar", wx.OK | wx.ICON_ERROR, self)

    def on_publish(self, _event):
        """Preview deterministic provider actions, confirm, and publish once."""
        if not self.descriptors:
            return
        try:
            destination = self.destination.GetValue().strip()
            decisions = self.publication_service.plan("GOOGLE", destination, self.descriptors)
            counts = {action: 0 for action in ("CREATE", "UPDATE", "CANCEL", "SKIP")}
            for decision in decisions:
                counts[decision.action] += 1
            message = (
                f"Google Calendar: {destination}\n\n"
                f"Create: {counts['CREATE']}   Update: {counts['UPDATE']}   "
                f"Cancel: {counts['CANCEL']}   Unchanged: {counts['SKIP']}\n\n"
                "Publish this preview now? ChurchManager remains the source of truth."
            )
            if wx.MessageBox(message, "Confirm Calendar Publication",
                             wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) != wx.YES:
                return
            if self.google_provider is None:
                self.google_provider = connect_google_calendar()
            results = self.publication_service.publish(
                "GOOGLE", destination, decisions, self.google_provider,
            )
            totals = {name: sum(1 for _decision, result, _code in results if result == name)
                      for name in ("SUCCESS", "CANCELLED", "SKIPPED", "ERROR")}
            wx.MessageBox(
                f"Published: {totals['SUCCESS']}   Cancelled: {totals['CANCELLED']}   "
                f"Unchanged: {totals['SKIPPED']}   Errors: {totals['ERROR']}",
                "Calendar Publication Complete",
                wx.OK | (wx.ICON_WARNING if totals["ERROR"] else wx.ICON_INFORMATION), self,
            )
            self.on_preview(None)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Publish Calendar", wx.OK | wx.ICON_ERROR, self)

    def on_export(self, _event):
        if not self.descriptors:
            return
        default_name = f"ChurchManager-Calendar-{_date_value(self.from_date):%Y-%m-%d}.ics"
        dialog = wx.FileDialog(self, "Export Calendar", wildcard="iCalendar files (*.ics)|*.ics", defaultFile=default_name,
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        try:
            if dialog.ShowModal() != wx.ID_OK: return
            target = self.export_service.write(dialog.GetPath(), self.descriptors, overwrite=True)
            wx.MessageBox(f"Calendar exported to:\n{target}", "Calendar Export Complete", wx.OK | wx.ICON_INFORMATION, self)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Export Calendar", wx.OK | wx.ICON_ERROR, self)
        finally:
            dialog.Destroy()


def show_calendar_integration(parent, connection, authorization, test_mode=False):
    """Open the protected calendar preview and export screen."""
    authorization.require("calendar.view", "open Calendar Integration")
    dialog = CalendarIntegrationDialog(parent, connection, authorization, test_mode)
    try: return dialog.ShowModal()
    finally: dialog.Destroy()
