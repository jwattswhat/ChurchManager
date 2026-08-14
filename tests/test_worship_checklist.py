import unittest
from pathlib import Path

from worship_checklist import checklist_counts, overall_checklist_status


ROOT = Path(__file__).resolve().parents[1]


class WorshipChecklistTests(unittest.TestCase):
    def test_counts_three_reminder_states(self):
        rows = [
            (1, 1, "One", "MANUAL", 1, "", "DONE"),
            (2, 2, "Two", "MANUAL", 1, "", "NOT_DONE"),
            (3, 3, "Three", "MANUAL", 1, "", "NOT_NEEDED"),
        ]
        self.assertEqual(checklist_counts(rows), {
            "DONE": 1, "NOT_DONE": 1, "NOT_NEEDED": 1,
        })

    def test_migration_preserves_legacy_columns_and_adds_report_views(self):
        source = (ROOT / "migrations" / "050_normalize_worship_preparation_checklists.sql").read_text()
        self.assertIn("CREATE TABLE tblServiceChecklistItem", source)
        self.assertNotIn("DROP COLUMN CheckList", source)
        self.assertIn("rpt_worship_planner_checklist_summary", source)

    def test_standard_planner_does_not_print_checklist_by_default(self):
        source = (ROOT / "visual_reports" / "definitions" / "CMWP01.json").read_text()
        self.assertNotIn('"repeatcollection": "checklist"', source)

    def test_participant_summary_uses_current_assignment_status_column(self):
        source = (ROOT / "worship_checklist.py").read_text()
        self.assertIn("AssignmentStatus<>'DECLINED'", source)
        self.assertNotIn("COALESCE(Status", source)

    def test_close_button_ends_the_modal_dialog(self):
        source = (ROOT / "worship_checklist.py").read_text()
        self.assertIn("close.Bind(wx.EVT_BUTTON", source)
        self.assertIn("self.EndModal(wx.ID_CLOSE)", source)

    def test_overall_status_respects_required_items_and_override(self):
        unfinished = [(1, 1, "Required", "MANUAL", 1, "", "NOT_DONE")]
        optional = [(1, 1, "Optional", "MANUAL", 0, "", "NOT_DONE")]
        self.assertEqual(overall_checklist_status(unfinished), "Needs attention")
        self.assertEqual(overall_checklist_status(optional), "Ready")
        self.assertEqual(
            overall_checklist_status(unfinished, manually_confirmed=True),
            "Manually confirmed complete",
        )

    def test_this_time_task_is_service_only_and_manual(self):
        source = (ROOT / "worship_checklist.py").read_text()
        self.assertIn("def add_service_task", source)
        self.assertIn("VALUES (?,NULL,?,?,'MANUAL',?,'NOT_DONE')", source)
        self.assertIn('label="Add This-Time Task..."', source)

    def test_double_click_toggles_done_and_not_done(self):
        source = (ROOT / "worship_checklist.py").read_text()
        self.assertIn("wx.EVT_LIST_ITEM_ACTIVATED, self.toggle_selected", source)
        self.assertIn('self.change("NOT_DONE" if current == "DONE" else "DONE")', source)

    def test_normalized_checklist_maintenance_is_on_main_menu(self):
        menu = (ROOT / "main_menu.py").read_text()
        application = (ROOT / "cm.py").read_text()
        source = (ROOT / "worship_checklist.py").read_text()
        self.assertNotIn('"lblCheckList": "frmCheckList"', menu)
        self.assertIn('case "lblCheckList":', application)
        self.assertIn("show_checklist_maintenance", application)
        self.assertIn("class ChecklistMaintenanceDialog", source)
        self.assertIn("Create Custom from Selected...", source)


if __name__ == "__main__":
    unittest.main()
