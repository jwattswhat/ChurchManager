"""Protect the public Pastoral Care and recovery guidance."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PastoralCareDocumentationTests(unittest.TestCase):
    def test_user_guide_documents_safe_workflow_and_handoffs(self):
        guide = (ROOT / "Documentation" / "ChurchManager.UserGuide.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## 7. Pastoral Care", guide)
        self.assertIn("Assigned to Me", guide)
        self.assertIn("does not copy an attendance-event note", guide)
        self.assertIn("the wording\nof a prayer request", guide)
        self.assertIn("Neither report includes\nrestricted notes", guide)

    def test_user_guide_documents_restricted_note_gate_and_recovery_pair(self):
        guide = (ROOT / "Documentation" / "ChurchManager.UserGuide.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Restricted narrative entry is not enabled", guide)
        self.assertIn("key rotation", guide)
        self.assertIn("two matched files", guide)
        self.assertIn("protected pastoral\nrecovery sidecar", guide)
        self.assertIn("ChurchManager does not store that password", guide)

    def test_roadmap_keeps_restricted_notes_gated(self):
        roadmap = (ROOT / "Documentation" / "ChurchManager.FixList.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("safe scheduling release complete; restricted notes gated", roadmap)
        self.assertIn("actual-ciphertext\n  replacement-machine recovery", roadmap)

    def test_approved_spec_defines_fail_closed_key_rotation(self):
        specification = (
            ROOT / "Documentation" / "ChurchManager.PastoralCare.Specification.md"
        ).read_text(encoding="utf-8")
        self.assertIn("### 4.4 Key rotation contract", specification)
        self.assertIn("active key version", specification)
        self.assertIn("complete pre-rotation SQL backup", specification)
        self.assertIn("inside one database\n   transaction", specification)
        self.assertIn("are not deleted\nautomatically", specification)
        self.assertIn("must not become active implicitly", specification)


if __name__ == "__main__":
    unittest.main()
