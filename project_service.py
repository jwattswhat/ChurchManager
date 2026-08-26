"""Authorization and lifecycle rules for bounded congregational projects."""

from __future__ import annotations

from datetime import date


class ProjectValidationError(ValueError):
    """Raised when project work violates the approved business rules."""


class ProjectService:
    """Validate project and step commands before persistence."""

    PROJECT_STATUSES=("Planned","Active","On Hold","Completed","Cancelled")
    STEP_STATUSES=("Not Started","In Progress","Blocked","Complete","Not Needed")
    PRIORITIES=("Low","Normal","High","Urgent")
    OWNER_TYPES=("Person","Group","User")

    def __init__(self,repository,session,authorization):
        self.repository=repository; self.session=session; self.authorization=authorization

    def list_projects(self,church_id,statuses=None):
        self.authorization.require("projects.view","view projects")
        return self.repository.list_projects(_id(church_id,"church"),statuses or ())

    def churches(self):
        self.authorization.require("projects.view","view project churches")
        return self.repository.churches()

    def owners(self,church_id,owner_type):
        self.authorization.require("projects.view","view project owners")
        return self.repository.owners(_id(church_id,"church"),owner_type)

    def steps(self,project_id):
        project=self.project(project_id)
        return self.repository.steps(project["id"])

    def due_work(self,church_id,through_date):
        self.authorization.require("projects.view","view due project work")
        return self.repository.due_work(_id(church_id,"church"),through_date)

    def project(self,project_id):
        self.authorization.require("projects.view","view a project")
        item=self.repository.project(_id(project_id,"project"))
        if not item: raise ProjectValidationError("The project is unavailable.")
        return item

    def save_project(self,values,project_id=None):
        self.authorization.require("projects.manage","save a project")
        item=self._project_values(values)
        if item["owner_type"]: self.authorization.require("projects.assign","assign a project owner")
        self._validate_owner(item["church_id"],item["owner_type"],item["owner_id"])
        if project_id is None:
            item["project_number"]=self.repository.next_project_number(item["church_id"])
            return self.repository.create_project(item,self.session.user_id)
        current=self.project(project_id)
        if current["church_id"]!=item["church_id"]: raise ProjectValidationError("A project cannot be moved to another church.")
        requested=str(item.get("project_number") or "").strip()
        if requested and current["project_number"]!=requested: raise ProjectValidationError("The project number cannot be changed.")
        item["project_number"]=current["project_number"]
        if current["status"]!=item["status"]: self.authorization.require("projects.complete","change project status")
        if item["status"]=="Completed" and self.repository.incomplete_step_count(current["id"]):
            reason=str(values.get("completion_reason") or "").strip()
            if not reason: raise ProjectValidationError("Explain why the project is complete with unfinished steps.")
            item["completion_reason"]=reason[:500]
        return self.repository.update_project(current,item,self.session.user_id)

    def save_step(self,project_id,values,step_id=None):
        self.authorization.require("projects.manage","save a project step")
        project=self.project(project_id)
        if project["status"]!="Active" and step_id is None: raise ProjectValidationError("Only Active projects accept new steps.")
        item=self._step_values(values)
        if item["assignee_type"]: self.authorization.require("projects.assign","assign project work")
        self._validate_owner(project["church_id"],item["assignee_type"],item["assignee_id"])
        if step_id is None:
            item["sequence"]=self.repository.next_step_sequence(project["id"])
            return self.repository.create_step(project["id"],item,self.session.user_id)
        current=self.repository.step(_id(step_id,"step"))
        if not current or current["project_id"]!=project["id"]: raise ProjectValidationError("The project step is unavailable.")
        if current["status"]!=item["status"]: self.authorization.require("projects.complete","change step status")
        return self.repository.update_step(current,item,self.session.user_id)

    def add_dependency(self,step_id,predecessor_id):
        self.authorization.require("projects.manage","add a step dependency")
        step=self.repository.step(_id(step_id,"step")); predecessor=self.repository.step(_id(predecessor_id,"predecessor step"))
        if not step or not predecessor or step["project_id"]!=predecessor["project_id"]: raise ProjectValidationError("Dependencies must belong to the same project.")
        if step["id"]==predecessor["id"]: raise ProjectValidationError("A step cannot depend on itself.")
        graph=self.repository.dependency_graph(step["project_id"])
        graph.setdefault(step["id"],set()).add(predecessor["id"])
        if _has_cycle(graph): raise ProjectValidationError("That dependency would create a cycle.")
        return self.repository.add_dependency(step["id"],predecessor["id"],self.session.user_id)

    def remove_dependency(self,step_id,predecessor_id):
        self.authorization.require("projects.manage","remove a step dependency")
        return self.repository.remove_dependency(_id(step_id,"step"),_id(predecessor_id,"predecessor step"),self.session.user_id)

    def dependencies(self,step_id):
        self.authorization.require("projects.view","view step dependencies")
        return self.repository.dependencies(_id(step_id,"step"))

    def move_step(self,project_id,step_id,direction):
        self.authorization.require("projects.manage","reorder project steps")
        if direction not in (-1,1):raise ProjectValidationError("The requested step movement is invalid.")
        project=self.project(project_id); step=self.repository.step(_id(step_id,"step"))
        if not step or step["project_id"]!=project["id"]:raise ProjectValidationError("The project step is unavailable.")
        return self.repository.move_step(project["id"],step["id"],direction,self.session.user_id)

    def documents(self,project_id):
        project=self.project(project_id)
        return {"available":self.repository.documents(project["church_id"]),"linked":self.repository.project_documents(project["id"])}

    def link_document(self,project_id,document_id,step_id=None):
        self.authorization.require("projects.manage","link a project document")
        project=self.project(project_id); available={row["id"] for row in self.repository.documents(project["church_id"])}; document_id=_id(document_id,"document")
        if document_id not in available:raise ProjectValidationError("The document is not available to this church.")
        if step_id is not None:
            step=self.repository.step(_id(step_id,"step"))
            if not step or step["project_id"]!=project["id"]:raise ProjectValidationError("The project step is unavailable.")
        if any(row["id"]==document_id for row in self.repository.project_documents(project["id"])):
            raise ProjectValidationError("That document is already linked to this project.")
        return self.repository.link_document(project["id"],step_id,document_id,self.session.user_id)

    def unlink_document(self,project_id,link_id):
        self.authorization.require("projects.manage","unlink a project document")
        links={row["link_id"] for row in self.documents(project_id)["linked"]}
        link_id=_id(link_id,"document link")
        if link_id not in links:raise ProjectValidationError("The project document link is unavailable.")
        return self.repository.unlink_document(link_id,self.session.user_id)

    def _validate_owner(self,church_id,owner_type,owner_id):
        if owner_type is None:return
        if owner_type not in self.OWNER_TYPES: raise ProjectValidationError("Select a valid owner type.")
        if not self.repository.owner_is_valid(church_id,owner_type,owner_id): raise ProjectValidationError("The selected owner is not available to this church.")

    def _project_values(self,values):
        status=values.get("status") or "Planned"; priority=values.get("priority") or "Normal"
        if status not in self.PROJECT_STATUSES: raise ProjectValidationError("Select a valid project status.")
        if priority not in self.PRIORITIES: raise ProjectValidationError("Select a valid project priority.")
        start=values.get("planned_start"); target=values.get("target_date")
        if start and target and target<start: raise ProjectValidationError("The target date cannot precede the planned start.")
        completed=values.get("completed_date")
        if status=="Completed" and not completed: completed=date.today()
        if status!="Completed": completed=None
        return {"church_id":_id(values.get("church_id"),"church"),"project_number":values.get("project_number"),"name":_required(values.get("name"),160,"project name"),"purpose":_optional(values.get("purpose"),1000),"owner_type":values.get("owner_type") or None,"owner_id":_optional_id(values.get("owner_id")),"status":status,"priority":priority,"planned_start":start or None,"target_date":target or None,"completed_date":completed,"calendar_eligible":bool(values.get("calendar_eligible")),"note":_optional(values.get("note"),2000)}

    def _step_values(self,values):
        status=values.get("status") or "Not Started"
        if status not in self.STEP_STATUSES: raise ProjectValidationError("Select a valid step status.")
        note=_optional(values.get("note"),1000)
        if status=="Blocked" and not note: raise ProjectValidationError("A blocked step requires a reason.")
        completed=values.get("completed_date")
        if status=="Complete" and not completed: completed=date.today()
        if completed and completed>date.today(): raise ProjectValidationError("A completion date cannot be in the future.")
        if status!="Complete": completed=None
        return {"title":_required(values.get("title"),200,"step title"),"assignee_type":values.get("assignee_type") or None,"assignee_id":_optional_id(values.get("assignee_id")),"status":status,"due_date":values.get("due_date") or None,"completed_date":completed,"calendar_eligible":bool(values.get("calendar_eligible")),"note":note}


def _has_cycle(graph):
    visiting=set(); visited=set()
    def visit(node):
        if node in visiting:return True
        if node in visited:return False
        visiting.add(node)
        if any(visit(parent) for parent in graph.get(node,set())):return True
        visiting.remove(node); visited.add(node); return False
    return any(visit(node) for node in graph)

def _id(value,label):
    try:value=int(value)
    except (TypeError,ValueError):raise ProjectValidationError(f"A valid {label} is required.")
    if value<=0:raise ProjectValidationError(f"A valid {label} is required.")
    return value
def _optional_id(value):return None if value in (None,"") else _id(value,"selection")
def _required(value,limit,label):
    text=str(value or "").strip()
    if not text:raise ProjectValidationError(f"{label.title()} is required.")
    if len(text)>limit:raise ProjectValidationError(f"{label.title()} is too long.")
    return text
def _optional(value,limit):
    text=str(value or "").strip(); return text[:limit] or None
