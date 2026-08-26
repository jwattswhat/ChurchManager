"""Contract tests for the protected pastoral-care database foundation."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "096_add_pastoral_care_foundation.sql"
POSITIVE_CHURCH_IDS = ROOT / "migrations" / "097_normalize_positive_church_ids.sql"
ENCRYPTION_STATE = ROOT / "migrations" / "105_add_pastoral_encryption_state.sql"


class PastoralCareFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MIGRATION.read_text(encoding="utf-8")

    def test_separates_need_action_and_restricted_note(self):
        self.assertIn("CREATE TABLE IF NOT EXISTS tblPastoralCareNeed", self.source)
        self.assertIn("CREATE TABLE IF NOT EXISTS tblPastoralCareAction", self.source)
        self.assertIn("CREATE TABLE IF NOT EXISTS tblPastoralRestrictedNote", self.source)

    def test_restricted_note_has_ciphertext_only(self):
        note = self.source.split("CREATE TABLE IF NOT EXISTS tblPastoralRestrictedNote", 1)[1]
        note = note.split("CREATE TABLE", 1)[0]
        for field in ("Ciphertext", "Nonce", "AuthenticationTag", "Algorithm", "KeyVersion"):
            self.assertIn(field, note)
        self.assertNotIn("Plaintext", note)
        self.assertNotIn("Narrative", note)

    def test_all_permissions_are_sensitive_and_master_only_by_default(self):
        expected = {
            "pastoral.care.view.assigned", "pastoral.care.view.all", "pastoral.care.create",
            "pastoral.care.assign", "pastoral.care.update", "pastoral.care.close",
            "pastoral.notes.view", "pastoral.notes.edit", "pastoral.care.report",
            "pastoral.care.admin",
        }
        for permission in expected:
            self.assertIn(f"('{permission}'", self.source)
        self.assertIn("WHERE r.Name='Master Administrator'", self.source)

    def test_recurrence_and_minimum_necessary_fields_are_bounded(self):
        self.assertIn("ScheduleText varchar(255)", self.source)
        self.assertIn("ScheduleRule varchar(255)", self.source)
        self.assertIn("SafeSummary varchar(500)", self.source)
        self.assertIn("SafeOutcome varchar(500)", self.source)

    def test_church_identifiers_are_normalized_to_positive_keys(self):
        source = POSITIVE_CHURCH_IDS.read_text(encoding="utf-8")
        self.assertIn("WHERE ID=0", source)
        self.assertIn("SET ChurchID=? WHERE ChurchID=0", source)
        self.assertIn("ALTER COLUMN ChurchID DROP DEFAULT", source)
        self.assertNotIn("CHECK (ID > 0)", source)

    def test_encryption_state_has_one_positive_active_version(self):
        source = ENCRYPTION_STATE.read_text(encoding="utf-8")
        self.assertIn("CREATE TABLE IF NOT EXISTS tblPastoralEncryptionState", source)
        self.assertIn("ActiveKeyVersion", source)
        self.assertIn("CHECK (ID=1)", source)
        self.assertIn("CHECK (ActiveKeyVersion > 0)", source)
        self.assertIn("VALUES (1, 1, 0)", source)


if __name__ == "__main__":
    unittest.main()
