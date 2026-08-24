"""Tests for Group meeting validation and authorization."""

from datetime import datetime
from types import SimpleNamespace
import unittest

from group_meeting_service import GroupMeetingService, GroupValidationError


class Authorization:
    def __init__(self, permissions): self.permissions = set(permissions)
    def require(self, name, _action):
        if name not in self.permissions: raise PermissionError(name)


class Groups:
    def group(self, _group_id):
        return {"id": 4, "church_id": 2, "status": "ACTIVE", "privacy_class": "STANDARD"}


class Repository:
    def create_meeting(self, values): self.created = values; return 8
    def meeting(self, _meeting_id):
        return {"id": 8, "group_id": 4, "church_id": 2, "starts_at": datetime(2026, 8, 24, 19),
                "status": "SCHEDULED", "attendance_mode": "ROSTER", "title": "Council", "location": None, "version": 1}
    def roster_for_date(self, *_args): return [{"person_id": 10, "person": "Ada Member", "is_member": 1}]
    def attendance(self, _meeting_id): return []
    def available_people(self, _church_id): return [{"id": 10, "person": "Ada Member"}, {"id": 11, "person": "Gus Guest"}]
    def add_guest(self, meeting_id, person_id, user_id): self.guest = (meeting_id, person_id, user_id); return True
    def replace_attendance(self, meeting, entries, count, user_id): self.recorded = (meeting, entries, count, user_id); return True
    def cancel_meeting(self, meeting, user_id): self.cancelled = (meeting, user_id); return True
    def reschedule_meeting(self, meeting, values): self.rescheduled = (meeting, values); return 9


class GroupMeetingServiceTests(unittest.TestCase):
    def service(self, permissions):
        return GroupMeetingService(Repository(), Groups(), SimpleNamespace(user_id=7), Authorization(permissions))

    def test_meeting_requires_ordered_times(self):
        service = self.service({"groups.meetings.edit"})
        with self.assertRaisesRegex(GroupValidationError, "cannot precede"):
            service.create_meeting(4, {"title": "Council", "starts_at": "2026-08-24 19:00", "ends_at": "2026-08-24 18:00"})

    def test_existing_person_guest_does_not_create_membership(self):
        service = self.service({"groups.attendance.record"})
        self.assertTrue(service.add_guest(8, 11))
        self.assertEqual(service.repository.guest, (8, 11, 7))
        self.assertFalse(hasattr(service.repository, "create_membership"))

    def test_attendance_rejects_duplicates_and_negative_head_count(self):
        service = self.service({"groups.attendance.record"})
        with self.assertRaisesRegex(GroupValidationError, "only once"):
            service.record_attendance(8, [(10, "PRESENT"), (10, "ABSENT")])
        with self.assertRaisesRegex(GroupValidationError, "cannot be negative"):
            service.record_attendance(8, [(10, "PRESENT")], -1)

    def test_cancel_and_reschedule_preserve_original_occurrence(self):
        service = self.service({"groups.meetings.edit"})
        self.assertTrue(service.cancel_meeting(8))
        self.assertEqual(service.reschedule_meeting(8, {"starts_at": "2026-08-31 19:00"}), 9)
        self.assertEqual(service.repository.rescheduled[0]["id"], 8)


if __name__ == "__main__": unittest.main()
