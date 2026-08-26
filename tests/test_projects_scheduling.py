"""Contracts for the approved bounded Projects and Scheduling subsystem."""

from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]


class ProjectsSchedulingFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql=(ROOT/"migrations"/"119_add_projects_scheduling_foundation.sql").read_text(encoding="utf-8")

    def test_new_normalized_tables_do_not_restore_retired_generic_tables(self):
        for table in (
            "tblMinistryProject", "tblMinistryProjectStep",
            "tblMinistryProjectStepDependency", "tblMinistryProjectDocument",
        ):
            self.assertIn(f"CREATE TABLE {table}",self.sql)
        self.assertNotIn("CREATE TABLE tblProject ",self.sql)
        self.assertNotIn("CREATE TABLE tblTask ",self.sql)

    def test_permissions_cover_separate_project_responsibilities(self):
        for permission in (
            "projects.view", "projects.manage", "projects.assign",
            "projects.complete", "projects.admin", "projects.reports",
            "projects.calendar",
        ):
            self.assertIn(permission,self.sql)

    def test_project_and_step_lifecycle_checks_are_database_backstops(self):
        for token in (
            "ck_ministry_project_owner", "ck_ministry_project_status",
            "ck_ministry_project_completed", "ck_ministry_project_step_assignee",
            "ck_ministry_project_step_status", "ck_ministry_project_step_blocked",
            "ck_ministry_dependency_not_self",
        ):
            self.assertIn(token,self.sql)

    def test_safe_report_views_are_church_scoped(self):
        for view in (
            "rpt_ministry_project_summary", "rpt_ministry_project_due",
            "rpt_ministry_project_plan", "rpt_ministry_project_completed",
        ):
            self.assertIn(f"VIEW {view}",self.sql)
        self.assertGreaterEqual(self.sql.count("ChurchID"),8)

    def test_project_document_link_reuses_existing_document_record(self):
        self.assertIn("FOREIGN KEY (DocumentID) REFERENCES tblDocument(ID)",self.sql)

    def test_repository_uses_only_normalized_project_tables(self):
        source=(ROOT/"project_repository.py").read_text(encoding="utf-8")
        self.assertIn("tblMinistryProject",source)
        self.assertIn("tblMinistryProjectStep",source)
        self.assertNotIn("FROM tblProject ",source)
        self.assertNotIn("FROM tblTask ",source)

    def test_reordering_uses_only_positive_temporary_sequences(self):
        source=(ROOT/"project_repository.py").read_text(encoding="utf-8")
        self.assertIn("Sequence=Sequence+?",source)
        self.assertNotIn("Sequence=-ID",source)

    def test_project_workspace_is_registered_in_dashboard_and_menu(self):
        dashboard=(ROOT/"Forms"/"frmMain.json").read_text(encoding="utf-8")
        menu=(ROOT/"Menus"/"main.menu.json").read_text(encoding="utf-8")
        permissions=(ROOT/"permission_catalog.py").read_text(encoding="utf-8")
        self.assertIn('"lblProjects"',dashboard)
        self.assertIn("churchmanager.projects",menu)
        self.assertIn('"lblProjects": "projects.view"',permissions)

    def test_four_project_reports_use_safe_project_views(self):
        inventory=(ROOT/"visual_reports"/"report_inventory.py").read_text(encoding="utf-8")
        provider=(ROOT/"visual_reports"/"tabular_dataset.py").read_text(encoding="utf-8")
        for code,view in (("CMPS01","rpt_ministry_project_summary"),("CMPS02","rpt_ministry_project_due"),("CMPS03","rpt_ministry_project_plan"),("CMPS04","rpt_ministry_project_completed")):
            self.assertIn(f'ReportSpec("{code}"',inventory)
            self.assertIn(view,provider)

    def test_project_reports_are_registered_in_the_catalog(self):
        registration=(ROOT/"migrations"/"120_register_project_reports.sql").read_text(encoding="utf-8")
        for code in ("CMPS01","CMPS02","CMPS03","CMPS04"):
            self.assertIn(code,registration)
        self.assertEqual(4,registration.count("INSERT INTO tblReports"))
        self.assertIn("projects.reports",registration)


if __name__ == "__main__":
    unittest.main()
