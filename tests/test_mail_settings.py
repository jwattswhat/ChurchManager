"""Tests for protected ChurchManager email configuration."""

import unittest

from mail_settings import ChurchMailServiceFactory
from participant_notifications import TestModeMailService


class ExplodingConnection:
    def cursor(self):
        raise AssertionError("test mode must not query mail settings")


class MailSettingsTests(unittest.TestCase):
    def test_test_mode_cannot_read_settings_credentials_or_open_smtp(self):
        service = ChurchMailServiceFactory(ExplodingConnection(), test_mode=True).build()
        self.assertIsInstance(service, TestModeMailService)
        with self.assertRaisesRegex(RuntimeError, "disabled"):
            service.send((), None)

    def test_migration_stores_no_password_column(self):
        with open("migrations/071_add_secure_mail_settings.sql", encoding="utf-8") as source:
            text = source.read()
        self.assertIn("CredentialTarget", text)
        table_body = text.split("CREATE TABLE", 1)[1]
        self.assertNotRegex(table_body, r"(?im)^\s*Password\s")
        self.assertIn("STARTTLS", text)
        self.assertIn("SSL", text)


if __name__ == "__main__":
    unittest.main()
