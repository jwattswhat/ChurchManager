"""Tests for stable-key custom profile import and export."""

import csv
import json
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest

from custom_profile_exchange import CustomProfileExchangeService, FORMAT
from custom_profile_fields import CustomProfileValidationError


class Authorization:
    def __init__(self, permissions): self.permissions = set(permissions)
    def has_permission(self, name): return name in self.permissions
    def require(self, name, _operation):
        if name not in self.permissions: raise PermissionError(name)


class Repository:
    def __init__(self): self.saved = None; self.audit = None
    def profile_catalog(self, _church, entity):
        if entity == "PERSON":
            return [{"id": 11, "first_name": "Agnes", "middle_name": "", "last_name": "Agricola", "display_name": "Agricola, Agnes"}]
        return [{"id": 21, "family_name": "Agricola", "display_name": "Agricola"}]
    def profile_values(self, _entity, _profile, _definitions): return {"parking_space": 17, "ministry": "choir"}
    def options(self, definition_id, active_only=False):
        return [{"id": 8, "option_key": "choir", "label": "Choir", "display_order": 0, "active": 1}] if definition_id == 5 else []
    def audit_exchange(self, *values): self.audit = values
    def save_profile_value_batch(self, entity, profiles, user_id): self.saved = (entity, profiles, user_id); return True


class Fields:
    def __init__(self, permissions):
        self.repository = Repository(); self.session = SimpleNamespace(user_id=7)
        self.authorization = Authorization(permissions)
        self.rows = [
            {"id": 4, "church_id": 2, "entity_type": "PERSON", "field_key": "parking_space",
             "label": "Parking Space", "help_text": None, "section_label": "Additional Information",
             "data_type": "INTEGER", "lifecycle_status": "ACTIVE", "privacy_class": "STANDARD",
             "display_order": 1, "required": 0, "searchable": 1, "report_allowed": 1,
             "export_allowed": 1, "max_length": None, "minimum_value": None,
             "maximum_value": None, "decimal_places": 0},
            {"id": 5, "church_id": 2, "entity_type": "PERSON", "field_key": "ministry",
             "label": "Ministry", "help_text": None, "section_label": "Additional Information",
             "data_type": "SINGLE_CHOICE", "lifecycle_status": "ACTIVE", "privacy_class": "RESTRICTED",
             "display_order": 2, "required": 0, "searchable": 0, "report_allowed": 0,
             "export_allowed": 1, "max_length": None, "minimum_value": None,
             "maximum_value": None, "decimal_places": 0},
        ]
    def definitions(self, _church, _entity):
        restricted = self.authorization.has_permission("profiles.custom_fields.view_restricted")
        return [row for row in self.rows if row["privacy_class"] == "STANDARD" or restricted]


class CustomProfileExchangeTests(unittest.TestCase):
    def service(self, *permissions): return CustomProfileExchangeService(Fields(set(permissions)))

    def test_export_writes_stable_keys_and_manifest_without_restricted_by_default(self):
        service = self.service("profiles.custom_fields.view")
        with TemporaryDirectory() as folder:
            target = Path(folder) / "profiles.csv"
            count, manifest = service.export(2, "PERSON", target)
            self.assertEqual(count, 1)
            with target.open("r", encoding="utf-8-sig", newline="") as stream:
                row = next(csv.DictReader(stream))
            self.assertEqual(row["custom.parking_space"], "17")
            self.assertNotIn("custom.ministry", row)
            metadata = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(metadata["format"], FORMAT)
            self.assertEqual(metadata["fields"][0]["stable_key"], "parking_space")

    def test_restricted_export_requires_explicit_permission(self):
        service = self.service("profiles.custom_fields.view")
        with TemporaryDirectory() as folder:
            with self.assertRaises(PermissionError):
                service.export(2, "PERSON", Path(folder) / "profiles.csv", include_restricted=True)

    def test_import_previews_stable_keys_then_commits_one_batch(self):
        service = self.service("profiles.custom_fields.view", "profiles.custom_fields.edit")
        with TemporaryDirectory() as folder:
            source = Path(folder) / "profiles.csv"
            source.write_text("First Name,Middle Name,Last Name,custom.parking_space\nAgnes,,Agricola,25\n", encoding="utf-8")
            preview = service.preview_import(2, "PERSON", source)
            self.assertFalse(preview[0].errors); self.assertEqual(preview[0].profile_id, 11)
            self.assertEqual(preview[0].changes[4][1], 25)
            self.assertEqual(service.commit_import(2, "PERSON", source, preview), 1)
            self.assertEqual(service.repository.saved[0], "PERSON")
            self.assertEqual(service.repository.saved[1][0][0], 11)

    def test_import_rejects_unknown_field_without_writing(self):
        service = self.service("profiles.custom_fields.view", "profiles.custom_fields.edit")
        with TemporaryDirectory() as folder:
            source = Path(folder) / "profiles.csv"
            source.write_text("First Name,Middle Name,Last Name,custom.unknown\nAgnes,,Agricola,x\n", encoding="utf-8")
            with self.assertRaisesRegex(CustomProfileValidationError, "Unknown or inactive"):
                service.preview_import(2, "PERSON", source)
            self.assertIsNone(service.repository.saved)


if __name__ == "__main__": unittest.main()
