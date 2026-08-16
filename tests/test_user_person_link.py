"""Tests for optional application-user links to congregation people."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from participant_notifications import configured_mail_service
from user_admin import UserAdministrationService


ROOT = Path(__file__).resolve().parents[1]


class SequenceCursor:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.closed = False

    def execute(self, sql, values=()):
        self.calls.append((sql, values))

    def fetchone(self):
        return self.responses.pop(0)

    def close(self):
        self.closed = True


class Connection:
    def __init__(self, responses):
        self.cursor_value = SequenceCursor(responses)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.cursor_value

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class Mail:
    def __init__(self, succeeded=True):
        self.succeeded = succeeded
        self.calls = []

    def send(self, recipients, message):
        self.calls.append((recipients, message))
        return (SimpleNamespace(succeeded=self.succeeded),)


class FailingMail:
    def send(self, _recipients, _message):
        raise OSError("SMTP unavailable")


class UserPersonLinkTests(unittest.TestCase):
    def test_migration_adds_optional_unique_safe_foreign_key(self):
        migration = (ROOT / "migrations" / "070_link_users_to_people.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("PersonID int NULL", migration)
        self.assertIn("UNIQUE (PersonID)", migration)
        self.assertIn("REFERENCES tblPerson(ID) ON DELETE SET NULL", migration)
        self.assertIn("Duplicate tblUser.PersonID", migration)
        self.assertIn("Invalid tblUser.PersonID", migration)

    def test_link_change_is_atomic_unique_and_safely_audited(self):
        connection = Connection([
            ("Old Name", "old@example.org", "555-0100", None),
            (1,),
            (0,),
        ])
        service = UserAdministrationService(connection, acting_user_id=7)
        self.assertTrue(
            service.update_contact(
                4, "Old Name", "old@example.org", "555-0100", person_id=23,
            )
        )
        self.assertEqual(connection.commits, 1)
        update = next(call for call in connection.cursor_value.calls if call[0].startswith("UPDATE tblUser"))
        self.assertIn("PersonID=?", update[0])
        self.assertEqual(update[1][-2:], (23, 4))
        audit = connection.cursor_value.calls[-1]
        self.assertIn("USER_PERSON_LINK_CHANGED", audit[0])
        self.assertEqual(json.loads(audit[1][-1]), {"linked": True})
        self.assertNotIn("23", audit[1][-1])

    def test_person_already_linked_to_another_user_is_rejected(self):
        connection = Connection([
            ("Old Name", "old@example.org", "555-0100", None),
            (1,),
            (1,),
        ])
        service = UserAdministrationService(connection, acting_user_id=7)
        with self.assertRaisesRegex(ValueError, "already linked"):
            service.update_contact(
                4, "Old Name", "old@example.org", "555-0100", person_id=23,
            )
        self.assertEqual(connection.commits, 0)
        self.assertEqual(connection.rollbacks, 1)
        self.assertFalse(any(sql.startswith("UPDATE tblUser") for sql, _ in connection.cursor_value.calls))

    def test_welcome_email_contains_instructions_but_never_a_password(self):
        connection = Connection([("sarah", "Sarah Johnson", "sarah@example.org")])
        mail = Mail()
        service = UserAdministrationService(connection, acting_user_id=7)
        results = service.send_welcome_email(4, mail)
        self.assertTrue(results[0].succeeded)
        recipients, message = mail.calls[0]
        self.assertEqual(recipients, ("sarah@example.org",))
        self.assertIn("Username: sarah", message.body)
        self.assertIn("must be changed", message.body)
        self.assertIn("separate channel", message.body)
        self.assertNotIn("Secret123", message.body)
        audit_sql, audit_values = connection.cursor_value.calls[-1]
        self.assertIn("USER_WELCOME_EMAIL_SENT", audit_values)
        self.assertNotIn("sarah@example.org", repr(audit_values))
        self.assertNotIn("sarah", repr(audit_values))
        self.assertEqual(connection.commits, 1)

    def test_failed_welcome_delivery_keeps_account_and_records_safe_failure(self):
        connection = Connection([("sarah", "Sarah Johnson", "sarah@example.org")])
        service = UserAdministrationService(connection, acting_user_id=7)
        with self.assertRaisesRegex(RuntimeError, "account remains available"):
            service.send_welcome_email(4, Mail(succeeded=False))
        self.assertEqual(connection.commits, 1)
        self.assertIn("USER_WELCOME_EMAIL_FAILED", connection.cursor_value.calls[-1][1])
        self.assertNotIn("sarah@example.org", repr(connection.cursor_value.calls[-1][1]))

    def test_welcome_transport_exception_is_safely_audited(self):
        connection = Connection([("sarah", "Sarah Johnson", "sarah@example.org")])
        service = UserAdministrationService(connection, acting_user_id=7)
        with self.assertRaisesRegex(RuntimeError, "account remains available"):
            service.send_welcome_email(4, FailingMail())
        self.assertEqual(connection.commits, 1)
        self.assertIn("USER_WELCOME_EMAIL_FAILED", connection.cursor_value.calls[-1][1])
        self.assertNotIn("SMTP unavailable", repr(connection.cursor_value.calls[-1][1]))

    def test_user_administration_exposes_optional_person_and_welcome_controls(self):
        source = (ROOT / "user_admin.py").read_text(encoding="utf-8")
        self.assertIn('label="Linked person"', source)
        self.assertIn("Not linked to a congregation person", source)
        self.assertIn("def list_available_people", source)
        self.assertIn("def send_welcome_email", source)
        self.assertIn("temporary password is not included", source)

    def test_test_mode_mail_factory_cannot_send(self):
        mail = configured_mail_service(test_mode=True)
        with self.assertRaisesRegex(RuntimeError, "disabled.*TEST MODE"):
            mail.send(("fictional@example.org",), object())

    def test_application_passes_test_mode_to_every_mail_entry_point(self):
        main_source = (ROOT / "cm.py").read_text(encoding="utf-8")
        participant_source = (ROOT / "participant_notification_dialog.py").read_text(
            encoding="utf-8"
        )
        user_source = (ROOT / "user_admin.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(main_source.count("test_mode=context.test_mode"), 2)
        self.assertIn("configured_mail_service(test_mode=test_mode)", participant_source)
        self.assertIn("configured_mail_service(test_mode=test_mode)", user_source)


if __name__ == "__main__":
    unittest.main()
