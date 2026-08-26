"""Tests for provider-neutral, privacy-safe calendar source adapters."""

from datetime import date, datetime
import unittest

from calendar_sources import CalendarEventDescriptor, CalendarSourceError, CalendarSourceService


class Authorization:
    def __init__(self, permissions): self.permissions = set(permissions)
    def require(self, permission, _operation=None):
        if permission not in self.permissions: raise PermissionError(permission)


class Repository:
    def church_events(self, church_id, _end):
        return [{"id": 4, "church_id": church_id, "title": "Food Shelf", "description": "Public collection",
                 "starts_at": datetime(2026, 8, 25, 9), "ends_at": datetime(2026, 8, 25, 10),
                 "all_day": 0, "time_zone": "America/Chicago", "location": "Narthex",
                 "status": "CONFIRMED", "schedule_rule": "RRULE:FREQ=WEEKLY;BYDAY=TU,TH", "version": 2}]
    def worship_services(self, church_id, _start, _end):
        return [{"id": 8, "church_id": church_id, "starts_at": datetime(2026, 8, 30, 9),
                 "location": "Sanctuary", "title": "Fourteenth Sunday after Pentecost"}]
    def group_meetings(self, church_id, _start, _end):
        return [{"id": 9, "church_id": church_id, "starts_at": datetime(2026, 8, 31, 18),
                 "ends_at": datetime(2026, 8, 31, 19), "title": "Council", "location": "Library",
                 "status": "SCHEDULED", "version": 1}]
    def project_milestones(self,church_id,_start,_end):
        return [{"id":10,"church_id":church_id,"project_number":"PRJ-0001","project_name":"Paint Office","event_date":date(2026,9,1),"status":"Active","version":2}]
    def project_steps(self,church_id,_start,_end):
        return [{"id":11,"church_id":church_id,"project_number":"PRJ-0001","project_name":"Paint Office","step_title":"Select color","event_date":date(2026,8,29),"status":"Not Started","version":1}]


class CalendarSourceTests(unittest.TestCase):
    def service(self, permissions): return CalendarSourceService(Repository(), Authorization(permissions))

    def test_event_recurrence_expands_to_stable_occurrence_descriptors(self):
        rows = self.service({"calendar.view"}).descriptors(
            "CHURCH_EVENT", 2, date(2026, 8, 25), date(2026, 8, 28))
        self.assertEqual([row.starts_at.date() for row in rows], [date(2026, 8, 25), date(2026, 8, 27)])
        self.assertEqual(rows[0].uid, "event-4-20260825@churchmanager.local")
        self.assertEqual(rows[0].description, "Public collection")

    def test_each_source_requires_its_own_view_permission(self):
        with self.assertRaises(PermissionError):
            self.service({"calendar.view"}).descriptors("WORSHIP_SERVICE", 2, "2026-08-01", "2026-09-01")
        with self.assertRaises(PermissionError):
            self.service({"calendar.view", "groups.view"}).descriptors("GROUP_MEETING", 2, "2026-08-01", "2026-09-01")

    def test_worship_and_group_use_the_same_contract(self):
        service = self.service({"calendar.view", "worship.manage", "groups.view", "groups.meetings.view"})
        worship = service.descriptors("WORSHIP_SERVICE", 2, "2026-08-01", "2026-09-01")[0]
        group = service.descriptors("GROUP_MEETING", 2, "2026-08-01", "2026-09-01")[0]
        self.assertIsInstance(worship, CalendarEventDescriptor)
        self.assertIsInstance(group, CalendarEventDescriptor)
        self.assertEqual(worship.uid, "worship-8@churchmanager.local")
        self.assertEqual(group.description, "")

    def test_invalid_ranges_and_unapproved_sources_fail_closed(self):
        service = self.service({"calendar.view"})
        with self.assertRaises(CalendarSourceError): service.descriptors("PERSON", 2, "2026-08-01", "2026-09-01")
        with self.assertRaises(CalendarSourceError): service.descriptors("CHURCH_EVENT", 2, "2026-09-01", "2026-08-01")

    def test_project_targets_and_steps_are_safe_all_day_descriptors(self):
        service=self.service({"calendar.view","projects.view","projects.calendar"})
        target=service.descriptors("PROJECT_MILESTONE",2,"2026-08-01","2026-09-02")[0]
        step=service.descriptors("PROJECT_STEP",2,"2026-08-01","2026-09-02")[0]
        self.assertTrue(target.all_day); self.assertTrue(step.all_day)
        self.assertEqual("project-10@churchmanager.local",target.uid)
        self.assertNotIn("note",target.description.casefold())

    def test_repository_query_excludes_restricted_groups_and_notes(self):
        from pathlib import Path
        source = Path("calendar_sources.py").read_text(encoding="utf-8")
        self.assertIn("g.PrivacyClass='STANDARD'", source)
        self.assertNotIn("m.Notes notes", source)


if __name__ == "__main__": unittest.main()
