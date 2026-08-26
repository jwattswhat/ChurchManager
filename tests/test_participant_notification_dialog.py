"""Static safety checks for the review-first notification screen."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ParticipantNotificationDialogTests(unittest.TestCase):
    def test_main_menu_uses_review_screen_not_legacy_immediate_send(self):
        source = (ROOT / "cm.py").read_text(encoding="utf-8-sig")
        self.assertIn("show_participant_notifications(", source)
        self.assertNotIn("fnSchedule.notifyviaeMail", source)

    def test_review_screen_exposes_required_review_and_confirmation_controls(self):
        source = (ROOT / "participant_notification_dialog.py").read_text(encoding="utf-8")
        for label in (
            "Participant", "Position(s)", "Email", "Status", "Subject", "Message",
            "Generate Current Report", "Preview Report", "Confirm Participant Notification",
        ):
            self.assertIn(label, source)
        self.assertIn("wx.YES_NO | wx.NO_DEFAULT", source)
        self.assertIn("self.send.Disable()", source)


if __name__ == "__main__":
    unittest.main()
