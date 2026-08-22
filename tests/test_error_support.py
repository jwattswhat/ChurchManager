"""ChurchManager integration checks for JSForm diagnostic reporting."""

from __future__ import annotations

import os
import tempfile
import unittest
import zipfile
from unittest.mock import patch
from pathlib import Path

import churchmanager_error_support as support
from JSForm.error_reporting import ErrorReporter, ErrorReportingConfig
from JSForm.support_package import create_support_package
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

    def test_redactor_removes_confidential_giving_values(self):
        confidential = {
            "Contributor: Sarah Johnson": "Sarah Johnson",
            "Envelope number=00101": "00101",
            "Check reference: CHECK-7781": "CHECK-7781",
            "Address is 101 Private Lane": "101 Private Lane",
            "Imported row: 2027-01-07|Sarah Johnson|65.00": "2027-01-07|Sarah Johnson|65.00",
        }
        for source, private_value in confidential.items():
            with self.subTest(source=source):
                result = support._churchmanager_redactor(source)
                self.assertNotIn(private_value, result)
                self.assertIn("[CONFIDENTIAL]", result)

    def test_giving_values_are_redacted_in_log_and_support_package(self):
        private_values = (
            "Sarah Johnson", "00101", "CHECK-7781",
            "101 Private Lane", "2027-01-07|Sarah Johnson|65.00",
        )
        message = (
            "Contributor: Sarah Johnson; Envelope number=00101; "
            "Check reference: CHECK-7781; Address is 101 Private Lane; "
            "Imported row: 2027-01-07|Sarah Johnson|65.00"
        )
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            reporter = ErrorReporter(ErrorReportingConfig(
                application_name="ChurchManager",
                application_version="test",
                log_directory=root / "logs",
                redactors=(support._churchmanager_redactor,),
            ))
            reporter.report(ValueError(message), context={"operation": "giving.acceptance"})
            logged = reporter.log_path.read_text(encoding="utf-8")
            package = create_support_package(reporter, root / "support.zip")
            with zipfile.ZipFile(package) as archive:
                bundled = archive.read("logs/errors.jsonl").decode("utf-8")
            for private_value in private_values:
                self.assertNotIn(private_value, logged)
                self.assertNotIn(private_value, bundled)
            self.assertIn("[CONFIDENTIAL]", logged)
            self.assertIn("[CONFIDENTIAL]", bundled)

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
