"""Native Group meeting history and attendance entry screens."""

from __future__ import annotations

from datetime import date, datetime, time

import wx
import wx.adv

from group_meeting_repository import MariaDBGroupMeetingRepository
from group_meeting_service import GroupMeetingService


def _date_from_picker(control):
    value = control.GetValue()
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


def _selected_id(control):
    selection = control.GetSelection()
    return control.rows[selection][0] if 0 <= selection < len(control.rows) else None


class NewGroupMeetingDialog(wx.Dialog):
    """Collect a single meeting occurrence rather than a recurrence rule."""

    def __init__(self, parent, group, meeting=None):
        super().__init__(parent, title="Reschedule Group Meeting" if meeting else "New Group Meeting", size=(570, 430))
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label="Schedule one meeting. Attendance can be recorded after it is created.")
        note.SetForegroundColour(wx.Colour(0, 82, 155)); outer.Add(note, 0, wx.ALL, 14)
        grid = wx.FlexGridSizer(cols=2, vgap=10, hgap=12); grid.AddGrowableCol(1, 1)
        self.title = wx.TextCtrl(panel, value=(meeting or {}).get("title") or group["name"])
        self.meeting_date = wx.adv.DatePickerCtrl(panel)
        self.meeting_time = wx.adv.TimePickerCtrl(panel); self.meeting_time.SetTime(19, 0, 0)
        self.location = wx.TextCtrl(panel, value=(meeting or {}).get("location") or group.get("default_location") or "")
        self.mode = wx.Choice(panel, choices=["Roster", "Head count", "Both"]); self.mode.SetSelection(0)
        self.notes = wx.TextCtrl(panel, value=(meeting or {}).get("notes") or "", style=wx.TE_MULTILINE)
        for label, control in (("Title", self.title), ("Date", self.meeting_date), ("Time", self.meeting_time),
                               ("Location", self.location), ("Attendance", self.mode), ("Administrative note", self.notes)):
            grid.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL); grid.Add(control, 1, wx.EXPAND)
        outer.Add(grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer()
        buttons.Add(wx.Button(panel, wx.ID_OK, "Create Replacement" if meeting else "Create Meeting"), 0, wx.RIGHT, 8)
        buttons.Add(wx.Button(panel, wx.ID_CANCEL, "Cancel"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)

    def values(self):
        hour, minute, second = self.meeting_time.GetTime()
        mode = {"Roster": "ROSTER", "Head count": "HEADCOUNT", "Both": "BOTH"}[self.mode.GetStringSelection()]
        return {"title": self.title.GetValue(), "starts_at": datetime.combine(_date_from_picker(self.meeting_date), time(hour, minute, second)),
                "location": self.location.GetValue(), "attendance_mode": mode, "notes": self.notes.GetValue()}


class AddMeetingGuestDialog(wx.Dialog):
    """Choose an existing same-congregation Person as a meeting-only guest."""

    def __init__(self, parent, rows):
        super().__init__(parent, title="Add Meeting Guest", size=(520, 170))
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(wx.StaticText(panel, label="This adds attendance only; it does not create Group membership."), 0, wx.ALL, 14)
        self.person = wx.Choice(panel, choices=[row["person"] for row in rows]); self.person.rows = [(row["id"], row["person"]) for row in rows]
        if rows: self.person.SetSelection(0)
        outer.Add(self.person, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer()
        buttons.Add(wx.Button(panel, wx.ID_OK, "Add Guest"), 0, wx.RIGHT, 8); buttons.Add(wx.Button(panel, wx.ID_CANCEL, "Cancel"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)


class GroupAttendanceDialog(wx.Dialog):
    """Record roster and guest statuses with a separate anonymous head count."""

    CYCLE = {"UNKNOWN": "PRESENT", "PRESENT": "ABSENT", "ABSENT": "EXCUSED", "EXCUSED": "UNKNOWN"}

    def __init__(self, parent, service, meeting_id):
        super().__init__(parent, title="Group Meeting Attendance", size=(780, 600), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.service = service; self.meeting_id = meeting_id
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        self.heading = wx.StaticText(panel); font = self.heading.GetFont(); font.MakeBold(); self.heading.SetFont(font)
        outer.Add(self.heading, 0, wx.ALL, 14)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Person", 300), ("Relationship", 120), ("Attendance", 130))):
            self.list.InsertColumn(index, label, width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        controls = wx.BoxSizer(wx.HORIZONTAL)
        self.guest = wx.Button(panel, label="Add Guest..."); controls.Add(self.guest, 0, wx.RIGHT, 12)
        for status in ("Present", "Absent", "Excused", "Unknown"):
            button = wx.Button(panel, label=status); button.Bind(wx.EVT_BUTTON, lambda _event, value=status.upper(): self.set_status(value))
            controls.Add(button, 0, wx.RIGHT, 6)
        controls.AddStretchSpacer(); controls.Add(wx.StaticText(panel, label="Total head count"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.head_count = wx.SpinCtrl(panel, min=-1, max=100000, initial=-1); controls.Add(self.head_count)
        outer.Add(controls, 0, wx.EXPAND | wx.ALL, 14)
        guidance = wx.StaticText(panel, label="Double-click a person to cycle Unknown, Present, Absent, and Excused. Use -1 when no head count was recorded.")
        guidance.SetForegroundColour(wx.Colour(0, 82, 155)); outer.Add(guidance, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer()
        buttons.Add(wx.Button(panel, wx.ID_SAVE, "Save Attendance"), 0, wx.RIGHT, 8); buttons.Add(wx.Button(panel, wx.ID_CLOSE, "Close"))
        outer.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14); panel.SetSizer(outer)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_cycle); self.guest.Bind(wx.EVT_BUTTON, self.on_guest)
        self.Bind(wx.EVT_BUTTON, self.on_save, id=wx.ID_SAVE); self.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE), id=wx.ID_CLOSE)
        self.refresh()

    def refresh(self):
        self.meeting, self.rows = self.service.attendance_rows(self.meeting_id)
        self.heading.SetLabel(f'{self.meeting["title"]}  ·  {self.meeting["starts_at"]:%B %d, %Y at %I:%M %p}')
        self.head_count.SetValue(-1 if self.meeting.get("total_head_count") is None else self.meeting["total_head_count"])
        self.list.DeleteAllItems()
        for row in self.rows:
            index = self.list.InsertItem(self.list.GetItemCount(), row["person"])
            self.list.SetItem(index, 1, "Member" if row["is_member"] else "Guest")
            self.list.SetItem(index, 2, row["attendance_status"].title())

    def _selected(self):
        selected = self.list.GetFirstSelected()
        return selected if 0 <= selected < len(self.rows) else None

    def set_status(self, status):
        selected = self._selected()
        if selected is None: return
        self.rows[selected]["attendance_status"] = status; self.list.SetItem(selected, 2, status.title())

    def on_cycle(self, _event):
        selected = self._selected()
        if selected is not None: self.set_status(self.CYCLE[self.rows[selected]["attendance_status"]])

    def on_guest(self, _event):
        rows = self.service.available_guests(self.meeting_id)
        if not rows:
            wx.MessageBox("Every Person in this congregation is already displayed.", "Add Meeting Guest", wx.OK | wx.ICON_INFORMATION, self); return
        dialog = AddMeetingGuestDialog(self, rows)
        try:
            if dialog.ShowModal() == wx.ID_OK: self.service.add_guest(self.meeting_id, _selected_id(dialog.person)); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Add Guest", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_save(self, _event):
        try:
            count = self.head_count.GetValue(); count = None if count < 0 else count
            self.service.record_attendance(self.meeting_id, [(row["person_id"], row["attendance_status"]) for row in self.rows], count)
            self.refresh(); wx.MessageBox("Attendance saved.", "Group Meeting Attendance", wx.OK | wx.ICON_INFORMATION, self)
        except Exception as error: wx.MessageBox(str(error), "Unable to Save Attendance", wx.OK | wx.ICON_ERROR, self)


class GroupMeetingsDialog(wx.Dialog):
    """List a Group's meeting history and open attendance entry."""

    def __init__(self, parent, connection, group_service, group_id):
        super().__init__(parent, title="Group Meetings", size=(900, 560), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.group_service = group_service; self.group_id = group_id
        self.service = GroupMeetingService(MariaDBGroupMeetingRepository(connection), group_service,
                                           group_service.session, group_service.authorization)
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        group = group_service.group(group_id)
        title = wx.StaticText(panel, label=f'{group["name"]} Meetings'); font = title.GetFont(); font.MakeBold(); title.SetFont(font)
        outer.Add(title, 0, wx.ALL, 14)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Date and time", 170), ("Meeting", 260), ("Location", 190), ("Status", 100), ("Head count", 90))):
            self.list.InsertColumn(index, label, width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); self.new = wx.Button(panel, label="New Meeting..."); self.attendance = wx.Button(panel, label="Record Attendance...")
        self.reschedule = wx.Button(panel, label="Reschedule..."); self.cancel = wx.Button(panel, label="Cancel Meeting")
        buttons.Add(self.new, 0, wx.RIGHT, 8); buttons.Add(self.attendance, 0, wx.RIGHT, 16)
        buttons.Add(self.reschedule, 0, wx.RIGHT, 8); buttons.Add(self.cancel)
        buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel, wx.ID_CLOSE, "Close"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)
        self.new.Bind(wx.EVT_BUTTON, self.on_new); self.attendance.Bind(wx.EVT_BUTTON, self.on_attendance)
        self.reschedule.Bind(wx.EVT_BUTTON, self.on_reschedule); self.cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_attendance); self.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE), id=wx.ID_CLOSE)
        self.refresh()

    def refresh(self):
        self.rows = self.service.meetings(self.group_id); self.list.DeleteAllItems()
        for row in self.rows:
            index = self.list.InsertItem(self.list.GetItemCount(), row["starts_at"].strftime("%m/%d/%Y %I:%M %p"))
            for column, value in enumerate((row["title"], row.get("location") or "", row["status"].title(),
                                            "" if row.get("total_head_count") is None else str(row["total_head_count"])), 1):
                self.list.SetItem(index, column, value)

    def on_new(self, _event):
        dialog = NewGroupMeetingDialog(self, self.group_service.group(self.group_id))
        try:
            if dialog.ShowModal() == wx.ID_OK: self.service.create_meeting(self.group_id, dialog.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Create Meeting", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_attendance(self, _event):
        selected = self.list.GetFirstSelected()
        if selected < 0: return
        dialog = GroupAttendanceDialog(self, self.service, self.rows[selected]["id"])
        try: dialog.ShowModal()
        finally: dialog.Destroy(); self.refresh()

    def _selected_meeting(self):
        selected = self.list.GetFirstSelected()
        return self.rows[selected] if 0 <= selected < len(self.rows) else None

    def on_reschedule(self, _event):
        meeting = self._selected_meeting()
        if meeting is None: return
        dialog = NewGroupMeetingDialog(self, self.group_service.group(self.group_id), meeting)
        try:
            if dialog.ShowModal() == wx.ID_OK: self.service.reschedule_meeting(meeting["id"], dialog.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Reschedule Meeting", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_cancel(self, _event):
        meeting = self._selected_meeting()
        if meeting is None: return
        if wx.MessageBox(f'Cancel {meeting["title"]} on {meeting["starts_at"]:%m/%d/%Y}?', "Cancel Group Meeting",
                         wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) != wx.YES: return
        try: self.service.cancel_meeting(meeting["id"]); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Cancel Meeting", wx.OK | wx.ICON_ERROR, self)


class GroupAttendanceLauncherDialog(wx.Dialog):
    """Open routine Group attendance directly from the main menu."""

    def __init__(self, parent, connection, session, authorization):
        super().__init__(parent, title="Group Attendance", size=(880, 560), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        from group_repository import MariaDBGroupRepository
        from group_service import GroupService
        group_repository = MariaDBGroupRepository(connection)
        self.group_service = GroupService(group_repository, session, authorization)
        self.service = GroupMeetingService(MariaDBGroupMeetingRepository(connection), self.group_service, session, authorization)
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(panel, label="Group Attendance"); font = title.GetFont(); font.MakeBold(); font.SetPointSize(font.GetPointSize() + 2); title.SetFont(font)
        outer.Add(title, 0, wx.ALL, 14)
        filters = wx.BoxSizer(wx.HORIZONTAL)
        filters.Add(wx.StaticText(panel, label="Church"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        churches = group_repository.churches(); self.church = wx.Choice(panel, choices=[str(row[1]) for row in churches]); self.church.rows = list(churches)
        if churches: self.church.SetSelection(0)
        filters.Add(self.church, 1, wx.RIGHT, 12)
        filters.Add(wx.StaticText(panel, label="Group"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.group = wx.Choice(panel); self.group.rows = []; filters.Add(self.group, 1)
        outer.Add(filters, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for index, (label, width) in enumerate((("Date and time", 180), ("Meeting", 280), ("Location", 190), ("Status", 100), ("Head count", 90))):
            self.list.InsertColumn(index, label, width=width)
        outer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 14)
        buttons = wx.BoxSizer(wx.HORIZONTAL); self.open = wx.Button(panel, label="Record Attendance...")
        buttons.Add(self.open); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel, wx.ID_CLOSE, "Close"))
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 14); panel.SetSizer(outer)
        self.church.Bind(wx.EVT_CHOICE, self.refresh_groups); self.group.Bind(wx.EVT_CHOICE, self.refresh_meetings)
        self.open.Bind(wx.EVT_BUTTON, self.on_open); self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open)
        self.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE), id=wx.ID_CLOSE)
        self.refresh_groups()

    def refresh_groups(self, _event=None):
        church_id = _selected_id(self.church)
        rows = self.group_service.list_groups(church_id, "ACTIVE") if church_id else []
        self.group.Set([row["name"] for row in rows]); self.group.rows = [(row["id"], row["name"]) for row in rows]
        if rows: self.group.SetSelection(0)
        self.refresh_meetings()

    def refresh_meetings(self, _event=None):
        group_id = _selected_id(self.group)
        self.rows = self.service.meetings(group_id) if group_id else []; self.list.DeleteAllItems()
        for row in self.rows:
            index = self.list.InsertItem(self.list.GetItemCount(), row["starts_at"].strftime("%m/%d/%Y %I:%M %p"))
            for column, value in enumerate((row["title"], row.get("location") or "", row["status"].title(),
                                            "" if row.get("total_head_count") is None else str(row["total_head_count"])), 1):
                self.list.SetItem(index, column, value)

    def on_open(self, _event):
        selected = self.list.GetFirstSelected()
        if selected < 0: return
        dialog = GroupAttendanceDialog(self, self.service, self.rows[selected]["id"])
        try: dialog.ShowModal()
        finally: dialog.Destroy(); self.refresh_meetings()


def show_group_attendance(parent, connection, session, authorization):
    """Open direct Group attendance selection from the main menu."""
    dialog = GroupAttendanceLauncherDialog(parent, connection, session, authorization)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
