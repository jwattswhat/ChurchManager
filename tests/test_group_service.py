"""Tests for the Group authorization and validation boundary."""

from datetime import date
from types import SimpleNamespace
import unittest

from group_service import GroupService, GroupValidationError


class Authorization:
    def __init__(self, permissions): self.permissions = set(permissions)
    def has_permission(self, name): return name in self.permissions
    def require(self, name, _action):
        if name not in self.permissions: raise PermissionError(name)


class Repository:
    def __init__(self): self.created = None
    def group(self, _group_id): return {"id": 4, "church_id": 2, "privacy_class": "STANDARD"}
    def person_church_id(self, _person_id): return 2
    def membership_overlaps(self, *_args): return False
    def create_membership(self, values): self.created = values; return 9


class GroupServiceTests(unittest.TestCase):
    def service(self, permissions):
        return GroupService(Repository(), SimpleNamespace(user_id=7), Authorization(permissions))

    def test_membership_requires_same_church_and_no_overlap(self):
        service = self.service({"groups.membership.edit"})
        self.assertEqual(service.add_membership(4, 8, date(2026, 8, 24)), 9)
        service.repository.person_church_id = lambda _person_id: 3
        with self.assertRaisesRegex(GroupValidationError, "same church"):
            service.add_membership(4, 8, date(2026, 8, 24))

    def test_closed_group_requires_end_date(self):
        service = self.service({"groups.edit"})
        with self.assertRaisesRegex(GroupValidationError, "requires an end date"):
            service.create_group({
                "church_id": 2, "group_key": "elders", "name": "Elders",
                "group_type_id": 1, "status": "CLOSED",
            })

    def test_restricted_group_requires_dedicated_permission(self):
        service = self.service({"groups.edit"})
        with self.assertRaises(PermissionError):
            service.create_group({
                "church_id": 2, "group_key": "care-team", "name": "Care Team",
                "group_type_id": 1, "privacy_class": "RESTRICTED",
            })


if __name__ == "__main__": unittest.main()
