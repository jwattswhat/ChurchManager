"""Tests for ChurchManager application-user contact information."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from user_admin import UserAdministrationService


ROOT = Path(__file__).resolve().parents[1]


class Cursor:
    def __init__(self, existing=("Old Name", "old@example.org", "555-0100")):
        self.existing = existing
        self.calls = []
        self.closed = False

    def execute(self, sql, values=()):
        self.calls.append((sql, values))

    def fetchone(self):
        return self.existing

    def close(self):
        self.closed = True


class Connection:
    def __init__(self, existing=("Old Name", "old@example.org", "555-0100")):
        self.cursor_value = Cursor(existing)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.cursor_value

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class UserContactTests(unittest.TestCase):
    def test_migration_adds_optional_fields_with_approved_lengths(self):
        migration = (ROOT / "migrations" / "063_add_user_contact_information.sql").read_text(encoding="utf-8")
        self.assertIn("Email varchar(254) NULL", migration)
        self.assertIn("Phone varchar(50) NULL", migration)

    def test_contact_normalization_preserves_readable_values_and_nulls(self):
        self.assertEqual(
            UserAdministrationService.normalize_contact(
                "  Sarah   Johnson ", " sarah@example.org ", " (555)  0100 ext. 12 ",
            ),
            ("Sarah Johnson", "sarah@example.org", "(555) 0100 ext. 12"),
        )
        self.assertEqual(
            UserAdministrationService.normalize_contact("Sarah Johnson", "", " "),
            ("Sarah Johnson", None, None),
        )
        self.assertEqual(
            UserAdministrationService.normalize_contact("Sarah Johnson", None, "9999999999"),
            ("Sarah Johnson", None, "9999999999"),
        )

    def test_invalid_contact_is_rejected_before_database_access(self):
        for email, phone in (("not an email", None), (None, "abc"), ("x" * 255, None)):
            with self.subTest(email=email, phone=phone):
                with self.assertRaises(ValueError):
                    UserAdministrationService.normalize_contact("Sarah", email, phone)

    def test_update_is_atomic_and_audit_contains_field_names_not_values(self):
        connection = Connection()
        service = UserAdministrationService(connection, acting_user_id=7)
        changed = service.update_contact(4, "Sarah Johnson", "sarah@example.org", "555-0199")
        self.assertTrue(changed)
        self.assertEqual(connection.commits, 1)
        self.assertEqual(connection.rollbacks, 0)
        audit_sql, audit_values = connection.cursor_value.calls[-1]
        self.assertIn("USER_CONTACT_UPDATED", audit_sql)
        audit_json = audit_values[-1]
        self.assertEqual(
            json.loads(audit_json),
            {"changed_fields": ["DisplayName", "Email", "Phone"]},
        )
        self.assertNotIn("sarah@example.org", audit_json)
        self.assertNotIn("555-0199", audit_json)

    def test_unchanged_contact_releases_transaction_without_audit(self):
        connection = Connection()
        service = UserAdministrationService(connection, acting_user_id=7)
        self.assertFalse(service.update_contact(4, "Old Name", "old@example.org", "555-0100"))
        self.assertEqual(connection.commits, 0)
        self.assertEqual(connection.rollbacks, 1)
        self.assertEqual(len(connection.cursor_value.calls), 1)

    def test_user_administration_has_new_and_edit_contact_controls(self):
        source = (ROOT / "user_admin.py").read_text(encoding="utf-8")
        self.assertIn('("Edit Details", self.on_contact)', source)
        self.assertIn('("Send Welcome", self.on_welcome)', source)
        self.assertIn('grid.Add(wx.StaticText(self, label="Email"))', source)
        self.assertIn('grid.Add(wx.StaticText(self, label="Phone"))', source)
        self.assertIn('JSForm.phone_display(user.phone)', source)
        self.assertIn('JSForm.phone_storage(phone)', source)


if __name__ == "__main__":
    unittest.main()
