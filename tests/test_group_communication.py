"""Tests for privacy-safe Group recipient review and delivery."""

from datetime import date
from types import SimpleNamespace
import unittest

import JSForm

from group_communication import GroupCommunicationService


class Authorization:
    def __init__(self, permissions): self.permissions = set(permissions)
    def require(self, permission, _operation=None):
        if permission not in self.permissions: raise PermissionError(permission)


class Repository:
    def __init__(self): self.audits = []
    def group(self, _group_id): return (4, "Elders", "STANDARD", 1)
    def members(self, _group_id, _effective):
        return [(10, "Alex Able", "Chair"), (11, "Bailey Baker", "Secretary"),
                (12, "Casey Carter", "Member")]
    def email_facts(self, person_id):
        return {10: [("alex@example.org", 0)], 11: [("private@example.org", 1)], 12: []}[person_id]
    def audit(self, user_id, action, group_id, summary): self.audits.append((user_id, action, group_id, summary))


class Mail:
    def send(self, recipients, message):
        self.sent = (recipients, message)
        return [JSForm.DeliveryResult(item, True) for item in recipients]


class GroupCommunicationTests(unittest.TestCase):
    def service(self, permissions, mail=None):
        repository = Repository()
        return GroupCommunicationService(repository, SimpleNamespace(user_id=7), Authorization(permissions), mail), repository

    def test_review_never_displays_unlisted_address(self):
        service, repository = self.service({"groups.communication.prepare"})
        plan = service.prepare(4, date(2026, 8, 24))
        self.assertEqual([item.status for item in plan.recipients], ["Ready", "Unlisted email", "Missing email"])
        self.assertEqual(plan.recipients[1].email, "")
        self.assertNotIn("private@example.org", repr(plan))
        self.assertEqual(repository.audits[-1][3]["recipient_count"], 1)

    def test_send_revalidates_and_audits_counts_only(self):
        mail = Mail(); permissions = {"groups.communication.prepare", "groups.communication.send"}
        service, repository = self.service(permissions, mail)
        plan = service.prepare(4, date(2026, 8, 24))
        results = service.send(plan, "Meeting", "Please attend.")
        self.assertEqual(len(results), 1); self.assertEqual(mail.sent[0], ("alex@example.org",))
        audit = repository.audits[-1]
        self.assertEqual(audit[1], "GROUP_COMMUNICATION_SENT")
        self.assertNotIn("alex@example.org", repr(audit)); self.assertNotIn("Please attend", repr(audit))

    def test_disabled_and_restricted_groups_fail_closed(self):
        service, repository = self.service({"groups.communication.prepare"})
        repository.group = lambda _group_id: (4, "Care Team", "RESTRICTED", 1)
        with self.assertRaises(PermissionError): service.prepare(4)
        repository.group = lambda _group_id: (4, "Elders", "STANDARD", 0)
        with self.assertRaisesRegex(ValueError, "not enabled"): service.prepare(4)


if __name__ == "__main__": unittest.main()
