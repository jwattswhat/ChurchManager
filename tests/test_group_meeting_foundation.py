"""Regression tests for Group meetings and attendance foundation."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GroupMeetingFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = (ROOT / "Migrations" / "107_add_group_meetings_and_attendance.sql").read_text(encoding="utf-8")

    def test_separate_group_meeting_tables_are_created(self):
        self.assertIn("CREATE TABLE tblGroupMeeting (", self.sql)
        self.assertIn("CREATE TABLE tblGroupMeetingAttendance (", self.sql)
        self.assertNotIn("tblAttendanceEvent", self.sql)

    def test_attendance_identity_and_status_are_constrained(self):
        self.assertIn("UNIQUE KEY uq_group_meeting_person (GroupMeetingID,PersonID)", self.sql)
        for status in ("PRESENT", "ABSENT", "EXCUSED", "UNKNOWN"):
            self.assertIn(status, self.sql)

    def test_anonymous_head_count_does_not_require_fake_people(self):
        self.assertIn("TotalHeadCount int NULL", self.sql)
        self.assertNotIn("VisitorName", self.sql)

    def test_permissions_match_approved_contract(self):
        for permission in ("groups.meetings.view", "groups.meetings.edit", "groups.attendance.view", "groups.attendance.record"):
            self.assertIn(permission, self.sql)


if __name__ == "__main__": unittest.main()
