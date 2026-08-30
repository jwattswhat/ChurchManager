"""Friendly prayer and announcement editors with natural-language schedules."""

from datetime import date, datetime, timedelta

import wx
import wx.adv

from bulletin_orders import portable_connection
from pastoral_care_dialog import show_new_pastoral_follow_up
from sunday_content_rules import (
    EVERY_SUNDAY, describe_rule, next_occurrences, occurs_in_service_week,
    parse_schedule, service_week,
)


def _date_to_wx(value):
    value = value or date.today()
    return wx.DateTime.FromDMY(value.day, value.month - 1, value.year)


def _wx_to_date(value):
    return date(value.GetYear(), value.GetMonth() + 1, value.GetDay())


class SundayContentRepository:
    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def churches(self):
        return self.all("SELECT ID,Church FROM tblChurch ORDER BY Church,ID")

    def categories(self, kind):
        field = "PrayerCategory" if kind == "prayer" else "AnnouncementCategory"
        values = []
        for row in self.all("SELECT Choices FROM tblChoices WHERE Field=? ORDER BY ID", (field,)):
            text = str(row[0] or "").replace("[", "").replace("]", "")
            for value in text.replace(",", "\n").splitlines():
                value = value.strip().strip("'\"")
                if value and value not in values:
                    values.append(value)
        return values

    def rows(self, kind):
        if kind == "prayer":
            return self.all(
                "SELECT ID,ChurchID,PrayerCategory,RequestFor,RequestBy,ScheduleText,ScheduleRule,"
                "StartDate,EndDate,COALESCE(Note,'') FROM tblPrayer "
                "ORDER BY PrayerCategory,RequestFor,ID"
            )
        return self.all(
            "SELECT ID,ChurchID,AnnouncementCategory,Announcement,RequestBy,ScheduleText,ScheduleRule,"
            "StartDate,EndDate,COALESCE(Note,'') FROM tblAnnouncement "
            "ORDER BY AnnouncementCategory,Announcement,ID"
        )

    def save(self, kind, item_id, values):
        church_id, category, content, requested_by, schedule_text, rule, start, end, note = values
        cursor = self.connection.cursor()
        try:
            if kind == "prayer":
                fields = (church_id, category, category, content, requested_by, schedule_text, rule, start, end, note)
                if item_id is None:
                    cursor.execute(
                        "INSERT INTO tblPrayer (ChurchID,PrayerCategory,Request,RequestFor,RequestBy,"
                        "ScheduleText,ScheduleRule,StartDate,EndDate,Note) VALUES (?,?,?,?,?,?,?,?,?,?)", fields,
                    )
                else:
                    cursor.execute(
                        "UPDATE tblPrayer SET ChurchID=?,PrayerCategory=?,Request=?,RequestFor=?,RequestBy=?,"
                        "ScheduleText=?,ScheduleRule=?,StartDate=?,EndDate=?,Note=? WHERE ID=?", fields + (item_id,),
                    )
            else:
                fields = (church_id, category, content, requested_by, schedule_text, rule, start, end, note)
                if item_id is None:
                    cursor.execute(
                        "INSERT INTO tblAnnouncement (ChurchID,AnnouncementCategory,Announcement,RequestBy,"
                        "ScheduleText,ScheduleRule,StartDate,EndDate,Note) VALUES (?,?,?,?,?,?,?,?,?)", fields,
                    )
                else:
                    cursor.execute(
                        "UPDATE tblAnnouncement SET ChurchID=?,AnnouncementCategory=?,Announcement=?,RequestBy=?,"
                        "ScheduleText=?,ScheduleRule=?,StartDate=?,EndDate=?,Note=? WHERE ID=?", fields + (item_id,),
                    )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def delete(self, kind, item_id):
        cursor = self.connection.cursor()
        try:
            if kind == "prayer":
                cursor.execute("DELETE FROM tblPrayer WHERE ID=?", (item_id,))
            else:
                cursor.execute("DELETE FROM tblAnnouncement WHERE ID=?", (item_id,))
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def preview(self, kind, church_id, report_date):
        week_start, week_end = service_week(report_date)
        if kind == "prayer":
            rows = self.all(
                "SELECT PrayerCategory,RequestFor,ScheduleRule,StartDate,EndDate "
                "FROM rpt_sunday_prayer WHERE ChurchID=? ORDER BY PrayerCategory,RequestFor",
                (church_id,),
            )
        else:
            rows = self.all(
                "SELECT AnnouncementCategory,Announcement,ScheduleRule,StartDate,EndDate "
                "FROM rpt_sunday_announcement WHERE ChurchID=? "
                "ORDER BY AnnouncementCategory,Announcement",
                (church_id,),
            )
        return [
            row for row in rows
            if occurs_in_service_week(row[2], report_date, row[3], row[4])
        ]

    def services_for_week(self, church_id, value):
        week_start, week_end = service_week(value)
        return self.all(
            "SELECT DateTime,COALESCE(LiturgicalDate,''),COALESCE(Location,'') "
            "FROM tblService WHERE ChurchID=? AND DateTime>=? AND DateTime<? "
            "ORDER BY DateTime,ID",
            (church_id, week_start, week_end + timedelta(days=1)),
        )


class SundayContentEditDialog(wx.Dialog):
    def __init__(self, parent, repository, kind, row=None):
        title = "Prayer" if kind == "prayer" else "Announcement"
        super().__init__(parent, title=title, size=(680, 660), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository, self.kind, self.row = repository, kind, row
        self.rule = row[6] if row else EVERY_SUNDAY
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        form = wx.FlexGridSizer(cols=2, vgap=8, hgap=12); form.AddGrowableCol(1, 1)
        self.churches = repository.churches(); self.church = wx.Choice(panel, choices=[r[1] for r in self.churches])
        self.categories = repository.categories(kind)
        self.heading = wx.Choice(panel, choices=self.categories)
        self.content = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.content.SetMinSize((-1, 130)); self.requested_by = wx.TextCtrl(panel)
        for label, control in (
            ("Church", self.church), ("Category", self.heading),
            ("Prayer request" if kind == "prayer" else "Announcement", self.content),
            ("Requested by", self.requested_by),
        ):
            form.Add(wx.StaticText(panel, label=label + ":"), 0, wx.ALIGN_TOP)
            form.Add(control, 1, wx.EXPAND)
        outer.Add(form, 0, wx.EXPAND | wx.ALL, 12)
        schedule_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Schedule")
        self.schedule = wx.TextCtrl(panel)
        self.schedule.SetHint("Examples: Every Sunday; First and third Sundays of each month; Every Christmas Eve")
        self.schedule.Bind(wx.EVT_KILL_FOCUS, self.on_schedule)
        schedule_box.Add(self.schedule, 0, wx.EXPAND | wx.ALL, 8)
        self.schedule_text = wx.StaticText(panel)
        self.schedule_text.SetForegroundColour(wx.Colour(0, 90, 190))
        schedule_box.Add(self.schedule_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        self.schedule_preview = wx.StaticText(panel)
        schedule_box.Add(self.schedule_preview, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        bounds = wx.BoxSizer(wx.HORIZONTAL)
        self.use_start = wx.CheckBox(panel, label="Starts"); self.start = wx.adv.DatePickerCtrl(panel, style=wx.adv.DP_DROPDOWN)
        self.use_end = wx.CheckBox(panel, label="Ends"); self.end = wx.adv.DatePickerCtrl(panel, style=wx.adv.DP_DROPDOWN)
        for control in (self.use_start, self.start, self.use_end, self.end): bounds.Add(control, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        schedule_box.Add(bounds, 0, wx.ALL, 8); outer.Add(schedule_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        outer.Add(wx.StaticText(panel, label="Internal note:"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 12)
        self.note = wx.TextCtrl(panel, style=wx.TE_MULTILINE); outer.Add(self.note, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        buttons = wx.StdDialogButtonSizer()
        for button_id in (wx.ID_OK, wx.ID_CANCEL):
            button = wx.Button(panel, button_id); button.Bind(wx.EVT_BUTTON, lambda _e, value=button_id: self.EndModal(value)); buttons.AddButton(button)
        buttons.Realize(); outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 12); panel.SetSizer(outer)
        self._load()

    def _load(self):
        self.church.SetSelection(0 if self.churches else wx.NOT_FOUND)
        self.schedule.SetValue(str(self.row[5] if self.row else describe_rule(self.rule)))
        self._interpret_schedule(show_error=False)
        if not self.row: return
        self.church.SetSelection(next((i for i, row in enumerate(self.churches) if row[0] == self.row[1]), 0))
        category = str(self.row[2] or "")
        self.heading.SetSelection(self.categories.index(category) if category in self.categories else wx.NOT_FOUND)
        self.content.SetValue(str(self.row[3] or "")); self.requested_by.SetValue(str(self.row[4] or ""))
        self.use_start.SetValue(self.row[7] is not None); self.use_end.SetValue(self.row[8] is not None)
        if self.row[7]: self.start.SetValue(_date_to_wx(self.row[7]))
        if self.row[8]: self.end.SetValue(_date_to_wx(self.row[8]))
        self.note.SetValue(str(self.row[9] or ""))

    def _interpret_schedule(self, show_error=True):
        try:
            canonical, rule = parse_schedule(self.schedule.GetValue())
            self.rule = rule
            self.schedule.SetValue(canonical)
            self.schedule_text.SetLabel(f"ChurchManager understands this as: {canonical}")
            dates = next_occurrences(rule, date.today(), 3)
            self.schedule_preview.SetLabel(
                "Next dates: " + ", ".join(value.strftime("%B %d, %Y").replace(" 0", " ") for value in dates)
                if dates else "No future occurrences."
            )
            return canonical, rule
        except ValueError as error:
            self.schedule_text.SetLabel(str(error))
            self.schedule_preview.SetLabel("")
            if show_error:
                self.schedule.SetFocus()
            raise

    def on_schedule(self, event):
        try:
            self._interpret_schedule(show_error=False)
        except ValueError:
            pass
        event.Skip()

    def values(self):
        if self.church.GetSelection() < 0: raise ValueError("Select a church.")
        if self.heading.GetSelection() < 0: raise ValueError("Select a category.")
        if not self.content.GetValue().strip(): raise ValueError("Enter the prayer request or announcement.")
        schedule_text, rule = self._interpret_schedule()
        start = _wx_to_date(self.start.GetValue()) if self.use_start.GetValue() else None
        end = _wx_to_date(self.end.GetValue()) if self.use_end.GetValue() else None
        if start and end and end < start: raise ValueError("The ending date cannot be before the starting date.")
        return (self.churches[self.church.GetSelection()][0], self.categories[self.heading.GetSelection()], self.content.GetValue().strip(), self.requested_by.GetValue().strip() or None, schedule_text, rule, start, end, self.note.GetValue().strip() or None)


class SundayContentManagerDialog(wx.Dialog):
    def __init__(self, parent, connection, kind, session=None, authorization=None):
        title = "Prayers" if kind == "prayer" else "Announcements"
        super().__init__(parent, title=title, size=(920, 600), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository, self.kind, self.rows = SundayContentRepository(connection), kind, []
        self.session, self.authorization = session, authorization
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(panel, label="Schedules are shown in plain language. Double-click an item to edit it.")
        note.SetForegroundColour(wx.Colour(0, 90, 190)); outer.Add(note, 0, wx.ALL, 10)
        self.grid = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (("Category", 190), ("Content", 300), ("Schedule", 245), ("Dates", 150)):
            self.grid.AppendColumn(label, width=width)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit); outer.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        actions = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (("Add...", self.on_add), ("Edit...", self.on_edit), ("Delete", self.on_delete)):
            button = wx.Button(panel, label=label); button.Bind(wx.EVT_BUTTON, handler); actions.Add(button, 0, wx.RIGHT, 8)
        if kind == "prayer" and session is not None and authorization is not None and authorization.has_permission("pastoral.care.create"):
            follow_up = wx.Button(panel, label="Create Care Follow-up...")
            follow_up.Bind(wx.EVT_BUTTON, self.on_care_follow_up)
            actions.Add(follow_up, 0, wx.RIGHT, 8)
        actions.AddStretchSpacer(); actions.Add(wx.Button(panel, wx.ID_CANCEL, "Close")); outer.Add(actions, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer); self.refresh()

    def refresh(self):
        self.rows = self.repository.rows(self.kind); self.grid.DeleteAllItems()
        for index, row in enumerate(self.rows):
            item = self.grid.InsertItem(index, str(row[2] or "")); self.grid.SetItem(item, 1, str(row[3] or "").replace("\n", " "))
            self.grid.SetItem(item, 2, str(row[5] or describe_rule(row[6]))); dates = ""
            if row[7]: dates += f"From {row[7]}"
            if row[8]: dates += ("  " if dates else "") + f"Through {row[8]}"
            self.grid.SetItem(item, 3, dates)

    def selected(self):
        index = self.grid.GetFirstSelected(); return self.rows[index] if index >= 0 else None

    def _edit(self, row):
        dialog = SundayContentEditDialog(self, self.repository, self.kind, row)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.repository.save(self.kind, row[0] if row else None, dialog.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error), "Unable to Save", wx.OK | wx.ICON_ERROR, self)
        finally: dialog.Destroy()

    def on_add(self, _event): self._edit(None)
    def on_edit(self, _event):
        row = self.selected()
        if row: self._edit(row)
    def on_delete(self, _event):
        row = self.selected()
        if row and wx.MessageBox("Delete the selected item?", "Delete", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) == wx.YES:
            self.repository.delete(self.kind, row[0]); self.refresh()

    def on_care_follow_up(self, _event):
        row = self.selected()
        if row is None:
            wx.MessageBox("Select a prayer request first.", "Prayers", wx.OK | wx.ICON_INFORMATION, self)
            return
        show_new_pastoral_follow_up(
            self, self.repository.connection, self.session, self.authorization,
            {
                "church_id": row[1],
                "category": "Prayer Follow-up",
                "source": "PRAYER_REQUEST",
                "safe_summary": "Follow up from prayer-request review.",
            },
        )


class SundayContentPreviewDialog(wx.Dialog):
    def __init__(self, parent, connection, kind, initial_date, generate_handler):
        title = "Weekly Prayers Preview" if kind == "prayer" else "Weekly Announcements Preview"
        super().__init__(parent, title=title, size=(850, 600), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository, self.kind, self.generate_handler = SundayContentRepository(connection), kind, generate_handler
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        date_row = wx.BoxSizer(wx.HORIZONTAL)
        self.churches=self.repository.churches()
        date_row.Add(wx.StaticText(panel,label="Church:"),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,8)
        self.church=wx.Choice(panel,choices=[row[1] for row in self.churches])
        if self.churches: self.church.SetSelection(0)
        self.church.Bind(wx.EVT_CHOICE,self.refresh)
        date_row.Add(self.church,1,wx.RIGHT,16)
        date_row.Add(wx.StaticText(panel, label="Service week containing:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.report_date = wx.adv.DatePickerCtrl(panel, style=wx.adv.DP_DROPDOWN)
        self.report_date.SetValue(_date_to_wx(initial_date)); self.report_date.Bind(wx.adv.EVT_DATE_CHANGED, self.refresh)
        date_row.Add(self.report_date, 0); date_row.AddStretchSpacer()
        self.count = wx.StaticText(panel); date_row.Add(self.count, 0, wx.ALIGN_CENTER_VERTICAL)
        outer.Add(date_row, 0, wx.EXPAND | wx.ALL, 10)
        self.week_label = wx.StaticText(panel); self.week_label.SetFont(self.week_label.GetFont().Bold())
        self.service_label = wx.StaticText(panel); self.service_label.SetForegroundColour(wx.Colour(0,90,190))
        outer.Add(self.week_label,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        outer.Add(self.service_label,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        self.grid = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.grid.AppendColumn("Category", width=220); self.grid.AppendColumn("Included content", width=570)
        outer.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        actions = wx.BoxSizer(wx.HORIZONTAL); actions.AddStretchSpacer()
        generate = wx.Button(panel, label="Generate Plain Text"); generate.Bind(wx.EVT_BUTTON, self.on_generate); actions.Add(generate, 0, wx.RIGHT, 8)
        actions.Add(wx.Button(panel, wx.ID_CANCEL, "Close")); outer.Add(actions, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer); self.refresh()

    def selected_date(self): return _wx_to_date(self.report_date.GetValue())
    def selected_church_id(self):
        return self.churches[self.church.GetSelection()][0] if self.church.GetSelection()>=0 else None

    def refresh(self, _event=None):
        selected=self.selected_date(); week_start,week_end=service_week(selected)
        church_id=self.selected_church_id()
        rows = self.repository.preview(self.kind,church_id,selected) if church_id is not None else []
        self.grid.DeleteAllItems()
        for index, row in enumerate(rows):
            item = self.grid.InsertItem(index, str(row[0] or "")); self.grid.SetItem(item, 1, str(row[1] or "").replace("\n", " "))
        self.count.SetLabel(f"{len(rows)} item{'s' if len(rows) != 1 else ''} included")
        self.week_label.SetLabel(
            f"Service week: {week_start.strftime('%B')} {week_start.day} through "
            f"{week_end.strftime('%B')} {week_end.day}, {week_end.year}"
        )
        services=self.repository.services_for_week(church_id,selected) if church_id is not None else []
        if services:
            names=[f"{row[0].strftime('%a %m/%d %I:%M %p')} {row[1] or row[2]}".strip() for row in services]
            self.service_label.SetLabel("Services: " + "  |  ".join(names))
        else:
            self.service_label.SetLabel("No worship services are currently scheduled for this week.")

    def on_generate(self, _event):
        if self.selected_church_id() is None:
            wx.MessageBox("Select a church.","Weekly Output",wx.OK|wx.ICON_WARNING,self); return
        self.generate_handler(self.selected_date(),self.selected_church_id())


def show_sunday_preview(parent, connection, kind, initial_date, generate_handler):
    dialog = SundayContentPreviewDialog(parent, connection, kind, initial_date, generate_handler)
    try: return dialog.ShowModal()
    finally: dialog.Destroy()


def show_prayers(parent, connection, session=None, authorization=None):
    dialog = SundayContentManagerDialog(parent, connection, "prayer", session, authorization)
    try: return dialog.ShowModal()
    finally: dialog.Destroy()


def show_announcements(parent, connection):
    dialog = SundayContentManagerDialog(parent, connection, "announcement")
    try: return dialog.ShowModal()
    finally: dialog.Destroy()
