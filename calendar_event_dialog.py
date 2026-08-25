"""Compact agenda and editor for standalone Church events."""

from __future__ import annotations

from datetime import datetime, time

import wx
import wx.adv

from calendar_events import CalendarEventError, CalendarEventService, MariaDBCalendarEventRepository


def _selected_id(control):
    index = control.GetSelection()
    return control.rows[index][0] if 0 <= index < len(control.rows) else None


def _wx_date(control):
    value = control.GetValue()
    return value.GetYear(), value.GetMonth() + 1, value.GetDay()


def _time_text(value):
    return value.strftime("%I:%M %p") if value else ""


class EventEditorDialog(wx.Dialog):
    """Edit one safe, nonrecurring event without imitating a calendar."""

    def __init__(self, parent, event=None):
        super().__init__(parent, title="Church Event", size=(620, 610))
        self.event = event or {}; panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label="Enter public-safe event information. Recurrence and reminders belong in the external calendar.")
        note.SetForegroundColour(wx.Colour(0, 82, 165)); outer.Add(note, 0, wx.EXPAND | wx.ALL, 14)
        grid = wx.FlexGridSizer(cols=2, hgap=12, vgap=9); grid.AddGrowableCol(1, 1)
        self.title = wx.TextCtrl(panel, value=str(self.event.get("title") or ""))
        self.date = wx.adv.DatePickerCtrl(panel)
        self.start = wx.adv.TimePickerCtrl(panel); self.end = wx.adv.TimePickerCtrl(panel)
        self.has_end = wx.CheckBox(panel, label="Use an end time")
        self.all_day = wx.CheckBox(panel, label="All-day event")
        self.location = wx.TextCtrl(panel, value=str(self.event.get("location") or ""))
        self.status = wx.Choice(panel, choices=["Planned", "Confirmed", "Cancelled", "Completed"])
        self.status.SetStringSelection(str(self.event.get("status") or "PLANNED").title())
        self.eligible = wx.CheckBox(panel, label="Eligible for external calendar export")
        self.eligible.SetValue(bool(self.event.get("calendar_eligible")))
        self.description = wx.TextCtrl(panel, value=str(self.event.get("description") or ""), style=wx.TE_MULTILINE)
        starts = self.event.get("starts_at") or datetime.now().replace(second=0, microsecond=0)
        ends = self.event.get("ends_at")
        self.date.SetValue(wx.DateTime(starts.day, starts.month - 1, starts.year))
        self.start.SetTime(starts.hour, starts.minute, 0)
        if ends: self.end.SetTime(ends.hour, ends.minute, 0); self.has_end.SetValue(True)
        else: self.end.SetTime(min(starts.hour + 1, 23), starts.minute, 0)
        self.all_day.SetValue(bool(self.event.get("all_day")))
        for label, control in (("Title", self.title), ("Date", self.date), ("Start time", self.start),
                               ("End", self._end_panel(panel)), ("Timing", self.all_day),
                               ("Location", self.location), ("Status", self.status),
                               ("Publication", self.eligible), ("Safe description", self.description)):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL); grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer()
        buttons.Add(wx.Button(panel, wx.ID_OK, "Save Event"), 0, wx.RIGHT, 8); buttons.Add(wx.Button(panel, wx.ID_CANCEL, "Cancel"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)
        self.all_day.Bind(wx.EVT_CHECKBOX, self._timing); self.has_end.Bind(wx.EVT_CHECKBOX, self._timing); self._timing(None)

    def _end_panel(self, parent):
        panel = wx.Panel(parent); row = wx.BoxSizer(wx.HORIZONTAL); row.Add(self.has_end, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10); row.Add(self.end, 1); panel.SetSizer(row); return panel

    def _timing(self, _event):
        timed = not self.all_day.GetValue(); self.start.Enable(timed); self.has_end.Enable(timed); self.end.Enable(timed and self.has_end.GetValue())

    def values(self):
        year, month, day = _wx_date(self.date)
        if self.all_day.GetValue():
            starts = datetime(year, month, day); ends = None
        else:
            start = self.start.GetValue(); starts = datetime(year, month, day, start.GetHour(), start.GetMinute())
            end = self.end.GetValue(); ends = datetime(year, month, day, end.GetHour(), end.GetMinute()) if self.has_end.GetValue() else None
        return {**self.event, "title": self.title.GetValue(), "starts_at": starts, "ends_at": ends,
                "all_day": self.all_day.GetValue(), "location": self.location.GetValue(),
                "status": self.status.GetStringSelection().upper(), "calendar_eligible": self.eligible.GetValue(),
                "description": self.description.GetValue(), "time_zone": self.event.get("time_zone") or "America/Chicago"}


class CalendarEventsDialog(wx.Dialog):
    """Show an agenda list of ChurchManager-owned standalone events."""

    def __init__(self, parent, connection, session, authorization):
        super().__init__(parent, title="Church Events", size=(980, 650))
        self.service = CalendarEventService(MariaDBCalendarEventRepository(connection), session, authorization)
        self.rows = []; panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        heading = wx.StaticText(panel, label="Church Events"); font = heading.GetFont(); font.SetPointSize(font.GetPointSize()+2); font.SetWeight(wx.FONTWEIGHT_BOLD); heading.SetFont(font)
        outer.Add(heading, 0, wx.ALL, 14)
        guidance = wx.StaticText(panel, label="A simple event list for ChurchManager dates. Use your external calendar for recurring events, reminders, and invitations.")
        guidance.SetForegroundColour(wx.Colour(0, 82, 165)); outer.Add(guidance, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        church_row = wx.BoxSizer(wx.HORIZONTAL); church_row.Add(wx.StaticText(panel, label="Church"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        churches = self.service.repository.churches(); self.church = wx.Choice(panel, choices=[row[1] for row in churches]); self.church.rows = churches
        if churches: self.church.SetSelection(0)
        church_row.Add(self.church, 1); outer.Add(church_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("When",150),("Event",260),("Location",180),("Status",100),("Calendar",90))): self.list.InsertColumn(index,label,width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (("New Event", self.on_new), ("Open Event", self.on_open), ("Cancel Event", self.on_cancel), ("Complete Event", self.on_complete)):
            button = wx.Button(panel, label=label); button.Bind(wx.EVT_BUTTON, handler); buttons.Add(button, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer(); close = wx.Button(panel, wx.ID_CLOSE, "Close"); close.Bind(wx.EVT_BUTTON, lambda _e:self.EndModal(wx.ID_CLOSE)); buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)
        self.church.Bind(wx.EVT_CHOICE, lambda _e:self.refresh()); self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open); self.refresh()

    def selected(self):
        index = self.list.GetFirstSelected(); return self.rows[index] if 0 <= index < len(self.rows) else None

    def refresh(self):
        self.list.DeleteAllItems(); church_id = _selected_id(self.church)
        self.rows = self.service.events(church_id) if church_id else []
        for row in self.rows:
            when = row["starts_at"].strftime("%m/%d/%Y") if row["all_day"] else row["starts_at"].strftime("%m/%d/%Y %I:%M %p")
            index = self.list.InsertItem(self.list.GetItemCount(), when)
            for column, value in enumerate((row["title"], row["location"] or "", row["status"].title(), "Yes" if row["calendar_eligible"] else "No"), 1): self.list.SetItem(index,column,str(value))

    def on_new(self, _event): self._edit({"church_id": _selected_id(self.church)})
    def on_open(self, _event):
        row = self.selected()
        if row: self._edit(row)
    def _edit(self, row):
        dialog = EventEditorDialog(self, row)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.service.save(dialog.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Save Event", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()
    def _status(self, status):
        row = self.selected()
        if not row: return
        self._edit({**row, "status": status})
    def on_cancel(self, _event): self._status("CANCELLED")
    def on_complete(self, _event): self._status("COMPLETED")


def show_calendar_events(parent, connection, session, authorization):
    """Open the protected Church Events agenda."""
    dialog = CalendarEventsDialog(parent, connection, session, authorization)
    try: return dialog.ShowModal()
    finally: dialog.Destroy()
