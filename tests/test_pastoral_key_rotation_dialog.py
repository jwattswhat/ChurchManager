"""Protect the administrator-facing pastoral key-rotation workflow."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PastoralKeyRotationDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "backup_restore_dialog.py").read_text(encoding="utf-8")

    def test_rotation_is_master_administered_and_requires_password(self):
        handler = self.source.split("def on_rotate_pastoral_key", 1)[1].split(
            "def record_success", 1
        )[0]
        self.assertIn('"pastoral.care.admin"', handler)
        self.assertIn("wx.PasswordEntryDialog", handler)
        self.assertIn("wx.NO_DEFAULT", handler)

    def test_rotation_uses_distinct_before_and_verified_backups(self):
        handler = self.source.split("def on_rotate_pastoral_key", 1)[1].split(
            "def record_success", 1
        )[0]
        self.assertIn('create_named_backup("Before")', handler)
        self.assertIn('create_named_backup("Verified")', handler)
        self.assertIn("PastoralKeyRotationService", handler)

    def test_rotation_control_is_disabled_until_recovery_is_configured(self):
        self.assertIn(
            "self.rotation_button.Enable(self.pastoral_recovery.configured)",
            self.source,
        )
        self.assertIn("self.rotation_button.Enable(True)", self.source)


if __name__ == "__main__":
    unittest.main()
