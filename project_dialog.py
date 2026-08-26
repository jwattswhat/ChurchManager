"""Native project planning workspaces for bounded congregational projects."""

from __future__ import annotations

from datetime import date, timedelta

import wx
import wx.adv

from project_repository import MariaDBProjectRepository
from project_service import ProjectService


def _choice(parent, rows, blank=True):
    control=wx.Choice(parent); control._ids=[]
    if blank: control.Append("Not assigned"); control._ids.append(None)
    for row in rows: control.Append(str(row.get("name") or "")); control._ids.append(row.get("id"))
    if control.GetCount(): control.SetSelection(0)
    return control


def _selected(control):
    index=control.GetSelection()
    return control._ids[index] if 0<=index<len(control._ids) else None


def _select(control, value):
    try: control.SetSelection(control._ids.index(value))
    except ValueError: control.SetSelection(0)


def _date_value(control):
    value=control.GetValue()
    if not value.IsValid(): return None
    return date(value.GetYear(),value.GetMonth()+1,value.GetDay())


def _set_date(control, value):
    if value: control.SetValue(wx.DateTime.FromDMY(value.day,value.month-1,value.year))
    else: control.SetValue(wx.DateTime())


def _optional_date(parent):
    control=wx.adv.DatePickerCtrl(parent,style=wx.adv.DP_DROPDOWN|wx.adv.DP_ALLOWNONE)
    control.SetValue(wx.DateTime()); return control


def _error(parent, title, error):
    wx.MessageBox(str(error),title,wx.OK|wx.ICON_ERROR,parent)


class StepDialog(wx.Dialog):
    """Collect one project step without exposing implementation sequence values."""

    def __init__(self,parent,service,project,record=None):
        super().__init__(parent,title="Project Step",size=(590,510),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.service=service; self.project=project; self.record=record
        panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL); grid=wx.FlexGridSizer(cols=2,vgap=9,hgap=12); grid.AddGrowableCol(1,1)
        self.title=wx.TextCtrl(panel); self.assignee_type=wx.Choice(panel,choices=["Not assigned","Person","Group","User"]); self.assignee_type.SetSelection(0)
        self.assignee=_choice(panel,[]); self.status=wx.Choice(panel,choices=list(ProjectService.STEP_STATUSES)); self.status.SetStringSelection("Not Started")
        self.due=_optional_date(panel); self.calendar=wx.CheckBox(panel,label="Include the due date in Calendar Integration"); self.note=wx.TextCtrl(panel,style=wx.TE_MULTILINE)
        for label,control in (("Step",self.title),("Assign to",self.assignee_type),("Assignee",self.assignee),("Status",self.status),("Due date",self.due),("",self.calendar),("Note / blocked reason",self.note)):
            grid.Add(wx.StaticText(panel,label=label),0,wx.ALIGN_CENTER_VERTICAL); grid.Add(control,1,wx.EXPAND)
        outer.Add(grid,1,wx.EXPAND|wx.ALL,14); buttons=wx.BoxSizer(wx.HORIZONTAL); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel,wx.ID_OK,"Save Step"),0,wx.RIGHT,8); buttons.Add(wx.Button(panel,wx.ID_CANCEL,"Cancel")); outer.Add(buttons,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,14); panel.SetSizer(outer)
        self.assignee_type.Bind(wx.EVT_CHOICE,self.on_owner_type); self._fill()

    def on_owner_type(self,_event=None):
        owner_type=self.assignee_type.GetStringSelection()
        rows=[] if owner_type=="Not assigned" else self.service.owners(self.project["church_id"],owner_type)
        current=_selected(self.assignee) if hasattr(self.assignee,"_ids") else None
        self.assignee.Clear(); self.assignee._ids=[]; self.assignee.Append("Not assigned"); self.assignee._ids.append(None)
        for row in rows: self.assignee.Append(row["name"]); self.assignee._ids.append(row["id"])
        _select(self.assignee,current)

    def _fill(self):
        record=self.record
        if not record:return
        self.title.SetValue(record["title"]); self.assignee_type.SetStringSelection(record.get("assignee_type") or "Not assigned"); self.on_owner_type(); _select(self.assignee,record.get("assignee_id")); self.status.SetStringSelection(record["status"]); _set_date(self.due,record.get("due_date")); self.calendar.SetValue(bool(record.get("calendar_eligible"))); self.note.SetValue(record.get("note") or "")

    def values(self):
        kind=self.assignee_type.GetStringSelection()
        return {"title":self.title.GetValue(),"assignee_type":None if kind=="Not assigned" else kind,"assignee_id":_selected(self.assignee),"status":self.status.GetStringSelection(),"due_date":_date_value(self.due),"calendar_eligible":self.calendar.GetValue(),"note":self.note.GetValue()}


class DependenciesDialog(wx.Dialog):
    """Maintain same-project predecessors for one selected step."""

    def __init__(self,parent,service,project_id,step):
        super().__init__(parent,title=f"Dependencies - {step['title']}",size=(620,430),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.service=service; self.project_id=project_id; self.step=step
        panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        outer.Add(wx.StaticText(panel,label="This step cannot begin until the selected predecessor steps are complete."),0,wx.ALL,12)
        self.list=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL); self.list.InsertColumn(0,"Required predecessor",width=390)
        outer.Add(self.list,1,wx.EXPAND|wx.LEFT|wx.RIGHT,12)
        buttons=wx.BoxSizer(wx.HORIZONTAL); add=wx.Button(panel,label="Add Dependency..."); remove=wx.Button(panel,label="Remove Dependency"); buttons.Add(add,0,wx.RIGHT,8); buttons.Add(remove); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel,wx.ID_CLOSE,"Close")); outer.Add(buttons,0,wx.EXPAND|wx.ALL,12); panel.SetSizer(outer)
        add.Bind(wx.EVT_BUTTON,self.on_add); remove.Bind(wx.EVT_BUTTON,self.on_remove); self.Bind(wx.EVT_BUTTON,lambda _event:self.EndModal(wx.ID_CLOSE),id=wx.ID_CLOSE); self.refresh()

    def refresh(self):
        self.rows=self.service.dependencies(self.step["id"]); self.list.DeleteAllItems()
        for row in self.rows:self.list.InsertItem(self.list.GetItemCount(),row["name"])

    def on_add(self,_event):
        linked={row["id"] for row in self.rows}; choices=[row for row in self.service.steps(self.project_id) if row["id"]!=self.step["id"] and row["id"] not in linked]
        if not choices:wx.MessageBox("There are no other available predecessor steps.","Dependencies",wx.OK|wx.ICON_INFORMATION,self); return
        dialog=wx.SingleChoiceDialog(self,"Select the step that must be completed first.","Add Dependency",[row["title"] for row in choices])
        try:
            if dialog.ShowModal()==wx.ID_OK:self.service.add_dependency(self.step["id"],choices[dialog.GetSelection()]["id"]); self.refresh()
        except Exception as error:_error(self,"Unable to Add Dependency",error)
        finally:dialog.Destroy()

    def on_remove(self,_event):
        selected=self.list.GetFirstSelected()
        if selected<0:return
        try:self.service.remove_dependency(self.step["id"],self.rows[selected]["id"]); self.refresh()
        except Exception as error:_error(self,"Unable to Remove Dependency",error)


class ProjectDocumentsDialog(wx.Dialog):
    """Link existing nonconfidential ChurchManager documents to a project."""

    def __init__(self,parent,service,project_id):
        super().__init__(parent,title="Project Documents",size=(680,450),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.service=service; self.project_id=project_id; panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        outer.Add(wx.StaticText(panel,label="Links point to existing ChurchManager documents; files are not duplicated."),0,wx.ALL,12)
        self.list=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL); self.list.InsertColumn(0,"Document",width=430); self.list.InsertColumn(1,"Date",width=100); outer.Add(self.list,1,wx.EXPAND|wx.LEFT|wx.RIGHT,12)
        buttons=wx.BoxSizer(wx.HORIZONTAL); add=wx.Button(panel,label="Link Document..."); remove=wx.Button(panel,label="Remove Link"); buttons.Add(add,0,wx.RIGHT,8); buttons.Add(remove); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel,wx.ID_CLOSE,"Close")); outer.Add(buttons,0,wx.EXPAND|wx.ALL,12); panel.SetSizer(outer)
        add.Bind(wx.EVT_BUTTON,self.on_add); remove.Bind(wx.EVT_BUTTON,self.on_remove); self.Bind(wx.EVT_BUTTON,lambda _event:self.EndModal(wx.ID_CLOSE),id=wx.ID_CLOSE); self.refresh()

    def refresh(self):
        data=self.service.documents(self.project_id); self.available=data["available"]; self.rows=data["linked"]; self.list.DeleteAllItems()
        for row in self.rows:
            index=self.list.InsertItem(self.list.GetItemCount(),row["name"]); self.list.SetItem(index,1,str(row.get("date") or ""))

    def on_add(self,_event):
        linked={row["id"] for row in self.rows}; choices=[row for row in self.available if row["id"] not in linked]
        if not choices:wx.MessageBox("There are no additional documents available for this church.","Project Documents",wx.OK|wx.ICON_INFORMATION,self); return
        dialog=wx.SingleChoiceDialog(self,"Select a document to link.","Link Document",[row["name"] for row in choices])
        try:
            if dialog.ShowModal()==wx.ID_OK:self.service.link_document(self.project_id,choices[dialog.GetSelection()]["id"]); self.refresh()
        except Exception as error:_error(self,"Unable to Link Document",error)
        finally:dialog.Destroy()

    def on_remove(self,_event):
        selected=self.list.GetFirstSelected()
        if selected<0:return
        try:self.service.unlink_document(self.project_id,self.rows[selected]["link_id"]); self.refresh()
        except Exception as error:_error(self,"Unable to Remove Document Link",error)


class ProjectEditorDialog(wx.Dialog):
    """Edit a project and its ordered, separately assignable steps."""

    def __init__(self,parent,service,church_id,project_id=None):
        super().__init__(parent,title="Project Plan",size=(970,740),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.service=service; self.church_id=church_id; self.project_id=project_id; self.record=service.project(project_id) if project_id else None
        panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL); top=wx.FlexGridSizer(cols=4,vgap=8,hgap=10); top.AddGrowableCol(1,1); top.AddGrowableCol(3,1)
        self.number=wx.TextCtrl(panel,style=wx.TE_READONLY); self.name=wx.TextCtrl(panel); self.status=wx.Choice(panel,choices=list(ProjectService.PROJECT_STATUSES)); self.status.SetStringSelection("Planned"); self.priority=wx.Choice(panel,choices=list(ProjectService.PRIORITIES)); self.priority.SetStringSelection("Normal")
        self.owner_type=wx.Choice(panel,choices=["Not assigned","Person","Group","User"]); self.owner_type.SetSelection(0); self.owner=_choice(panel,[]); self.start=_optional_date(panel); self.target=_optional_date(panel); self.calendar=wx.CheckBox(panel,label="Publish the target date through Calendar Integration"); self.purpose=wx.TextCtrl(panel,style=wx.TE_MULTILINE); self.note=wx.TextCtrl(panel,style=wx.TE_MULTILINE)
        for label,control in (("Number",self.number),("Project",self.name),("Status",self.status),("Priority",self.priority),("Owner type",self.owner_type),("Owner",self.owner),("Planned start",self.start),("Target date",self.target)):
            top.Add(wx.StaticText(panel,label=label),0,wx.ALIGN_CENTER_VERTICAL); top.Add(control,1,wx.EXPAND)
        outer.Add(top,0,wx.EXPAND|wx.ALL,12); outer.Add(self.calendar,0,wx.LEFT|wx.RIGHT|wx.BOTTOM,12)
        text_grid=wx.FlexGridSizer(cols=2,vgap=8,hgap=10); text_grid.AddGrowableCol(1,1); text_grid.AddGrowableRow(0,1); text_grid.AddGrowableRow(1,1)
        for label,control in (("Purpose",self.purpose),("Notes",self.note)): text_grid.Add(wx.StaticText(panel,label=label),0); text_grid.Add(control,1,wx.EXPAND)
        outer.Add(text_grid,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,12)
        step_label=wx.StaticText(panel,label="Project Steps"); font=step_label.GetFont(); font.MakeBold(); step_label.SetFont(font); outer.Add(step_label,0,wx.LEFT|wx.RIGHT,12)
        self.steps=wx.ListCtrl(panel,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for i,(label,width) in enumerate((("Step",300),("Assigned to",150),("Status",100),("Due",85),("Calendar",70))):self.steps.InsertColumn(i,label,width=width)
        outer.Add(self.steps,2,wx.EXPAND|wx.ALL,12)
        step_buttons=wx.BoxSizer(wx.HORIZONTAL); self.add_step=wx.Button(panel,label="Add Step..."); self.open_step=wx.Button(panel,label="Open Step"); self.move_up=wx.Button(panel,label="Move Up"); self.move_down=wx.Button(panel,label="Move Down"); self.dependencies=wx.Button(panel,label="Dependencies..."); self.documents=wx.Button(panel,label="Documents...")
        for control in (self.add_step,self.open_step,self.move_up,self.move_down,self.dependencies):step_buttons.Add(control,0,wx.RIGHT,8)
        step_buttons.AddStretchSpacer(); step_buttons.Add(self.documents); outer.Add(step_buttons,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,12)
        buttons=wx.BoxSizer(wx.HORIZONTAL); save=wx.Button(panel,label="Save Project"); buttons.Add(save); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel,wx.ID_CLOSE,"Close")); outer.Add(buttons,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,12); panel.SetSizer(outer)
        self.owner_type.Bind(wx.EVT_CHOICE,self.on_owner_type); self.steps.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.on_open_step); self.add_step.Bind(wx.EVT_BUTTON,self.on_add_step); self.open_step.Bind(wx.EVT_BUTTON,self.on_open_step); self.move_up.Bind(wx.EVT_BUTTON,lambda event:self.on_move(-1)); self.move_down.Bind(wx.EVT_BUTTON,lambda event:self.on_move(1)); self.dependencies.Bind(wx.EVT_BUTTON,self.on_dependencies); self.documents.Bind(wx.EVT_BUTTON,self.on_documents); save.Bind(wx.EVT_BUTTON,self.on_save); self.Bind(wx.EVT_BUTTON,lambda e:self.EndModal(wx.ID_CLOSE),id=wx.ID_CLOSE); self._fill(); self.refresh_steps()

    def on_owner_type(self,_event=None):
        kind=self.owner_type.GetStringSelection(); current=_selected(self.owner); rows=[] if kind=="Not assigned" else self.service.owners(self.church_id,kind)
        self.owner.Clear(); self.owner._ids=[]; self.owner.Append("Not assigned"); self.owner._ids.append(None)
        for row in rows:self.owner.Append(row["name"]); self.owner._ids.append(row["id"])
        _select(self.owner,current)

    def _fill(self):
        r=self.record
        if not r:self.number.SetValue("Assigned when saved"); return
        self.number.SetValue(r["project_number"]); self.name.SetValue(r["name"]); self.status.SetStringSelection(r["status"]); self.priority.SetStringSelection(r["priority"]); self.owner_type.SetStringSelection(r.get("owner_type") or "Not assigned"); self.on_owner_type(); _select(self.owner,r.get("owner_id")); _set_date(self.start,r.get("planned_start")); _set_date(self.target,r.get("target_date")); self.calendar.SetValue(bool(r.get("calendar_eligible"))); self.purpose.SetValue(r.get("purpose") or ""); self.note.SetValue(r.get("note") or "")

    def values(self):
        kind=self.owner_type.GetStringSelection()
        return {"church_id":self.church_id,"project_number":self.number.GetValue() if self.project_id else None,"name":self.name.GetValue(),"status":self.status.GetStringSelection(),"priority":self.priority.GetStringSelection(),"owner_type":None if kind=="Not assigned" else kind,"owner_id":_selected(self.owner),"planned_start":_date_value(self.start),"target_date":_date_value(self.target),"calendar_eligible":self.calendar.GetValue(),"purpose":self.purpose.GetValue(),"note":self.note.GetValue()}

    def refresh_steps(self):
        self.rows=self.service.steps(self.project_id) if self.project_id else []; self.steps.DeleteAllItems(); self.add_step.Enable(bool(self.project_id) and self.record["status"]=="Active"); self.documents.Enable(bool(self.project_id))
        for row in self.rows:
            assignee="" if not row.get("assignee_type") else f"{row['assignee_type']} #{row['assignee_id']}"
            i=self.steps.InsertItem(self.steps.GetItemCount(),row["title"])
            for col,value in enumerate((assignee,row["status"],str(row.get("due_date") or ""),"Yes" if row.get("calendar_eligible") else "No"),1):self.steps.SetItem(i,col,value)

    def on_save(self,_event):
        try:
            self.project_id=self.service.save_project(self.values(),self.project_id); self.record=self.service.project(self.project_id); self._fill(); self.refresh_steps(); wx.MessageBox("The project was saved.","Project Saved",wx.OK|wx.ICON_INFORMATION,self)
        except Exception as error:_error(self,"Unable to Save Project",error)

    def _edit_step(self,record=None):
        dialog=StepDialog(self,self.service,self.record,record)
        try:
            if dialog.ShowModal()==wx.ID_OK:self.service.save_step(self.project_id,dialog.values(),record["id"] if record else None); self.refresh_steps()
        except Exception as error:_error(self,"Unable to Save Step",error)
        finally:dialog.Destroy()

    def on_add_step(self,_event):self._edit_step()
    def on_open_step(self,_event):
        selected=self.steps.GetFirstSelected()
        if selected>=0:self._edit_step(self.rows[selected])

    def on_move(self,direction):
        selected=self.steps.GetFirstSelected()
        if selected<0:return
        try:
            moved=self.service.move_step(self.project_id,self.rows[selected]["id"],direction); self.refresh_steps()
            if moved:self.steps.Select(max(0,min(len(self.rows)-1,selected+direction)))
        except Exception as error:_error(self,"Unable to Reorder Step",error)

    def on_dependencies(self,_event):
        selected=self.steps.GetFirstSelected()
        if selected<0:return
        dialog=DependenciesDialog(self,self.service,self.project_id,self.rows[selected])
        try:dialog.ShowModal()
        finally:dialog.Destroy()

    def on_documents(self,_event):
        if not self.project_id:return
        dialog=ProjectDocumentsDialog(self,self.service,self.project_id)
        try:dialog.ShowModal()
        finally:dialog.Destroy()


class ProjectsDialog(wx.Dialog):
    """List current projects and due work without exposing obsolete task screens."""

    def __init__(self,parent,connection,session,authorization):
        super().__init__(parent,title="Projects and Scheduling",size=(1050,680),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.service=ProjectService(MariaDBProjectRepository(connection),session,authorization); panel=wx.Panel(self); outer=wx.BoxSizer(wx.VERTICAL)
        heading=wx.StaticText(panel,label="Projects and Scheduling"); font=heading.GetFont(); font.MakeBold(); font.SetPointSize(font.GetPointSize()+2); heading.SetFont(font); outer.Add(heading,0,wx.ALL,14)
        filters=wx.BoxSizer(wx.HORIZONTAL); self.church=_choice(panel,self.service.churches(),False); self.status=wx.Choice(panel,choices=["Current","All","Planned","Active","On Hold","Completed","Cancelled"]); self.status.SetSelection(0); filters.Add(wx.StaticText(panel,label="Church"),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,6); filters.Add(self.church,1,wx.RIGHT,14); filters.Add(wx.StaticText(panel,label="Show"),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,6); filters.Add(self.status,0); outer.Add(filters,0,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,14)
        self.book=wx.Notebook(panel); projects=wx.Panel(self.book); due=wx.Panel(self.book); self.book.AddPage(projects,"Projects"); self.book.AddPage(due,"Due Work")
        ps=wx.BoxSizer(wx.VERTICAL); self.list=wx.ListCtrl(projects,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for i,(label,width) in enumerate((("Number",90),("Project",250),("Status",90),("Priority",75),("Target",90),("Steps complete",105),("Open",60))):self.list.InsertColumn(i,label,width=width)
        ps.Add(self.list,1,wx.EXPAND|wx.ALL,10); projects.SetSizer(ps)
        ds=wx.BoxSizer(wx.VERTICAL); self.due=wx.ListCtrl(due,style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        for i,(label,width) in enumerate((("Due",90),("Project",250),("Step",280),("Status",90),("Assigned",120))):self.due.InsertColumn(i,label,width=width)
        ds.Add(self.due,1,wx.EXPAND|wx.ALL,10); due.SetSizer(ds); outer.Add(self.book,1,wx.EXPAND|wx.LEFT|wx.RIGHT,10)
        buttons=wx.BoxSizer(wx.HORIZONTAL); new=wx.Button(panel,label="New Project..."); open_button=wx.Button(panel,label="Open Project"); buttons.Add(new,0,wx.RIGHT,8); buttons.Add(open_button); buttons.AddStretchSpacer(); buttons.Add(wx.Button(panel,wx.ID_CLOSE,"Close")); outer.Add(buttons,0,wx.EXPAND|wx.ALL,14); panel.SetSizer(outer)
        self.church.Bind(wx.EVT_CHOICE,self.refresh); self.status.Bind(wx.EVT_CHOICE,self.refresh); self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.on_open); new.Bind(wx.EVT_BUTTON,self.on_new); open_button.Bind(wx.EVT_BUTTON,self.on_open); self.Bind(wx.EVT_BUTTON,lambda e:self.EndModal(wx.ID_CLOSE),id=wx.ID_CLOSE); self.refresh()

    def refresh(self,_event=None):
        church_id=_selected(self.church); selected=self.status.GetStringSelection(); statuses=("Planned","Active","On Hold") if selected=="Current" else (() if selected=="All" else (selected,)); self.rows=self.service.list_projects(church_id,statuses); self.list.DeleteAllItems()
        for row in self.rows:
            i=self.list.InsertItem(self.list.GetItemCount(),row["project_number"])
            for col,value in enumerate((row["name"],row["status"],row["priority"],str(row.get("target_date") or ""),str(row.get("completed_steps") or 0),str(row.get("open_steps") or 0)),1):self.list.SetItem(i,col,value)
            if row.get("is_overdue"):self.list.SetItemTextColour(i,wx.RED)
        self.due_rows=self.service.due_work(church_id,date.today()+timedelta(days=30)); self.due.DeleteAllItems()
        for row in self.due_rows:
            i=self.due.InsertItem(self.due.GetItemCount(),str(row.get("due_date") or ""))
            for col,value in enumerate((f"{row['project_number']} - {row['project_name']}",row["step_title"],row["status"],f"{row.get('assignee_type') or ''} #{row.get('assignee_id') or ''}".strip()),1):self.due.SetItem(i,col,value)
            if row.get("is_overdue"):self.due.SetItemTextColour(i,wx.RED)

    def _open(self,project_id=None):
        dialog=ProjectEditorDialog(self,self.service,_selected(self.church),project_id)
        try:dialog.ShowModal(); self.refresh()
        finally:dialog.Destroy()

    def on_new(self,_event):self._open()
    def on_open(self,_event):
        selected=self.list.GetFirstSelected()
        if selected>=0:self._open(self.rows[selected]["id"])


def show_projects(parent,connection,session,authorization):
    """Open the authorized project workspace."""
    dialog=ProjectsDialog(parent,connection,session,authorization)
    try:dialog.ShowModal()
    finally:dialog.Destroy()
