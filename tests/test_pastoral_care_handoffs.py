"""Contract tests for deliberate minimum-necessary pastoral-care handoffs."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PastoralCareHandoffTests(unittest.TestCase):
    def test_attendance_handoff_is_deliberate_and_copies_no_notes(self):
        source = (ROOT / "attendance_dialog.py").read_text(encoding="utf-8")
        handoff = source.split("def on_care_follow_up", 1)[1].split("def on_new", 1)[0]
        self.assertIn('"source": "ATTENDANCE_FOLLOWUP"', handoff)
        self.assertIn("Create Care Follow-up...", source)
        self.assertNotIn('event[9]', handoff)

    def test_prayer_handoff_does_not_copy_prayer_wording(self):
        source = (ROOT / "sunday_content_dialog.py").read_text(encoding="utf-8")
        handoff = source.split("def on_care_follow_up", 1)[1].split("class SundayContentPreviewDialog", 1)[0]
        self.assertIn('"source": "PRAYER_REQUEST"', handoff)
        self.assertIn('"category": "Prayer Follow-up"', handoff)
        self.assertNotIn("row[3]", handoff)

    def test_handoffs_remain_permission_controlled(self):
        source = (ROOT / "pastoral_care_dialog.py").read_text(encoding="utf-8")
        self.assertIn('authorization.require("pastoral.care.create"', source)


if __name__ == "__main__":
    unittest.main()
