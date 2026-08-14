from pathlib import Path
import unittest

from attendance_dialog import AttendanceRepository


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


if __name__ == "__main__":
    unittest.main()
