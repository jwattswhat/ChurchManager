"""Unified split-panel view of a Worship Service and its weekly order."""

from __future__ import annotations

import json
import wx

from bulletin_orders import (
    BulletinOrderRepository,
    WeeklyBulletinOrderRepository,
    portable_connection,
)


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

    def weekly_hymns(self, service_id):
        return dict(self.all(
            "SELECT ServiceBulletinOrderLineID,HymnID FROM tblHymnUsage "
            "WHERE ServiceID=? AND ServiceBulletinOrderLineID IS NOT NULL",
            (service_id,),
        ))


class UnifiedWorshipServiceEditor(wx.Dialog):
    """First-stage unified editor: one window, independently scrolling panels."""

    def __init__(self, parent, connection, service_id):
        super().__init__(parent, title="Worship Service and Order of Service", size=(1280, 760),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = UnifiedWorshipServiceRepository(connection)
        self.service_id = service_id
        self.record = self.repository.service(service_id)
        if not self.record:
            raise ValueError("The selected Worship Service is unavailable.")
        self.loading = True
        self.template_rows = []
        self.proper_rows = []
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
        right.SetScrollRate(0, 12)
        splitter.SplitVertically(left, right, 810)
        splitter.SetMinimumPaneSize(330)
        splitter.SetSashGravity(0.67)

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
        left_box.Add(wx.StaticText(left, label="Red lines require attention."), 0, wx.ALL, 8)
        left.SetSizer(left_box)

        self.detail_box = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(right, label="Service Details")
        title.SetFont(title.GetFont().Bold())
        self.detail_box.Add(title, 0, wx.ALL, 8)
        self.fields = {}
        for key, label, multiline, inline in (
            ("church", "Church", False, True), ("when", "Date and time", False, True),
            ("location", "Location", False, True), ("proper", "Proper", False, False),
            ("liturgical", "Printed liturgical title", False, False),
            ("communion", "Holy Communion", False, True),
            ("psalm", "Psalm or Introit", False, True), ("sermon", "Sermon", False, False),
            ("bulletin", "Bulletin", False, False),
            ("check_complete", "Checklist complete", False, True),
            ("checklist", "Checklist", True, False),
            ("os_note", "Order of Service notes (from template - read only)", True, False),
            ("note", "Notes for this service", True, False),
        ):
            self._add_field(right, key, label, multiline, inline)
        self.fields["os_note"].SetToolTip(
            "This note comes from the selected Order of Service template and cannot be changed here."
        )
        self.fields["os_note"].SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        )
        right.SetSizer(self.detail_box)

        outer.Add(splitter, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        actions = wx.BoxSizer(wx.HORIZONTAL)
        stage = wx.StaticText(panel, label="Unified editing and Save are the next implementation stage.")
        stage.SetForegroundColour(wx.Colour(110, 80, 0))
        actions.Add(stage, 0, wx.ALIGN_CENTER_VERTICAL)
        actions.AddStretchSpacer()
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        actions.Add(close)
        outer.Add(actions, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer)

    def _add_field(self, parent, key, label, multiline, inline):
        if key == "proper":
            control = wx.Choice(parent)
            control.Bind(wx.EVT_CHOICE, self.on_proper)
        else:
            style = wx.TE_MULTILINE | wx.TE_READONLY if multiline else wx.TE_READONLY
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
        church = self.repository.one("SELECT Church FROM tblChurch WHERE ID=?", (r[1],))
        values = {
            "church": church[0] if church else "",
            "when": r[2].strftime("%m/%d/%Y %I:%M %p") if hasattr(r[2], "strftime") else str(r[2]),
            "location": r[3],
            "liturgical": r[5], "communion": "Yes" if r[6] else "No",
            "psalm": r[9], "sermon": self.repository.sermon_name(r[10]),
            "bulletin": r[11], "check_complete": "Yes" if r[12] else "No",
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
            self.fields[key].SetValue(str(value or ""))
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

    def on_template(self, _event):
        if self.loading or self.template.GetSelection() == wx.NOT_FOUND:
            return
        if self.working_lines and wx.MessageBox(
            "Changing the template will replace the displayed working Order of Service. Continue?",
            "Replace Working Order", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self,
        ) != wx.YES:
            return
        template_id = self.template_rows[self.template.GetSelection()][0]
        season_row = self.repository.one(
            "SELECT COALESCE(p.Season,'') FROM tblService s LEFT JOIN tblPropers p "
            "ON p.ID=s.PropersID WHERE s.ID=?", (self.service_id,),
        )
        season = str(season_row[0] if season_row else "").casefold()
        communion = self.fields["communion"].GetValue() == "Yes"
        self.working_lines = [
            self._template_line(row, communion, season)
            for row in self.repository.templates.lines(template_id)
        ]
        self.apply_proper()

    def on_proper(self, _event):
        if not self.loading:
            self.apply_proper()

    def apply_proper(self):
        selection = self.fields["proper"].GetSelection()
        proper_id = None if selection == wx.NOT_FOUND else self.proper_rows[selection][0]
        readings, suggestions = self.repository.proper_values(proper_id)
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


def show_unified_worship_service(parent, connection, service_id):
    dialog = UnifiedWorshipServiceEditor(parent, connection, service_id)
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()
