"""Tests for pastoral-care service-layer authorization and validation."""

import unittest
from datetime import date, datetime
from types import SimpleNamespace

from pastoral_care_service import PastoralCareService, PastoralCareValidationError


class AuthorizationStub:
    def __init__(self, permissions=()):
        self.permissions = set(permissions)

    def has_permission(self, permission):
        return permission in self.permissions

    def require(self, permission, operation=None):
        if not self.has_permission(permission):
            raise PermissionError(operation or permission)


class RepositoryStub:
    def __init__(self, record=None, default_church_id=1):
        self.record = record
        self._default_church_id = default_church_id
        self.calls = []

    def default_church_id(self):
        self.calls.append(("default_church_id",))
        return self._default_church_id

    def church_id_for_name(self, church_name):
        self.calls.append(("church_id_for_name", church_name))
        return 2 if church_name == "Test Church" else None

    def work_list(self, assigned_user_id):
        self.calls.append(("work_list", assigned_user_id))
        return []

    def need(self, care_need_id):
        self.calls.append(("need", care_need_id))
        return self.record

    def create_need(self, values):
        self.calls.append(("create", values))
        return 11

    def assign(self, record, assignee, version, user_id):
        self.calls.append(("assign", assignee, version, user_id))
        return True

    def record_action(self, record, values):
        self.calls.append(("action", values))
        return 22

    def change_status(self, record, status, version, user_id):
        self.calls.append(("status", status, version, user_id))
        return True


class PastoralCareServiceTests(unittest.TestCase):
    def service(self, permissions, record=None):
        repository = RepositoryStub(record)
        service = PastoralCareService(
            repository, SimpleNamespace(user_id=7), AuthorizationStub(permissions)
        )
        return service, repository

    def test_assigned_work_list_is_scoped_to_current_user(self):
        service, repository = self.service({"pastoral.care.view.assigned"})
        service.work_list()
        self.assertEqual(repository.calls, [("work_list", 7)])

    def test_all_work_list_requires_separate_permission(self):
        service, repository = self.service({"pastoral.care.view.assigned"})
        with self.assertRaises(PermissionError):
            service.work_list("all")
        self.assertEqual(repository.calls, [])

    def test_assigned_user_can_open_own_record_but_not_another_users_record(self):
        service, _ = self.service(
            {"pastoral.care.view.assigned"}, {"assigned_user_id": 7}
        )
        self.assertEqual(service.need(4)["assigned_user_id"], 7)
        service, _ = self.service(
            {"pastoral.care.view.assigned"}, {"assigned_user_id": 8}
        )
        with self.assertRaises(PermissionError):
            service.need(4)

    def test_create_requires_exactly_one_subject_and_safe_fields(self):
        service, repository = self.service({"pastoral.care.create"})
        result = service.create_need({
            "church_id": 1, "person_id": 4, "category": "Hospital", "opened_date": date(2026, 8, 22),
            "safe_summary": "Follow up next week.",
        })
        self.assertEqual(result, 11)
        values = repository.calls[0][1]
        self.assertEqual(values["source"], "MANUAL")
        self.assertEqual(values["created_by_user_id"], 7)
        with self.assertRaises(PastoralCareValidationError):
            service.create_need({"church_id": 1, "person_id": 4, "family_id": 3, "category": "Other"})

    def test_create_uses_the_only_congregation_when_dialog_omits_church_id(self):
        service, repository = self.service({"pastoral.care.create"})
        self.assertEqual(service.create_need({"person_id": 4, "category": "Hospital"}), 11)
        self.assertEqual(repository.calls[0], ("default_church_id",))
        self.assertEqual(repository.calls[1][1]["church_id"], 1)

    def test_create_resolves_the_visible_church_name(self):
        service, repository = self.service({"pastoral.care.create"})
        result = service.create_need({
            "church_id": 999, "church_name": "Test Church",
            "person_id": 4, "category": "Hospital",
        })
        self.assertEqual(result, 11)
        self.assertEqual(repository.calls[0], ("church_id_for_name", "Test Church"))
        self.assertEqual(repository.calls[1][1]["church_id"], 2)

    def test_create_refuses_to_guess_when_no_single_congregation_exists(self):
        repository = RepositoryStub(default_church_id=None)
        service = PastoralCareService(
            repository, SimpleNamespace(user_id=7),
            AuthorizationStub({"pastoral.care.create"}),
        )
        with self.assertRaisesRegex(PastoralCareValidationError, "valid church ID"):
            service.create_need({"person_id": 4, "category": "Hospital"})

    def test_assigning_another_user_requires_assign_permission(self):
        service, repository = self.service(
            {"pastoral.care.create"}, {"assigned_user_id": 7}
        )
        with self.assertRaises(PermissionError):
            service.create_need({
                "church_id": 1, "person_id": 4, "assigned_user_id": 8, "category": "Other"
            })
        self.assertEqual(repository.calls, [])

    def test_record_action_requires_update_and_record_access(self):
        service, repository = self.service(
            {"pastoral.care.update", "pastoral.care.view.assigned"},
            {"assigned_user_id": 7},
        )
        action_id = service.record_action(3, {
            "action_type": "Visit", "result": "Completed",
            "action_datetime": datetime(2026, 8, 22, 10, 30),
        })
        self.assertEqual(action_id, 22)
        self.assertEqual(repository.calls[-1][1]["caregiver_user_id"], 7)

    def test_status_change_uses_dedicated_close_permission(self):
        service, repository = self.service(
            {"pastoral.care.close", "pastoral.care.view.all"},
            {"assigned_user_id": 8},
        )
        self.assertTrue(service.change_status(3, "Closed - Not Needed", 2))
        self.assertEqual(repository.calls[-1], ("status", "CLOSED_NOT_NEEDED", 2, 7))


if __name__ == "__main__":
    unittest.main()
