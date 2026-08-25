"""Contracts for the approved standalone Church event foundation."""

from datetime import datetime
from pathlib import Path
import unittest

from calendar_events import CalendarEventError, CalendarEventService
from event_schedule_rules import event_occurrences, parse_event_schedule


class Authorization:
    def __init__(self, permissions): self.permissions = set(permissions)
    def require(self, permission, _operation=None):
        if permission not in self.permissions: raise PermissionError(permission)


class Repository:
    def __init__(self): self.created = None; self.updated = None
    def events(self, church_id): return [{"church_id": church_id}]
    def create(self, values): self.created = values; return 9
    def update(self, values): self.updated = values; return True


class CalendarEventTests(unittest.TestCase):
    def service(self, permissions=("calendar.view", "calendar.events.manage")):
        repository = Repository()
        service = CalendarEventService(repository, type("Session", (), {"user_id": 7})(), Authorization(permissions))
        return service, repository

    def test_view_and_edit_have_separate_permissions(self):
        service, _repository = self.service(("calendar.view",))
        self.assertEqual(service.events(2)[0]["church_id"], 2)
        with self.assertRaises(PermissionError): service.save({})

    def test_create_validates_and_assigns_stable_key(self):
        service, repository = self.service()
        result = service.save({"church_id": 2, "title": "Community Supper",
                               "starts_at": datetime(2026, 9, 10, 17, 30),
                               "schedule_text": "Every Thursday", "status": "Confirmed"})
        self.assertEqual(result, 9); self.assertTrue(repository.created["event_key"].startswith("202609101730-"))
        self.assertEqual(repository.created["schedule_text"], "Every Thursday")
        self.assertEqual(repository.created["schedule_rule"], "RRULE:FREQ=WEEKLY;BYDAY=TH")

    def test_end_before_start_is_rejected(self):
        service, _repository = self.service()
        with self.assertRaises(CalendarEventError):
            service.save({"church_id": 2, "title": "Bad", "starts_at": "2026-09-10T12:00:00",
                          "ends_at": "2026-09-10T11:00:00", "schedule_text": "Every Thursday"})

    def test_unrecognized_natural_schedule_is_rejected(self):
        service, _repository = self.service()
        with self.assertRaisesRegex(CalendarEventError, "Schedule not understood"):
            service.save({"church_id": 2, "title": "Bad", "starts_at": "2026-09-10T12:00:00",
                          "schedule_text": "Whenever convenient"})

    def test_event_rules_are_broader_than_sunday_content_rules(self):
        cases = (
            ("Every Tuesday and Thursday.", "Every Tuesday and Thursday", "RRULE:FREQ=WEEKLY;BYDAY=TU,TH"),
            ("1st Tuesday of Every month.", "First Tuesday of every month", "RRULE:FREQ=MONTHLY;BYDAY=1TU"),
            ("Last Tuesday of the month.", "Last Tuesday of every month", "RRULE:FREQ=MONTHLY;BYDAY=-1TU"),
            ("Frist tuseday in October.", "First Tuesday in October", "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=1TU"),
        )
        for phrase, text, rule in cases:
            self.assertEqual(parse_event_schedule(phrase), (text, rule))
        self.assertEqual(event_occurrences(cases[0][2], datetime(2026, 8, 24).date(), 2),
                         [datetime(2026, 8, 25).date(), datetime(2026, 8, 27).date()])

    def test_main_menu_is_permission_guarded(self):
        from main_menu import MENU_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertIn("lblCalendarEvents", MENU_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblCalendarEvents"], "calendar.view")

    def test_end_controls_are_children_of_their_sizer_panel(self):
        source = Path("calendar_event_dialog.py").read_text(encoding="utf-8")
        self.assertIn("wx.CheckBox(self.end_panel", source)
        self.assertIn("wx.adv.TimePickerCtrl(self.end_panel)", source)


if __name__ == "__main__": unittest.main()
