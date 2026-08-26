import json
from pathlib import Path
import tempfile
import unittest

from accounting.attachment_service import (
    AttachmentPolicy, AttachmentStore, load_attachment_policy,
)
from accounting.draft_service import AccountingDraftError


class AttachmentStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "protected"
        self.store = AttachmentStore(AttachmentPolicy(
            self.root, frozenset({".pdf", ".txt"}), 100,
        ))

    def tearDown(self):
        self.temporary.cleanup()

    def source(self, name, content=b"source document"):
        path = Path(self.temporary.name) / name
        path.write_bytes(content)
        return path

    def test_add_generates_name_and_verify_detects_change(self):
        source = self.source("Offering Receipt.PDF")
        stored, original, digest, size = self.store.add(source)
        self.assertEqual(original, "Offering Receipt.PDF")
        self.assertNotIn("Offering Receipt", stored)
        self.assertEqual(Path(stored).suffix, ".pdf")
        self.assertEqual(size, len(b"source document"))
        protected = self.store.verify(stored, digest)
        protected.write_bytes(b"changed")
        with self.assertRaisesRegex(AccountingDraftError, "changed"):
            self.store.verify(stored, digest)

    def test_executable_and_oversize_files_are_rejected(self):
        with self.assertRaisesRegex(AccountingDraftError, "type"):
            self.store.add(self.source("unsafe.exe"))
        with self.assertRaisesRegex(AccountingDraftError, "size"):
            self.store.add(self.source("large.pdf", b"x" * 101))

    def test_stored_path_cannot_escape_root(self):
        with self.assertRaisesRegex(AccountingDraftError, "outside"):
            self.store.verify("../outside.pdf", "unused")

    def test_test_and_production_roots_are_selected_separately(self):
        config = {"attachments": {
            "production_root": str(self.root / "live"),
            "test_root": str(self.root / "test"),
            "allowed_extensions": ["pdf"], "maximum_megabytes": 1,
        }}
        live = load_attachment_policy(config, False)
        test = load_attachment_policy(config, True)
        self.assertNotEqual(live.root, test.root)
        self.assertEqual(test.allowed_extensions, frozenset({".pdf"}))

    def test_policy_refuses_executable_allow_list(self):
        config = {"attachments": {
            "production_root": str(self.root), "allowed_extensions": [".exe"],
            "maximum_megabytes": 1,
        }}
        with self.assertRaisesRegex(RuntimeError, "Executable"):
            load_attachment_policy(config)


if __name__ == "__main__":
    unittest.main()
