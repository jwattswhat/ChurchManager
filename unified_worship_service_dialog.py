"""Unified split-panel view of a Worship Service and its weekly order."""

from __future__ import annotations

import json
from datetime import datetime
import wx
import wx.adv

from bulletin_orders import (
    BulletinOrderRepository,
    WeeklyBulletinOrderRepository,
    portable_connection,
)


def normalize_line_sequences(lines):
    """Make displayed list order the complete persisted order."""
    for sequence, line in enumerate(lines, 1):
        line["sequence"] = sequence
    return lines


class UnifiedWorshipServiceRepository:
    def __init__(self, connection):
        self.connection = portable_connection(connection)
        self.templates = BulletinOrderRepository(self.connection)
        self.weekly = WeeklyBulletinOrderRepository(self.connection)

    def one(self, sql, values):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchone()
        finally:
            cursor.close()

    def all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def service(self, service_id):
        return self.one(
            "SELECT s.ID,s.ChurchID,s.DateTime,COALESCE(s.Location,''),s.PropersID,"
            "COALESCE(s.LiturgicalDate,''),s.HolyCommunion,s.BulletinOrderTemplateID,"
            "COALESCE(s.OSNote,''),COALESCE(s.PsalmorIntroit,''),s.SermonID,"
            "COALESCE(s.Bulletin,''),COALESCE(s.CheckListComplete,0),"
            "COALESCE(s.CheckList,'{}'),COALESCE(s.Note,''),COALESCE(t.Name,'Not selected') "
            "FROM tblService s LEFT JOIN tblBulletinOrderTemplate t "
            "ON t.ID=s.BulletinOrderTemplateID WHERE s.ID=?", (service_id,),
        )

    def proper_name(self, proper_id):
        if not proper_id:
            return "Not selected"
        row = self.one(
            "SELECT CONCAT(ls.Name,CASE WHEN COALESCE(p.Cycle,'')='' THEN '' "
            "ELSE CONCAT(' - Year ',p.Cycle) END,' - ',p.LiturgicalDate) "
            "FROM tblPropers p JOIN tblLectionarySystem ls ON ls.ID=p.LectionarySystemID "
            "WHERE p.ID=?", (proper_id,),
        )
        return row[0] if row else "Not selected"

    def sermon_name(self, sermon_id):
        if not sermon_id:
            return "Not selected"
        row = self.one(
            "SELECT CONCAT(ID,' - ',COALESCE(Reference,''),' - ',COALESCE(Title,'')) "
            "FROM tblSermon WHERE ID=?", (sermon_id,),
        )
        return row[0] if row else "Not selected"

    def propers(self, church_id):
        return self.all(
            "SELECT p.ID,CONCAT(ls.Name,CASE WHEN COALESCE(p.Cycle,'')='' THEN '' "
            "ELSE CONCAT(' - Year ',p.Cycle) END,' - ',p.LiturgicalDate) "
            "FROM tblPropers p JOIN tblLectionarySystem ls ON ls.ID=p.LectionarySystemID "
            "WHERE (SELECT PrimaryLectionarySystemID FROM tblChurch WHERE ID=?) IS NULL "
            "OR p.LectionarySystemID=(SELECT PrimaryLectionarySystemID FROM tblChurch WHERE ID=?) "
            "ORDER BY ls.Name,p.Cycle,p.Sort,p.ID", (church_id, church_id),
        )

    def proper_values(self, proper_id):
        readings = self.all(
            "SELECT Reading,Reference FROM tblReading WHERE PropersID=? ORDER BY ID",
            (proper_id,),
        ) if proper_id else []
        hymns = self.all(
            "SELECT s.HymnID,TRIM(CONCAT_WS(' ',h.Hymn,h.Title)),s.SuggestedAs "
            "FROM tblProperHymnSuggestion s JOIN tblHymn h ON h.ID=s.HymnID "
            "WHERE s.PropersID=? ORDER BY s.ID", (proper_id,),
        ) if proper_id else []
        return readings, hymns

    def proper_detail(self, proper_id):
        return self.one(
            "SELECT ls.Name,COALESCE(p.Cycle,''),COALESCE(p.Season,''),"
            "COALESCE(p.LiturgicalDate,''),COALESCE(p.Theme,''),COALESCE(p.Color,''),"
            "COALESCE(p.AltColor,''),COALESCE(p.Introit,''),COALESCE(p.Note,'') "
            "FROM tblPropers p JOIN tblLectionarySystem ls ON ls.ID=p.LectionarySystemID "
            "WHERE p.ID=?", (proper_id,),
        )

    def choice_values(self, field):
        values = []
        for row in self.all(
            "SELECT Choices FROM tblChoices WHERE Field=? ORDER BY ID", (field,),
        ):
            text = str(row[0] or "").replace("[", "").replace("]", "")
            for value in text.replace(",", "\n").splitlines():
                value = value.strip().strip("'\"")
                if value and value not in values:
                    values.append(value)
        return values

    def weekly_hymns(self, service_id):
        return dict(self.all(
            "SELECT ServiceBulletinOrderLineID,HymnID FROM tblHymnUsage "
            "WHERE ServiceID=? AND ServiceBulletinOrderLineID IS NOT NULL",
            (service_id,),
        ))

    def save(self, service_id, service_values, template_id, lines):
        """Persist the service and its complete displayed weekly order atomically."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE tblService SET DateTime=?,Location=?,PropersID=?,LiturgicalDate=?,"
                "HolyCommunion=?,BulletinOrderTemplateID=?,OSNote=?,PsalmorIntroit=?,SermonID=?,"
                "Bulletin=?,CheckListComplete=?,CheckList=?,Note=? WHERE ID=?",
                service_values + (service_id,),
            )
            cursor.execute("SELECT ChurchID FROM tblService WHERE ID=?", (service_id,))
            church_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM tblHymnUsage WHERE ServiceID=?", (service_id,))
            cursor.execute("DELETE FROM tblServiceBulletinOrderLine WHERE ServiceID=?", (service_id,))
            cursor.execute(
                "INSERT INTO tblServiceBulletinOrder (ServiceID,TemplateID) VALUES (?,?) "
                "ON DUPLICATE KEY UPDATE TemplateID=VALUES(TemplateID),GeneratedPlainText=NULL,"
                "GeneratedHtml=NULL,GeneratedAt=NULL", (service_id, template_id),
            )
            for line in normalize_line_sequences(lines):
                cursor.execute(
                    "INSERT INTO tblServiceBulletinOrderLine "
                    "(ServiceID,TemplateLineID,Sequence,Included,LineType,Label,ValueSource,"
                    "ValueKey,WeeklyValue,ReferenceText,StyleName,LabelBold,ValueBold,Italic,"
                    "IndentLevel,TabPosition,TabAlignment,TabLeader,Note) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        service_id, line.get("template_line_id"), line["sequence"],
                        int(line["included"]), line["type"], line["label"], line["source"],
                        line["key"], line["value"] or None, line["reference"] or None,
                        line.get("style") or "Normal", int(bool(line.get("label_bold"))),
                        int(bool(line.get("value_bold"))), int(bool(line.get("italic"))),
                        int(line.get("indent") or 0), line.get("tab_position"),
                        line.get("tab_alignment") or "LEFT", line.get("tab_leader") or "NONE",
                        line.get("note") or None,
                    ),
                )
                weekly_line_id = cursor.lastrowid
                if line.get("hymn_id") is not None:
                    cursor.execute(
                        "INSERT INTO tblHymnUsage "
                        "(ChurchID,ServiceID,ServiceBulletinOrderLineID,HymnID,UsedAs) "
                        "VALUES (?,?,?,?,?)",
                        (church_id, service_id, weekly_line_id, line["hymn_id"], line["key"]),
                    )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def hymns(self, service_id):
        return self.search_hymns(service_id, "", "All fields")

    def hymnal_name(self, service_id):
        row = self.one(
            "SELECT CASE WHEN h.ID IS NULL THEN 'All hymnals' "
            "ELSE CONCAT(h.Hymnal,' - ',h.Title) END FROM tblService s "
            "JOIN tblChurch c ON c.ID=s.ChurchID "
            "LEFT JOIN tblHymnal h ON h.ID=c.PrimaryHymnalID WHERE s.ID=?",
            (service_id,),
        )
        return row[0] if row else "All hymnals"

    def search_hymns(self, service_id, search, search_in):
        columns = {
            "Hymn number": "h.Hymn", "Title": "h.Title", "Bible reference": "h.BibleText",
            "Category": "h.Category", "Notes": "h.Note",
        }
        sql = (
            "SELECT h.ID,COALESCE(h.Hymn,''),COALESCE(h.Title,''),"
            "COALESCE(h.BibleText,''),COALESCE(h.Category,''),COALESCE(h.Note,'') "
            "FROM tblHymn h JOIN tblService s ON s.ID=? "
            "JOIN tblChurch c ON c.ID=s.ChurchID WHERE "
            "(c.PrimaryHymnalID IS NULL OR h.HymnalID=c.PrimaryHymnalID)"
        )
        values = [service_id]
        text = str(search or "").strip()
        if text:
            pattern = "%" + text + "%"
            if search_in in columns:
                sql += " AND " + columns[search_in] + " LIKE ?"
                values.append(pattern)
            else:
                sql += (
                    " AND (h.Hymn LIKE ? OR h.Title LIKE ? OR h.BibleText LIKE ? "
                    "OR h.Category LIKE ? OR h.Note LIKE ?)"
                )
                values.extend([pattern] * 5)
        sql += " ORDER BY h.Hymn,h.Title"
        return self.all(sql, tuple(values))


class UnifiedWorshipServiceEditor(wx.Dialog):
    """First-stage unified editor: one window, independently scrolling panels."""

    def __init__(self, parent, connection, service_id):
        super().__init__(parent, title="Worship Service and Order of Service", size=(1400, 780),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = UnifiedWorshipServiceRepository(connection)
        self.service_id = service_id
        self.record = self.repository.service(service_id)
        if not self.record:
            raise ValueError("The selected Worship Service is unavailable.")
        self.loading = True
        self.template_rows = []
        self.proper_rows = []
        self.sermon_rows = []
        self.working_lines = []
        self._build()
        self._load()
        self.loading = False
        self.CentreOnParent()

    def _build(self):
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        note = wx.StaticText(
            panel,
            label="The weekly Order of Service is on the left; service-specific information is on the right.",
        )
        note.SetForegroundColour(wx.Colour(0, 90, 190))
        outer.Add(note, 0, wx.ALL, 10)

        splitter = wx.SplitterWindow(panel, style=wx.SP_LIVE_UPDATE | wx.SP_3D)
        left = wx.Panel(splitter)
        right = wx.ScrolledWindow(splitter, style=wx.VSCROLL)
        right.SetMinSize((430, -1))
        right.SetScrollRate(0, 12)
        splitter.SplitVertically(left, right, 890)
        splitter.SetMinimumPaneSize(330)
        splitter.SetSashGravity(0.66)

        left_box = wx.BoxSizer(wx.VERTICAL)
        template_row = wx.BoxSizer(wx.HORIZONTAL)
        template_row.Add(wx.StaticText(left, label="Order of Service template:"), 0,
                         wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.template = wx.Choice(left)
        self.template.Bind(wx.EVT_CHOICE, self.on_template)
        template_row.Add(self.template, 1, wx.EXPAND)
        left_box.Add(template_row, 0, wx.EXPAND | wx.ALL, 8)
        self.grid = wx.ListCtrl(left, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (("Service line", 270), ("Weekly value", 300),
                             ("Reference", 150), ("Status", 100)):
            self.grid.AppendColumn(label, width=width)
        left_box.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        line_actions = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (
            ("Edit Line...", self.on_edit_line),
            ("Select Hymn...", self.on_select_hymn),
            ("Move Up", lambda event: self.on_move_line(-1)),
            ("Move Down", lambda event: self.on_move_line(1)),
        ):
            button = wx.Button(left, label=label)
            button.Bind(wx.EVT_BUTTON, handler)
            line_actions.Add(button, 0, wx.RIGHT, 8)
        line_actions.AddStretchSpacer()
        line_actions.Add(wx.StaticText(left, label="Red lines require attention."), 0,
                         wx.ALIGN_CENTER_VERTICAL)
        left_box.Add(line_actions, 0, wx.EXPAND | wx.ALL, 8)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_line)
        left.SetSizer(left_box)

        self.detail_box = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(right, label="Service Details")
        title.SetFont(title.GetFont().Bold())
        self.detail_box.Add(title, 0, wx.ALL, 8)
        self.fields = {}
        for key, label, multiline, inline in (
            ("church", "Church", False, True),
            ("date_time", "Date and time", False, True),
            ("location", "Location", False, True), ("proper", "Proper", False, False),
            ("liturgical", "Printed liturgical title", False, False),
            ("communion", "Holy Communion", False, True),
            ("psalm", "Psalm or Introit", False, True), ("sermon", "Sermon", False, False),
            ("bulletin", "Bulletin", False, False),
            ("check_complete", "Checklist complete", False, True),
            ("checklist", "Checklist", True, False),
            ("note", "Notes for this service", True, False),
            ("os_note", "Order of Service notes (from template - read only)", True, False),
        ):
            self._add_field(right, key, label, multiline, inline)
            if key == "proper":
                view_proper = wx.Button(right, label="View Proper...")
                view_proper.Bind(wx.EVT_BUTTON, self.on_view_proper)
                self.detail_box.Add(view_proper, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        self.fields["os_note"].SetToolTip(
            "This note comes from the selected Order of Service template and cannot be changed here."
        )
        self.fields["os_note"].SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        )
        # Keep controls clear of the native vertical scrollbar. On Windows the
        # scrollbar can consume part of the scrolled window's reported client
        # width after the sizer has calculated its expanding children.
        right_layout = wx.BoxSizer(wx.HORIZONTAL)
        right_layout.Add(self.detail_box, 1, wx.EXPAND)
        right_layout.AddSpacer(32)
        right.SetSizer(right_layout)

        outer.Add(splitter, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        actions = wx.BoxSizer(wx.HORIZONTAL)
        save = wx.Button(panel, label="Save Service")
        save.Bind(wx.EVT_BUTTON, self.on_save)
        actions.Add(save, 0, wx.RIGHT, 8)
        self.save_status = wx.StaticText(panel, label="Changes are not saved until Save Service is selected.")
        self.save_status.SetForegroundColour(wx.Colour(110, 80, 0))
        actions.Add(self.save_status, 0, wx.ALIGN_CENTER_VERTICAL)
        actions.AddStretchSpacer()
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        actions.Add(close)
        outer.Add(actions, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer)

    def _add_field(self, parent, key, label, multiline, inline):
        if key == "date_time":
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(wx.StaticText(parent, label="Service date:", size=(92, -1)), 0,
                    wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            service_date = wx.adv.DatePickerCtrl(
                parent, size=(130, -1), style=wx.adv.DP_DROPDOWN
            )
            row.Add(service_date, 0, wx.RIGHT, 12)
            row.Add(wx.StaticText(parent, label="Time:"), 0,
                    wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            service_time = wx.adv.TimePickerCtrl(parent, size=(115, -1))
            row.Add(service_time, 0)
            self.detail_box.Add(row, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
            self.fields["service_date"] = service_date
            self.fields["service_time"] = service_time
            return
        if key in ("proper", "sermon", "location"):
            control = wx.Choice(parent)
            if key == "proper":
                control.Bind(wx.EVT_CHOICE, self.on_proper)
        elif key in ("communion", "check_complete"):
            control = wx.CheckBox(parent)
        elif key == "bulletin":
            control = wx.FilePickerCtrl(parent, message="Select the bulletin file")
        else:
            readonly = key in ("church", "os_note")
            style = wx.TE_MULTILINE if multiline else 0
            if readonly:
                style |= wx.TE_READONLY
            size = (-1, 85) if multiline else (-1, -1)
            control = wx.TextCtrl(parent, style=style, size=size)
        if inline:
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(wx.StaticText(parent, label=label + ":", size=(125, -1)), 0,
                    wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
            row.Add(control, 1, wx.EXPAND)
            self.detail_box.Add(row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        else:
            self.detail_box.Add(wx.StaticText(parent, label=label), 0,
                                wx.LEFT | wx.RIGHT | wx.TOP, 8)
            self.detail_box.Add(control, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        self.fields[key] = control

    def _load(self):
        r = self.record
        self.template_rows = [row for row in self.repository.templates.templates_for_service(
            self.service_id
        ) if row[3]]
        self.template.Set([str(row[1]) for row in self.template_rows])
        assignment = self.repository.weekly.assignment(self.service_id)
        selected_template = assignment[1] if assignment else r[7]
        self._select(self.template, self.template_rows, selected_template)
        self.proper_rows = self.repository.propers(r[1])
        self.fields["proper"].Set([str(row[1]) for row in self.proper_rows])
        self._select(self.fields["proper"], self.proper_rows, r[4])
        self.sermon_rows = self.repository.all(
            "SELECT ID,CONCAT(ID,' - ',COALESCE(Reference,''),' - ',COALESCE(Title,'')) "
            "FROM tblSermon ORDER BY ID DESC"
        )
        self.fields["sermon"].Set([str(row[1]) for row in self.sermon_rows])
        self._select(self.fields["sermon"], self.sermon_rows, r[10])
        self.location_values = self.repository.choice_values("Location")
        if r[3] and r[3] not in self.location_values:
            self.location_values.append(r[3])
        self.fields["location"].Set(self.location_values)
        self.fields["location"].SetSelection(
            self.location_values.index(r[3]) if r[3] in self.location_values else wx.NOT_FOUND
        )
        church = self.repository.one("SELECT Church FROM tblChurch WHERE ID=?", (r[1],))
        values = {
            "church": church[0] if church else "",
            "liturgical": r[5], "communion": bool(r[6]),
            "psalm": r[9], "bulletin": r[11], "check_complete": bool(r[12]),
            "os_note": r[8], "note": r[14],
        }
        try:
            checklist = json.loads(r[13]) if r[13] else {}
            values["checklist"] = "\n".join(
                ("[x] " if str(done).casefold() == "true" else "[ ] ") + str(item)
                for item, done in checklist.items()
            )
        except (TypeError, ValueError):
            values["checklist"] = str(r[13])
        for key, value in values.items():
            control = self.fields[key]
            if isinstance(control, wx.CheckBox):
                control.SetValue(bool(value))
            elif isinstance(control, wx.FilePickerCtrl):
                control.SetPath(str(value or ""))
            else:
                control.SetValue(str(value or ""))
        when = r[2]
        if hasattr(when, "year"):
            self.fields["service_date"].SetValue(
                wx.DateTime.FromDMY(when.day, when.month - 1, when.year)
            )
            time_value = wx.DateTime.Now()
            time_value.SetHour(when.hour)
            time_value.SetMinute(when.minute)
            time_value.SetSecond(when.second)
            self.fields["service_time"].SetValue(time_value)
        hymn_ids = self.repository.weekly_hymns(self.service_id)
        self.working_lines = [
            self._weekly_line(row, hymn_ids.get(row[0]))
            for row in self.repository.weekly.lines(self.service_id)
        ]
        self.refresh_grid()

    @staticmethod
    def _select(choice, rows, value):
        choice.SetSelection(next(
            (index for index, row in enumerate(rows) if row[0] == value), wx.NOT_FOUND
        ))

    @staticmethod
    def _weekly_line(row, hymn_id=None):
        return {
            "sequence": row[1], "included": bool(row[2]), "type": row[3],
            "label": row[4], "source": row[5], "key": row[6],
            "value": row[7] or "", "reference": row[8] or "", "hymn_id": hymn_id,
            "style": row[9], "label_bold": row[10], "value_bold": row[11],
            "italic": row[12], "indent": row[13], "tab_position": row[14],
            "tab_alignment": row[15], "tab_leader": row[16], "note": row[17],
            "template_line_id": row[18],
        }

    @staticmethod
    def _template_line(row, communion, season):
        included = (
            row[15] == "ALWAYS"
            or (row[15] == "COMMUNION" and communion)
            or (row[15] == "NO_COMMUNION" and not communion)
            or (row[15] == "INCLUDE_SEASON" and str(row[16] or "").casefold() == season)
            or (row[15] == "EXCLUDE_SEASON" and str(row[16] or "").casefold() != season)
        )
        return {
            "sequence": row[1], "included": included, "type": row[2], "label": row[3],
            "source": row[4], "key": row[5], "value": "", "reference": row[6] or "",
            "hymn_id": None,
            "style": row[7], "label_bold": row[8], "value_bold": row[9],
            "italic": row[10], "indent": row[11], "tab_position": row[12],
            "tab_alignment": row[13], "tab_leader": row[14], "note": row[17],
            "template_line_id": row[0],
        }

    def refresh_grid(self):
        hymn_counts = {}
        for line in self.working_lines:
            if line["hymn_id"] is not None:
                hymn_counts[line["hymn_id"]] = hymn_counts.get(line["hymn_id"], 0) + 1
        self.grid.DeleteAllItems()
        for index, line in enumerate(self.working_lines):
            item = self.grid.InsertItem(index, str(line["label"]))
            duplicate = line["hymn_id"] is not None and hymn_counts[line["hymn_id"]] > 1
            required = bool(line["included"] and line["source"] and not line["value"])
            status = "DUPLICATE" if duplicate else ("Required" if required else "")
            for column, value in enumerate((line["value"], line["reference"], status), 1):
                self.grid.SetItem(item, column, str(value))
            if not line["included"]:
                self.grid.SetItemTextColour(item, wx.Colour(130, 130, 130))
            elif status:
                self.grid.SetItemTextColour(item, wx.RED)

    def selected_line_index(self):
        selected = self.grid.GetFirstSelected()
        return None if selected < 0 else selected

    def on_edit_line(self, _event):
        index = self.selected_line_index()
        if index is None:
            return
        line = self.working_lines[index]
        if line["source"] == "SERVICE_HYMN":
            self.on_select_hymn(None)
            return
        dialog = wx.TextEntryDialog(
            self,
            "Enter the weekly value for this service line. Leave it blank to clear it.",
            f"Edit {line['label']}",
            value=str(line["value"] or ""),
        )
        try:
            if dialog.ShowModal() == wx.ID_OK:
                line["value"] = dialog.GetValue().strip()
                # A typed value is not a catalog-backed hymn selection. The hymn
                # chooser added in the next stage will set this ID explicitly.
                if line["source"] == "SERVICE_HYMN":
                    line["hymn_id"] = None
                self.refresh_grid()
                self.grid.Select(index)
        finally:
            dialog.Destroy()

    def on_select_hymn(self, _event):
        index = self.selected_line_index()
        if index is None:
            return
        line = self.working_lines[index]
        if line["source"] != "SERVICE_HYMN":
            wx.MessageBox("Select a hymn line first.", "Select Hymn",
                          wx.OK | wx.ICON_INFORMATION, self)
            return
        used_ids = [
            item["hymn_id"] for item in self.working_lines
            if item is not line and item["hymn_id"] is not None
        ]
        dialog = HymnPickerDialog(
            self, self.repository, self.service_id, line["label"], used_ids,
        )
        try:
            if dialog.ShowModal() == wx.ID_OK:
                selected = dialog.selected_hymn
                line["hymn_id"] = selected[0]
                line["value"] = " ".join(value for value in (selected[1], selected[2]) if value)
                self.refresh_grid()
                self.grid.Select(index)
            elif dialog.clear_requested:
                line["hymn_id"], line["value"] = None, ""
                self.refresh_grid()
                self.grid.Select(index)
        finally:
            dialog.Destroy()

    def on_move_line(self, direction):
        index = self.selected_line_index()
        target = None if index is None else index + direction
        if index is None or target < 0 or target >= len(self.working_lines):
            return
        self.working_lines[index], self.working_lines[target] = (
            self.working_lines[target], self.working_lines[index]
        )
        normalize_line_sequences(self.working_lines)
        self.refresh_grid()
        self.grid.Select(target)
        self.grid.EnsureVisible(target)

    def on_template(self, _event):
        if self.loading or self.template.GetSelection() == wx.NOT_FOUND:
            return
        if self.working_lines and wx.MessageBox(
            "Changing the template will replace the displayed working Order of Service. Continue?",
            "Replace Working Order", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self,
        ) != wx.YES:
            return
        template_id = self.template_rows[self.template.GetSelection()][0]
        self.fields["os_note"].SetValue(str(
            self.template_rows[self.template.GetSelection()][2] or ""
        ))
        season_row = self.repository.one(
            "SELECT COALESCE(p.Season,'') FROM tblService s LEFT JOIN tblPropers p "
            "ON p.ID=s.PropersID WHERE s.ID=?", (self.service_id,),
        )
        season = str(season_row[0] if season_row else "").casefold()
        communion = self.fields["communion"].GetValue()
        self.working_lines = [
            self._template_line(row, communion, season)
            for row in self.repository.templates.lines(template_id)
        ]
        self.apply_proper()

    def on_proper(self, _event):
        if not self.loading:
            self.apply_proper()

    def on_view_proper(self, _event):
        selection = self.fields["proper"].GetSelection()
        if selection == wx.NOT_FOUND:
            wx.MessageBox("Select a Proper first.", "View Proper",
                          wx.OK | wx.ICON_INFORMATION, self)
            return
        proper_id = self.proper_rows[selection][0]
        dialog = ProperReadOnlyDialog(self, self.repository, proper_id)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()

    def apply_proper(self):
        selection = self.fields["proper"].GetSelection()
        proper_id = None if selection == wx.NOT_FOUND else self.proper_rows[selection][0]
        readings, suggestions = self.repository.proper_values(proper_id)
        if proper_id:
            detail = self.repository.proper_detail(proper_id)
            self.fields["liturgical"].SetValue(str(detail[3] or ""))
        readings_by_use = {row[0]: row[1] for row in readings}
        unused = list(suggestions)
        for line in self.working_lines:
            if line["source"] == "SERVICE_READING":
                line["value"] = readings_by_use.get(line["key"], "")
            elif line["source"] == "SERVICE_HYMN":
                match = next((i for i, hymn in enumerate(unused) if hymn[2] == line["key"]), None)
                if match is None:
                    line["value"], line["hymn_id"] = "", None
                else:
                    hymn = unused.pop(match)
                    line["hymn_id"], line["value"] = hymn[0], hymn[1]
        self.refresh_grid()

    @staticmethod
    def _choice_value(choice, rows):
        selection = choice.GetSelection()
        return None if selection == wx.NOT_FOUND else rows[selection][0]

    def checklist_json(self):
        result = {}
        for raw in self.fields["checklist"].GetValue().splitlines():
            text = raw.strip()
            if not text:
                continue
            checked = text.startswith("[x]") or text.startswith("[X]")
            label = text[3:].strip() if text.startswith("[") and len(text) >= 3 else text
            result[label] = "True" if checked else "False"
        return json.dumps(result)

    def validation_counts(self):
        hymn_ids = [line["hymn_id"] for line in self.working_lines if line["hymn_id"] is not None]
        duplicates = len(hymn_ids) - len(set(hymn_ids))
        missing = sum(
            1 for line in self.working_lines
            if line["included"] and line["source"] and not line["value"]
        )
        return duplicates, missing

    def on_save(self, _event):
        template_id = self._choice_value(self.template, self.template_rows)
        if template_id is None:
            wx.MessageBox("Select an Order of Service template before saving.",
                          "Template Required", wx.OK | wx.ICON_WARNING, self)
            return
        duplicates, missing = self.validation_counts()
        if duplicates or missing:
            message = (
                f"The service has {duplicates} duplicate hymn occurrence(s) and "
                f"{missing} unfinished required line(s).\n\n"
                "These items are shown in red. Save the service anyway?"
            )
            if wx.MessageBox(message, "Worship Service Validation",
                             wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self) != wx.YES:
                return
        selected_date = self.fields["service_date"].GetValue()
        selected_time = self.fields["service_time"].GetValue()
        when = datetime(
            selected_date.GetYear(), selected_date.GetMonth() + 1, selected_date.GetDay(),
            selected_time.GetHour(), selected_time.GetMinute(), selected_time.GetSecond(),
        )
        service_values = (
            when, self.fields["location"].GetStringSelection() or None,
            self._choice_value(self.fields["proper"], self.proper_rows),
            self.fields["liturgical"].GetValue().strip() or None,
            int(self.fields["communion"].GetValue()), template_id,
            self.fields["os_note"].GetValue() or None,
            self.fields["psalm"].GetValue().strip() or None,
            self._choice_value(self.fields["sermon"], self.sermon_rows),
            self.fields["bulletin"].GetPath() or None,
            int(self.fields["check_complete"].GetValue()), self.checklist_json(),
            self.fields["note"].GetValue() or None,
        )
        try:
            self.repository.save(
                self.service_id, service_values, template_id, self.working_lines,
            )
            self.save_status.SetLabel("Worship Service and weekly Order of Service saved.")
            self.save_status.SetForegroundColour(wx.Colour(0, 120, 0))
            wx.MessageBox("The complete Worship Service was saved.", "Worship Service",
                          wx.OK | wx.ICON_INFORMATION, self)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Save Worship Service",
                          wx.OK | wx.ICON_ERROR, self)


class HymnPickerDialog(wx.Dialog):
    SEARCH_FIELDS = (
        "All fields", "Hymn number", "Title", "Bible reference", "Category", "Notes",
    )

    def __init__(self, parent, repository, service_id, used_as, used_hymn_ids):
        super().__init__(parent, title="Select Hymn", size=(980, 650),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = repository
        self.service_id = service_id
        self.used_ids = set(used_hymn_ids)
        self.rows = []
        self.selected_hymn = None
        self.clear_requested = False
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        context = wx.StaticText(
            panel,
            label=f"Selecting hymn for: {used_as}    |    Hymnal: {repository.hymnal_name(service_id)}",
        )
        context.SetForegroundColour(wx.Colour(0, 90, 190))
        outer.Add(context, 0, wx.ALL, 10)
        search_row = wx.BoxSizer(wx.HORIZONTAL)
        search_row.Add(wx.StaticText(panel, label="Search:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.search = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        search_row.Add(self.search, 1, wx.RIGHT, 8)
        self.search_in = wx.Choice(panel, choices=list(self.SEARCH_FIELDS))
        self.search_in.SetSelection(0)
        search_row.Add(self.search_in, 0, wx.RIGHT, 8)
        find = wx.Button(panel, label="Search")
        find.Bind(wx.EVT_BUTTON, self.on_search)
        search_row.Add(find, 0, wx.RIGHT, 8)
        clear_search = wx.Button(panel, label="Clear Search")
        clear_search.Bind(wx.EVT_BUTTON, self.on_clear_search)
        search_row.Add(clear_search)
        outer.Add(search_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.search.Bind(wx.EVT_TEXT_ENTER, self.on_search)

        self.grid = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (
            ("Hymn", 95), ("Title", 275), ("Bible reference", 145),
            ("Category", 120), ("Notes", 230), ("Status", 90),
        ):
            self.grid.AppendColumn(label, width=width)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_select)
        outer.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        choose = wx.Button(panel, wx.ID_OK, "Select Hymn")
        choose.Bind(wx.EVT_BUTTON, self.on_select)
        buttons.Add(choose, 0, wx.RIGHT, 8)
        clear_position = wx.Button(panel, label="Clear This Position")
        clear_position.Bind(wx.EVT_BUTTON, self.on_clear_position)
        buttons.Add(clear_position)
        buttons.AddStretchSpacer()
        cancel = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        buttons.Add(cancel)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer)
        self.load_results()
        self.search.SetFocus()

    def load_results(self):
        self.rows = self.repository.search_hymns(
            self.service_id, self.search.GetValue(), self.search_in.GetStringSelection(),
        )
        self.grid.DeleteAllItems()
        for index, row in enumerate(self.rows):
            item = self.grid.InsertItem(index, str(row[1]))
            status = "Already used" if row[0] in self.used_ids else ""
            for column, value in enumerate((row[2], row[3], row[4], row[5], status), 1):
                self.grid.SetItem(item, column, str(value))
            if status:
                self.grid.SetItemTextColour(item, wx.Colour(190, 90, 0))

    def on_search(self, _event):
        self.load_results()

    def on_clear_search(self, _event):
        self.search.SetValue("")
        self.search_in.SetSelection(0)
        self.load_results()

    def on_select(self, _event):
        index = self.grid.GetFirstSelected()
        if index < 0:
            wx.MessageBox("Select a hymn first.", "Select Hymn",
                          wx.OK | wx.ICON_INFORMATION, self)
            return
        self.selected_hymn = self.rows[index]
        self.EndModal(wx.ID_OK)

    def on_clear_position(self, _event):
        self.clear_requested = True
        self.EndModal(wx.ID_CANCEL)


class ProperReadOnlyDialog(wx.Dialog):
    def __init__(self, parent, repository, proper_id):
        super().__init__(parent, title="Proper (Read Only)", size=(780, 620),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        detail = repository.proper_detail(proper_id)
        readings, hymns = repository.proper_values(proper_id)
        panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        banner = wx.StaticText(panel, label="This Proper is displayed for reference only.")
        banner.SetForegroundColour(wx.Colour(0, 90, 190))
        outer.Add(banner, 0, wx.ALL, 10)
        labels = (
            ("Lectionary", detail[0]), ("Cycle", detail[1]), ("Season", detail[2]),
            ("Liturgical date", detail[3]), ("Theme", detail[4]),
            ("Color", detail[5]), ("Alternate color", detail[6]),
            ("Introit", detail[7]), ("Note", detail[8]),
        )
        info = wx.FlexGridSizer(cols=2, vgap=5, hgap=10)
        info.AddGrowableCol(1, 1)
        for label, value in labels:
            info.Add(wx.StaticText(panel, label=label + ":"), 0, wx.ALIGN_TOP)
            info.Add(wx.StaticText(panel, label=str(value or "")), 1, wx.EXPAND)
        outer.Add(info, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        book = wx.Notebook(panel)
        reading_page, hymn_page = wx.Panel(book), wx.Panel(book)
        book.AddPage(reading_page, "Readings")
        book.AddPage(hymn_page, "Suggested Hymns")
        reading_grid = wx.ListCtrl(reading_page, style=wx.LC_REPORT)
        reading_grid.AppendColumn("Reading", width=180)
        reading_grid.AppendColumn("Reference", width=500)
        for index, row in enumerate(readings):
            item = reading_grid.InsertItem(index, str(row[0]))
            reading_grid.SetItem(item, 1, str(row[1] or ""))
        reading_box = wx.BoxSizer(wx.VERTICAL); reading_box.Add(reading_grid, 1, wx.EXPAND | wx.ALL, 6)
        reading_page.SetSizer(reading_box)
        hymn_grid = wx.ListCtrl(hymn_page, style=wx.LC_REPORT)
        hymn_grid.AppendColumn("Suggested Use", width=190)
        hymn_grid.AppendColumn("Hymn", width=490)
        for index, row in enumerate(hymns):
            item = hymn_grid.InsertItem(index, str(row[2]))
            hymn_grid.SetItem(item, 1, str(row[1]))
        hymn_box = wx.BoxSizer(wx.VERTICAL); hymn_box.Add(hymn_grid, 1, wx.EXPAND | wx.ALL, 6)
        hymn_page.SetSizer(hymn_box)
        outer.Add(book, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer(); buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer)


def show_unified_worship_service(parent, connection, service_id):
    dialog = UnifiedWorshipServiceEditor(parent, connection, service_id)
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()
