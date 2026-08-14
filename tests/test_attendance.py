from pathlib import Path
import unittest

from attendance_dialog import AttendanceRepository
from visual_reports.report_inventory import REPORTS_BY_CODE


ROOT = Path(__file__).resolve().parents[1]


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.executed = []

    def execute(self, sql, values=()):
        self.executed.append((sql, values))

    def fetchall(self):
        return list(self.rows)

    def close(self):
        pass


class FakeConnection:
    def __init__(self, rows):
        self.cursor_value = FakeCursor(rows)

    def cursor(self):
        return self.cursor_value


class AttendanceTests(unittest.TestCase):
    def test_choice_values_are_read_from_tblchoices(self):
        connection = FakeConnection([("[Visit\rWorship Service]",)])
        values = AttendanceRepository(connection).choices("AttendanceType")
        self.assertEqual(values, ["Visit", "Worship Service"])
        self.assertIn("FROM tblChoices", connection.cursor_value.executed[0][0])

    def test_editor_synchronizes_complete_known_person_set(self):
        source = (ROOT / "attendance_dialog.py").read_text(encoding="utf-8")
        self.assertIn("DELETE FROM tblAttendance WHERE ID=?", source)
        self.assertIn("UPDATE tblAttendance SET Communion=?,Note=?", source)
        self.assertIn("INSERT INTO tblAttendance", source)
        self.assertIn("Known people:", source)
        self.assertIn("Unnamed:", source)

    def test_service_save_generates_attendance_event_from_managed_choice(self):
        source = (ROOT / "unified_worship_service_dialog.py").read_text(encoding="utf-8")
        self.assertIn("def _sync_empty_attendance_event", source)
        self.assertIn("Field='AttendanceType'", source)
        self.assertIn("INSERT INTO tblAttendanceEvent", source)
        self.assertIn("events and any", source)

    def test_main_menu_routes_both_old_entry_points_to_combined_editor(self):
        menu = (ROOT / "main_menu.py").read_text(encoding="utf-8")
        cm = (ROOT / "cm.py").read_text(encoding="utf-8")
        self.assertNotIn('"lblRecordAttendance": "frmRecordAttendance"', menu)
        self.assertIn('case "lblAttendanceEvent" | "lblRecordAttendance"', cm)
        self.assertIn("show_attendance", cm)

    def test_attendance_reports_separate_events_from_weekly_summary(self):
        inventory = (ROOT / "visual_reports" / "report_inventory.py").read_text(encoding="utf-8")
        migration = (ROOT / "migrations" / "057_improve_attendance_reports.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn('"CMAT01", "Attendance Event Listing"', inventory)
        self.assertIn('"CMAT02", "Weekly Attendance Summary"', inventory)
        self.assertIn("rpt_attendance_weekly", inventory)
        self.assertIn("KnownAttendance", migration)
        self.assertIn("UnnamedAttendance", migration)
        self.assertEqual(REPORTS_BY_CODE["CMAT01"].dataset_version, 2)
        self.assertEqual(REPORTS_BY_CODE["CMAT02"].dataset_version, 2)

    def test_attendance_editor_uses_its_saved_repository(self):
        source = (ROOT / "attendance_dialog.py").read_text(encoding="utf-8")
        self.assertIn(
            'choices=self.repository.choices("AttendanceType")',
            source,
        )

    def test_people_are_sorted_members_first_and_checkboxes_are_single_click(self):
        connection = FakeConnection([])
        AttendanceRepository(connection).people(12, 3)
        sql = connection.cursor_value.executed[0][0]
        self.assertIn("ORDER BY COALESCE(p.Member,0) DESC,p.LastName,p.FirstName", sql)
        source = (ROOT / "attendance_dialog.py").read_text(encoding="utf-8")
        self.assertIn("EVT_GRID_CELL_LEFT_CLICK", source)
        self.assertIn("def on_cell_click", source)

    def test_ytd_summary_preserves_known_and_unnamed_counts(self):
        connection = FakeConnection([])
        AttendanceRepository(connection).year_to_date(3, 2026)
        sql = connection.cursor_value.executed[0][0]
        self.assertIn("KnownAttendance", sql)
        self.assertIn("GREATEST(SUM(e.HandCount)-SUM(e.KnownAttendance),0)", sql)

    def test_individual_attendance_report_is_registered(self):
        inventory = (ROOT / "visual_reports" / "report_inventory.py").read_text(encoding="utf-8")
        migration = (ROOT / "migrations" / "058_add_individual_attendance_report.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn('"CMAT03", "Individual Attendance History"', inventory)
        self.assertIn("rpt_individual_attendance", migration)
        self.assertIn("PersonID", migration)

    def test_pastors_attendance_comparison_uses_same_date_in_three_years(self):
        inventory = (ROOT / "visual_reports" / "report_inventory.py").read_text(encoding="utf-8")
        migration = (
            ROOT / "migrations" / "059_add_pastors_attendance_comparison.sql"
        ).read_text(encoding="utf-8")
        self.assertIn('"CMAT04", "Pastor\'s Attendance Comparison"', inventory)
        self.assertIn("YEAR(CURDATE())-1", migration)
        self.assertIn("YEAR(CURDATE())-2", migration)
        self.assertIn("FullYearAttendance", migration)
        self.assertIn("ThroughDateAttendance", migration)

    def test_member_followup_report_supports_a_missed_week_threshold(self):
        inventory = (ROOT / "visual_reports" / "report_inventory.py").read_text(encoding="utf-8")
        migration = (
            ROOT / "migrations" / "060_add_member_attendance_followup.sql"
        ).read_text(encoding="utf-8")
        report_form = (ROOT / "Forms" / "frmReports.json").read_text(encoding="utf-8")
        self.assertIn('"CMAT05", "Member Attendance Follow-up"', inventory)
        self.assertIn('row_color_field="FlagColor"', inventory)
        self.assertIn("MissedWeeks", migration)
        self.assertIn('"MissedWeeks"', report_form)
        self.assertIn('"value": 3', report_form)


if __name__ == "__main__":
    unittest.main()
