"""Flexible preparation reminders for a Worship Service."""
from __future__ import annotations

from datetime import datetime
import wx

from bulletin_orders import portable_connection

VALID_STATUSES = {"NOT_DONE", "DONE", "NOT_NEEDED"}


def checklist_counts(rows):
    counts = {"DONE": 0, "NOT_DONE": 0, "NOT_NEEDED": 0}
    for row in rows:
        status = str(row[6] or "NOT_DONE")
        counts[status] = counts.get(status, 0) + 1
    return counts


def overall_checklist_status(rows, manually_confirmed=False):
    """Return the plain-language state shown at the top of the checklist."""
    if manually_confirmed:
        return "Manually confirmed complete"
    unfinished_required = any(bool(row[4]) and row[6] == "NOT_DONE" for row in rows)
    return "Needs attention" if unfinished_required else "Ready"


class WorshipChecklistRepository:
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

    def service(self, service_id):
        return self.one(
            "SELECT s.ID,s.ChurchID,s.DateTime,COALESCE(s.LiturgicalDate,''),"
            "COALESCE(s.CheckListComplete,0),s.WorshipChecklistTemplateID "
            "FROM tblService s WHERE s.ID=?", (service_id,),
        )

    def templates(self, church_id):
        return self.all(
            "SELECT ID,Name,IsStarter FROM tblWorshipChecklistTemplate "
            "WHERE Active=1 AND (ChurchID IS NULL OR ChurchID=?) "
            "ORDER BY IsStarter DESC,Name", (church_id,),
        )

    def maintenance_templates(self, church_id):
        return self.all(
            "SELECT ID,Name,IsStarter,ChurchID,COALESCE(Note,'') "
            "FROM tblWorshipChecklistTemplate WHERE Active=1 "
            "AND (ChurchID IS NULL OR ChurchID=?) ORDER BY IsStarter DESC,Name", (church_id,),
        )

    def template_items(self, template_id):
        return self.all(
            "SELECT ID,Sequence,Task,CompletionSource,Required FROM "
            "tblWorshipChecklistTemplateItem WHERE TemplateID=? AND Active=1 "
            "ORDER BY Sequence,ID", (template_id,),
        )

    def create_custom_template(self, church_id, source_id, name):
        name = str(name or "").strip()
        if not name:
            raise ValueError("Enter a name for the custom checklist.")
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO tblWorshipChecklistTemplate (ChurchID,Name,IsStarter,Active) "
                "VALUES (?,?,0,1)", (church_id, name),
            )
            template_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO tblWorshipChecklistTemplateItem "
                "(TemplateID,Sequence,Task,CompletionSource,Required,Active) "
                "SELECT ?,Sequence,Task,CompletionSource,Required,Active FROM "
                "tblWorshipChecklistTemplateItem WHERE TemplateID=? ORDER BY Sequence,ID",
                (template_id, source_id),
            )
            self.connection.commit(); return template_id
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def delete_custom_template(self, template_id, church_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT IsStarter,ChurchID FROM tblWorshipChecklistTemplate WHERE ID=?",
                (template_id,),
            )
            row = cursor.fetchone()
            if not row or row[0] or row[1] != church_id:
                raise ValueError("Starter checklists cannot be deleted.")
            cursor.execute(
                "SELECT COUNT(*) FROM tblService WHERE WorshipChecklistTemplateID=?",
                (template_id,),
            )
            if cursor.fetchone()[0]:
                raise ValueError("This checklist is already used by a Worship Service and cannot be deleted.")
            cursor.execute("DELETE FROM tblWorshipChecklistTemplate WHERE ID=?", (template_id,))
            self.connection.commit()
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def save_template_item(self, template_id, item_id, task, source, required):
        task = str(task or "").strip()
        if not task:
            raise ValueError("Enter a preparation task.")
        if source not in {"MANUAL", "HYMNS", "ORDER", "PARTICIPANTS"}:
            raise ValueError("Select a valid completion method.")
        cursor = self.connection.cursor()
        try:
            if item_id is None:
                cursor.execute(
                    "SELECT COALESCE(MAX(Sequence),0)+1 FROM tblWorshipChecklistTemplateItem "
                    "WHERE TemplateID=?", (template_id,),
                )
                cursor.execute(
                    "INSERT INTO tblWorshipChecklistTemplateItem "
                    "(TemplateID,Sequence,Task,CompletionSource,Required,Active) "
                    "VALUES (?,?,?,?,?,1)",
                    (template_id, cursor.fetchone()[0], task, source, int(bool(required))),
                )
            else:
                cursor.execute(
                    "UPDATE tblWorshipChecklistTemplateItem SET Task=?,CompletionSource=?,"
                    "Required=? WHERE ID=? AND TemplateID=?",
                    (task, source, int(bool(required)), item_id, template_id),
                )
            self.connection.commit()
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def delete_template_item(self, template_id, item_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "DELETE FROM tblWorshipChecklistTemplateItem WHERE ID=? AND TemplateID=?",
                (item_id, template_id),
            )
            self._renumber(cursor, template_id); self.connection.commit()
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    @staticmethod
    def _renumber(cursor, template_id):
        cursor.execute(
            "SELECT ID FROM tblWorshipChecklistTemplateItem WHERE TemplateID=? "
            "ORDER BY Sequence,ID", (template_id,),
        )
        for sequence, row in enumerate(cursor.fetchall(), 1):
            cursor.execute(
                "UPDATE tblWorshipChecklistTemplateItem SET Sequence=? WHERE ID=?",
                (-sequence, row[0]),
            )
        cursor.execute(
            "UPDATE tblWorshipChecklistTemplateItem SET Sequence=-Sequence "
            "WHERE TemplateID=?", (template_id,),
        )

    def move_template_item(self, template_id, item_id, direction):
        rows = self.template_items(template_id)
        index = next((i for i, row in enumerate(rows) if row[0] == item_id), None)
        target = None if index is None else index + direction
        if index is None or target < 0 or target >= len(rows):
            return
        reordered = list(rows); reordered[index], reordered[target] = reordered[target], reordered[index]
        cursor = self.connection.cursor()
        try:
            for sequence, row in enumerate(reordered, 1):
                cursor.execute("UPDATE tblWorshipChecklistTemplateItem SET Sequence=? WHERE ID=?", (-sequence, row[0]))
            cursor.execute("UPDATE tblWorshipChecklistTemplateItem SET Sequence=-Sequence WHERE TemplateID=?", (template_id,))
            self.connection.commit()
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def ensure_items(self, service_id):
        service = self.service(service_id)
        if not service:
            raise ValueError("The Worship Service is unavailable.")
        if self.items(service_id):
            return
        template_id = service[5]
        if not template_id:
            templates = self.templates(service[1])
            template_id = templates[0][0] if templates else None
        if template_id:
            self.apply_template(service_id, template_id)

    def apply_template(self, service_id, template_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM tblServiceChecklistItem WHERE ServiceID=?", (service_id,))
            cursor.execute(
                "INSERT INTO tblServiceChecklistItem "
                "(ServiceID,TemplateItemID,Sequence,Task,CompletionSource,Required,Status) "
                "SELECT ?,ID,Sequence,Task,CompletionSource,Required,'NOT_DONE' "
                "FROM tblWorshipChecklistTemplateItem WHERE TemplateID=? AND Active=1 "
                "ORDER BY Sequence", (service_id, template_id),
            )
            cursor.execute(
                "UPDATE tblService SET WorshipChecklistTemplateID=?,CheckListComplete=0 WHERE ID=?",
                (template_id, service_id),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def items(self, service_id):
        return self.all(
            "SELECT ID,Sequence,Task,CompletionSource,Required,COALESCE(Note,''),Status "
            "FROM tblServiceChecklistItem WHERE ServiceID=? ORDER BY Sequence,ID", (service_id,),
        )

    def automatic_summary(self, service_id):
        hymn = self.one(
            "SELECT COUNT(*),SUM(CASE WHEN Included=1 AND ValueSource='SERVICE_HYMN' "
            "AND COALESCE(WeeklyValue,'')='' THEN 1 ELSE 0 END) "
            "FROM tblServiceBulletinOrderLine WHERE ServiceID=? AND Included=1 "
            "AND ValueSource='SERVICE_HYMN'", (service_id,),
        ) or (0, 0)
        order = self.one(
            "SELECT COUNT(*),SUM(CASE WHEN Included=1 AND COALESCE(ValueSource,'')<>'' "
            "AND COALESCE(WeeklyValue,'')='' THEN 1 ELSE 0 END) "
            "FROM tblServiceBulletinOrderLine WHERE ServiceID=?", (service_id,),
        ) or (0, 0)
        required = self.one(
            "SELECT COALESCE(SUM(RequiredCount),0) FROM tblWorshipRoleRequirement r "
            "JOIN tblService s ON s.BulletinOrderTemplateID=r.BulletinOrderTemplateID "
            "WHERE s.ID=? AND r.Active=1", (service_id,),
        ) or (0,)
        filled = self.one(
            "SELECT COALESCE(SUM(LEAST(r.RequiredCount,COALESCE(a.AssignedCount,0))),0) "
            "FROM tblService s JOIN tblWorshipRoleRequirement r "
            "ON r.BulletinOrderTemplateID=s.BulletinOrderTemplateID AND r.Active=1 "
            "LEFT JOIN (SELECT WorshipRoleID,COUNT(*) AssignedCount FROM tblServiceRole "
            "WHERE ServiceID=? AND AssignmentStatus<>'DECLINED' GROUP BY WorshipRoleID) a "
            "ON a.WorshipRoleID=r.WorshipRoleID WHERE s.ID=?", (service_id, service_id),
        ) or (0,)
        return {
            "HYMNS": "Complete" if hymn[0] and not (hymn[1] or 0) else "Not complete",
            "ORDER": "Complete" if order[0] and not (order[1] or 0) else "Not complete",
            "PARTICIPANTS": f"{min(filled[0], required[0])} of {required[0]} required positions filled",
        }

    def set_status(self, item_id, status):
        if status not in VALID_STATUSES:
            raise ValueError("Invalid checklist status.")
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE tblServiceChecklistItem SET Status=?,CompletedAt=? WHERE ID=?",
                (status, datetime.now() if status == "DONE" else None, item_id),
            )
            self.connection.commit()
        finally:
            cursor.close()

    def add_service_task(self, service_id, task, required=True):
        task = str(task or "").strip()
        if not task:
            raise ValueError("Enter a description for the preparation task.")
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT COALESCE(MAX(Sequence),0)+1 FROM tblServiceChecklistItem "
                "WHERE ServiceID=?", (service_id,),
            )
            sequence = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO tblServiceChecklistItem "
                "(ServiceID,TemplateItemID,Sequence,Task,CompletionSource,Required,Status) "
                "VALUES (?,NULL,?,?,'MANUAL',?,'NOT_DONE')",
                (service_id, sequence, task, int(bool(required))),
            )
            self.connection.commit()
            return cursor.lastrowid
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def set_override(self, service_id, complete):
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE tblService SET CheckListComplete=? WHERE ID=?", (int(complete), service_id))
            self.connection.commit()
        finally:
            cursor.close()


class PreparationChecklistDialog(wx.Dialog):
    def __init__(self, parent, connection, service_id):
        super().__init__(parent, title="Worship Preparation Checklist", size=(820, 620),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.repository = WorshipChecklistRepository(connection); self.service_id = service_id
        self.repository.ensure_items(service_id)
        panel = wx.Panel(self); outer = wx.BoxSizer(wx.VERTICAL)
        self.heading = wx.StaticText(panel); self.heading.SetFont(self.heading.GetFont().Bold())
        outer.Add(self.heading, 0, wx.ALL, 10)
        self.overall_status = wx.StaticText(panel)
        status_font = self.overall_status.GetFont()
        status_font.SetPointSize(status_font.GetPointSize() + 2)
        status_font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.overall_status.SetFont(status_font)
        outer.Add(self.overall_status, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.summary = wx.StaticText(panel); self.summary.SetForegroundColour(wx.Colour(0, 90, 190))
        outer.Add(self.summary, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.automatic = wx.StaticText(panel)
        outer.Add(self.automatic, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.grid = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for label, width in (("Status",110),("Preparation item",390),("How completed",150),("Note",120)):
            self.grid.AppendColumn(label,width=width)
        self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.toggle_selected)
        outer.Add(self.grid,1,wx.EXPAND|wx.LEFT|wx.RIGHT,10)
        buttons=wx.BoxSizer(wx.HORIZONTAL)
        for label,status in (("Done","DONE"),("Not Done","NOT_DONE"),("Not Needed","NOT_NEEDED")):
            button=wx.Button(panel,label=label); button.Bind(wx.EVT_BUTTON,lambda _e,s=status:self.change(s)); buttons.Add(button,0,wx.RIGHT,6)
        add_task = wx.Button(panel, label="Add This-Time Task...")
        add_task.Bind(wx.EVT_BUTTON, self.add_task)
        buttons.Add(add_task, 0, wx.LEFT, 8)
        self.override=wx.Button(panel); self.override.Bind(wx.EVT_BUTTON,self.toggle_override)
        buttons.AddStretchSpacer(); buttons.Add(self.override,0,wx.RIGHT,8)
        close = wx.Button(panel, wx.ID_CLOSE, "Close")
        close.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_CLOSE))
        buttons.Add(close)
        outer.Add(buttons,0,wx.EXPAND|wx.ALL,10); panel.SetSizer(outer); self.refresh()

    def refresh(self):
        service=self.repository.service(self.service_id); self.rows=self.repository.items(self.service_id)
        auto=self.repository.automatic_summary(self.service_id)
        effective=[]
        for row in self.rows:
            if row[3] in ("HYMNS", "ORDER"):
                row=tuple(list(row[:6])+["DONE" if auto[row[3]] == "Complete" else "NOT_DONE"])
            elif row[3] == "PARTICIPANTS":
                required=int(auto["PARTICIPANTS"].split(" of ",1)[1].split(" ",1)[0])
                filled=int(auto["PARTICIPANTS"].split(" of ",1)[0])
                row=tuple(list(row[:6])+["DONE" if required == filled else "NOT_DONE"])
            effective.append(row)
        self.rows=effective
        self.heading.SetLabel(f"{service[3] or 'Worship Service'} — {service[2]}")
        counts=checklist_counts(self.rows)
        status = overall_checklist_status(self.rows, bool(service[4]))
        self.overall_status.SetLabel("Overall status: " + status)
        self.overall_status.SetForegroundColour(
            wx.Colour(0, 120, 0) if status != "Needs attention" else wx.Colour(190, 45, 35)
        )
        prefix="Checklist complete — manually confirmed.  " if service[4] else ""
        self.summary.SetLabel(prefix + f"{counts['DONE']} done · {counts['NOT_DONE']} not done · {counts['NOT_NEEDED']} not needed")
        self.automatic.SetLabel(f"Participants: {auto['PARTICIPANTS']}     Hymns: {auto['HYMNS']}     Order: {auto['ORDER']}")
        self.override.SetLabel("Reopen Checklist" if service[4] else "Mark Whole Checklist Complete")
        self.grid.DeleteAllItems()
        display={"DONE":"Done","NOT_DONE":"Not done","NOT_NEEDED":"Not needed"}
        for n,row in enumerate(self.rows):
            item=self.grid.InsertItem(n,display.get(row[6],row[6])); self.grid.SetItem(item,1,str(row[2])); self.grid.SetItem(item,2,"Automatic" if row[3] != "MANUAL" else "Manual"); self.grid.SetItem(item,3,str(row[5]))
            if row[6] == "NOT_DONE": self.grid.SetItemTextColour(item,wx.RED)

    def change(self,status):
        selected=self.grid.GetFirstSelected()
        if selected < 0: return
        row=self.rows[selected]
        if row[3] != "MANUAL":
            wx.MessageBox("This item is calculated from the Worship Service.","Automatic Item",wx.OK|wx.ICON_INFORMATION,self); return
        self.repository.set_status(row[0],status); self.refresh(); self.grid.Select(selected)

    def toggle_selected(self, _event):
        selected = self.grid.GetFirstSelected()
        if selected < 0:
            return
        current = self.rows[selected][6]
        self.change("NOT_DONE" if current == "DONE" else "DONE")

    def toggle_override(self,_event):
        service=self.repository.service(self.service_id)
        self.repository.set_override(self.service_id,not bool(service[4])); self.refresh()

    def add_task(self, _event):
        dialog = wx.TextEntryDialog(
            self,
            "Enter a preparation task needed only for this Worship Service.",
            "Add This-Time Task",
        )
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return
            task = dialog.GetValue().strip()
            if not task:
                wx.MessageBox("Enter a task description.", "Preparation Checklist",
                              wx.OK | wx.ICON_INFORMATION, self)
                return
            self.repository.add_service_task(self.service_id, task)
            self.refresh()
            index = self.grid.GetItemCount() - 1
            if index >= 0:
                self.grid.Select(index); self.grid.EnsureVisible(index)
        except Exception as error:
            wx.MessageBox(str(error), "Unable to Add Task", wx.OK | wx.ICON_ERROR, self)
        finally:
            dialog.Destroy()


class ChecklistTaskDialog(wx.Dialog):
    SOURCES = (("Manual", "MANUAL"), ("Selected hymns", "HYMNS"),
               ("Weekly Order of Service", "ORDER"), ("Required participants", "PARTICIPANTS"))

    def __init__(self, parent, task="", source="MANUAL", required=True):
        super().__init__(parent, title="Checklist Task", size=(480, 245))
        panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        form=wx.FlexGridSizer(cols=2,vgap=10,hgap=10); form.AddGrowableCol(1,1)
        form.Add(wx.StaticText(panel,label="Task:"),0,wx.ALIGN_CENTER_VERTICAL)
        self.task=wx.TextCtrl(panel,value=task); form.Add(self.task,1,wx.EXPAND)
        form.Add(wx.StaticText(panel,label="Completion:"),0,wx.ALIGN_CENTER_VERTICAL)
        self.source=wx.Choice(panel,choices=[row[0] for row in self.SOURCES])
        self.source.SetSelection(next((i for i,row in enumerate(self.SOURCES) if row[1]==source),0)); form.Add(self.source,1,wx.EXPAND)
        form.Add(wx.StaticText(panel,label="Required:"),0,wx.ALIGN_CENTER_VERTICAL)
        self.required=wx.CheckBox(panel,label="Include in overall Ready status"); self.required.SetValue(bool(required)); form.Add(self.required)
        outer.Add(form,1,wx.EXPAND|wx.ALL,15); outer.Add(self.CreateSeparatedButtonSizer(wx.OK|wx.CANCEL),0,wx.EXPAND|wx.ALL,10)
        panel.SetSizer(outer)

    def values(self):
        return self.task.GetValue().strip(),self.SOURCES[self.source.GetSelection()][1],self.required.GetValue()


class ChecklistMaintenanceDialog(wx.Dialog):
    def __init__(self, parent, connection):
        super().__init__(parent,title="Worship Checklist Maintenance",size=(1000,650),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.repository=WorshipChecklistRepository(connection)
        church=self.repository.one("SELECT ID,Church FROM tblChurch ORDER BY ID LIMIT 1")
        if not church: raise ValueError("No church record is available.")
        self.church_id=church[0]; self.template_rows=[]; self.item_rows=[]
        panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        banner=wx.StaticText(panel,label="Create a custom checklist from a starter, then arrange its preparation tasks. Starter checklists are protected.")
        banner.SetForegroundColour(wx.Colour(0,90,190)); outer.Add(banner,0,wx.ALL,10)
        body=wx.BoxSizer(wx.HORIZONTAL)
        self.templates=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        self.templates.AppendColumn("Checklist",width=270); self.templates.AppendColumn("Status",width=90)
        self.templates.Bind(wx.EVT_LIST_ITEM_SELECTED,lambda _e:self.load_items())
        body.Add(self.templates,0,wx.EXPAND|wx.RIGHT,10)
        self.items=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for label,width in (("Order",60),("Preparation task",330),("Completion",155),("Required",75)): self.items.AppendColumn(label,width=width)
        self.items.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.edit_item); body.Add(self.items,1,wx.EXPAND)
        outer.Add(body,1,wx.EXPAND|wx.LEFT|wx.RIGHT,10)
        actions=wx.BoxSizer(wx.HORIZONTAL)
        for label,handler in (("Create Custom from Selected...",self.create_custom),("Delete Custom",self.delete_custom),("Add Task...",self.add_item),("Edit Task...",self.edit_item),("Delete Task",self.delete_item),("Move Up",lambda e:self.move_item(-1)),("Move Down",lambda e:self.move_item(1))):
            button=wx.Button(panel,label=label); button.Bind(wx.EVT_BUTTON,handler); actions.Add(button,0,wx.RIGHT,6)
        actions.AddStretchSpacer(); close=wx.Button(panel,wx.ID_CLOSE,"Close"); close.Bind(wx.EVT_BUTTON,lambda _e:self.EndModal(wx.ID_CLOSE)); actions.Add(close)
        outer.Add(actions,0,wx.EXPAND|wx.ALL,10); panel.SetSizer(outer); self.load_templates()

    def selected_template(self):
        index=self.templates.GetFirstSelected(); return None if index<0 else self.template_rows[index]

    def selected_item(self):
        index=self.items.GetFirstSelected(); return None if index<0 else self.item_rows[index]

    def editable_template(self):
        row=self.selected_template()
        if not row: return None
        if row[2] or row[3] != self.church_id:
            wx.MessageBox("Create a custom copy before changing a starter checklist.","Protected Checklist",wx.OK|wx.ICON_INFORMATION,self); return None
        return row

    def load_templates(self, select_id=None):
        self.template_rows=self.repository.maintenance_templates(self.church_id); self.templates.DeleteAllItems()
        selection=0
        for i,row in enumerate(self.template_rows):
            item=self.templates.InsertItem(i,str(row[1])); self.templates.SetItem(item,1,"Starter" if row[2] else "Customized")
            if not row[2]: self.templates.SetItemTextColour(item,wx.Colour(0,90,190))
            if row[0]==select_id: selection=i
        if self.template_rows: self.templates.Select(selection); self.load_items()

    def load_items(self, select_id=None):
        row=self.selected_template(); self.item_rows=self.repository.template_items(row[0]) if row else []; self.items.DeleteAllItems()
        labels={"MANUAL":"Manual","HYMNS":"Selected hymns","ORDER":"Weekly order","PARTICIPANTS":"Participants"}
        selection=0
        for i,itemrow in enumerate(self.item_rows):
            line=self.items.InsertItem(i,str(itemrow[1])); self.items.SetItem(line,1,str(itemrow[2])); self.items.SetItem(line,2,labels.get(itemrow[3],itemrow[3])); self.items.SetItem(line,3,"Yes" if itemrow[4] else "No")
            if itemrow[0]==select_id: selection=i
        if self.item_rows: self.items.Select(selection)

    def create_custom(self,_event):
        row=self.selected_template()
        if not row: return
        dialog=wx.TextEntryDialog(self,"Name the editable custom checklist.","Create Custom Checklist",value=str(row[1])+" - Custom")
        try:
            if dialog.ShowModal()==wx.ID_OK:
                new_id=self.repository.create_custom_template(self.church_id,row[0],dialog.GetValue()); self.load_templates(new_id)
        except Exception as error: wx.MessageBox(str(error),"Unable to Create Checklist",wx.OK|wx.ICON_ERROR,self)
        finally: dialog.Destroy()

    def delete_custom(self,_event):
        row=self.editable_template()
        if not row: return
        if wx.MessageBox(f"Delete custom checklist '{row[1]}'?","Delete Checklist",wx.YES_NO|wx.NO_DEFAULT|wx.ICON_WARNING,self)!=wx.YES: return
        try: self.repository.delete_custom_template(row[0],self.church_id); self.load_templates()
        except Exception as error: wx.MessageBox(str(error),"Unable to Delete Checklist",wx.OK|wx.ICON_ERROR,self)

    def add_item(self,_event): self._edit(None)
    def edit_item(self,_event):
        item=self.selected_item()
        if item: self._edit(item)

    def _edit(self,item):
        template=self.editable_template()
        if not template: return
        dialog=ChecklistTaskDialog(self,*(item[2:5] if item else ()))
        try:
            if dialog.ShowModal()==wx.ID_OK:
                self.repository.save_template_item(template[0],item[0] if item else None,*dialog.values()); self.load_items(item[0] if item else None)
        except Exception as error: wx.MessageBox(str(error),"Unable to Save Task",wx.OK|wx.ICON_ERROR,self)
        finally: dialog.Destroy()

    def delete_item(self,_event):
        template=self.editable_template(); item=self.selected_item()
        if not template or not item: return
        if wx.MessageBox(f"Delete '{item[2]}'?","Delete Task",wx.YES_NO|wx.NO_DEFAULT|wx.ICON_WARNING,self)==wx.YES:
            self.repository.delete_template_item(template[0],item[0]); self.load_items()

    def move_item(self,direction):
        template=self.editable_template(); item=self.selected_item()
        if not template or not item: return
        self.repository.move_template_item(template[0],item[0],direction); self.load_items(item[0])


def show_preparation_checklist(parent, connection, service_id):
    dialog=PreparationChecklistDialog(parent,connection,service_id)
    try: dialog.ShowModal()
    finally: dialog.Destroy()


def show_checklist_maintenance(parent, connection):
    dialog=ChecklistMaintenanceDialog(parent,connection)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
