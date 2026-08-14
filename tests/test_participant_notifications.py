"""Tests for worship participant notification planning; no real email is sent."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from participant_notifications import (
    NotificationServiceContext, ParticipantNotificationService,
)


class Repository:
    connection = object()

    def service_context(self, service_id):
        return NotificationServiceContext(
            service_id, 2, "Reformation Lutheran Church",
            datetime(2026, 8, 16, 9, 0), "Eleventh Sunday after Pentecost",
        )

    def assigned_participants(self, service_id):
        return [
            (1, "Sarah Johnson", "Sarah@example.org", "Reader"),
            (1, "Sarah Johnson", "Sarah@example.org", "Usher"),
            (2, "John Smith", " sarah@example.org ", "Acolyte"),
            (3, "No Address", "", "Elder"),
            (4, "Bad Address", "invalid", "Organist"),
        ]


class Authorization:
    def __init__(self): self.calls = []
    def require(self, permission, operation=None): self.calls.append((permission, operation))


class Reports:
    def __init__(self, output): self.output = output; self.calls = []
    def render_worship_planning(self, *args, **kwargs):
        self.calls.append((args, kwargs)); self.output.write_bytes(b"%PDF-test"); return self.output


class Mail:
    def __init__(self): self.calls = []
    def send(self, recipients, message): self.calls.append((recipients, message)); return ("sent",)


class ParticipantNotificationTests(unittest.TestCase):
    def test_plan_groups_positions_and_flags_address_problems(self):
        service = ParticipantNotificationService(Repository(), Authorization(), Reports(Path("unused")))
        plan = service.prepare(8)
        self.assertEqual(plan.recipients[0].positions, ("Reader", "Usher"))
        self.assertEqual(
            [recipient.status for recipient in plan.recipients],
            ["Ready", "Shared address", "Missing email", "Invalid email"],
        )
        self.assertEqual(plan.sendable_addresses, ("Sarah@example.org",))
        self.assertIn("Sunday, August 16, 2026 at 9:00 AM", plan.subject)

    def test_fresh_report_is_required_and_generated_silently(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "CMWP01.pdf"
            reports = Reports(output)
            authorization = Authorization()
            service = ParticipantNotificationService(Repository(), authorization, reports)
            plan = service.generate_attachment(service.prepare(8), output)
            self.assertEqual(plan.attachment, output)
            self.assertTrue(output.is_file())
            self.assertFalse(reports.calls[0][1]["open_output"])
            self.assertIn(("reports.worship.run", "Generate participant attachment"), authorization.calls)

    def test_send_uses_only_ready_unique_addresses_and_current_attachment(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "CMWP01.pdf"; output.write_bytes(b"%PDF-test")
            mail = Mail()
            service = ParticipantNotificationService(Repository(), Authorization(), Reports(output), mail)
            plan = service.prepare(8)
            plan = type(plan)(plan.service, plan.recipients, plan.subject, plan.body, output)
            self.assertEqual(service.send(plan), ("sent",))
            self.assertEqual(mail.calls[0][0], ("Sarah@example.org",))
            self.assertEqual(mail.calls[0][1].attachments, (output,))


if __name__ == "__main__":
    unittest.main()
