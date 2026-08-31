"""Tests for installed entry points and executable build specifications."""

import unittest
import json
import tempfile
from types import SimpleNamespace
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import installed_launcher
import installed_package_check
import installed_setup
from build_windows_release import msi_version


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

    @patch("installed_launcher.ensure_configuration")
    @patch("installed_launcher.setup_required", return_value=True)
    def test_explicit_test_mode_bypasses_production_setup(self, required, ensure):
        fake_cm = SimpleNamespace(main=lambda arguments: arguments)
        with patch.dict("sys.modules", {"cm": fake_cm}), \
             patch("installed_setup.main") as setup:
            self.assertEqual(installed_launcher.main(["--test"]), ["--test"])
        setup.assert_not_called()

    @patch("installed_launcher.find_mariadb_tool", return_value=None)
    def test_missing_mariadb_has_plain_message_without_traceback(self, _find):
        error = RuntimeError("The database connection could not be established.")
        message = installed_launcher.database_startup_message(error)
        self.assertIn("MariaDB Server is not installed yet", message)
        self.assertIn("https://mariadb.org/download/", message)
        self.assertNotIn("Traceback", message)

    def test_friendly_dialog_provides_clickable_mariadb_download(self):
        source = Path(installed_launcher.__file__).read_text(encoding="utf-8")
        self.assertIn("wx.adv.HyperlinkCtrl", source)
        self.assertIn('label="Download MariaDB Server"', source)
        self.assertIn('url="https://mariadb.org/download/"', source)

    @patch("installed_launcher.find_mariadb_tool", return_value=Path("mariadb.exe"))
    def test_authentication_failure_is_not_mislabeled_as_missing_server(self, _find):
        cause = RuntimeError("Authentication plugin 'auth_gssapi_client' is not supported")
        error = RuntimeError("The database connection could not be established.")
        error.__cause__ = cause
        message = installed_launcher.database_startup_message(error)
        self.assertIn("could not sign in to MariaDB", message)
        self.assertNotIn("not installed yet", message)

    @patch("installed_launcher.ensure_configuration")
    @patch("installed_launcher.setup_required", return_value=False)
    def test_expected_database_failure_is_shown_without_escaping(self, _required, _ensure):
        error = RuntimeError("The database connection could not be established.")
        fake_cm = SimpleNamespace(main=lambda _arguments: (_ for _ in ()).throw(error))
        with patch.dict("sys.modules", {"cm": fake_cm}), \
             patch("installed_launcher.database_startup_message", return_value="Friendly") as classify, \
             patch("installed_launcher.show_database_startup_message") as show:
            self.assertEqual(installed_launcher.main([]), 1)
        classify.assert_called_once_with(error)
        show.assert_called_once_with("Friendly")

    @patch("installed_launcher.ensure_configuration")
    @patch("installed_launcher.setup_required", return_value=False)
    def test_unexpected_programming_error_still_escapes(self, _required, _ensure):
        error = ValueError("unexpected")
        fake_cm = SimpleNamespace(main=lambda _arguments: (_ for _ in ()).throw(error))
        with patch.dict("sys.modules", {"cm": fake_cm}):
            with self.assertRaisesRegex(ValueError, "unexpected"):
                installed_launcher.main([])

    def test_specs_include_framework_forms_baseline_catalogs_and_guide(self):
        for filename in ("ChurchManager.spec", "ChurchManagerSetup.spec", "ChurchManagerBundle.spec"):
            source = (ROOT / "packaging" / filename).read_text(encoding="utf-8")
            for required in (
                "JSForm/Forms", '"Menus"', "JSForm/assets", "installation", "migrations", "packages",
                "visual_reports/definitions", "accounting/report_definitions",
                "ChurchManager.UserGuide.pdf", 'console=False',
            ):
                self.assertIn(required, source)

    def test_specs_explicitly_bundle_readiness_checked_pdf_runtime(self):
        for filename in ("ChurchManager.spec", "ChurchManagerSetup.spec", "ChurchManagerBundle.spec"):
            source = (ROOT / "packaging" / filename).read_text(encoding="utf-8")
            self.assertIn('collect_submodules("pypdf")', source)

    def test_specs_bundle_mysql_connector_localization_data(self):
        for filename in ("ChurchManager.spec", "ChurchManagerSetup.spec", "ChurchManagerBundle.spec"):
            source = (ROOT / "packaging" / filename).read_text(encoding="utf-8")
            self.assertIn('collect_submodules("mysql.connector.locales")', source)
            self.assertIn('collect_submodules("mysql.connector.plugins")', source)

    def test_bundle_and_msi_define_both_installed_entry_points(self):
        bundle = (ROOT / "packaging" / "ChurchManagerBundle.spec").read_text(encoding="utf-8")
        self.assertIn('name="ChurchManager"', bundle)
        self.assertIn('name="ChurchManagerSetup"', bundle)
        installer = ROOT / "packaging" / "ChurchManager.wxs"
        ET.parse(installer)
        source = installer.read_text(encoding="utf-8")
        self.assertIn("ChurchManager.exe", source)
        self.assertIn("ChurchManagerSetup.exe", source)
        self.assertIn("MajorUpgrade", source)
        self.assertIn('AllowSameVersionUpgrades="yes"', source)
        self.assertNotIn("AppData", source)
        self.assertNotIn("Backup", source)

    def test_package_check_reports_missing_resources_without_database_access(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "package-check.json"
            self.assertEqual(installed_package_check.package_check(
                output, module_file=Path(temporary) / "app.py"
            ), 2)
            evidence = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(evidence["passed"])
            self.assertIn("forms", evidence["missing"])
            self.assertIn("main_menu", evidence["missing"])
            self.assertIn("jsform_icon", evidence["missing"])
            self.assertEqual(evidence["missing_components"], [])

    def test_setup_package_check_uses_the_same_noninteractive_proof(self):
        with patch("installed_setup.package_check", return_value=0) as check:
            result = installed_setup.main(["--package-check", "proof.json"])
        self.assertEqual(result, 0)
        check.assert_called_once_with("proof.json")

    def test_release_suffix_is_removed_from_numeric_msi_version(self):
        self.assertEqual(msi_version("0.2.0-dev"), "0.2.0")
        self.assertEqual(msi_version("0.2.0-beta.1"), "0.2.0")
        with self.assertRaises(ValueError):
            msi_version("0.2-dev")


if __name__ == "__main__":
    unittest.main()
