"""Unified split-panel view of a Worship Service and its weekly order."""

from __future__ import annotations

import json
import time
from datetime import datetime
import wx
import wx.adv

from ui_dimensions import DATE_PICKER_SIZE, TIME_PICKER_SIZE
from hymn_validation import duplicate_selection_status, normalize_tune
from hymn_stanzas import StanzaSelectionError, format_hymn_reference, format_stanza_notation, normalize_stanzas
from worship_scheduling import show_service_participants
from worship_checklist import show_preparation_checklist
from worship_checklist import WorshipChecklistRepository, checklist_counts
from liturgical_colors import liturgical_color_hex

from bulletin_orders import (
    BulletinOrderGenerator,
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
            "COALESCE(s.OSNote,''),s.SermonID,"
            "COALESCE(s.Bulletin,''),COALESCE(s.CheckListComplete,0),"
            "COALESCE(s.Note,''),COALESCE(t.Name,'Not selected'),"
            "COALESCE(s.LiturgicalColorOverride,'') "
            "FROM tblService s LEFT JOIN tblBulletinOrderTemplate t "
            "ON t.ID=s.BulletinOrderTemplateID WHERE s.ID=?", (service_id,),
        )

    def churches(self):
        return self.all("SELECT ID,Church FROM tblChurch ORDER BY Church,ID")

    def create_service(self, church_id):
        """Create the temporary database identity needed by the unified editor."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO tblService "
                "(ChurchID,DateTime,HolyCommunion,CheckListComplete) "
                "VALUES (?,?,0,0)",
                (church_id, datetime.now().replace(microsecond=0)),
            )
            service_id = cursor.lastrowid
            self.connection.commit()
            return service_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def discard_unsaved_service(self, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM tblService WHERE ID=?", (service_id,))
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def delete_service(self, service_id, session):
        """Delete an unused service, preserving attendance and schedule history."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT s.DateTime,COALESCE(s.LiturgicalDate,''),COALESCE(s.Location,'') "
                "FROM tblService s WHERE s.ID=? FOR UPDATE", (service_id,),
            )
            service = cursor.fetchone()
            if not service:
                raise ValueError("The selected Worship Service no longer exists.")
            dependencies = []
            cursor.execute(
                "SELECT COUNT(a.ID),COALESCE(SUM(ae.HandCount),0),"
                "COALESCE(SUM(ae.HandCountCommunion),0) "
                "FROM tblAttendanceEvent ae LEFT JOIN tblAttendance a "
                "ON a.AttendanceEventID=ae.ID WHERE ae.ServiceID=?", (service_id,),
            )
            attendance = cursor.fetchone()
            if any(attendance):
                dependencies.append("recorded attendance")
            for table, description in (
                ("tblServiceRole", "participant assignment(s)"),
            ):
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE ServiceID=?", (service_id,))
                count = cursor.fetchone()[0]
                if count:
                    dependencies.append(f"{count} {description}")
            if dependencies:
                raise ValueError(
                    "This service cannot be deleted because it has "
                    + " and ".join(dependencies)
                    + ". Remove or reassign those records first."
                )
            before = json.dumps(
                {
                    "date_time": service[0].isoformat(sep=" ")
                    if hasattr(service[0], "isoformat") else str(service[0]),
                    "liturgical_date": service[1],
                    "location": service[2],
                },
                separators=(",", ":"),
            )
            cursor.execute("DELETE FROM tblHymnUsage WHERE ServiceID=?", (service_id,))
            cursor.execute("DELETE FROM tblServiceBulletinOrderLine WHERE ServiceID=?", (service_id,))
            cursor.execute("DELETE FROM tblServiceBulletinOrder WHERE ServiceID=?", (service_id,))
            cursor.execute("DELETE FROM tblAttendanceEvent WHERE ServiceID=?", (service_id,))
            cursor.execute("DELETE FROM tblService WHERE ID=?", (service_id,))
            cursor.execute(
                "INSERT INTO tblSecurityAuditEvent "
                "(UserID,Action,EntityType,EntityID,BeforeJSON,Workstation) "
                "VALUES (?,'WORSHIP_SERVICE_DELETED','WORSHIP_SERVICE',?,?,?)",
                (
                    getattr(session, "user_id", None), str(service_id), before,
                    getattr(session, "workstation", None),
                ),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

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
            "SELECT s.HymnID,COALESCE(h.Hymn,''),COALESCE(h.Title,''),s.SuggestedAs,"
            "COALESCE(h.Tune,'') "
            "FROM tblProperHymnSuggestion s JOIN tblHymn h ON h.ID=s.HymnID "
            "WHERE s.PropersID=? ORDER BY s.ID", (proper_id,),
        ) if proper_id else []
        return readings, hymns

    def proper_detail(self, proper_id):
        return self.one(
            "SELECT ls.Name,COALESCE(p.Cycle,''),COALESCE(p.Season,''),"
            "COALESCE(p.LiturgicalDate,''),COALESCE(p.Theme,''),COALESCE(p.Color,''),"
            "COALESCE(p.AltColor,''),COALESCE(p.Note,'') "
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
        return {row[0]: (row[1], row[2] or "", row[3], row[4] or "") for row in self.all(
            "SELECT u.ServiceBulletinOrderLineID,u.HymnID,COALESCE(h.Tune,''),u.Stanzas,"
            "COALESCE(h.Hymn,'') "
            "FROM tblHymnUsage u JOIN tblHymn h ON h.ID=u.HymnID "
            "WHERE u.ServiceID=? AND u.ServiceBulletinOrderLineID IS NOT NULL",
            (service_id,),
        )}

    def save(self, service_id, service_values, template_id, lines):
        """Persist the service and its complete displayed weekly order atomically."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE tblService SET DateTime=?,Location=?,PropersID=?,LiturgicalDate=?,"
                "LiturgicalColorOverride=?,HolyCommunion=?,BulletinOrderTemplateID=?,OSNote=?,SermonID=?,"
                "Bulletin=?,Note=? WHERE ID=?",
                service_values + (service_id,),
            )
            cursor.execute("SELECT ChurchID FROM tblService WHERE ID=?", (service_id,))
            church_id = cursor.fetchone()[0]
            self._sync_empty_attendance_event(
                cursor, service_id, church_id, service_values[0], service_values[3],
                bool(service_values[5]),
            )
            cursor.execute("DELETE FROM tblHymnUsage WHERE ServiceID=?", (service_id,))
            cursor.execute("DELETE FROM tblServiceBulletinOrderLine WHERE ServiceID=?", (service_id,))
            cursor.execute(
                "INSERT INTO tblServiceBulletinOrder (ServiceID,TemplateID,TemplateName) "
                "SELECT ?,ID,Name FROM tblBulletinOrderTemplate WHERE ID=? "
                "ON DUPLICATE KEY UPDATE TemplateID=VALUES(TemplateID),"
                "TemplateName=VALUES(TemplateName),GeneratedPlainText=NULL,"
                "GeneratedHtml=NULL,GeneratedAt=NULL", (service_id, template_id),
            )
            for line in normalize_line_sequences(lines):
                cursor.execute(
                    "INSERT INTO tblServiceBulletinOrderLine "
                    "(ServiceID,TemplateLineID,Sequence,Included,LineType,Label,ValueSource,"
                    "ValueKey,WeeklyValue,ReferenceText,StyleName,LabelBold,ValueBold,Italic,"
                    "IndentLevel,TabPosition,TabAlignment,TabLeader,ConditionType,ConditionValue,Note) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        service_id, line.get("template_line_id"), line["sequence"],
                        int(line["included"]), line["type"], line["label"], line["source"],
                        line["key"], line["value"] or None, line["reference"] or None,
                        line.get("style") or "Normal", int(bool(line.get("label_bold"))),
                        int(bool(line.get("value_bold"))), int(bool(line.get("italic"))),
                        int(line.get("indent") or 0), line.get("tab_position"),
                        line.get("tab_alignment") or "LEFT", line.get("tab_leader") or "NONE",
                        line.get("condition_type") or "ALWAYS", line.get("condition_value"),
                        line.get("note") or None,
                    ),
                )
                weekly_line_id = cursor.lastrowid
                if line.get("hymn_id") is not None:
                    cursor.execute(
                        "INSERT INTO tblHymnUsage "
                        "(ChurchID,ServiceID,ServiceBulletinOrderLineID,HymnID,UsedAs,Stanzas) "
                        "VALUES (?,?,?,?,?,?)",
                        (church_id, service_id, weekly_line_id, line["hymn_id"], line["key"],
                         line.get("stanzas")),
                    )
            self._sync_reading_snapshots(cursor, service_id, service_values[2], lines)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    @staticmethod
    def _reading_role(value):
        """Map familiar outline labels to normalized appointment roles."""
        text = str(value or "").strip().casefold()
        if text in {"old testament", "old testament reading", "first reading"}:
            return "FIRST_READING"
        if text in {"epistle", "epistle reading", "second reading"}:
            return "SECOND_READING"
        if text in {"gospel", "holy gospel"}:
            return "GOSPEL"
        if text in {"psalm", "psalm/canticle", "canticle"}:
            return "PSALM_CANTICLE"
        return ""

    def _sync_reading_snapshots(self, cursor, service_id, proper_id, lines):
        """Replace service-owned citations from the weekly outline being saved."""
        cursor.execute("DELETE FROM tblServiceReadingSnapshot WHERE ServiceID=?", (service_id,))
        context = None
        appointments = []
        if proper_id:
            cursor.execute(
                "SELECT p.ID,ls.SystemCode,COALESCE(e.EditionCode,''),p.ProperKey,"
                "ls.Name,COALESCE(e.Name,''),COALESCE(c.DisplayName,p.Cycle,''),"
                "p.LiturgicalDate FROM tblPropers p "
                "JOIN tblLectionarySystem ls ON ls.ID=p.LectionarySystemID "
                "LEFT JOIN tblLectionaryEdition e ON e.ID=p.LectionaryEditionID "
                "LEFT JOIN tblLectionaryCycle c ON c.ID=p.LectionaryCycleID WHERE p.ID=?",
                (proper_id,),
            )
            context = cursor.fetchone()
            cursor.execute(
                "SELECT ID,AppointmentKey,COALESCE(Role,''),COALESCE(DisplayRole,Reading,''),"
                "COALESCE(DisplayCitation,Reference,''),COALESCE(NormalizedCitation,''),"
                "COALESCE(TrackCode,''),COALESCE(OptionGroupCode,''),COALESCE(OptionType,'') "
                "FROM tblReading WHERE PropersID=? ORDER BY COALESCE(Sequence,ID),ID",
                (proper_id,),
            )
            appointments = cursor.fetchall()
        for line in lines:
            if not line.get("included") or str(line.get("type") or "").upper() != "READING":
                continue
            label = str(line.get("label") or line.get("key") or "Reading").strip()
            key = str(line.get("key") or label).strip()
            role = self._reading_role(key) or self._reading_role(label)
            source = next((row for row in appointments if role and row[2] == role), None)
            if source is None:
                wanted = {key.casefold(), label.casefold()}
                source = next((row for row in appointments if row[3].casefold() in wanted), None)
            citation = str(line.get("value") or line.get("reference") or "").strip()
            cursor.execute(
                "INSERT INTO tblServiceReadingSnapshot "
                "(ServiceID,SourceProperID,SourceAppointmentID,SourceSystemCode,"
                "SourceEditionCode,SourceProperKey,SourceAppointmentKey,SystemName,EditionName,"
                "CycleName,ProperName,Role,Reading,Reference,NormalizedCitation,TrackCode,"
                "OptionGroupCode,OptionType,Sequence) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    service_id, proper_id if context else None, source[0] if source else None,
                    context[1] if context else None, context[2] if context else None,
                    context[3] if context else None, source[1] if source else None,
                    context[4] if context else None, context[5] if context else None,
                    context[6] if context else None, context[7] if context else None,
                    source[2] if source and source[2] else role or None, label, citation,
                    source[5] if source else None, source[6] if source else None,
                    source[7] if source else None, source[8] if source else None,
                    int(line["sequence"]),
                ),
            )

    def _sync_empty_attendance_event(
        self, cursor, service_id, church_id, date_time, liturgical_date, communion_offered,
    ):
        """Create or update the service event until attendance becomes historical."""
        cursor.execute(
            "SELECT ae.ID,COALESCE(ae.HandCount,0),COALESCE(ae.HandCountCommunion,0),"
            "COUNT(a.ID) FROM tblAttendanceEvent ae "
            "LEFT JOIN tblAttendance a ON a.AttendanceEventID=ae.ID "
            "WHERE ae.ServiceID=? GROUP BY ae.ID ORDER BY ae.ID", (service_id,),
        )
        events = cursor.fetchall()
        if events and any(row[1] or row[2] or row[3] for row in events):
            return
        cursor.execute("SELECT Choices FROM tblChoices WHERE Field='AttendanceType' ORDER BY ID")
        attendance_types = []
        for row in cursor.fetchall():
            for value in str(row[0] or "").replace("[", "").replace("]", "").replace(",", "\n").splitlines():
                value = value.strip().strip("'\"")
                if value and value not in attendance_types:
                    attendance_types.append(value)
        attendance_type = next(
            (value for value in attendance_types if value.casefold() == "worship service"),
            "Worship Service",
        )
        description = str(liturgical_date or "").strip() or "Worship Service"
        if events:
            cursor.execute(
                "UPDATE tblAttendanceEvent SET ChurchID=?,DateTime=?,Description=?,"
                "AttendanceType=?,CommunionOffered=? WHERE ID=?",
                (
                    church_id, date_time, description, attendance_type,
                    int(communion_offered), events[0][0],
                ),
            )
            return
        cursor.execute(
            "INSERT INTO tblAttendanceEvent "
            "(ChurchID,ServiceID,DateTime,Description,AttendanceType,CommunionOffered,"
            "HandCount,HandCountCommunion) VALUES (?,?,?,?,?,?,0,0)",
            (
                church_id, service_id, date_time, description, attendance_type,
                int(communion_offered),
            ),
        )

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
            "Tune": "h.Tune", "Category": "h.Category", "Notes": "h.Note",
        }
        sql = (
            "SELECT h.ID,COALESCE(h.Hymn,''),COALESCE(h.Title,''),COALESCE(h.Tune,''),"
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
                    " AND (h.Hymn LIKE ? OR h.Title LIKE ? OR h.Tune LIKE ? OR h.BibleText LIKE ? "
                    "OR h.Category LIKE ? OR h.Note LIKE ?)"
                )
                values.extend([pattern] * 6)
        sql += " ORDER BY h.Hymn,h.Title"
        return self.all(sql, tuple(values))


class UnifiedWorshipServiceEditor(wx.Dialog):
    """First-stage unified editor: one window, independently scrolling panels."""

    def __init__(self, parent, connection, service_id, new_service=False):
        super().__init__(parent, title="Worship Service and Order of Service", size=(1400, 780),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = UnifiedWorshipServiceRepository(connection)
        self.service_id = service_id
        self.new_service = new_service
        self.saved = False
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
        for label, width in (("Service line", 225), ("Weekly value", 245),
                             ("Reference", 145), ("Stanzas", 90), ("Status", 90)):
            self.grid.AppendColumn(label, width=width)
        left_box.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        line_actions = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (
            ("Edit Line...", self.on_edit_line),
            ("Select Hymn...", self.on_select_hymn),
            ("Edit Stanzas...", self.on_edit_stanzas),
            ("Delete Line", self.on_delete_line),
            ("Move Up", lambda event: self.on_move_line(-1)),
            ("Move Down", lambda event: self.on_move_line(1)),
        ):
            button = wx.Button(left, label=label)
            button.Bind(wx.EVT_BUTTON, handler)
            if label.startswith("Select Hymn"):
                self.select_hymn_button = button
                button.Enable(False)
            elif label.startswith("Edit Stanzas"):
                self.edit_stanzas_button = button
                button.Enable(False)
            elif label == "Delete Line":
                self.delete_line_button = button
                button.Enable(False)
            line_actions.Add(button, 0, wx.RIGHT, 8)
        line_actions.AddStretchSpacer()
        line_actions.Add(wx.StaticText(left, label="Red lines require attention."), 0,
                         wx.ALIGN_CENTER_VERTICAL)
        left_box.Add(line_actions, 0, wx.EXPAND | wx.ALL, 8)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_line)
        self.grid.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_line_selection)
        self.grid.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_line_selection)
        left.SetSizer(left_box)

        self.detail_box = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(right, label="Service Details")
        title.SetFont(title.GetFont().Bold())
        self.detail_box.Add(title, 0, wx.ALL, 8)
        participants = wx.Button(right, label="Participants...")
        participants.SetToolTip("Assign, edit, and preview suggested participants for this service.")
        participants.Bind(
            wx.EVT_BUTTON,
            lambda _event: show_service_participants(
                self, self.repository.connection, self.service_id,
            ),
        )
        self.detail_box.Add(participants, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        checklist_row = wx.BoxSizer(wx.HORIZONTAL)
        checklist = wx.Button(right, label="Preparation Checklist...")
        checklist.SetToolTip("Review preparation reminders and completion summaries.")
        checklist.Bind(wx.EVT_BUTTON, self.on_checklist)
        checklist_row.Add(checklist, 0, wx.RIGHT, 8)
        self.checklist_status = wx.StaticText(right, label="")
        checklist_row.Add(self.checklist_status, 1, wx.ALIGN_CENTER_VERTICAL)
        self.detail_box.Add(checklist_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        self.fields = {}
        for key, label, multiline, inline in (
            ("church", "Church", False, True),
            ("date_time", "Date and time", False, True),
            ("location", "Location", False, True), ("proper", "Proper", False, False),
            ("color_override", "Color override", False, True),
            ("liturgical", "Printed liturgical title", False, False),
            ("communion", "Holy Communion", False, True),
            ("sermon", "Sermon", False, False),
            ("bulletin", "Bulletin", False, False),
            ("note", "Notes for this service", True, False),
            ("os_note", "Order of Service notes (from template - read only)", True, False),
        ):
            self._add_field(right, key, label, multiline, inline)
            if key == "proper":
                proper_row = wx.BoxSizer(wx.HORIZONTAL)
                view_proper = wx.Button(right, label="View Proper...")
                view_proper.Bind(wx.EVT_BUTTON, self.on_view_proper)
                proper_row.Add(view_proper, 0, wx.RIGHT, 18)
                self.liturgical_color_label = wx.StaticText(right, label="Liturgical color:")
                proper_row.Add(self.liturgical_color_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
                self.liturgical_color_swatch = wx.Panel(
                    right, size=(24, 18), style=wx.BORDER_SIMPLE,
                )
                proper_row.Add(self.liturgical_color_swatch, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
                self.liturgical_color_text = wx.StaticText(right, label="")
                proper_row.Add(self.liturgical_color_text, 0, wx.ALIGN_CENTER_VERTICAL)
                self.detail_box.Add(proper_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
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
                parent, size=DATE_PICKER_SIZE, style=wx.adv.DP_DROPDOWN
            )
            row.Add(service_date, 0, wx.RIGHT, 12)
            row.Add(wx.StaticText(parent, label="Time:"), 0,
                    wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            service_time = wx.adv.TimePickerCtrl(parent, size=TIME_PICKER_SIZE)
            row.Add(service_time, 0)
            self.detail_box.Add(row, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
            self.fields["service_date"] = service_date
            self.fields["service_time"] = service_time
            return
        if key in ("proper", "sermon", "location", "color_override"):
            control = wx.Choice(parent)
            if key == "proper":
                control.Bind(wx.EVT_CHOICE, self.on_proper)
            elif key == "color_override":
                control.Bind(wx.EVT_CHOICE, self.on_color_override)
        elif key == "communion":
            control = wx.CheckBox(parent)
            if key == "communion":
                control.Bind(wx.EVT_CHECKBOX, self.on_communion)
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
        # Liturgical colors are maintained centrally in tblChoices (Field=Color).
        self.color_override_values = ["Use Proper color"] + self.repository.choice_values("Color")
        self.fields["color_override"].Set(self.color_override_values)
        override = str(r[14] or "")
        if override and override not in self.color_override_values:
            self.color_override_values.append(override)
            self.fields["color_override"].Append(override)
        self.fields["color_override"].SetSelection(
            self.color_override_values.index(override) if override else 0
        )
        self.sermon_rows = self.repository.all(
            "SELECT ID,CONCAT(ID,' - ',COALESCE(Reference,''),' - ',COALESCE(Title,'')) "
            "FROM tblSermon ORDER BY ID DESC"
        )
        self.fields["sermon"].Set([str(row[1]) for row in self.sermon_rows])
        self._select(self.fields["sermon"], self.sermon_rows, r[9])
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
            "bulletin": r[10],
            "os_note": r[8], "note": r[12],
        }
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
        hymn_assignments = self.repository.weekly_hymns(self.service_id)
        self.working_lines = [
            self._weekly_line(row, *(hymn_assignments.get(row[0]) or (None, "", None, "")))
            for row in self.repository.weekly.lines(self.service_id)
        ]
        self.refresh_grid()
        self.refresh_checklist_status()
        self._show_liturgical_color_for_selected_proper()

    def _show_liturgical_color(self, value):
        text = str(value or "").strip()
        color = liturgical_color_hex(text)
        self.liturgical_color_label.Show(bool(text))
        self.liturgical_color_text.SetLabel(text)
        self.liturgical_color_text.Show(bool(text))
        self.liturgical_color_swatch.Show(bool(color))
        if color:
            self.liturgical_color_swatch.SetBackgroundColour(wx.Colour(color))
            self.liturgical_color_swatch.Refresh()
            self.liturgical_color_swatch.Update()
        self.liturgical_color_swatch.GetParent().Layout()

    def _selected_proper_color(self):
        selection = self.fields["proper"].GetSelection()
        proper_id = None if selection == wx.NOT_FOUND else self.proper_rows[selection][0]
        detail = self.repository.proper_detail(proper_id) if proper_id else None
        return detail[5] if detail else ""

    def _show_liturgical_color_for_selected_proper(self):
        override = ""
        if self.fields["color_override"].GetSelection() > 0:
            override = self.fields["color_override"].GetStringSelection()
        self._show_liturgical_color(override or self._selected_proper_color())

    @staticmethod
    def _select(choice, rows, value):
        choice.SetSelection(next(
            (index for index, row in enumerate(rows) if row[0] == value), wx.NOT_FOUND
        ))

    @staticmethod
    def _weekly_line(row, hymn_id=None, tune="", stanzas=None, hymn_reference=""):
        return {
            "sequence": row[1], "included": bool(row[2]), "type": row[3],
            "label": row[4], "source": row[5], "key": row[6],
            "value": row[7] or "",
            "reference": (format_hymn_reference(hymn_reference, stanzas)
                          if hymn_id is not None else row[8] or ""),
            "hymn_id": hymn_id,
            "tune": tune or "", "stanzas": stanzas,
            "style": row[9], "label_bold": row[10], "value_bold": row[11],
            "italic": row[12], "indent": row[13], "tab_position": row[14],
            "tab_alignment": row[15], "tab_leader": row[16], "note": row[17],
            "template_line_id": row[18],
            "condition_type": row[19] or "ALWAYS", "condition_value": row[20],
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
            "hymn_id": None, "tune": "", "stanzas": None,
            "style": row[7], "label_bold": row[8], "value_bold": row[9],
            "italic": row[10], "indent": row[11], "tab_position": row[12],
            "tab_alignment": row[13], "tab_leader": row[14], "note": row[17],
            "template_line_id": row[0], "condition_type": row[15],
            "condition_value": row[16],
        }

    def refresh_grid(self):
        duplicate_statuses, _hymn_duplicates, _tune_duplicates = duplicate_selection_status(
            self.working_lines
        )
        self.grid.DeleteAllItems()
        self.select_hymn_button.Enable(False)
        self.edit_stanzas_button.Enable(False)
        self.delete_line_button.Enable(False)
        for index, line in enumerate(self.working_lines):
            item = self.grid.InsertItem(index, str(line["label"]))
            required = bool(line["included"] and line["source"] and not line["value"])
            status = duplicate_statuses[index] or ("Required" if required else "")
            for column, value in enumerate((
                line["value"], line["reference"], format_stanza_notation(line.get("stanzas")), status,
            ), 1):
                self.grid.SetItem(item, column, str(value))
            if not line["included"]:
                self.grid.SetItemTextColour(item, wx.Colour(130, 130, 130))
            elif status:
                self.grid.SetItemTextColour(item, wx.RED)

    def selected_line_index(self):
        selected = self.grid.GetFirstSelected()
        return None if selected < 0 else selected

    def on_line_selection(self, _event=None):
        index = self.selected_line_index()
        enabled = index is not None and self.working_lines[index]["source"] == "SERVICE_HYMN"
        self.select_hymn_button.Enable(enabled)
        self.edit_stanzas_button.Enable(
            bool(enabled and self.working_lines[index].get("hymn_id") is not None)
        )
        self.delete_line_button.Enable(index is not None)

    def on_checklist(self, _event):
        show_preparation_checklist(self, self.repository.connection, self.service_id)
        self.refresh_checklist_status()

    def refresh_checklist_status(self):
        repository = WorshipChecklistRepository(self.repository.connection)
        rows = repository.items(self.service_id)
        counts = checklist_counts(rows)
        automatic = repository.automatic_summary(self.service_id)
        self.checklist_status.SetLabel(
            f"{counts['DONE']} done · {counts['NOT_DONE']} not done · "
            f"{counts['NOT_NEEDED']} not needed\n"
            f"Participants: {automatic['PARTICIPANTS']} · Hymns: {automatic['HYMNS'].lower()}"
        )

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
        used = [item for item in self.working_lines if item is not line and item["hymn_id"] is not None]
        dialog = HymnPickerDialog(
            self, self.repository, self.service_id, line["label"],
            [item["hymn_id"] for item in used], [item.get("tune") for item in used],
        )
        try:
            if dialog.ShowModal() == wx.ID_OK:
                selected = dialog.selected_hymn
                if line.get("hymn_id") != selected[0]:
                    line["stanzas"] = None
                line["hymn_id"] = selected[0]
                line["value"] = selected[2] or ""
                line["reference"] = selected[1] or ""
                line["tune"] = selected[3] or ""
                self.refresh_grid()
                self.grid.Select(index)
            elif dialog.clear_requested:
                line["hymn_id"], line["value"], line["reference"], line["tune"] = (
                    None, "", "", ""
                )
                line["stanzas"] = None
                self.refresh_grid()
                self.grid.Select(index)
        finally:
            dialog.Destroy()

    def on_edit_stanzas(self, _event):
        index = self.selected_line_index()
        if index is None:
            return
        line = self.working_lines[index]
        if line["source"] != "SERVICE_HYMN" or line.get("hymn_id") is None:
            wx.MessageBox("Select a hymn first.", "Edit Stanzas",
                          wx.OK | wx.ICON_INFORMATION, self)
            return
        dialog = wx.TextEntryDialog(
            self,
            "Enter stanza numbers, lists, or ranges (example: 1,3,11-12).\n\n"
            f"{line['reference']}  {line['value']}",
            "Edit Hymn Stanzas",
            str(line.get("stanzas") or ""),
        )
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            try:
                stanzas = normalize_stanzas(dialog.GetValue())
            except StanzaSelectionError as error:
                wx.MessageBox(str(error), "Invalid Stanza Selection",
                              wx.OK | wx.ICON_WARNING, self)
                return
            hymn = self.repository.one(
                "SELECT COALESCE(Hymn,'') FROM tblHymn WHERE ID=?", (line["hymn_id"],),
            )
            line["stanzas"] = stanzas
            line["reference"] = format_hymn_reference(hymn[0] if hymn else "", stanzas)
            self.refresh_grid()
            self.grid.Select(index)
        finally:
            dialog.Destroy()

    def on_delete_line(self, _event):
        index = self.selected_line_index()
        if index is None:
            return
        line = self.working_lines[index]
        if wx.MessageBox(
            f"Delete '{line['label']}' from this service's weekly Order of Service?\n\n"
            "The reusable template will not be changed.",
            "Delete Weekly Order Line",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
            self,
        ) != wx.YES:
            return
        del self.working_lines[index]
        normalize_line_sequences(self.working_lines)
        self.refresh_grid()
        if self.working_lines:
            target = min(index, len(self.working_lines) - 1)
            self.grid.Select(target)
            self.grid.EnsureVisible(target)

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

    def on_color_override(self, event):
        if not self.loading:
            # Use the event's value directly; on some Windows wxPython builds
            # GetStringSelection still reports the previous item in this handler.
            selected = event.GetString() if event.GetSelection() > 0 else ""
            self._show_liturgical_color(selected or self._selected_proper_color())
        event.Skip()

    def on_communion(self, _event):
        if not self.loading:
            self._refresh_conditional_lines()
            self.refresh_grid()

    def _refresh_conditional_lines(self):
        proper_id = self._choice_value(self.fields["proper"], self.proper_rows)
        detail = self.repository.proper_detail(proper_id) if proper_id else None
        season = detail[2] if detail else ""
        communion = self.fields["communion"].GetValue()
        for line in self.working_lines:
            line["included"] = BulletinOrderGenerator.condition_included(
                line.get("condition_type") or "ALWAYS", line.get("condition_value"),
                communion, season,
            )

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
        else:
            self.fields["liturgical"].SetValue("")
        self._show_liturgical_color_for_selected_proper()
        self._refresh_conditional_lines()
        readings_by_use = {row[0]: row[1] for row in readings}
        unused = list(suggestions)
        for line in self.working_lines:
            if line["source"] == "SERVICE_READING":
                line["value"] = readings_by_use.get(line["key"], "")
            elif line["source"] == "SERVICE_HYMN":
                match = next((i for i, hymn in enumerate(unused) if hymn[3] == line["key"]), None)
                if match is None:
                    line["value"], line["reference"] = "", ""
                    line["hymn_id"], line["tune"] = None, ""
                    line["stanzas"] = None
                else:
                    hymn = unused.pop(match)
                    if line.get("hymn_id") != hymn[0]:
                        line["stanzas"] = None
                    line["hymn_id"] = hymn[0]
                    line["reference"] = format_hymn_reference(hymn[1], line.get("stanzas"))
                    line["value"], line["tune"] = hymn[2], hymn[4]
        self.refresh_grid()

    @staticmethod
    def _choice_value(choice, rows):
        selection = choice.GetSelection()
        return None if selection == wx.NOT_FOUND else rows[selection][0]

    def validation_counts(self):
        _statuses, hymn_duplicates, tune_duplicates = duplicate_selection_status(self.working_lines)
        missing = sum(
            1 for line in self.working_lines
            if line["included"] and line["source"] and not line["value"]
        )
        return hymn_duplicates, tune_duplicates, missing

    def on_save(self, _event):
        template_id = self._choice_value(self.template, self.template_rows)
        if template_id is None:
            wx.MessageBox("Select an Order of Service template before saving.",
                          "Template Required", wx.OK | wx.ICON_WARNING, self)
            return
        hymn_duplicates, tune_duplicates, missing = self.validation_counts()
        if hymn_duplicates or tune_duplicates or missing:
            message = (
                f"The service has {hymn_duplicates} duplicate hymn occurrence(s), "
                f"{tune_duplicates} different hymn(s) sharing a tune, and "
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
            (self.fields["color_override"].GetStringSelection()
             if self.fields["color_override"].GetSelection() > 0 else None),
            int(self.fields["communion"].GetValue()), template_id,
            self.fields["os_note"].GetValue() or None,
            self._choice_value(self.fields["sermon"], self.sermon_rows),
            self.fields["bulletin"].GetPath() or None,
            self.fields["note"].GetValue() or None,
        )
        try:
            self.repository.save(
                self.service_id, service_values, template_id, self.working_lines,
            )
            self.saved = True
            self.save_status.SetLabel("Worship Service and weekly Order of Service saved.")
            self.save_status.SetForegroundColour(wx.Colour(0, 120, 0))
            wx.MessageBox("The complete Worship Service was saved.", "Worship Service",
                          wx.OK | wx.ICON_INFORMATION, self)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Save Worship Service",
                          wx.OK | wx.ICON_ERROR, self)


class HymnPickerDialog(wx.Dialog):
    SEARCH_FIELDS = (
        "All fields", "Hymn number", "Title", "Tune", "Bible reference", "Category", "Notes",
    )

    def __init__(self, parent, repository, service_id, used_as, used_hymn_ids, used_tunes=()):
        super().__init__(parent, title="Select Hymn", size=(980, 650),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = repository
        self.service_id = service_id
        self.used_ids = set(used_hymn_ids)
        self.used_tunes = {normalize_tune(tune) for tune in used_tunes if normalize_tune(tune)}
        self.rows = []
        self._last_header_click = (None, 0.0)
        self._sort_column = None
        self._sort_reverse = False
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
            ("Hymn", 90), ("Title", 235), ("Tune", 180), ("Bible reference", 125),
            ("Category", 105), ("Notes", 145), ("Status", 105),
        ):
            self.grid.AppendColumn(label, width=width)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_select)
        self.grid.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)
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
        self._populate_grid()

    def _status(self, row):
        if row[0] in self.used_ids:
            return "Already used"
        if normalize_tune(row[3]) in self.used_tunes:
            return "Tune already used"
        return ""

    def _populate_grid(self):
        self.grid.DeleteAllItems()
        for index, row in enumerate(self.rows):
            item = self.grid.InsertItem(index, str(row[1]))
            status = self._status(row)
            for column, value in enumerate((row[2], row[3], row[4], row[5], row[6], status), 1):
                self.grid.SetItem(item, column, str(value))
            if status:
                self.grid.SetItemTextColour(item, wx.Colour(190, 90, 0))

    def on_column_click(self, event):
        """Sort only after two clicks on the same header in quick succession."""
        column = event.GetColumn()
        now = time.monotonic()
        previous_column, previous_time = self._last_header_click
        self._last_header_click = (column, now)
        if column != previous_column or now - previous_time > 0.65:
            return
        self._last_header_click = (None, 0.0)
        self._sort_reverse = not self._sort_reverse if self._sort_column == column else False
        self._sort_column = column
        value_indexes = (1, 2, 3, 4, 5, 6)
        if column < len(value_indexes):
            key = lambda row: str(row[value_indexes[column]] or "").casefold()
        else:
            key = lambda row: self._status(row).casefold()
        self.rows.sort(key=key, reverse=self._sort_reverse)
        self._populate_grid()

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
            ("Note", detail[7]),
        )
        info = wx.FlexGridSizer(cols=2, vgap=5, hgap=10)
        info.AddGrowableCol(1, 1)
        for label, value in labels:
            info.Add(wx.StaticText(panel, label=label + ":"), 0, wx.ALIGN_TOP)
            if label == "Color" and str(value or "").strip():
                color_row = wx.BoxSizer(wx.HORIZONTAL)
                color = liturgical_color_hex(value)
                if color:
                    swatch = wx.Panel(panel, size=(24, 18), style=wx.BORDER_SIMPLE)
                    swatch.SetBackgroundColour(wx.Colour(color))
                    color_row.Add(swatch, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
                color_row.Add(
                    wx.StaticText(panel, label=str(value)), 0, wx.ALIGN_CENTER_VERTICAL,
                )
                info.Add(color_row, 1, wx.EXPAND)
            else:
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
            item = hymn_grid.InsertItem(index, str(row[3]))
            hymn_grid.SetItem(item, 1, " ".join(value for value in (row[1], row[2]) if value))
        hymn_box = wx.BoxSizer(wx.VERTICAL); hymn_box.Add(hymn_grid, 1, wx.EXPAND | wx.ALL, 6)
        hymn_page.SetSizer(hymn_box)
        outer.Add(book, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        buttons = wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer(); buttons.Add(close)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(outer)


def show_unified_worship_service(parent, connection, service_id, new_service=False):
    dialog = UnifiedWorshipServiceEditor(parent, connection, service_id, new_service)
    try:
        dialog.ShowModal()
        return dialog.saved
    finally:
        dialog.Destroy()
