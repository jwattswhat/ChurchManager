"""Contract tests for privacy-safe Group reports."""

import unittest
from pathlib import Path

from visual_reports.report_inventory import REPORTS_BY_CODE


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "Migrations" / "108_add_group_reports.sql"


class GroupReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MIGRATION.read_text(encoding="utf-8")

    def test_group_reports_use_dedicated_permission(self):
        for code in ("CMGR01", "CMGR02", "CMGR03"):
            self.assertEqual(REPORTS_BY_CODE[code].permission, "groups.reports.view")
            self.assertIn(f"'{code}'", self.source)

    def test_reports_expose_privacy_class_for_fail_closed_filtering(self):
        for view_name in (
            "rpt_group_current_roster", "rpt_person_group_participation",
            "rpt_group_meeting_attendance",
        ):
            view = self.source.split(f"VIEW {view_name}", 1)[1]
            view = view.split("CREATE OR REPLACE", 1)[0].split("INSERT INTO", 1)[0]
            self.assertIn("g.PrivacyClass", view)

    def test_roster_uses_current_membership_terms(self):
        roster = self.source.split("VIEW rpt_group_current_roster", 1)[1]
        roster = roster.split("CREATE OR REPLACE", 1)[0]
        self.assertIn("m.StartDate<=CURRENT_DATE", roster)
        self.assertIn("m.EndDate IS NULL OR m.EndDate>=CURRENT_DATE", roster)

    def test_meeting_attendance_is_not_worship_attendance(self):
        attendance = self.source.split("VIEW rpt_group_meeting_attendance", 1)[1]
        attendance = attendance.split("INSERT INTO", 1)[0]
        self.assertIn("tblGroupMeetingAttendance", attendance)
        self.assertNotIn("tblAttendance", attendance)


if __name__ == "__main__":
    unittest.main()
