"""Tests for writable source and installed configuration resolution."""

import json
import tempfile
import unittest
from pathlib import Path

from configuration_paths import ROOT, configuration_path, ensure_configuration


class ConfigurationPathTests(unittest.TestCase):
    """Keep development local while installed configuration remains writable."""

    def test_source_mode_keeps_repository_configuration(self):
        self.assertEqual(configuration_path(frozen=False, environment={}), ROOT / "churchmanager.json")

    def test_installed_mode_uses_local_application_data(self):
        path = configuration_path(
            frozen=True, environment={"LOCALAPPDATA": r"C:\Users\Example\AppData\Local"},
        )
        self.assertEqual(
            path,
            Path(r"C:\Users\Example\AppData\Local\ChurchManager\churchmanager.json"),
        )

    def test_explicit_override_has_precedence(self):
        path = configuration_path(
            frozen=True, environment={"CHURCHMANAGER_CONFIG": r"C:\Temp\cm.json"},
        )
        self.assertEqual(path, Path(r"C:\Temp\cm.json"))

    def test_default_template_contains_no_password_and_can_be_copied(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "profile" / "churchmanager.json"
            ensure_configuration(target)
            values = json.loads(target.read_text(encoding="utf-8"))
            self.assertNotIn("password", values["database_settings"])
            self.assertEqual(values["database_settings"]["host"], "127.0.0.1")
            self.assertFalse(values["security"]["production_enabled"])


if __name__ == "__main__":
    unittest.main()
