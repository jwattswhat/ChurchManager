"""ChurchManager integration checks for JSForm diagnostic reporting."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch
from pathlib import Path

import churchmanager_error_support as support
from main_menu import MENU_CONTROLS


class ChurchManagerErrorSupportTests(unittest.TestCase):
    def setUp(self):
        support._SAFE_CONTEXT.clear()
        support._SAFE_CONTEXT.update({
            "application_mode": "unknown",
            "database_scope": "unknown",
            "authenticated": False,
        })

    def test_runtime_context_classifies_test_without_private_identity(self):
        support.update_runtime_context(
            {"database": "ChurchDBTest", "test_mode": True},
            session=object(),
        )
        self.assertEqual(support._SAFE_CONTEXT, {
            "application_mode": "test",
            "database_scope": "test",
            "database_name": "ChurchDBTest",
            "authenticated": True,
        })

    def test_redactor_removes_user_profile_email_and_phone(self):
        with patch.dict(os.environ, {"USERPROFILE": r"C:\Users\PrivateUser"}):
            result = support._churchmanager_redactor(
                r"C:\Users\PrivateUser\Documents\file.txt person@example.com (555) 010-1234"
            )
        self.assertNotIn("PrivateUser", result)
        self.assertNotIn("person@example.com", result)
        self.assertNotIn("555", result)
        self.assertIn("[USERPROFILE]", result)
        self.assertIn("[EMAIL]", result)
        self.assertIn("[PHONE]", result)

    def test_support_diagnostics_is_on_main_menu(self):
        self.assertIn("lblSupportDiagnostics", MENU_CONTROLS)

    def test_support_permission_grants_only_active_roles(self):
        migration = (
            Path(__file__).resolve().parents[1]
            / "migrations" / "062_add_support_diagnostics_permission.sql"
        ).read_text(encoding="utf-8")
        self.assertIn("WHERE r.Active=1", migration)
        self.assertNotIn("r.IsActive", migration)


if __name__ == "__main__":
    unittest.main()
