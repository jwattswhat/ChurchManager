"""Combined attendance-event and individual-attendance editor."""

from __future__ import annotations

from datetime import datetime

import wx
import wx.adv
import wx.grid

from bulletin_orders import portable_connection
from ui_dimensions import DATE_PICKER_SIZE, TIME_PICKER_SIZE


class AttendanceRepository:
    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def one(self, sql, values=()):
        rows = self.all(sql, values)
        return rows[0] if rows else None

    def events(self):
        return self.all(
            "SELECT ae.ID,ae.DateTime,COALESCE(ae.Description,''),"
            "COALESCE(ae.AttendanceType,''),COALESCE(ae.HandCount,0),COUNT(a.ID),"
            "ae.ServiceID FROM tblAttendanceEvent ae LEFT JOIN tblAttendance a "
            "ON a.AttendanceEventID=ae.ID GROUP BY ae.ID "
            "ORDER BY ae.DateTime DESC,ae.ID DESC"
        )

    def event(self, event_id):
        return self.one(
            "SELECT ae.ID,ae.ChurchID,ae.ServiceID,ae.DateTime,"
            "COALESCE(ae.Description,''),COALESCE(ae.AttendanceType,''),"
            "ae.CommunionOffered,COALESCE(ae.HandCount,0),"
            "COALESCE(ae.HandCountCommunion,0),COALESCE(ae.Note,''),"
            "COALESCE(c.Church,''),COALESCE(s.LiturgicalDate,'') "
            "FROM tblAttendanceEvent ae JOIN tblChurch c ON c.ID=ae.ChurchID "
            "LEFT JOIN tblService s ON s.ID=ae.ServiceID WHERE ae.ID=?", (event_id,),
        )

    def people(self, event_id, church_id):
        return self.all(
            "SELECT p.ID,TRIM(CONCAT_WS(' ',NULLIF(p.FirstName,''),"
            "NULLIF(p.MiddleName,''),NULLIF(p.LastName,''))),"
            "CASE WHEN p.Member=1 THEN 'Member' ELSE 'Visitor' END,"
            "CASE WHEN a.ID IS NULL THEN 0 ELSE 1 END,COALESCE(a.Communion,0),"
            "COALESCE(a.Note,'') FROM tblPerson p LEFT JOIN tblAttendance a "
            "ON a.PersonID=p.ID AND a.AttendanceEventID=? "
            "WHERE p.ChurchID=? ORDER BY p.LastName,p.FirstName,p.ID",
            (event_id, church_id),
        )

    def choices(self, field):
        values = []
        for row in self.all("SELECT Choices FROM tblChoices WHERE Field=? ORDER BY ID", (field,)):
            for value in str(row[0] or "").replace("[", "").replace("]", "").replace(",", "\n").splitlines():
                value = value.strip().strip("'\"")
                if value and value not in values:
                    values.append(value)
        return values

    def churches(self):
        return self.all("SELECT ID,Church FROM tblChurch ORDER BY Church,ID")

    def create_event(self, church_id):
        attendance_types = self.choices("AttendanceType")
        attendance_type = attendance_types[0] if attendance_types else "Worship Service"
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO tblAttendanceEvent "
                "(ChurchID,DateTime,Description,AttendanceType,CommunionOffered,"
                "HandCount,HandCountCommunion) VALUES (?,?,?,?,0,0,0)",
                (church_id, datetime.now().replace(microsecond=0), "", attendance_type),
            )
            event_id = cursor.lastrowid
            self.connection.commit()
            return event_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def save(self, event_id, event_values, people):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE tblAttendanceEvent SET DateTime=?,Description=?,AttendanceType=?,"
                "CommunionOffered=?,HandCount=?,HandCountCommunion=?,Note=? WHERE ID=?",
                event_values + (event_id,),
            )
            cursor.execute(
                "SELECT ID,PersonID FROM tblAttendance WHERE AttendanceEventID=?", (event_id,),
            )
            existing = {row[1]: row[0] for row in cursor.fetchall()}
            wanted = {row["person_id"]: row for row in people if row["present"]}
            for person_id, attendance_id in existing.items():
                if person_id not in wanted:
                    cursor.execute("DELETE FROM tblAttendance WHERE ID=?", (attendance_id,))
            for person_id, row in wanted.items():
                if person_id in existing:
                    cursor.execute(
                        "UPDATE tblAttendance SET Communion=?,Note=? WHERE ID=?",
                        (int(row["communion"]), row["note"] or None, existing[person_id]),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO tblAttendance "
                        "(PersonID,AttendanceEventID,Communion,Note) VALUES (?,?,?,?)",
                        (person_id, event_id, int(row["communion"]), row["note"] or None),
                    )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()


class AttendanceEditorDialog(wx.Dialog):
    def __init__(self, parent, repository, event_id):
        super().__init__(parent, title="Attendance", size=(1000, 730),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = repository
        self.event_id = event_id
        self.event = repository.event(event_id)
        if not self.event:
            raise ValueError("The selected Attendance Event is unavailable.")
        self.people = [
            {"person_id": row[0], "name": row[1], "category": row[2],
             "present": bool(row[3]), "communion": bool(row[4]), "note": row[5] or ""}
            for row in repository.people(event_id, self.event[1])
        ]
        self.visible_people = []
        self._build()
        self._load()
        self.CentreOnParent()

    def _build(self):
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        banner = wx.StaticText(
            panel, label="Record the complete attendance for this event, then select Save Attendance.",
        )
        banner.SetForegroundColour(wx.Colour(0, 90, 190))
        outer.Add(banner, 0, wx.ALL, 10)
        info = wx.FlexGridSizer(cols=4, vgap=7, hgap=8)
        info.AddGrowableCol(1, 1); info.AddGrowableCol(3, 1)
        self.church = wx.StaticText(panel)
        self.service = wx.StaticText(panel)
        self.description = wx.TextCtrl(panel)
        self.attendance_type = wx.Choice(panel, choices=repository.choices("AttendanceType"))
        self.service_date = wx.adv.DatePickerCtrl(panel, size=DATE_PICKER_SIZE, style=wx.adv.DP_DROPDOWN)
        self.service_time = wx.adv.TimePickerCtrl(panel, size=TIME_PICKER_SIZE)
        self.communion_offered = wx.CheckBox(panel)
        self.hand_count = wx.SpinCtrl(panel, min=0, max=100000)
        self.hand_count.Bind(wx.EVT_SPINCTRL, lambda _event: self._refresh_summary())
        self.hand_count.Bind(wx.EVT_TEXT, lambda _event: self._refresh_summary())
        self.communion_count = wx.SpinCtrl(panel, min=0, max=100000)
        for label, control in (
            ("Church:", self.church), ("Linked service:", self.service),
            ("Description:", self.description), ("Attendance type:", self.attendance_type),
        ):
            info.Add(wx.StaticText(panel, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
            info.Add(control, 1, wx.EXPAND)
        date_row = wx.BoxSizer(wx.HORIZONTAL); date_row.Add(self.service_date, 0, wx.RIGHT, 8); date_row.Add(self.service_time)
        info.Add(wx.StaticText(panel, label="Date and time:"), 0, wx.ALIGN_CENTER_VERTICAL); info.Add(date_row, 1, wx.EXPAND)
        info.Add(wx.StaticText(panel, label="Communion offered:"), 0, wx.ALIGN_CENTER_VERTICAL); info.Add(self.communion_offered)
        info.Add(wx.StaticText(panel, label="Attendance hand count:"), 0, wx.ALIGN_CENTER_VERTICAL); info.Add(self.hand_count)
        info.Add(wx.StaticText(panel, label="Communion hand count:"), 0, wx.ALIGN_CENTER_VERTICAL); info.Add(self.communion_count)
        outer.Add(info, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        note_row = wx.BoxSizer(wx.HORIZONTAL)
        note_row.Add(wx.StaticText(panel, label="Event note:"), 0, wx.ALIGN_TOP | wx.RIGHT, 8)
        self.note = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, 60))
        note_row.Add(self.note, 1, wx.EXPAND)
        outer.Add(note_row, 0, wx.EXPAND | wx.ALL, 10)
        search_row = wx.BoxSizer(wx.HORIZONTAL)
        search_row.Add(wx.StaticText(panel, label="Find person:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.search = wx.TextCtrl(panel)
        self.search.Bind(wx.EVT_TEXT, self.on_search)
        search_row.Add(self.search, 1)
        self.summary = wx.StaticText(panel)
        search_row.Add(self.summary, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 16)
        outer.Add(search_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.grid = wx.grid.Grid(panel)
        self.grid.CreateGrid(0, 5)
        for column, (label, width) in enumerate(
            (("Present", 70), ("Person", 310), ("Member / Visitor", 125),
             ("Communion", 90), ("Note", 300))
        ):
            self.grid.SetColLabelValue(column, label); self.grid.SetColSize(column, width)
        self.grid.SetColFormatBool(0); self.grid.SetColFormatBool(3)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_cell_changed)
        outer.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        actions = wx.BoxSizer(wx.HORIZONTAL)
        save = wx.Button(panel, label="Save Attendance")
        save.Bind(wx.EVT_BUTTON, self.on_save); actions.Add(save)
        actions.AddStretchSpacer()
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE)); actions.Add(close)
        outer.Add(actions, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer)

    def _load(self):
        row = self.event
        self.church.SetLabel(str(row[10]))
        self.service.SetLabel(str(row[11] or "Not linked to a Worship Service"))
        self.description.SetValue(str(row[4]))
        self.attendance_type.SetStringSelection(str(row[5]))
        self.communion_offered.SetValue(bool(row[6]))
        self.hand_count.SetValue(int(row[7] or 0)); self.communion_count.SetValue(int(row[8] or 0))
        self.note.SetValue(str(row[9] or ""))
        when = row[3] or datetime.now()
        self.service_date.SetValue(wx.DateTime.FromDMY(when.day, when.month - 1, when.year))
        clock = wx.DateTime.Now(); clock.SetHour(when.hour); clock.SetMinute(when.minute); clock.SetSecond(when.second)
        self.service_time.SetValue(clock)
        if row[2] is not None:
            for control in (self.description, self.attendance_type, self.service_date,
                            self.service_time, self.communion_offered):
                control.Disable()
        self._populate_grid()

    def _capture_grid(self):
        for grid_row, person in enumerate(self.visible_people):
            person["present"] = self.grid.GetCellValue(grid_row, 0) == "1"
            person["communion"] = self.grid.GetCellValue(grid_row, 3) == "1"
            person["note"] = self.grid.GetCellValue(grid_row, 4).strip()

    def _populate_grid(self):
        search = self.search.GetValue().strip().casefold()
        self.visible_people = [row for row in self.people if not search or search in row["name"].casefold()]
        if self.grid.GetNumberRows():
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        if self.visible_people:
            self.grid.AppendRows(len(self.visible_people))
        for index, person in enumerate(self.visible_people):
            self.grid.SetCellValue(index, 0, "1" if person["present"] else "")
            self.grid.SetCellValue(index, 1, person["name"]); self.grid.SetReadOnly(index, 1)
            self.grid.SetCellValue(index, 2, person["category"]); self.grid.SetReadOnly(index, 2)
            self.grid.SetCellValue(index, 3, "1" if person["communion"] else "")
            self.grid.SetCellValue(index, 4, person["note"])
        self._refresh_summary()

    def _refresh_summary(self):
        named = sum(1 for person in self.people if person["present"])
        hand = self.hand_count.GetValue()
        if named > hand:
            self.summary.SetLabel(f"Hand count: {hand}  ·  Known people: {named}  ·  Check totals")
            self.summary.SetForegroundColour(wx.RED)
        else:
            self.summary.SetLabel(
                f"Hand count: {hand}  ·  Known people: {named}  ·  Unnamed: {hand - named}"
            )
            self.summary.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))

    def on_search(self, _event):
        self._capture_grid(); self._populate_grid()

    def on_cell_changed(self, event):
        if event.GetCol() == 3 and self.grid.GetCellValue(event.GetRow(), 3) == "1":
            self.grid.SetCellValue(event.GetRow(), 0, "1")
        self._capture_grid(); self._refresh_summary(); event.Skip()

    def on_save(self, _event):
        self._capture_grid()
        known = sum(1 for row in self.people if row["present"])
        known_communion = sum(1 for row in self.people if row["communion"])
        if self.hand_count.GetValue() < known:
            wx.MessageBox("The attendance hand count cannot be less than the known people marked present.",
                          "Attendance Validation", wx.OK | wx.ICON_WARNING, self)
            return
        if self.communion_count.GetValue() < known_communion:
            wx.MessageBox("The Communion hand count cannot be less than the known people marked as receiving Communion.",
                          "Attendance Validation", wx.OK | wx.ICON_WARNING, self)
            return
        if self.communion_count.GetValue() > self.hand_count.GetValue():
            wx.MessageBox("The Communion hand count cannot exceed the attendance hand count.",
                          "Attendance Validation", wx.OK | wx.ICON_WARNING, self)
            return
        if not self.communion_offered.GetValue() and any(row["communion"] for row in self.people):
            wx.MessageBox("Communion cannot be recorded because this event did not offer Communion.",
                          "Attendance Validation", wx.OK | wx.ICON_WARNING, self)
            return
        if not self.communion_offered.GetValue() and self.communion_count.GetValue():
            wx.MessageBox("The Communion hand count must be zero when Communion was not offered.",
                          "Attendance Validation", wx.OK | wx.ICON_WARNING, self)
            return
        date_value, time_value = self.service_date.GetValue(), self.service_time.GetValue()
        when = datetime(date_value.GetYear(), date_value.GetMonth() + 1, date_value.GetDay(),
                        time_value.GetHour(), time_value.GetMinute(), time_value.GetSecond())
        values = (
            when, self.description.GetValue().strip() or None,
            self.attendance_type.GetStringSelection() or None,
            int(self.communion_offered.GetValue()), self.hand_count.GetValue(),
            self.communion_count.GetValue(), self.note.GetValue().strip() or None,
        )
        try:
            self.repository.save(self.event_id, values, self.people)
            wx.MessageBox("Attendance was saved.", "Attendance", wx.OK | wx.ICON_INFORMATION, self)
            self.EndModal(wx.ID_OK)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Save Attendance", wx.OK | wx.ICON_ERROR, self)


class AttendanceCatalogDialog(wx.Dialog):
    def __init__(self, parent, connection, authorization=None):
        super().__init__(parent, title="Attendance", size=(880, 560),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = AttendanceRepository(connection)
        self.authorization = authorization
        self.rows = []
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        help_text = wx.StaticText(panel, label="Double-click an event to record or review its attendance.")
        help_text.SetForegroundColour(wx.Colour(0, 90, 190)); outer.Add(help_text, 0, wx.ALL, 10)
        self.grid = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (("Date and time", 165), ("Event", 245), ("Type", 145),
                             ("Hand count", 90), ("Named", 80)):
            self.grid.AppendColumn(label, width=width)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_open); outer.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        new_event = wx.Button(panel, label="New Other Event..."); new_event.Bind(wx.EVT_BUTTON, self.on_new); buttons.Add(new_event, 0, wx.RIGHT, 8)
        open_event = wx.Button(panel, label="Open Attendance"); open_event.Bind(wx.EVT_BUTTON, self.on_open); buttons.Add(open_event)
        buttons.AddStretchSpacer(); close = wx.Button(panel, wx.ID_CLOSE, "Close"); close.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE)); buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10); panel.SetSizer(outer)
        self.refresh(); self.CentreOnParent()

    def refresh(self):
        self.rows = self.repository.events(); self.grid.DeleteAllItems()
        for index, row in enumerate(self.rows):
            when = row[1].strftime("%m/%d/%Y %I:%M %p") if hasattr(row[1], "strftime") else str(row[1])
            item = self.grid.InsertItem(index, when)
            for column, value in enumerate((row[2], row[3], row[4], row[5]), 1):
                self.grid.SetItem(item, column, str(value))

    def on_open(self, _event):
        selected = self.grid.GetFirstSelected()
        if selected < 0:
            wx.MessageBox("Select an Attendance Event first.", "Attendance", wx.OK | wx.ICON_INFORMATION, self); return
        dialog = AttendanceEditorDialog(self, self.repository, self.rows[selected][0])
        try: dialog.ShowModal()
        finally: dialog.Destroy()
        self.refresh()

    def on_new(self, _event):
        if self.authorization is not None:
            try:
                self.authorization.require("attendance.events.manage", operation="Create Attendance Event")
            except Exception as error:
                wx.MessageBox(str(error), "Permission Required", wx.OK | wx.ICON_WARNING, self); return
        churches = self.repository.churches()
        if not churches:
            wx.MessageBox("Create a Church record first.", "Church Required", wx.OK | wx.ICON_WARNING, self); return
        chooser = wx.SingleChoiceDialog(self, "Select the church.", "New Attendance Event", [str(row[1]) for row in churches])
        try:
            if chooser.ShowModal() != wx.ID_OK: return
            event_id = self.repository.create_event(churches[chooser.GetSelection()][0])
        finally:
            chooser.Destroy()
        dialog = AttendanceEditorDialog(self, self.repository, event_id)
        try: dialog.ShowModal()
        finally: dialog.Destroy()
        self.refresh()


def show_attendance(parent, connection, authorization=None):
    dialog = AttendanceCatalogDialog(parent, connection, authorization)
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()
