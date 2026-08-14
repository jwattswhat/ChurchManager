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


def show_preparation_checklist(parent, connection, service_id):
    dialog=PreparationChecklistDialog(parent,connection,service_id)
    try: dialog.ShowModal()
    finally: dialog.Destroy()
