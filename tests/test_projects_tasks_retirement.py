"""Protect the complete retirement of generic Projects and Tasks."""

import json
from pathlib import Path
import unittest

from visual_reports.report_inventory import REPORTS_BY_CODE


ROOT = Path(__file__).resolve().parents[1]
FORMS = ROOT / "Forms"
REPORT_DEFINITIONS = ROOT / "visual_reports" / "definitions"
RETIRED_REPORTS = {"CMPJ01", "CMPJ02", "CMPJ03", "CMPJ04"}


class ProjectsTasksRetirementTests(unittest.TestCase):
    def test_retirement_migration_removes_database_surface(self):
        source = (ROOT / "migrations" / "098_retire_projects_and_tasks.sql").read_text(
            encoding="utf-8-sig"
        )
        for name in ("tblProject", "tblTask", "tblTaskWorker"):
            self.assertIn(f"DROP TABLE IF EXISTS {name}", source)
        for name in ("rpt_project", "rpt_task", "rpt_task_worker"):
            self.assertIn(f"DROP VIEW IF EXISTS {name}", source)
        self.assertIn("reports.ministry.run", source)
        for code in RETIRED_REPORTS:
            self.assertIn(code, source)

    def test_retired_forms_and_menu_routes_are_absent(self):
        for form in ("frmProject.json", "frmTask.json", "frmTaskWorker.json"):
            self.assertFalse((FORMS / form).exists())
        controls = json.loads((FORMS / "frmMain.json").read_text(encoding="utf-8"))[
            "frmMainFORM"
        ]["CONTROLS"]
        self.assertNotIn("lblProject", controls)
        self.assertNotIn("lblTask", controls)
        routes = (ROOT / "main_menu.py").read_text(encoding="utf-8")
        self.assertNotIn('"lblProject"', routes)
        self.assertNotIn('"lblTask"', routes)

    def test_retired_reports_and_project_filter_are_absent(self):
        self.assertEqual(RETIRED_REPORTS & set(REPORTS_BY_CODE), set())
        for code in RETIRED_REPORTS:
            self.assertFalse((REPORT_DEFINITIONS / f"{code}.json").exists())
        controls = json.loads((FORMS / "frmReports.json").read_text(encoding="utf-8"))[
            "frmReportsFORM"
        ]["CONTROLS"]
        self.assertNotIn("ProjectID", controls)


if __name__ == "__main__":
    unittest.main()
