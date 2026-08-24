"""Source-level safeguards for the Group meeting and attendance screens."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GroupMeetingDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "group_meeting_dialog.py").read_text(encoding="utf-8")
        cls.group_source = (ROOT / "group_dialog.py").read_text(encoding="utf-8")

    def test_group_detail_opens_meeting_history(self):
        self.assertIn('label="Meetings..."', self.group_source)
        self.assertIn("GroupMeetingsDialog", self.group_source)

    def test_main_menu_launcher_selects_group_and_meeting(self):
        self.assertIn("class GroupAttendanceLauncherDialog", self.source)
        self.assertIn("def show_group_attendance", self.source)

    def test_attendance_supports_status_cycle_and_guest_without_enrollment(self):
        self.assertIn("EVT_LIST_ITEM_ACTIVATED", self.source)
        self.assertIn('label="Add Guest..."', self.source)
        self.assertIn("does not create Group membership", self.source)

    def test_dialog_buttons_are_children_of_the_sized_panel(self):
        self.assertNotIn("self.CreateStdDialogButtonSizer", self.source)
        self.assertIn("wx.Button(panel, wx.ID_CANCEL", self.source)


if __name__ == "__main__": unittest.main()
