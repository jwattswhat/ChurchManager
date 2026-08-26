"""Authorization and validation tests for ChurchManager custom profiles."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
import unittest

from custom_profile_fields import CustomProfileFieldService, CustomProfileValidationError


class Authorization:
    def __init__(self, permissions): self.permissions = set(permissions)
    def has_permission(self, name): return name in self.permissions
    def require(self, name, _operation):
        if name not in self.permissions: raise PermissionError(name)


class Repository:
    def __init__(self):
        self.created = None; self.saved = None; self.tag_created = None
        self.definition_rows = [{
            "id": 4, "church_id": 2, "entity_type": "PERSON", "field_key": "parking_space",
            "label": "Parking Space", "help_text": None, "section_label": "Additional Information",
            "data_type": "INTEGER", "lifecycle_status": "ACTIVE", "privacy_class": "STANDARD",
            "display_order": 10, "required": 0, "searchable": 1, "report_allowed": 1,
            "export_allowed": 1, "max_length": None, "minimum_value": 1,
            "maximum_value": 999, "decimal_places": 0, "version": 1,
        }]
    def definitions(self, *_args): return self.definition_rows
    def definition_key_exists(self, *_args): return False
    def create_definition(self, item): self.created = item; return 4
    def definition(self, _definition_id): return self.definition_rows[0]
    def active_definition_count(self, *_args): return 0
    def options(self, *_args, **_kwargs): return []
    def set_definition_status(self, *_args): return True
    def update_definition(self, current, item): self.updated = (current, item); return True
    def create_option(self, *_args): return 5
    def profile_church_id(self, *_args): return 2
    def profile_definitions(self, *_args): return self.definition_rows
    def profile_values(self, *_args): return {"parking_space": 12}
    def save_profile_values(self, entity, profile_id, changes, user_id):
        self.saved = (entity, profile_id, changes, user_id); return True
    def tags(self, *_args): return []
    def tag(self, _tag_id):
        return {"id": 8, "church_id": 2, "entity_type": "PERSON", "privacy_class": "STANDARD", "active": 1}
    def tag_key_exists(self, *_args): return False
    def create_tag(self, item): self.tag_created = item; return 8
    def set_tag_active(self, *_args): return True
    def profile_tag_count(self, *_args): return 0
    def assigned_tag_ids(self, *_args): return {8}
    def set_tag(self, *_args): return True
    def search_profiles(self, definition, operator, value, limit=500):
        self.search = (definition, operator, value, limit)
        return [{"id": 10, "display_name": "Agricola, Agnes"}]


class CustomProfileServiceTests(unittest.TestCase):
    def service(self, permissions):
        return CustomProfileFieldService(
            Repository(), SimpleNamespace(user_id=7), Authorization(permissions),
        )

    def test_creation_requires_permission_and_boundary_confirmation(self):
        values = {"church_id": 2, "entity_type": "PERSON", "field_key": "parking_space",
                  "label": "Parking Space", "data_type": "INTEGER"}
        with self.assertRaises(PermissionError): self.service(set()).create_definition(values)
        with self.assertRaisesRegex(CustomProfileValidationError, "Confirm"):
            self.service({"profiles.custom_fields.define"}).create_definition(values)
        values["content_boundary_confirmed"] = True
        service = self.service({"profiles.custom_fields.define"})
        self.assertEqual(service.create_definition(values), 4)
        self.assertEqual(service.repository.created["user_id"], 7)

    def test_profile_values_are_typed_and_same_church(self):
        service = self.service({"profiles.custom_fields.view", "profiles.custom_fields.edit"})
        descriptors, values = service.profile(2, "person", 10)
        self.assertEqual(descriptors[0].key, "parking_space")
        self.assertEqual(values["parking_space"], 12)
        service.save_profile_values(2, "PERSON", 10, {"parking_space": "17"})
        saved = service.repository.saved[2][4][1]
        self.assertEqual(saved, 17)
        service.repository.profile_church_id = lambda *_args: 3
        with self.assertRaisesRegex(CustomProfileValidationError, "unavailable"):
            service.profile(2, "PERSON", 10)

    def test_draft_definition_can_change_structure(self):
        service = self.service({"profiles.custom_fields.define"})
        service.repository.definition_rows[0]["lifecycle_status"] = "DRAFT"
        self.assertTrue(service.update_definition(4, {
            "field_key": "parking_area", "label": "Parking Area", "data_type": "SHORT_TEXT",
        }))
        self.assertEqual(service.repository.updated[1]["field_key"], "parking_area")

    def test_active_definition_allows_safe_edits_but_locks_structure(self):
        service = self.service({"profiles.custom_fields.define"})
        self.assertTrue(service.update_definition(4, {"label": "Assigned Parking", "searchable": False}))
        self.assertEqual(service.repository.updated[1]["label"], "Assigned Parking")
        with self.assertRaisesRegex(CustomProfileValidationError, "locked"):
            service.update_definition(4, {"data_type": "SHORT_TEXT"})

    def test_retired_definition_is_read_only(self):
        service = self.service({"profiles.custom_fields.define"})
        service.repository.definition_rows[0]["lifecycle_status"] = "RETIRED"
        with self.assertRaisesRegex(CustomProfileValidationError, "read-only"):
            service.update_definition(4, {"label": "Changed"})

    def test_restricted_edit_requires_restricted_permission(self):
        service = self.service({"profiles.custom_fields.view", "profiles.custom_fields.edit",
                                "profiles.custom_fields.view_restricted"})
        service.repository.definition_rows[0]["privacy_class"] = "RESTRICTED"
        with self.assertRaises(PermissionError):
            service.save_profile_values(2, "PERSON", 10, {"parking_space": 18})

    def test_tag_definition_validates_color_and_stable_key(self):
        service = self.service({"profiles.tags.define"})
        values = {"church_id": 2, "entity_type": "FAMILY", "tag_key": "snowbird",
                  "label": "Snowbird", "display_color": "blue"}
        with self.assertRaisesRegex(CustomProfileValidationError, "#RRGGBB"):
            service.create_tag(values)
        values["display_color"] = "#2255AA"
        self.assertEqual(service.create_tag(values), 8)
        self.assertEqual(service.repository.tag_created["entity_type"], "FAMILY")

    def test_limits_are_enforced(self):
        service = self.service({"profiles.custom_fields.define", "profiles.tags.assign"})
        service.repository.definition_rows[0]["lifecycle_status"] = "DRAFT"
        service.repository.active_definition_count = lambda *_args: 25
        with self.assertRaisesRegex(CustomProfileValidationError, "25"):
            service.activate_definition(4)
        service.repository.profile_tag_count = lambda *_args: 25
        with self.assertRaisesRegex(CustomProfileValidationError, "25"):
            service.assign_tag(2, "PERSON", 10, 8, True)

    def test_profile_tags_preserve_assigned_catalog_identity(self):
        service = self.service({"profiles.tags.view"})
        service.repository.tags = lambda *_args, **_kwargs: [
            {"id": 8, "active": 0, "privacy_class": "STANDARD"},
            {"id": 9, "active": 1, "privacy_class": "STANDARD"},
        ]
        tags, assigned = service.profile_tags(2, "PERSON", 10)
        self.assertEqual([item["id"] for item in tags], [8, 9])
        self.assertEqual(assigned, {8})

    def test_search_is_limited_to_active_searchable_authorized_fields(self):
        service = self.service({"profiles.custom_fields.view"})
        rows = service.search_profiles(2, "PERSON", 4, "GREATER_THAN", "12")
        self.assertEqual(rows[0]["id"], 10)
        self.assertEqual(service.repository.search[1:3], ("GREATER_THAN", 12))
        service.repository.definition_rows[0]["searchable"] = 0
        with self.assertRaisesRegex(CustomProfileValidationError, "unavailable"):
            service.search_profiles(2, "PERSON", 4, "EQUALS", "12")


if __name__ == "__main__": unittest.main()
