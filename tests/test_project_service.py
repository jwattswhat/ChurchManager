"""Lifecycle tests for the bounded project service."""

from datetime import date,timedelta
from types import SimpleNamespace
import unittest

from project_service import ProjectService,ProjectValidationError


class Authorization:
    def __init__(self,permissions):self.permissions=set(permissions)
    def require(self,permission,operation=None):
        if permission not in self.permissions:raise PermissionError(operation or permission)


class Repository:
    def __init__(self):self.saved=None; self.steps=None; self.graph={2:{1}}
    def next_project_number(self,church_id):return "PRJ-0001"
    def create_project(self,item,user_id):self.saved=(item,user_id);return 4
    def project(self,item_id):return {"id":item_id,"church_id":3,"project_number":"PRJ-0001","status":"Active","version":1}
    def owner_is_valid(self,church_id,owner_type,owner_id):return church_id==3
    def incomplete_step_count(self,project_id):return 0
    def next_step_sequence(self,project_id):return 1
    def create_step(self,project_id,item,user_id):self.steps=(project_id,item,user_id);return 8
    def step(self,item_id):return {"id":item_id,"project_id":4,"status":"Not Started","version":1}
    def dependency_graph(self,project_id):return {key:set(value) for key,value in self.graph.items()}
    def add_dependency(self,step_id,predecessor_id,user_id):return 9
    def move_step(self,project_id,step_id,direction,user_id):self.moved=(project_id,step_id,direction,user_id);return True
    def documents(self,church_id):return [{"id":10,"name":"Meeting notes"}]
    def project_documents(self,project_id):return []
    def link_document(self,project_id,step_id,document_id,user_id):self.linked=(project_id,step_id,document_id,user_id);return 11


class ProjectServiceTests(unittest.TestCase):
    def service(self,permissions=("projects.view","projects.manage","projects.assign","projects.complete")):
        self.repository=Repository();return ProjectService(self.repository,SimpleNamespace(user_id=6),Authorization(permissions))

    def project_values(self):return {"church_id":3,"name":"Replace fellowship hall lights","status":"Active","priority":"Normal"}

    def test_new_project_receives_stable_number(self):
        self.assertEqual(4,self.service().save_project(self.project_values()))
        self.assertEqual("PRJ-0001",self.repository.saved[0]["project_number"])

    def test_cross_church_owner_is_rejected(self):
        service=self.service();self.repository.owner_is_valid=lambda *_:False
        values=self.project_values();values.update({"owner_type":"Group","owner_id":2})
        with self.assertRaises(ProjectValidationError):service.save_project(values)

    def test_application_user_can_own_work_for_a_valid_church(self):
        service=self.service();values=self.project_values();values.update({"owner_type":"User","owner_id":6})
        self.assertEqual(4,service.save_project(values))

    def test_edit_preserves_project_number_when_form_does_not_resubmit_it(self):
        service=self.service();self.repository.update_project=lambda current,item,user_id:(current,item,user_id)
        current,item,user_id=service.save_project(self.project_values(),4)
        self.assertEqual("PRJ-0001",item["project_number"])

    def test_only_active_project_accepts_new_steps(self):
        service=self.service();self.repository.project=lambda item_id:{"id":item_id,"church_id":3,"project_number":"PRJ-1","status":"Planned"}
        with self.assertRaises(ProjectValidationError):service.save_step(4,{"title":"Ask for bids"})

    def test_blocked_step_requires_reason(self):
        with self.assertRaises(ProjectValidationError):self.service().save_step(4,{"title":"Order lamps","status":"Blocked"})

    def test_future_step_completion_is_rejected(self):
        with self.assertRaises(ProjectValidationError):self.service().save_step(4,{"title":"Order lamps","status":"Complete","completed_date":date.today()+timedelta(days=1)})

    def test_cross_project_dependency_is_rejected(self):
        service=self.service();self.repository.step=lambda item_id:{"id":item_id,"project_id":item_id}
        with self.assertRaises(ProjectValidationError):service.add_dependency(2,1)

    def test_dependency_cycle_is_rejected(self):
        service=self.service();self.repository.step=lambda item_id:{"id":item_id,"project_id":4}
        with self.assertRaises(ProjectValidationError):service.add_dependency(1,2)

    def test_step_move_is_bounded_and_delegated(self):
        service=self.service()
        self.assertTrue(service.move_step(4,8,1))
        self.assertEqual((4,8,1,6),self.repository.moved)
        with self.assertRaises(ProjectValidationError):service.move_step(4,8,2)

    def test_document_link_requires_same_church_document(self):
        service=self.service()
        self.assertEqual(11,service.link_document(4,10))
        self.assertEqual((4,None,10,6),self.repository.linked)
        with self.assertRaises(ProjectValidationError):service.link_document(4,99)

    def test_duplicate_document_link_is_rejected(self):
        service=self.service();self.repository.project_documents=lambda _project_id:[{"id":10,"link_id":22}]
        with self.assertRaises(ProjectValidationError):service.link_document(4,10)


if __name__=="__main__":unittest.main()
