"""Normalized worship participants, requirements, and preview-based scheduling."""

from dataclasses import dataclass
from datetime import datetime

import wx
import wx.adv

from bulletin_orders import portable_connection


def dialog_button_sizer(dialog, parent, flags=wx.OK | wx.CANCEL):
    """Create standard dialog buttons with the same parent as the containing sizer."""
    buttons = wx.StdDialogButtonSizer()
    for button_id in (wx.ID_OK, wx.ID_CANCEL):
        wanted = wx.OK if button_id == wx.ID_OK else wx.CANCEL
        if flags & wanted:
            button = wx.Button(parent, button_id)
            button.Bind(wx.EVT_BUTTON, lambda _event, value=button_id: dialog.EndModal(value))
            buttons.AddButton(button)
    buttons.Realize()
    return buttons


def serialized_values(value):
    text = str(value or "").replace("[", "").replace("]", "")
    for separator in (";", "\r", "\n"):
        text = text.replace(separator, ",")
    return [item.strip().strip("'\"") for item in text.split(",") if item.strip().strip("'\"")]


def time_text(value):
    if value is None:
        return None
    if hasattr(value, "hour"):
        return f"{value.hour:02d}:{value.minute:02d}"
    if hasattr(value, "total_seconds"):
        seconds = int(value.total_seconds()) % 86400
        return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}"
    pieces = str(value).split(":")
    return ":".join(piece.zfill(2) for piece in pieces[:2]) if len(pieces) >= 2 else str(value)


def pattern_matches(pattern, starts_at, season):
    _pattern_id, _description, service_time, days, months, seasons = pattern[:6]
    if service_time is not None:
        candidate = time_text(service_time)
        if starts_at.strftime("%H:%M") != candidate:
            return False
    filters = (
        (serialized_values(days), starts_at.strftime("%A")),
        (serialized_values(months), starts_at.strftime("%B")),
        (serialized_values(seasons), str(season or "")),
    )
    return all(not values or "All" in values or current in values for values, current in filters)


@dataclass(frozen=True)
class AssignmentSuggestion:
    role_id: int
    role: str
    participant_id: int
    participant: str


def required_position_rows(requirements, assignments):
    """Combine required slots and actual assignments for screens and reports."""
    unused = list(assignments)
    rows = []
    for _requirement_id, role_id, role, required_count in requirements:
        matching = [row for row in unused if row[1] == role_id and row[5] != "DECLINED"]
        for slot in range(1, int(required_count) + 1):
            assignment = matching.pop(0) if matching else None
            if assignment:
                unused.remove(assignment)
            rows.append((role_id, role, slot, int(required_count), assignment, True))
    for assignment in unused:
        rows.append((assignment[1], assignment[2], None, None, assignment, False))
    return rows


class WorshipSchedulingRepository:
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

    def service_context(self, service_id):
        return self.one(
            "SELECT s.ID,s.ChurchID,s.DateTime,s.BulletinOrderTemplateID,"
            "COALESCE(p.Season,''),COALESCE(s.LiturgicalDate,'') "
            "FROM tblService s LEFT JOIN tblPropers p ON p.ID=s.PropersID WHERE s.ID=?",
            (service_id,),
        )

    def services(self):
        return self.all(
            "SELECT ID,CONCAT(DATE_FORMAT(DateTime,'%m/%d/%Y %h:%i %p'),' - ',"
            "COALESCE(LiturgicalDate,'')) FROM tblService ORDER BY DateTime DESC,ID DESC"
        )

    def roles(self, active_only=True):
        sql = "SELECT ID,Name,COALESCE(Description,''),DisplayOrder,Active FROM tblWorshipRole"
        if active_only:
            sql += " WHERE Active=1"
        return self.all(sql + " ORDER BY DisplayOrder,Name,ID")

    def participants(self, active_only=True):
        sql = (
            "SELECT p.ID,p.PersonID,COALESCE(NULLIF(p.DisplayName,''),p.Name),"
            "COALESCE(p.eMail,''),COALESCE(p.Phone,''),p.Active,p.ExternalParticipant,"
            "COALESCE(p.Note,''),COALESCE(GROUP_CONCAT(wr.Name ORDER BY wr.DisplayOrder SEPARATOR ', '),'') "
            "FROM tblParticipant p LEFT JOIN tblParticipantRole pr "
            "ON pr.ParticipantID=p.ID AND pr.Active=1 LEFT JOIN tblWorshipRole wr "
            "ON wr.ID=pr.WorshipRoleID GROUP BY p.ID,p.PersonID,p.DisplayName,p.Name,p.eMail,"
            "p.Phone,p.Active,p.ExternalParticipant,p.Note"
        )
        if active_only:
            sql += " HAVING p.Active=1"
        return self.all(sql + " ORDER BY 3,p.ID")

    def people(self):
        return self.all(
            "SELECT ID,TRIM(CONCAT_WS(' ',NULLIF(Title,''),FirstName,MiddleName,LastName)) "
            "FROM tblPerson ORDER BY LastName,FirstName,ID"
        )

    def patterns(self, active_only=True):
        sql = (
            "SELECT ID,Description,ServiceTime,DaysOfWeek,Months,Seasons,"
            "RotationIncrement,Active,COALESCE(Note,'') FROM tblWorshipSchedulePattern"
        )
        if active_only:
            sql += " WHERE Active=1"
        return self.all(sql + " ORDER BY Description,ID")

    def participant_role_ids(self, participant_id):
        return {row[0] for row in self.all(
            "SELECT WorshipRoleID FROM tblParticipantRole WHERE ParticipantID=? AND Active=1",
            (participant_id,),
        )}

    def participant_pattern_ids(self, participant_id):
        return {row[0] for row in self.all(
            "SELECT DISTINCT SchedulePatternID FROM tblParticipantAvailability "
            "WHERE ParticipantID=? AND Active=1", (participant_id,),
        )}

    def save_participant(self, participant_id, values, role_ids, pattern_ids):
        person_id, display_name, email, phone, active, external, note = values
        cursor = self.connection.cursor()
        try:
            legacy_roles = ";".join(str(row[1]) for row in self.all(
                "SELECT ID,COALESCE(LegacyRoleID,ID) FROM tblWorshipRole WHERE ID IN ("
                + ",".join("?" for _ in role_ids) + ")", tuple(role_ids),
            )) if role_ids else ""
            legacy_schedules = ";".join(str(row[1]) for row in self.all(
                "SELECT ID,COALESCE(SourceLegacyScheduleID,ID) FROM tblWorshipSchedulePattern WHERE ID IN ("
                + ",".join("?" for _ in pattern_ids) + ")", tuple(pattern_ids),
            )) if pattern_ids else ""
            if participant_id is None:
                cursor.execute(
                    "INSERT INTO tblParticipant "
                    "(PersonID,Name,DisplayName,Roles,Schedule,Phone,eMail,Active,ExternalParticipant,Note) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (person_id,display_name,display_name,legacy_roles,legacy_schedules,phone or None,
                     email or None,int(active),int(external),note or None),
                )
                participant_id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE tblParticipant SET PersonID=?,Name=?,DisplayName=?,Roles=?,Schedule=?,"
                    "Phone=?,eMail=?,Active=?,ExternalParticipant=?,Note=? WHERE ID=?",
                    (person_id,display_name,display_name,legacy_roles,legacy_schedules,phone or None,
                     email or None,int(active),int(external),note or None,participant_id),
                )
                cursor.execute("DELETE FROM tblParticipantRole WHERE ParticipantID=?", (participant_id,))
                cursor.execute("DELETE FROM tblParticipantAvailability WHERE ParticipantID=?", (participant_id,))
            for role_id in role_ids:
                cursor.execute(
                    "INSERT INTO tblParticipantRole (ParticipantID,WorshipRoleID) VALUES (?,?)",
                    (participant_id, role_id),
                )
            for role_id in role_ids:
                for pattern_id in pattern_ids:
                    cursor.execute(
                        "INSERT INTO tblParticipantAvailability "
                        "(ParticipantID,WorshipRoleID,SchedulePatternID) VALUES (?,?,?)",
                        (participant_id, role_id, pattern_id),
                    )
            self.connection.commit()
            return participant_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def save_role(self, role_id, name, description, order, active):
        cursor = self.connection.cursor()
        try:
            if role_id is None:
                cursor.execute(
                    "INSERT INTO tblWorshipRole (Name,Description,DisplayOrder,Active) VALUES (?,?,?,?)",
                    (name, description or None, order, int(active)),
                )
            else:
                cursor.execute(
                    "UPDATE tblWorshipRole SET Name=?,Description=?,DisplayOrder=?,Active=? WHERE ID=?",
                    (name, description or None, order, int(active), role_id),
                )
                cursor.execute("UPDATE tblServiceRole SET Role=? WHERE WorshipRoleID=?", (name, role_id))
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def delete_role(self, role_id):
        references = (
            ("tblParticipantRole", "eligible participant"),
            ("tblParticipantAvailability", "availability pattern"),
            ("tblWorshipRoleRequirement", "Order of Service template"),
            ("tblServiceRole", "worship service assignment"),
        )
        used = []
        cursor = self.connection.cursor()
        try:
            for table, description in references:
                cursor.execute(
                    f"SELECT COUNT(*) FROM {table} WHERE WorshipRoleID=?", (role_id,),
                )
                count = int(cursor.fetchone()[0])
                if count:
                    used.append(f"{count} {description}{'' if count == 1 else 's'}")
            if used:
                raise ValueError(
                    "This position cannot be deleted because it is used by "
                    + ", ".join(used)
                    + ". Edit the position and clear Active instead."
                )
            cursor.execute("DELETE FROM tblWorshipRole WHERE ID=?", (role_id,))
            if cursor.rowcount != 1:
                raise ValueError("The selected position no longer exists.")
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def save_pattern(self, pattern_id, values):
        cursor = self.connection.cursor()
        try:
            if pattern_id is None:
                cursor.execute(
                    "INSERT INTO tblWorshipSchedulePattern "
                    "(Description,ServiceTime,DaysOfWeek,Months,Seasons,RotationIncrement,Active,Note) "
                    "VALUES (?,?,?,?,?,?,?,?)", values,
                )
            else:
                cursor.execute(
                    "UPDATE tblWorshipSchedulePattern SET Description=?,ServiceTime=?,DaysOfWeek=?,"
                    "Months=?,Seasons=?,RotationIncrement=?,Active=?,Note=? WHERE ID=?",
                    values + (pattern_id,),
                )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def assignments(self, service_id):
        return self.all(
            "SELECT sr.ID,sr.WorshipRoleID,COALESCE(wr.Name,sr.Role),sr.ParticipantID,"
            "COALESCE(NULLIF(p.DisplayName,''),p.Name),sr.AssignmentStatus,COALESCE(sr.Note,'') "
            "FROM tblServiceRole sr JOIN tblParticipant p ON p.ID=sr.ParticipantID "
            "LEFT JOIN tblWorshipRole wr ON wr.ID=sr.WorshipRoleID "
            "WHERE sr.ServiceID=? ORDER BY COALESCE(wr.DisplayOrder,500),5,sr.ID", (service_id,),
        )

    def save_assignment(self, assignment_id, service_id, role_id, participant_id, status, note):
        role = self.one("SELECT Name FROM tblWorshipRole WHERE ID=?", (role_id,))
        if not role:
            raise ValueError("Select a valid worship role.")
        cursor = self.connection.cursor()
        try:
            if assignment_id is None:
                cursor.execute(
                    "INSERT INTO tblServiceRole "
                    "(ServiceID,ParticipantID,WorshipRoleID,Role,AssignmentStatus,Note) "
                    "VALUES (?,?,?,?,?,?)",
                    (service_id,participant_id,role_id,role[0],status,note or None),
                )
            else:
                cursor.execute(
                    "UPDATE tblServiceRole SET ParticipantID=?,WorshipRoleID=?,Role=?,"
                    "AssignmentStatus=?,Note=? WHERE ID=? AND ServiceID=?",
                    (participant_id,role_id,role[0],status,note or None,assignment_id,service_id),
                )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def delete_assignment(self, assignment_id, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM tblServiceRole WHERE ID=? AND ServiceID=?", (assignment_id, service_id))
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def requirements(self, service_id):
        context = self.service_context(service_id)
        if not context:
            return []
        template_id = context[3]
        if template_id is None:
            return []
        return self.template_requirements(template_id)

    def template_requirements(self, template_id):
        return self.all(
            "SELECT r.ID,r.WorshipRoleID,wr.Name,r.RequiredCount FROM tblWorshipRoleRequirement r "
            "JOIN tblWorshipRole wr ON wr.ID=r.WorshipRoleID "
            "WHERE r.BulletinOrderTemplateID=? AND r.Active=1 "
            "ORDER BY wr.DisplayOrder,wr.Name", (template_id,),
        )

    def save_requirements(self, service_id, counts):
        context = self.service_context(service_id)
        if not context:
            raise ValueError("The selected Worship Service is unavailable.")
        template_id = context[3]
        if template_id is None:
            raise ValueError(
                "Select and save an Order of Service template before setting required positions."
            )
        self.save_template_requirements(template_id, counts)

    def save_template_requirements(self, template_id, counts):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "DELETE FROM tblWorshipRoleRequirement WHERE BulletinOrderTemplateID=?",
                (template_id,),
            )
            for role_id, count in counts.items():
                if count > 0:
                    cursor.execute(
                        "INSERT INTO tblWorshipRoleRequirement "
                        "(BulletinOrderTemplateID,WorshipRoleID,RequiredCount) "
                        "VALUES (?,?,?)", (template_id,role_id,count),
                    )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def eligible_candidates(self, role_id, starts_at, season):
        participants = self.all(
            "SELECT p.ID,COALESCE(NULLIF(p.DisplayName,''),p.Name),"
            "(SELECT COUNT(*) FROM tblServiceRole history WHERE history.ParticipantID=p.ID "
            "AND history.WorshipRoleID=pr.WorshipRoleID) AS Uses "
            "FROM tblParticipantRole pr JOIN tblParticipant p ON p.ID=pr.ParticipantID "
            "WHERE pr.WorshipRoleID=? AND pr.Active=1 AND p.Active=1 ORDER BY Uses,2,p.ID",
            (role_id,),
        )
        result = []
        for participant in participants:
            patterns = self.all(
                "SELECT sp.ID,sp.Description,sp.ServiceTime,sp.DaysOfWeek,sp.Months,sp.Seasons "
                "FROM tblParticipantAvailability a JOIN tblWorshipSchedulePattern sp "
                "ON sp.ID=a.SchedulePatternID WHERE a.ParticipantID=? AND a.WorshipRoleID=? "
                "AND a.Active=1 AND sp.Active=1", (participant[0], role_id),
            )
            if not patterns or any(pattern_matches(pattern, starts_at, season) for pattern in patterns):
                result.append(participant)
        return result


class SchedulingSuggestionService:
    def __init__(self, repository):
        self.repository = repository

    def suggest(self, service_id):
        context = self.repository.service_context(service_id)
        if not context:
            raise ValueError("The selected Worship Service is unavailable.")
        requirements = self.repository.requirements(service_id)
        if not requirements:
            raise ValueError("No participant-role requirements are configured for this Order of Service.")
        existing = self.repository.assignments(service_id)
        counts = {}
        used_for_role = {}
        for row in existing:
            if row[5] != "DECLINED":
                counts[row[1]] = counts.get(row[1], 0) + 1
            used_for_role.setdefault(row[1], set()).add(row[3])
        suggestions = []
        for _id, role_id, role, required in requirements:
            missing = max(0, int(required) - counts.get(role_id, 0))
            candidates = self.repository.eligible_candidates(role_id, context[2], context[4])
            available = [row for row in candidates if row[0] not in used_for_role.get(role_id, set())]
            for participant in available[:missing]:
                suggestions.append(AssignmentSuggestion(role_id, role, participant[0], participant[1]))
        return suggestions

    def apply(self, service_id, suggestions):
        for item in suggestions:
            self.repository.save_assignment(
                None, service_id, item.role_id, item.participant_id, "SUGGESTED", "Suggested by ChurchManager",
            )
        return len(suggestions)


class ParticipantEditDialog(wx.Dialog):
    def __init__(self, parent, repository, participant=None):
        super().__init__(parent, title="Participant", size=(650, 650),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository, self.participant = repository, participant
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        form = wx.FlexGridSizer(cols=2, vgap=7, hgap=10); form.AddGrowableCol(1, 1)
        self.people = [(None, "Not linked to a member"), *repository.people()]
        self.person = wx.Choice(panel, choices=[row[1] for row in self.people])
        self.name, self.email, self.phone = wx.TextCtrl(panel), wx.TextCtrl(panel), wx.TextCtrl(panel)
        self.external, self.active = wx.CheckBox(panel, label="External participant"), wx.CheckBox(panel, label="Active")
        self.note = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        for label, control in (("Member link",self.person),("Display name",self.name),("Email",self.email),
                               ("Phone",self.phone),("",self.external),("",self.active),("Note",self.note)):
            form.Add(wx.StaticText(panel,label=label + (":" if label else "")),0,wx.ALIGN_CENTER_VERTICAL)
            form.Add(control,1,wx.EXPAND)
        outer.Add(form,0,wx.EXPAND|wx.ALL,10)
        lists = wx.BoxSizer(wx.HORIZONTAL)
        roles_box = wx.StaticBoxSizer(wx.VERTICAL,panel,"Eligible roles")
        self.roles = repository.roles(); self.role_list=wx.CheckListBox(panel,choices=[r[1] for r in self.roles])
        roles_box.Add(self.role_list,1,wx.EXPAND|wx.ALL,5); lists.Add(roles_box,1,wx.EXPAND|wx.RIGHT,5)
        patterns_box = wx.StaticBoxSizer(wx.VERTICAL,panel,"Usual service patterns")
        self.patterns=repository.patterns(); self.pattern_list=wx.CheckListBox(panel,choices=[p[1] for p in self.patterns])
        patterns_box.Add(self.pattern_list,1,wx.EXPAND|wx.ALL,5); lists.Add(patterns_box,1,wx.EXPAND|wx.LEFT,5)
        outer.Add(lists,1,wx.EXPAND|wx.LEFT|wx.RIGHT,10)
        buttons=dialog_button_sizer(self,panel); outer.Add(buttons,0,wx.EXPAND|wx.ALL,10)
        panel.SetSizer(outer); self._load()

    def _load(self):
        row=self.participant
        self.person.SetSelection(0); self.active.SetValue(True)
        if not row: return
        person_id=row[1]; self.person.SetSelection(next((i for i,p in enumerate(self.people) if p[0]==person_id),0))
        self.name.SetValue(str(row[2] or "")); self.email.SetValue(str(row[3] or "")); self.phone.SetValue(str(row[4] or ""))
        self.active.SetValue(bool(row[5])); self.external.SetValue(bool(row[6])); self.note.SetValue(str(row[7] or ""))
        role_ids=self.repository.participant_role_ids(row[0]); pattern_ids=self.repository.participant_pattern_ids(row[0])
        for i,item in enumerate(self.roles): self.role_list.Check(i,item[0] in role_ids)
        for i,item in enumerate(self.patterns): self.pattern_list.Check(i,item[0] in pattern_ids)

    def values(self):
        person_id=self.people[self.person.GetSelection()][0]
        name=self.name.GetValue().strip() or (self.people[self.person.GetSelection()][1] if person_id else "")
        if not name: raise ValueError("Enter a participant name or select a member.")
        roles=[row[0] for i,row in enumerate(self.roles) if self.role_list.IsChecked(i)]
        patterns=[row[0] for i,row in enumerate(self.patterns) if self.pattern_list.IsChecked(i)]
        return (person_id,name,self.email.GetValue().strip(),self.phone.GetValue().strip(),
                self.active.GetValue(),person_id is None or self.external.GetValue(),self.note.GetValue().strip()),roles,patterns


class ParticipantManagerDialog(wx.Dialog):
    def __init__(self,parent,connection):
        super().__init__(parent,title="Worship Participants",size=(900,600),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.repository=WorshipSchedulingRepository(connection); self.rows=[]
        panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        note=wx.StaticText(panel,label="Participants may be linked to a congregation member or maintained as an outside participant.")
        note.SetForegroundColour(wx.Colour(0,90,190)); outer.Add(note,0,wx.ALL,10)
        self.grid=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for label,width in (("Participant",220),("Type",90),("Email",210),("Phone",120),("Eligible roles",220)):
            self.grid.AppendColumn(label,width=width)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.on_edit); outer.Add(self.grid,1,wx.EXPAND|wx.LEFT|wx.RIGHT,10)
        actions=wx.BoxSizer(wx.HORIZONTAL)
        for label,handler in (("Add Participant...",self.on_add),("Edit Participant...",self.on_edit),("Manage Roles...",self.on_roles)):
            button=wx.Button(panel,label=label); button.Bind(wx.EVT_BUTTON,handler); actions.Add(button,0,wx.RIGHT,8)
        actions.AddStretchSpacer(); actions.Add(wx.Button(panel,wx.ID_CANCEL,"Close"))
        outer.Add(actions,0,wx.EXPAND|wx.ALL,10); panel.SetSizer(outer); self.refresh()

    def refresh(self):
        self.rows=self.repository.participants(False); self.grid.DeleteAllItems()
        for i,row in enumerate(self.rows):
            item=self.grid.InsertItem(i,str(row[2])); values=("External" if row[6] else "Member",row[3],row[4],row[8])
            for column,value in enumerate(values,1): self.grid.SetItem(item,column,str(value or ""))
            if not row[5]: self.grid.SetItemTextColour(item,wx.Colour(130,130,130))

    def selected(self):
        index=self.grid.GetFirstSelected(); return self.rows[index] if index>=0 else None

    def _edit(self,row):
        dialog=ParticipantEditDialog(self,self.repository,row)
        try:
            if dialog.ShowModal()==wx.ID_OK:
                values,roles,patterns=dialog.values(); self.repository.save_participant(row[0] if row else None,values,roles,patterns); self.refresh()
        except Exception as error: wx.MessageBox(str(error),"Unable to Save Participant",wx.OK|wx.ICON_ERROR,self)
        finally: dialog.Destroy()

    def on_add(self,_event): self._edit(None)
    def on_edit(self,_event):
        row=self.selected()
        if row: self._edit(row)
    def on_roles(self,_event):
        dialog=RoleManagerDialog(self,self.repository); dialog.ShowModal(); dialog.Destroy(); self.refresh()


class RoleManagerDialog(wx.Dialog):
    def __init__(self,parent,repository):
        super().__init__(parent,title="Worship Roles",size=(620,480),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.repository=repository; self.rows=[]; panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        self.grid=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for label,width in (("Role",180),("Description",300),("Active",70)): self.grid.AppendColumn(label,width=width)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.on_edit); outer.Add(self.grid,1,wx.EXPAND|wx.ALL,10)
        row=wx.BoxSizer(wx.HORIZONTAL)
        for label,handler in (("Add Role...",self.on_add),("Edit Role...",self.on_edit),("Delete Role",self.on_delete)):
            b=wx.Button(panel,label=label); b.Bind(wx.EVT_BUTTON,handler); row.Add(b,0,wx.RIGHT,8)
        row.AddStretchSpacer(); row.Add(wx.Button(panel,wx.ID_CANCEL,"Close")); outer.Add(row,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,10)
        panel.SetSizer(outer); self.refresh()
    def refresh(self):
        self.rows=self.repository.roles(False); self.grid.DeleteAllItems()
        for i,row in enumerate(self.rows):
            item=self.grid.InsertItem(i,row[1]); self.grid.SetItem(item,1,row[2]); self.grid.SetItem(item,2,"Yes" if row[4] else "No")
    def _edit(self,row):
        dialog=wx.Dialog(self,title="Worship Role"); panel=wx.Panel(dialog); s=wx.BoxSizer(wx.VERTICAL)
        name=wx.TextCtrl(panel,value=row[1] if row else ""); desc=wx.TextCtrl(panel,value=row[2] if row else "")
        order=wx.SpinCtrl(panel,min=1,max=999,initial=int(row[3]) if row else 100); active=wx.CheckBox(panel,label="Active"); active.SetValue(bool(row[4]) if row else True)
        for label,control in (("Role",name),("Description",desc),("Display order",order)):
            s.Add(wx.StaticText(panel,label=label+":"),0,wx.LEFT|wx.RIGHT|wx.TOP,8); s.Add(control,0,wx.EXPAND|wx.LEFT|wx.RIGHT,8)
        s.Add(active,0,wx.ALL,8); s.Add(dialog_button_sizer(dialog,panel),0,wx.EXPAND|wx.ALL,8); panel.SetSizer(s); dialog.Fit()
        try:
            if dialog.ShowModal()==wx.ID_OK:
                if not name.GetValue().strip(): raise ValueError("Enter a role name.")
                self.repository.save_role(row[0] if row else None,name.GetValue().strip(),desc.GetValue().strip(),order.GetValue(),active.GetValue()); self.refresh()
        except Exception as error: wx.MessageBox(str(error),"Unable to Save Role",wx.OK|wx.ICON_ERROR,self)
        finally: dialog.Destroy()
    def on_add(self,_event): self._edit(None)
    def on_edit(self,_event):
        index=self.grid.GetFirstSelected()
        if index>=0: self._edit(self.rows[index])
    def on_delete(self,_event):
        index=self.grid.GetFirstSelected()
        if index<0:
            return
        role=self.rows[index]
        if wx.MessageBox(
            f"Permanently delete the unused position '{role[1]}'?",
            "Delete Worship Position",wx.YES_NO|wx.NO_DEFAULT|wx.ICON_WARNING,self,
        )!=wx.YES:
            return
        try:
            self.repository.delete_role(role[0]); self.refresh()
        except Exception as error:
            wx.MessageBox(str(error),"Unable to Delete Position",wx.OK|wx.ICON_INFORMATION,self)


class SchedulePatternManagerDialog(wx.Dialog):
    DAYS=("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
    MONTHS=("January","February","March","April","May","June","July","August","September","October","November","December")
    def __init__(self,parent,connection):
        super().__init__(parent,title="Worship Schedule Patterns",size=(780,520),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.repository=WorshipSchedulingRepository(connection); self.rows=[]; panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        note=wx.StaticText(panel,label="Patterns describe usual availability. Blank day, month, or season lists mean any value.")
        note.SetForegroundColour(wx.Colour(0,90,190)); outer.Add(note,0,wx.ALL,10)
        self.grid=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for label,width in (("Pattern",220),("Time",90),("Days",190),("Months",190),("Active",60)): self.grid.AppendColumn(label,width=width)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.on_edit); outer.Add(self.grid,1,wx.EXPAND|wx.LEFT|wx.RIGHT,10)
        actions=wx.BoxSizer(wx.HORIZONTAL)
        for label,handler in (("Add Pattern...",self.on_add),("Edit Pattern...",self.on_edit)):
            b=wx.Button(panel,label=label); b.Bind(wx.EVT_BUTTON,handler); actions.Add(b,0,wx.RIGHT,8)
        actions.AddStretchSpacer(); actions.Add(wx.Button(panel,wx.ID_CANCEL,"Close")); outer.Add(actions,0,wx.EXPAND|wx.ALL,10)
        panel.SetSizer(outer); self.refresh()
    def refresh(self):
        self.rows=self.repository.patterns(False); self.grid.DeleteAllItems()
        for i,row in enumerate(self.rows):
            item=self.grid.InsertItem(i,row[1]); time=row[2].strftime("%I:%M %p") if hasattr(row[2],"strftime") else str(row[2] or "Any")
            for col,value in enumerate((time,row[3] or "Any",row[4] or "Any","Yes" if row[7] else "No"),1): self.grid.SetItem(item,col,str(value))
    def _edit(self,row):
        dialog=SchedulePatternEditDialog(self,row)
        try:
            if dialog.ShowModal()==wx.ID_OK: self.repository.save_pattern(row[0] if row else None,dialog.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error),"Unable to Save Pattern",wx.OK|wx.ICON_ERROR,self)
        finally: dialog.Destroy()
    def on_add(self,_event): self._edit(None)
    def on_edit(self,_event):
        index=self.grid.GetFirstSelected()
        if index>=0: self._edit(self.rows[index])


class SchedulePatternEditDialog(wx.Dialog):
    SEASONS=("Advent","Christmas","Epiphany","Lent","Easter","Pentecost")
    def __init__(self,parent,row=None):
        super().__init__(parent,title="Schedule Pattern",size=(660,570),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.row=row; panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        form=wx.FlexGridSizer(cols=2,vgap=7,hgap=10); form.AddGrowableCol(1,1)
        self.description=wx.TextCtrl(panel,value=row[1] if row else ""); self.time=wx.adv.TimePickerCtrl(panel)
        self.any_time=wx.CheckBox(panel,label="Any service time"); self.any_time.SetValue(not row or row[2] is None)
        self.increment=wx.SpinCtrl(panel,min=0,max=52,initial=int(row[6] or 0) if row else 0); self.active=wx.CheckBox(panel,label="Active"); self.active.SetValue(bool(row[7]) if row else True)
        self.note=wx.TextCtrl(panel,value=str(row[8] or "") if row else "",style=wx.TE_MULTILINE)
        for label,control in (("Description",self.description),("Service time",self.time),("",self.any_time),("Rotation increment",self.increment),("",self.active),("Note",self.note)):
            form.Add(wx.StaticText(panel,label=label+(":" if label else "")),0,wx.ALIGN_CENTER_VERTICAL); form.Add(control,1,wx.EXPAND)
        outer.Add(form,0,wx.EXPAND|wx.ALL,10)
        lists=wx.BoxSizer(wx.HORIZONTAL); self.days=wx.CheckListBox(panel,choices=SchedulePatternManagerDialog.DAYS); self.months=wx.CheckListBox(panel,choices=SchedulePatternManagerDialog.MONTHS); self.seasons=wx.CheckListBox(panel,choices=self.SEASONS)
        for label,control in (("Days",self.days),("Months",self.months),("Seasons",self.seasons)):
            box=wx.StaticBoxSizer(wx.VERTICAL,panel,label); box.Add(control,1,wx.EXPAND|wx.ALL,4); lists.Add(box,1,wx.EXPAND|wx.RIGHT,5)
        outer.Add(lists,1,wx.EXPAND|wx.LEFT|wx.RIGHT,10); outer.Add(dialog_button_sizer(self,panel),0,wx.EXPAND|wx.ALL,10); panel.SetSizer(outer)
        if row:
            if row[2] is not None:
                hour,minute=(int(value) for value in time_text(row[2]).split(":")); now=wx.DateTime.Now(); now.SetHour(hour); now.SetMinute(minute); now.SetSecond(0); self.time.SetValue(now)
            self._check(self.days,row[3]); self._check(self.months,row[4]); self._check(self.seasons,row[5])
    @staticmethod
    def _check(control,values):
        selected={v.casefold() for v in serialized_values(values)}
        for i in range(control.GetCount()): control.Check(i,control.GetString(i).casefold() in selected)
    @staticmethod
    def _selected(control): return ",".join(control.GetString(i) for i in range(control.GetCount()) if control.IsChecked(i)) or None
    def values(self):
        if not self.description.GetValue().strip(): raise ValueError("Enter a schedule description.")
        selected=self.time.GetValue(); service_time=None if self.any_time.GetValue() else selected.Format("%H:%M:%S")
        return (self.description.GetValue().strip(),service_time,self._selected(self.days),self._selected(self.months),self._selected(self.seasons),self.increment.GetValue() or None,int(self.active.GetValue()),self.note.GetValue().strip() or None)


class RequirementDialog(wx.Dialog):
    def __init__(self,parent,repository,service_id=None,template_id=None):
        super().__init__(parent,title="Required Positions",size=(470,610),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.repository,self.service_id=repository,service_id; self.roles=repository.roles()
        rows = repository.template_requirements(template_id) if template_id is not None else repository.requirements(service_id)
        existing={r[1]:int(r[3]) for r in rows}
        panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        heading=wx.StaticText(panel,label="Who normally serves in this Order of Service?")
        heading.SetFont(heading.GetFont().Bold().Larger())
        outer.Add(heading,0,wx.LEFT|wx.RIGHT|wx.TOP,14)
        note=wx.StaticText(panel,label="Enter the usual number needed for each position. Leave a position at zero when it is not normally used.")
        note.Wrap(425); outer.Add(note,0,wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM,14)
        staffing=wx.StaticBoxSizer(wx.VERTICAL,panel,"Normal staffing")
        headers=wx.BoxSizer(wx.HORIZONTAL)
        role_header=wx.StaticText(panel,label="Position",size=(275,-1)); role_header.SetFont(role_header.GetFont().Bold())
        count_header=wx.StaticText(panel,label="People needed"); count_header.SetFont(count_header.GetFont().Bold())
        headers.Add(role_header,0); headers.Add(count_header,0)
        staffing.Add(headers,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM,8)
        self.scroll=wx.ScrolledWindow(panel,style=wx.VSCROLL|wx.BORDER_NONE); self.scroll.SetScrollRate(0,10)
        self.position_grid=wx.FlexGridSizer(cols=2,vgap=7,hgap=12); self.counts={}
        self.scroll.SetSizer(self.position_grid); staffing.Add(self.scroll,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,8)
        outer.Add(staffing,1,wx.EXPAND|wx.LEFT|wx.RIGHT,14)
        summary_row=wx.BoxSizer(wx.HORIZONTAL)
        self.summary=wx.StaticText(panel)
        self.summary.SetForegroundColour(wx.Colour(0,90,190))
        summary_row.Add(self.summary,1,wx.ALIGN_CENTER_VERTICAL)
        manage=wx.Button(panel,label="Manage Positions...")
        manage.SetToolTip("Add, rename, activate, or deactivate worship positions.")
        manage.Bind(wx.EVT_BUTTON,self._manage_positions)
        summary_row.Add(manage,0,wx.LEFT,10)
        outer.Add(summary_row,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,14)
        outer.Add(dialog_button_sizer(self,panel),0,wx.EXPAND|wx.ALL,14)
        panel.SetSizer(outer); self._populate_positions(existing); self._update_summary()
    def _populate_positions(self,values=None):
        values=values or {}
        self.position_grid.Clear(delete_windows=True)
        self.roles=self.repository.roles(); self.counts={}
        for role in self.roles:
            label=wx.StaticText(self.scroll,label=role[1],size=(275,-1))
            self.position_grid.Add(label,0,wx.ALIGN_CENTER_VERTICAL)
            count=wx.SpinCtrl(self.scroll,min=0,max=20,initial=values.get(role[0],0),size=(72,-1))
            count.Bind(wx.EVT_SPINCTRL,self._update_summary)
            count.Bind(wx.EVT_TEXT,self._update_summary)
            self.position_grid.Add(count,0); self.counts[role[0]]=count
        self.scroll.FitInside(); self.scroll.Layout(); self._update_summary()
    def _manage_positions(self,_event):
        current=self.values()
        dialog=RoleManagerDialog(self,self.repository)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()
        self._populate_positions(current)
    def _update_summary(self,_event=None):
        if not hasattr(self,"summary"):
            return
        positions=sum(1 for control in self.counts.values() if control.GetValue()>0)
        people=sum(control.GetValue() for control in self.counts.values())
        if people:
            self.summary.SetLabel(f"This template normally requires {people} people in {positions} positions.")
        else:
            self.summary.SetLabel("No required positions have been set for this template.")
    def values(self): return {role_id:control.GetValue() for role_id,control in self.counts.items()}


class AssignmentEditDialog(wx.Dialog):
    STATUSES=("ASSIGNED","SUGGESTED","CONFIRMED","DECLINED")
    def __init__(self,parent,repository,row=None,required_role_id=None):
        super().__init__(parent,title="Service Participant Assignment"); self.repository=repository; self.roles=repository.roles(); self.participants=repository.participants(); panel=wx.Panel(self); s=wx.FlexGridSizer(cols=2,vgap=8,hgap=10); s.AddGrowableCol(1,1)
        self.role=wx.Choice(panel,choices=[r[1] for r in self.roles]); self.participant=wx.Choice(panel,choices=[p[2] for p in self.participants]); self.status=wx.Choice(panel,choices=list(self.STATUSES)); self.note=wx.TextCtrl(panel)
        for label,control in (("Role",self.role),("Participant",self.participant),("Status",self.status),("Note",self.note)): s.Add(wx.StaticText(panel,label=label+":"),0,wx.ALIGN_CENTER_VERTICAL); s.Add(control,1,wx.EXPAND)
        outer=wx.BoxSizer(wx.VERTICAL); outer.Add(s,1,wx.EXPAND|wx.ALL,10); outer.Add(dialog_button_sizer(self,panel),0,wx.EXPAND|wx.ALL,10); panel.SetSizer(outer); dialog_size=(520,260); self.SetSize(dialog_size)
        self.role.SetSelection(0 if self.roles else wx.NOT_FOUND); self.participant.SetSelection(0 if self.participants else wx.NOT_FOUND); self.status.SetSelection(0)
        if row:
            self.role.SetSelection(next((i for i,r in enumerate(self.roles) if r[0]==row[1]),0)); self.participant.SetSelection(next((i for i,p in enumerate(self.participants) if p[0]==row[3]),0)); self.status.SetSelection(next((i for i,v in enumerate(self.STATUSES) if v==row[5]),0)); self.note.SetValue(row[6] or "")
        elif required_role_id is not None:
            self.role.SetSelection(next((i for i,r in enumerate(self.roles) if r[0]==required_role_id),0))
            self.role.Enable(False)
    def values(self):
        if self.role.GetSelection()<0 or self.participant.GetSelection()<0: raise ValueError("Select both a role and a participant.")
        return (self.roles[self.role.GetSelection()][0],self.participants[self.participant.GetSelection()][0],self.status.GetStringSelection(),self.note.GetValue().strip())


class ServiceParticipantsDialog(wx.Dialog):
    def __init__(self,parent,connection,service_id):
        super().__init__(parent,title="Service Participants",size=(900,600),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.repository=WorshipSchedulingRepository(connection); self.service_id=service_id; self.rows=[]; context=self.repository.service_context(service_id)
        panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL); heading=wx.StaticText(panel,label=(str(context[5]) + " - " + str(context[2])) if context else "Worship Service"); heading.SetFont(heading.GetFont().Bold()); outer.Add(heading,0,wx.ALL,10)
        self.grid=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for label,width in (("Required position",200),("Participant",240),("Status",110),("Note",280)): self.grid.AppendColumn(label,width=width)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.on_edit); outer.Add(self.grid,1,wx.EXPAND|wx.LEFT|wx.RIGHT,10)
        actions=wx.BoxSizer(wx.HORIZONTAL)
        for label,handler in (("Add...",self.on_add),("Edit...",self.on_edit),("Remove",self.on_remove),("Preview Suggestions...",self.on_suggest)):
            b=wx.Button(panel,label=label); b.Bind(wx.EVT_BUTTON,handler); actions.Add(b,0,wx.RIGHT,7)
        actions.AddStretchSpacer(); actions.Add(wx.Button(panel,wx.ID_CANCEL,"Close")); outer.Add(actions,0,wx.EXPAND|wx.ALL,10); panel.SetSizer(outer); self.refresh()
    def refresh(self):
        assignments=self.repository.assignments(self.service_id); requirements=self.repository.requirements(self.service_id)
        self.rows=required_position_rows(requirements,assignments); self.grid.DeleteAllItems()
        for i,row in enumerate(self.rows):
            role_id,role,slot,total,assignment,required=row
            position=f"{role} {slot}" if required and total>1 else role
            item=self.grid.InsertItem(i,position)
            if assignment:
                for col,value in enumerate((assignment[4],assignment[5].title(),assignment[6]),1): self.grid.SetItem(item,col,str(value or ""))
                if assignment[5]=="DECLINED": self.grid.SetItemTextColour(item,wx.RED)
                elif assignment[5]=="SUGGESTED": self.grid.SetItemTextColour(item,wx.Colour(190,90,0))
            else:
                self.grid.SetItem(item,1,"Double-click to assign")
                self.grid.SetItem(item,2,"Open")
                self.grid.SetItemTextColour(item,wx.RED)
    def selected(self):
        index=self.grid.GetFirstSelected(); return self.rows[index] if index>=0 else None
    def _edit(self,row,required_role_id=None):
        dialog=AssignmentEditDialog(self,self.repository,row,required_role_id)
        try:
            if dialog.ShowModal()==wx.ID_OK:
                role,participant,status,note=dialog.values(); self.repository.save_assignment(row[0] if row else None,self.service_id,role,participant,status,note); self.refresh()
        except Exception as error: wx.MessageBox(str(error),"Unable to Save Assignment",wx.OK|wx.ICON_ERROR,self)
        finally: dialog.Destroy()
    def on_add(self,_event): self._edit(None)
    def on_edit(self,_event):
        row=self.selected()
        if row: self._edit(row[4],row[0] if row[4] is None else None)
    def on_remove(self,_event):
        row=self.selected()
        assignment=row[4] if row else None
        if assignment and wx.MessageBox(f"Remove {assignment[4]} as {assignment[2]}?","Remove Assignment",wx.YES_NO|wx.NO_DEFAULT|wx.ICON_WARNING,self)==wx.YES:
            self.repository.delete_assignment(assignment[0],self.service_id); self.refresh()
    def on_requirements(self,_event):
        dialog=RequirementDialog(self,self.repository,self.service_id)
        try:
            if dialog.ShowModal()==wx.ID_OK: self.repository.save_requirements(self.service_id,dialog.values()); self.refresh()
        except Exception as error: wx.MessageBox(str(error),"Unable to Save Requirements",wx.OK|wx.ICON_ERROR,self)
        finally: dialog.Destroy()
    def on_suggest(self,_event):
        try: suggestions=SchedulingSuggestionService(self.repository).suggest(self.service_id)
        except Exception as error: wx.MessageBox(str(error),"Unable to Suggest Participants",wx.OK|wx.ICON_INFORMATION,self); return
        if not suggestions: wx.MessageBox("All configured roles are filled, or no eligible available participant was found.","Participant Suggestions",wx.OK|wx.ICON_INFORMATION,self); return
        lines="\n".join(f"{s.role}: {s.participant}" for s in suggestions)
        if wx.MessageBox("ChurchManager suggests:\n\n"+lines+"\n\nAdd these as suggested assignments?","Preview Participant Suggestions",wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION,self)==wx.YES:
            SchedulingSuggestionService(self.repository).apply(self.service_id,suggestions); self.refresh()


class ServicePickerDialog(wx.Dialog):
    def __init__(self,parent,repository):
        super().__init__(parent,title="Select Worship Service",size=(650,180)); self.rows=repository.services(); panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL); outer.Add(wx.StaticText(panel,label="Worship Service:"),0,wx.LEFT|wx.RIGHT|wx.TOP,10); self.choice=wx.Choice(panel,choices=[r[1] for r in self.rows]);
        if self.rows: self.choice.SetSelection(0)
        outer.Add(self.choice,0,wx.EXPAND|wx.ALL,10); outer.Add(dialog_button_sizer(self,panel),0,wx.EXPAND|wx.ALL,10); panel.SetSizer(outer)
    def service_id(self): return self.rows[self.choice.GetSelection()][0] if self.choice.GetSelection()>=0 else None


def show_participants(parent,connection):
    dialog=ParticipantManagerDialog(parent,connection)
    try: return dialog.ShowModal()
    finally: dialog.Destroy()


def show_schedule_patterns(parent,connection):
    dialog=SchedulePatternManagerDialog(parent,connection)
    try: return dialog.ShowModal()
    finally: dialog.Destroy()


def show_service_participants(parent,connection,service_id=None):
    repository=WorshipSchedulingRepository(connection)
    if service_id is None:
        picker=ServicePickerDialog(parent,repository)
        try:
            if picker.ShowModal()!=wx.ID_OK: return None
            service_id=picker.service_id()
        finally: picker.Destroy()
    if service_id is None:
        wx.MessageBox("No Worship Service is available.","Service Participants",wx.OK|wx.ICON_INFORMATION,parent); return None
    dialog=ServiceParticipantsDialog(parent,connection,service_id)
    try: return dialog.ShowModal()
    finally: dialog.Destroy()
