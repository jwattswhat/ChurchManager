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
    def membership(self, _membership_id):
        return {"id": 9, "group_id": 4, "church_id": 2, "privacy_class": "STANDARD",
                "start_date": date(2026, 1, 1), "end_date": None, "version": 1}
    def end_membership(self, record, end_date, user_id): self.ended = (record, end_date, user_id); return True
    def role_church_id(self, _role_id): return 2
    def role_overlaps(self, *_args): return False
    def assign_role(self, values): self.created_role = values; return 10
    def catalog(self, _church_id, _kind): return []
    def create_catalog_item(self, kind, values): self.catalog_created = (kind, values); return 12
    def set_catalog_active(self, kind, item_id, active, user_id): return (kind, item_id, active, user_id)


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

    def test_membership_end_preserves_term_and_checks_dates(self):
        service = self.service({"groups.membership.edit"})
        self.assertTrue(service.end_membership(9, date(2026, 8, 24)))
        with self.assertRaisesRegex(GroupValidationError, "cannot precede"):
            service.end_membership(9, date(2025, 12, 31))

    def test_role_must_share_church_and_stay_within_membership(self):
        service = self.service({"groups.roles.assign"})
        self.assertEqual(service.assign_role(9, 3, date(2026, 8, 24)), 10)
        service.repository.role_church_id = lambda _role_id: 3
        with self.assertRaisesRegex(GroupValidationError, "same church"):
            service.assign_role(9, 3, date(2026, 8, 24))

    def test_catalog_creation_requires_specific_permission(self):
        service = self.service({"groups.define_types"})
        self.assertEqual(service.create_catalog_item(2, "type", {
            "item_key": "care-team", "label": "Care Team", "privacy_class": "RESTRICTED",
        }), 12)
        with self.assertRaises(PermissionError):
            service.create_catalog_item(2, "role", {"item_key": "host", "label": "Host"})


if __name__ == "__main__": unittest.main()
