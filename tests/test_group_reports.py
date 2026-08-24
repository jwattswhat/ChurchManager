"""Contract tests for privacy-safe Group reports."""

import unittest
from pathlib import Path

from visual_reports.report_inventory import REPORTS_BY_CODE
from visual_reports.tabular_dataset import TabularDatasetProvider


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = (
    ROOT / "Migrations" / "108_add_group_reports.sql",
    ROOT / "Migrations" / "109_add_group_attendance_sheet.sql",
)


class GroupReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = "\n".join(path.read_text(encoding="utf-8") for path in MIGRATIONS)

    def test_group_reports_use_dedicated_permission(self):
        for code in ("CMGR01", "CMGR02", "CMGR03", "CMGR04"):
            self.assertEqual(REPORTS_BY_CODE[code].permission, "groups.reports.view")
            self.assertIn(f"'{code}'", self.source)

    def test_reports_expose_privacy_class_for_fail_closed_filtering(self):
        for view_name in (
            "rpt_group_current_roster", "rpt_person_group_participation",
            "rpt_group_meeting_attendance",
            "rpt_group_attendance_sheet",
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

    def test_attendance_sheet_is_effective_dated_and_has_writable_columns(self):
        spec = REPORTS_BY_CODE["CMGR04"]
        self.assertIn("MembershipStartDate", spec.filter_fields)
        self.assertIn("MembershipEndDate", spec.filter_fields)
        self.assertEqual(
            [column.field for column in spec.columns][-4:],
            ["Present", "Absent", "Excused", "Notes"],
        )

    def test_attendance_sheet_adds_secretary_visitor_lines(self):
        rows = TabularDatasetProvider._group_attendance_visitor_rows(6)
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row["LastName"] == "Visitor / Guest" for row in rows))
        self.assertTrue(all(row["Notes"] == "" for row in rows))

    def test_start_date_is_labeled_as_meeting_date(self):
        self.assertEqual(
            TabularDatasetProvider._parameter_label("CMGR04", "StartDate"),
            "Meeting date",
        )


if __name__ == "__main__":
    unittest.main()
