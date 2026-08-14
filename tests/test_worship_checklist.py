import unittest
from pathlib import Path

from worship_checklist import checklist_counts


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


if __name__ == "__main__":
    unittest.main()
