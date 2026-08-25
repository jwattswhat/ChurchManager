"""Acceptance tests for portable ChurchManager iCalendar output."""

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from calendar_sources import CalendarEventDescriptor
from icalendar_export import ICalendarExportError, ICalendarExportService, serialize_calendar


class Authorization:
    def __init__(self, allowed=True): self.allowed = allowed
    def require(self, permission, _operation=None):
        if not self.allowed: raise PermissionError(permission)


class ICalendarExportTests(unittest.TestCase):
    def event(self, **changes):
        values = dict(source_type="CHURCH_EVENT", source_id=4, church_id=2,
                      uid="event-4-20260825@churchmanager.local", title="Food, Fun; Fellowship",
                      starts_at=datetime(2026, 8, 25, 9), ends_at=datetime(2026, 8, 25, 10),
                      location="Church\\Hall", description="Bring lunch\nAll welcome", version="2")
        values.update(changes); return CalendarEventDescriptor(**values)

    def test_timed_event_has_timezone_status_escaping_and_crlf(self):
        text = serialize_calendar([self.event()], now=datetime(2026, 8, 25, 12, tzinfo=timezone.utc))
        self.assertIn("DTSTART;TZID=America/Chicago:20260825T090000\r\n", text)
        self.assertIn("SUMMARY:Food\\, Fun\\; Fellowship", text)
        self.assertIn("LOCATION:Church\\\\Hall", text)
        self.assertIn("DESCRIPTION:Bring lunch\\nAll welcome", text)
        self.assertNotIn("\n", text.replace("\r\n", ""))

    def test_all_day_and_cancelled_events_use_portable_values(self):
        text = serialize_calendar([self.event(all_day=True, ends_at=None, status="CANCELLED")])
        self.assertIn("DTSTART;VALUE=DATE:20260825", text)
        self.assertIn("DTEND;VALUE=DATE:20260826", text)
        self.assertIn("STATUS:CANCELLED", text)

    def test_unicode_lines_fold_at_75_octets(self):
        text = serialize_calendar([self.event(title="Community " + "é" * 80)])
        physical = [line for line in text.split("\r\n") if line]
        self.assertTrue(all(len(line.encode("utf-8")) <= 75 for line in physical))
        self.assertTrue(any(line.startswith(" ") for line in physical))

    def test_writer_requires_permission_and_does_not_overwrite_silently(self):
        with TemporaryDirectory() as folder:
            target = Path(folder) / "events"
            written = ICalendarExportService(Authorization()).write(target, [self.event()])
            self.assertEqual(written.suffix, ".ics"); self.assertTrue(written.exists())
            with self.assertRaises(ICalendarExportError):
                ICalendarExportService(Authorization()).write(written, [self.event()])
            with self.assertRaises(PermissionError):
                ICalendarExportService(Authorization(False)).write(Path(folder) / "other.ics", [self.event()])

    def test_empty_or_unapproved_input_fails_closed(self):
        with self.assertRaises(ICalendarExportError): serialize_calendar([])
        with self.assertRaises(ICalendarExportError): serialize_calendar([{"title": "unsafe"}])

    def test_calendar_integration_is_registered_on_main_menu(self):
        from main_menu import MENU_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS

        self.assertIn("lblCalendarIntegration", MENU_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblCalendarIntegration"], "calendar.view")

    def test_calendar_integration_uses_current_church_name_column(self):
        source = Path("calendar_integration_dialog.py").read_text(encoding="utf-8")
        self.assertIn("SELECT ID,Church FROM tblChurch", source)
        self.assertNotIn("SELECT ID,ChurchName FROM tblChurch", source)

    def test_google_publish_is_wired_and_test_mode_fails_closed(self):
        source = Path("calendar_integration_dialog.py").read_text(encoding="utf-8")
        main = Path("cm.py").read_text(encoding="utf-8")
        self.assertIn("Connect to Google", source)
        self.assertIn("Publish Preview", source)
        self.assertIn("Google publishing is disabled in TEST MODE", source)
        self.assertIn("context.authorization, context.test_mode", main)


if __name__ == "__main__": unittest.main()
