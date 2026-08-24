"""Structural acceptance tests for custom profile fields and controlled tags."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "112_add_custom_profile_fields.sql"


class CustomProfileFieldMigrationTests(unittest.TestCase):
    def setUp(self):
        self.sql = MIGRATION.read_text(encoding="utf-8")

    def test_normalized_person_family_values_and_tags_are_present(self):
        for table in (
            "tblCustomFieldDefinition", "tblCustomFieldOption",
            "tblPersonCustomFieldValue", "tblFamilyCustomFieldValue",
            "tblPersonCustomFieldOptionValue", "tblFamilyCustomFieldOptionValue",
            "tblProfileTagDefinition", "tblPersonTag", "tblFamilyTag",
            "tblProfileCustomAuditEvent",
        ):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", self.sql)

    def test_entity_types_privacy_and_lifecycle_are_bounded(self):
        self.assertIn("EntityType IN ('PERSON','FAMILY')", self.sql)
        self.assertIn("LifecycleStatus IN ('DRAFT','ACTIVE','RETIRED')", self.sql)
        self.assertIn("PrivacyClass IN ('STANDARD','RESTRICTED')", self.sql)
        self.assertNotIn("DIRECTORY_APPROVED", self.sql)

    def test_limits_and_normalized_multiple_choice_storage_are_enforced(self):
        self.assertIn("DataType='SHORT_TEXT' AND MaxLength BETWEEN 1 AND 255", self.sql)
        self.assertIn("DataType='LONG_TEXT' AND MaxLength BETWEEN 1 AND 2000", self.sql)
        self.assertIn("PRIMARY KEY (PersonID,DefinitionID,OptionID)", self.sql)
        self.assertIn("PRIMARY KEY (FamilyID,DefinitionID,OptionID)", self.sql)

    def test_permission_catalog_matches_approved_contract(self):
        for permission in (
            "profiles.custom_fields.define", "profiles.custom_fields.view",
            "profiles.custom_fields.edit", "profiles.custom_fields.view_restricted",
            "profiles.custom_fields.edit_restricted", "profiles.tags.define",
            "profiles.tags.view", "profiles.tags.assign",
        ):
            self.assertIn(permission, self.sql)

    def test_new_field_dialog_uses_supported_checkbox_api(self):
        source = (ROOT / "custom_profile_admin_dialog.py").read_text(encoding="utf-8")
        self.assertIn("self.confirm = wx.CheckBox", source)
        self.assertNotIn("self.confirm.Wrap", source)


if __name__ == "__main__":
    unittest.main()
