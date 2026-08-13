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
        self._build()
        self._load()
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
        self.template = wx.TextCtrl(left, style=wx.TE_READONLY)
        template_row.Add(self.template, 1, wx.EXPAND)
        left_box.Add(template_row, 0, wx.EXPAND | wx.ALL, 8)
        self.grid = wx.ListCtrl(left, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (("Order", 65), ("Service line", 245), ("Weekly value", 270),
                             ("Reference", 140), ("Status", 90)):
            self.grid.AppendColumn(label, width=width)
        left_box.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        left_box.Add(wx.StaticText(left, label="Red lines require attention."), 0, wx.ALL, 8)
        left.SetSizer(left_box)

        self.detail_box = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(right, label="Service Details")
        title.SetFont(title.GetFont().Bold())
        self.detail_box.Add(title, 0, wx.ALL, 8)
        self.fields = {}
        for key, label, multiline in (
            ("church", "Church", False), ("when", "Date and time", False),
            ("location", "Location", False), ("proper", "Proper", False),
            ("liturgical", "Printed liturgical title", False),
            ("communion", "Holy Communion", False),
            ("psalm", "Psalm or Introit", False), ("sermon", "Sermon", False),
            ("bulletin", "Bulletin", False), ("check_complete", "Checklist complete", False),
            ("checklist", "Checklist", True), ("os_note", "Order of Service notes", True),
            ("note", "Notes for this service", True),
        ):
            self._add_field(right, key, label, multiline)
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

    def _add_field(self, parent, key, label, multiline):
        self.detail_box.Add(wx.StaticText(parent, label=label), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        style = wx.TE_MULTILINE | wx.TE_READONLY if multiline else wx.TE_READONLY
        size = (-1, 85) if multiline else (-1, -1)
        control = wx.TextCtrl(parent, style=style, size=size)
        self.detail_box.Add(control, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        self.fields[key] = control

    def _load(self):
        r = self.record
        church = self.repository.one("SELECT Church FROM tblChurch WHERE ID=?", (r[1],))
        values = {
            "church": church[0] if church else "",
            "when": r[2].strftime("%m/%d/%Y %I:%M %p") if hasattr(r[2], "strftime") else str(r[2]),
            "location": r[3], "proper": self.repository.proper_name(r[4]),
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
        self.template.SetValue(r[15])
        for key, value in values.items():
            self.fields[key].SetValue(str(value or ""))
        self.grid.DeleteAllItems()
        for index, row in enumerate(self.repository.weekly.lines(self.service_id)):
            item = self.grid.InsertItem(index, str(row[1]))
            required = bool(row[5] and not row[7])
            for column, value in enumerate((row[4], row[7] or "", row[8] or "",
                                            "Required" if required else ""), 1):
                self.grid.SetItem(item, column, str(value))
            if required:
                self.grid.SetItemTextColour(item, wx.RED)


def show_unified_worship_service(parent, connection, service_id):
    dialog = UnifiedWorshipServiceEditor(parent, connection, service_id)
    try:
        return dialog.ShowModal()
    finally:
        dialog.Destroy()
