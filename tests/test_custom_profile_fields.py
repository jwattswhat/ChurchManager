"""Structural acceptance tests for custom profile fields and controlled tags."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "112_add_custom_profile_fields.sql"
REPORT_MIGRATION = ROOT / "migrations" / "113_add_custom_profile_report.sql"


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
        for policy in ("searchable", "report_allowed", "export_allowed"):
            self.assertIn(f'("{policy}"', source)

    def test_definition_catalog_opens_complete_lifecycle_aware_record(self):
        source = (ROOT / "custom_profile_admin_dialog.py").read_text(encoding="utf-8")
        self.assertIn('("Open Field...", self.open_field)', source)
        self.assertIn("wx.EVT_LIST_ITEM_ACTIVATED, self.open_field", source)
        self.assertIn("Draft - all definition settings may be edited", source)
        self.assertIn("Retired - this historical definition is read-only", source)
        for field in ("field_key", "data_type", "privacy_class", "display_order",
                      "required", "searchable", "report_allowed", "export_allowed"):
            self.assertIn(f'"{field}"', source)

    def test_search_screen_is_routed_and_permission_guarded(self):
        form = (ROOT / "Menus" / "main.menu.json").read_text(encoding="utf-8")
        router = (ROOT / "main_menu.py").read_text(encoding="utf-8")
        permissions = (ROOT / "permission_catalog.py").read_text(encoding="utf-8")
        self.assertIn('churchmanager.custom_profile_search', form)
        self.assertIn('"lblCustomProfileSearch"', router)
        self.assertIn('"lblCustomProfileSearch": "profiles.custom_fields.view"', permissions)

    def test_approved_report_uses_safe_view_and_stable_field_identity(self):
        sql = REPORT_MIGRATION.read_text(encoding="utf-8")
        self.assertIn("CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_custom_profile_value", sql)
        self.assertIn("d.FieldKey", sql)
        self.assertIn("d.ReportAllowed=1", sql)
        self.assertIn("d.LifecycleStatus IN ('ACTIVE','RETIRED')", sql)
        self.assertIn("GROUP_CONCAT(o.Label", sql)
        self.assertIn("'CMMB11','Membership - Custom Profile Listing'", sql)

    def test_custom_profile_report_filters_restricted_values_without_permission(self):
        source = (ROOT / "visual_reports" / "tabular_dataset.py").read_text(encoding="utf-8")
        self.assertIn('view == "rpt_custom_profile_value"', source)
        self.assertIn('has_permission("profiles.custom_fields.view_restricted")', source)
        self.assertIn("where.append(\"PrivacyClass='STANDARD'\")", source)


if __name__ == "__main__":
    unittest.main()
