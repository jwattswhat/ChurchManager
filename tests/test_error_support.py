"""ChurchManager integration checks for JSForm diagnostic reporting."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

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

    def test_redactor_removes_user_profile_and_email(self):
        with patch.dict(os.environ, {"USERPROFILE": r"C:\Users\PrivateUser"}):
            result = support._churchmanager_redactor(
                r"C:\Users\PrivateUser\Documents\file.txt person@example.com"
            )
        self.assertNotIn("PrivateUser", result)
        self.assertNotIn("person@example.com", result)
        self.assertIn("[USERPROFILE]", result)
        self.assertIn("[EMAIL]", result)

    def test_support_diagnostics_is_on_main_menu(self):
        self.assertIn("lblSupportDiagnostics", MENU_CONTROLS)


if __name__ == "__main__":
    unittest.main()
