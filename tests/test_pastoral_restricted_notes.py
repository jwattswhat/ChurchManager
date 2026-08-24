"""Safety tests for authorized restricted pastoral-note persistence."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PastoralRestrictedNoteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "pastoral_restricted_notes.py").read_text()

    def test_authorization_precedes_repository_content_access(self):
        read = self.source.split("def read(self, note_id)", 1)[1].split("def create", 1)[0]
        self.assertLess(read.index("authorization.require"), read.index("repository.metadata"))
        self.assertLess(read.index("care_service.need"), read.index("repository.read"))

    def test_metadata_query_excludes_ciphertext(self):
        metadata = self.source.split("def metadata", 1)[1].split("def read(self, metadata", 1)[0]
        self.assertNotIn("Ciphertext", metadata)
        self.assertNotIn("AuthenticationTag", metadata)

    def test_new_note_is_bound_to_allocated_database_id(self):
        create = self.source.split("def create(self, need", 1)[1].split("def update", 1)[0]
        self.assertLess(create.index("lastrowid"), create.index("cipher.encrypt"))
        self.assertIn("self._binding(metadata)", create)

    def test_new_and_updated_notes_use_authoritative_active_key_version(self):
        create = self.source.split("def create(self, need", 1)[1].split(
            "def update", 1
        )[0]
        update = self.source.split("def update(self, metadata", 1)[1].split(
            "def _active_key_version", 1
        )[0]
        active = self.source.split("def _active_key_version", 1)[1].split(
            "def _write_ciphertext", 1
        )[0]
        self.assertIn("key_version = self._active_key_version(cursor)", create)
        self.assertIn("key_version=key_version", create)
        self.assertIn("key_version = self._active_key_version(cursor)", update)
        self.assertIn("key_version=key_version", update)
        self.assertIn("tblPastoralEncryptionState", active)
        self.assertIn("RecoveryVerified", active)
        self.assertIn("Pastoral-note recovery has not been verified", active)
        self.assertNotIn('"AES-256-GCM", 1, user_id', create)

    def test_writes_and_views_audit_without_narrative(self):
        for event in (
            "PASTORAL_NOTE_VIEWED", "PASTORAL_NOTE_CREATED", "PASTORAL_NOTE_UPDATED"
        ):
            self.assertIn(event, self.source)
        audit = self.source.split("def _audit", 1)[1]
        self.assertNotIn("plaintext", audit)
        self.assertNotIn("Ciphertext", audit)

    def test_note_update_uses_optimistic_lock(self):
        update = self.source.split("def update(self, metadata", 1)[1].split(
            "def _write_ciphertext", 1
        )[0]
        self.assertIn("WHERE ID=? AND Version=?", update)
        self.assertIn("PastoralRestrictedNoteConflictError", update)


if __name__ == "__main__":
    unittest.main()
