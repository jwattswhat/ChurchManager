"""Parameterized MariaDB persistence for congregational projects."""

from __future__ import annotations


class ProjectConflictError(RuntimeError):
    """Raised when optimistic persistence detects a concurrent edit."""


class MariaDBProjectRepository:
    """Persist projects, ordered steps, dependencies, and audit events."""

    def __init__(self,connection):
        self.connection=connection
        self.marker="%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"

    def _execute(self,cursor,sql,values=()):return cursor.execute(sql.replace("?",self.marker),values)
    @staticmethod
    def _rows(cursor):
        names=[item[0] for item in cursor.description];return [dict(zip(names,row)) for row in cursor.fetchall()]
    def _all(self,sql,values=()):
        cursor=self.connection.cursor()
        try:self._execute(cursor,sql,values);return self._rows(cursor)
        finally:cursor.close()

    def churches(self):return self._all("SELECT ID id,Church name FROM tblChurch WHERE ID>0 ORDER BY Church")
    def list_projects(self,church_id,statuses=()):
        sql=("SELECT ProjectID id,ProjectNumber project_number,ProjectName name,OwnerType owner_type,OwnerID owner_id,"
             "Status status,Priority priority,TargetDate target_date,IsOverdue is_overdue,CompletedSteps completed_steps,OpenSteps open_steps "
             "FROM rpt_ministry_project_summary WHERE ChurchID=?")
        values=[church_id]
        if statuses:
            sql+=f" AND Status IN ({','.join('?' for _ in statuses)})";values.extend(statuses)
        sql+=" ORDER BY IsOverdue DESC,COALESCE(TargetDate,'9999-12-31'),ProjectNumber"
        return self._all(sql,tuple(values))
    def project(self,project_id):
        rows=self._all("SELECT ID id,ChurchID church_id,ProjectNumber project_number,Name name,Purpose purpose,OwnerType owner_type,OwnerID owner_id,Status status,Priority priority,PlannedStartDate planned_start,TargetDate target_date,CompletedDate completed_date,CalendarEligible calendar_eligible,Note note,Version version FROM tblMinistryProject WHERE ID=?",(project_id,))
        return rows[0] if rows else None
    def steps(self,project_id):return self._all("SELECT ID id,ProjectID project_id,Sequence sequence,Title title,AssigneeType assignee_type,AssigneeID assignee_id,Status status,DueDate due_date,CompletedDate completed_date,CalendarEligible calendar_eligible,Note note,Version version FROM tblMinistryProjectStep WHERE ProjectID=? ORDER BY Sequence,ID",(project_id,))
    def step(self,step_id):
        rows=self._all("SELECT ID id,ProjectID project_id,Sequence sequence,Title title,AssigneeType assignee_type,AssigneeID assignee_id,Status status,DueDate due_date,CompletedDate completed_date,CalendarEligible calendar_eligible,Note note,Version version FROM tblMinistryProjectStep WHERE ID=?",(step_id,));return rows[0] if rows else None
    def due_work(self,church_id,through_date):return self._all("SELECT ProjectID project_id,ProjectNumber project_number,ProjectName project_name,StepID step_id,Sequence sequence,StepTitle step_title,AssigneeType assignee_type,AssigneeID assignee_id,Status status,DueDate due_date,IsOverdue is_overdue FROM rpt_ministry_project_due WHERE ChurchID=? AND DueDate IS NOT NULL AND DueDate<=? ORDER BY IsOverdue DESC,DueDate,ProjectNumber,Sequence",(church_id,through_date))

    def next_project_number(self,church_id):
        rows=self._all("SELECT COALESCE(MAX(CAST(SUBSTRING(ProjectNumber,5) AS UNSIGNED)),0)+1 value FROM tblMinistryProject WHERE ChurchID=? AND ProjectNumber REGEXP '^PRJ-[0-9]+$'",(church_id,))
        return f"PRJ-{int(rows[0]['value']):04d}"
    def next_step_sequence(self,project_id):
        rows=self._all("SELECT COALESCE(MAX(Sequence),0)+1 value FROM tblMinistryProjectStep WHERE ProjectID=?",(project_id,));return int(rows[0]["value"])
    def incomplete_step_count(self,project_id):
        rows=self._all("SELECT COUNT(*) value FROM tblMinistryProjectStep WHERE ProjectID=? AND Status IN ('Not Started','In Progress','Blocked')",(project_id,));return int(rows[0]["value"])

    def owner_is_valid(self,church_id,owner_type,owner_id):
        if owner_type=="User":
            return bool(self._all("SELECT ID FROM tblUser WHERE ID=? AND Active=1",(owner_id,)))
        table={"Person":"tblPerson","Group":"tblGroup"}.get(owner_type)
        if not table:return False
        return bool(self._all(f"SELECT ID FROM {table} WHERE ID=? AND ChurchID=?",(owner_id,church_id)))
    def owners(self,church_id,owner_type):
        if owner_type=="Person":return self._all("SELECT ID id,TRIM(CONCAT_WS(' ',FirstName,LastName)) name FROM tblPerson WHERE ChurchID=? ORDER BY LastName,FirstName",(church_id,))
        if owner_type=="Group":return self._all("SELECT ID id,Name name FROM tblGroup WHERE ChurchID=? AND Status='ACTIVE' ORDER BY Name",(church_id,))
        if owner_type=="User":return self._all("SELECT ID id,DisplayName name FROM tblUser WHERE Active=1 ORDER BY DisplayName")
        return []

    def create_project(self,item,user_id):return self._write_project(None,item,user_id)
    def update_project(self,current,item,user_id):return self._write_project(current,item,user_id)
    def _write_project(self,current,item,user_id):
        cursor=self.connection.cursor()
        try:
            keys=("church_id","project_number","name","purpose","owner_type","owner_id","status","priority","planned_start","target_date","completed_date","calendar_eligible","note")
            if current is None:
                fields="ChurchID,ProjectNumber,Name,Purpose,OwnerType,OwnerID,Status,Priority,PlannedStartDate,TargetDate,CompletedDate,CalendarEligible,Note,CreatedByUserID,UpdatedByUserID"
                values=tuple(item.get(key) for key in keys)+(user_id,user_id)
                self._execute(cursor,f"INSERT INTO tblMinistryProject ({fields}) VALUES ({','.join('?' for _ in values)})",values);result=cursor.lastrowid;action="MINISTRY_PROJECT_CREATED"
            else:
                columns=("ChurchID","ProjectNumber","Name","Purpose","OwnerType","OwnerID","Status","Priority","PlannedStartDate","TargetDate","CompletedDate","CalendarEligible","Note")
                values=tuple(item.get(key) for key in keys)+(user_id,current["id"],current["version"])
                self._execute(cursor,"UPDATE tblMinistryProject SET "+",".join(f"{column}=?" for column in columns)+",UpdatedByUserID=?,Version=Version+1 WHERE ID=? AND Version=?",values)
                if cursor.rowcount!=1:raise ProjectConflictError("This project changed. Reopen it and try again.")
                result=current["id"];action="MINISTRY_PROJECT_UPDATED"
            self._audit(cursor,user_id,action,result,"MinistryProject",item.get("completion_reason"));self.connection.commit();return result
        except Exception:self.connection.rollback();raise
        finally:cursor.close()

    def create_step(self,project_id,item,user_id):return self._write_step(None,project_id,item,user_id)
    def update_step(self,current,item,user_id):return self._write_step(current,current["project_id"],item,user_id)
    def _write_step(self,current,project_id,item,user_id):
        cursor=self.connection.cursor()
        try:
            keys=("title","assignee_type","assignee_id","status","due_date","completed_date","calendar_eligible","note")
            if current is None:
                values=(project_id,item["sequence"])+tuple(item.get(key) for key in keys)+(user_id,user_id)
                fields="ProjectID,Sequence,Title,AssigneeType,AssigneeID,Status,DueDate,CompletedDate,CalendarEligible,Note,CreatedByUserID,UpdatedByUserID"
                self._execute(cursor,f"INSERT INTO tblMinistryProjectStep ({fields}) VALUES ({','.join('?' for _ in values)})",values);result=cursor.lastrowid;action="MINISTRY_PROJECT_STEP_CREATED"
            else:
                columns=("Title","AssigneeType","AssigneeID","Status","DueDate","CompletedDate","CalendarEligible","Note")
                values=tuple(item.get(key) for key in keys)+(user_id,current["id"],current["version"])
                self._execute(cursor,"UPDATE tblMinistryProjectStep SET "+",".join(f"{column}=?" for column in columns)+",UpdatedByUserID=?,Version=Version+1 WHERE ID=? AND Version=?",values)
                if cursor.rowcount!=1:raise ProjectConflictError("This step changed. Reopen it and try again.")
                result=current["id"];action="MINISTRY_PROJECT_STEP_UPDATED"
            self._audit(cursor,user_id,action,result,"MinistryProjectStep");self.connection.commit();return result
        except Exception:self.connection.rollback();raise
        finally:cursor.close()

    def dependency_graph(self,project_id):
        rows=self._all("SELECT d.StepID step_id,d.PredecessorStepID predecessor_id FROM tblMinistryProjectStepDependency d JOIN tblMinistryProjectStep s ON s.ID=d.StepID WHERE s.ProjectID=?",(project_id,));graph={}
        for row in rows:graph.setdefault(row["step_id"],set()).add(row["predecessor_id"])
        return graph
    def dependencies(self,step_id):return self._all("SELECT d.PredecessorStepID id,s.Title name FROM tblMinistryProjectStepDependency d JOIN tblMinistryProjectStep s ON s.ID=d.PredecessorStepID WHERE d.StepID=? ORDER BY s.Sequence,s.ID",(step_id,))
    def add_dependency(self,step_id,predecessor_id,user_id):
        cursor=self.connection.cursor()
        try:self._execute(cursor,"INSERT INTO tblMinistryProjectStepDependency (StepID,PredecessorStepID,CreatedByUserID) VALUES (?,?,?)",(step_id,predecessor_id,user_id));item_id=cursor.lastrowid;self._audit(cursor,user_id,"MINISTRY_PROJECT_DEPENDENCY_ADDED",item_id,"MinistryProjectDependency");self.connection.commit();return item_id
        except Exception:self.connection.rollback();raise
        finally:cursor.close()
    def remove_dependency(self,step_id,predecessor_id,user_id):
        cursor=self.connection.cursor()
        try:self._execute(cursor,"DELETE FROM tblMinistryProjectStepDependency WHERE StepID=? AND PredecessorStepID=?",(step_id,predecessor_id));self._audit(cursor,user_id,"MINISTRY_PROJECT_DEPENDENCY_REMOVED",step_id,"MinistryProjectStep");self.connection.commit()
        except Exception:self.connection.rollback();raise
        finally:cursor.close()

    def move_step(self,project_id,step_id,direction,user_id):
        cursor=self.connection.cursor()
        try:
            self._execute(cursor,"SELECT ID,Sequence FROM tblMinistryProjectStep WHERE ProjectID=? ORDER BY Sequence,ID FOR UPDATE",(project_id,));rows=cursor.fetchall(); ids=[row[0] for row in rows]
            if step_id not in ids:self.connection.rollback();return False
            index=ids.index(step_id); target=index+direction
            if target<0 or target>=len(ids):self.connection.rollback();return False
            ids[index],ids[target]=ids[target],ids[index]
            temporary_offset=max((int(row[1]) for row in rows),default=0)+len(rows)+1
            self._execute(cursor,"UPDATE tblMinistryProjectStep SET Sequence=Sequence+? WHERE ProjectID=?",(temporary_offset,project_id))
            for sequence,item_id in enumerate(ids,1):
                self._execute(cursor,"UPDATE tblMinistryProjectStep SET Sequence=?,UpdatedByUserID=?,Version=Version+1 WHERE ID=?",(sequence,user_id,item_id))
            self._audit(cursor,user_id,"MINISTRY_PROJECT_STEP_REORDERED",step_id,"MinistryProjectStep");self.connection.commit();return True
        except Exception:self.connection.rollback();raise
        finally:cursor.close()

    def documents(self,church_id):return self._all("SELECT ID id,Title name FROM tblDocument WHERE ChurchID=? ORDER BY Date DESC,Title,ID",(church_id,))
    def project_documents(self,project_id):return self._all("SELECT l.ID link_id,d.ID id,d.Title name,d.Date date FROM tblMinistryProjectDocument l JOIN tblDocument d ON d.ID=l.DocumentID WHERE l.ProjectID=? ORDER BY d.Date DESC,d.Title",(project_id,))
    def link_document(self,project_id,step_id,document_id,user_id):
        cursor=self.connection.cursor()
        try:self._execute(cursor,"INSERT INTO tblMinistryProjectDocument (ProjectID,StepID,DocumentID,CreatedByUserID) VALUES (?,?,?,?)",(project_id,step_id,document_id,user_id));result=cursor.lastrowid;self._audit(cursor,user_id,"MINISTRY_PROJECT_DOCUMENT_LINKED",result,"MinistryProjectDocument");self.connection.commit();return result
        except Exception:self.connection.rollback();raise
        finally:cursor.close()
    def unlink_document(self,link_id,user_id):
        cursor=self.connection.cursor()
        try:self._execute(cursor,"DELETE FROM tblMinistryProjectDocument WHERE ID=?",(link_id,));self._audit(cursor,user_id,"MINISTRY_PROJECT_DOCUMENT_UNLINKED",link_id,"MinistryProjectDocument");self.connection.commit()
        except Exception:self.connection.rollback();raise
        finally:cursor.close()
    def _audit(self,cursor,user_id,action,entity_id,entity_type,reason=None):self._execute(cursor,"INSERT INTO tblSecurityAuditEvent (UserID,Action,EntityType,EntityID,Reason) VALUES (?,?,?,?,?)",(user_id,action,entity_type,str(entity_id),reason))
