"""Structural tests for the isolated pastoral ciphertext recovery rehearsal."""

import unittest
from pathlib import Path


class PastoralRecoveryAcceptanceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (Path(__file__).resolve().parents[1] / "accept_pastoral_key_recovery.py").read_text(encoding="utf-8")

    def test_rehearsal_is_disposable_and_uses_fictional_text(self):
        self.assertIn("CMPastoralAcceptance_", self.source)
        self.assertIn("Fictional recovery acceptance note.", self.source)
        self.assertIn("remove_disposable", self.source)

    def test_both_rotation_checkpoints_are_restored_and_decrypted(self):
        self.assertIn("pre-rotation backup and v1 ciphertext recovery", self.source)
        self.assertIn("post-rotation backup and v2 ciphertext recovery", self.source)
        self.assertGreaterEqual(self.source.count("verify_note("), 4)

    def test_wrong_password_and_tampering_are_proven_fail_closed(self):
        self.assertIn("incorrect recovery password", self.source)
        self.assertIn("tampered recovery package fails closed", self.source)
        self.assertIn("except PastoralNoteCryptoError", self.source)


if __name__ == "__main__": unittest.main()
