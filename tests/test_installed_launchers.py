"""Tests for installed entry points and executable build specifications."""

import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import installed_launcher
import installed_package_check
import installed_setup


ROOT = Path(__file__).resolve().parents[1]


class InstalledLauncherTests(unittest.TestCase):
    """Verify first-run routing and required packaged resources."""

    def test_setup_is_required_until_production_is_enabled_and_named(self):
        self.assertTrue(installed_launcher.setup_required({}))
        self.assertFalse(installed_launcher.setup_required({
            "security": {"production_enabled": True},
            "database_settings": {"user": "cm_churchdb", "database": "ChurchDB"},
        }))

    @patch("installed_launcher.ensure_configuration")
    @patch("installed_launcher.load_config")
    def test_incomplete_setup_does_not_launch_application(self, load, ensure):
        load.return_value = {"security": {"production_enabled": False}}
        with patch("installed_setup.main", return_value=0) as setup:
            self.assertEqual(installed_launcher.main([]), 0)
        ensure.assert_called_once()
        setup.assert_called_once()

    def test_specs_include_framework_forms_baseline_catalogs_and_guide(self):
        for filename in ("ChurchManager.spec", "ChurchManagerSetup.spec"):
            source = (ROOT / "packaging" / filename).read_text(encoding="utf-8")
            for required in (
                "JSForm/Forms", "installation", "migrations", "packages",
                "visual_reports/definitions", "accounting/report_definitions",
                "ChurchManager.UserGuide.pdf", 'console=False',
            ):
                self.assertIn(required, source)

    def test_package_check_reports_missing_resources_without_database_access(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "package-check.json"
            self.assertEqual(installed_package_check.package_check(
                output, module_file=Path(temporary) / "app.py"
            ), 2)
            evidence = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(evidence["passed"])
            self.assertIn("forms", evidence["missing"])

    def test_setup_package_check_uses_the_same_noninteractive_proof(self):
        with patch("installed_setup.package_check", return_value=0) as check:
            result = installed_setup.main(["--package-check", "proof.json"])
        self.assertEqual(result, 0)
        check.assert_called_once_with("proof.json")


if __name__ == "__main__":
    unittest.main()
