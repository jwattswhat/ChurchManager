"""Safety and readiness tests for packaged GUI smoke automation."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

import run_gui_packaged_profile as profile


class GUIPackagedProfileTests(unittest.TestCase):
    def test_only_exact_current_bundle_is_allowed(self):
        with mock.patch.object(Path, "is_file", return_value=True):
            self.assertEqual(profile.validate_executable(profile.BUNDLE), profile.BUNDLE.resolve())
            with self.assertRaisesRegex(RuntimeError, "current bundle"):
                profile.validate_executable(profile.ROOT / "ChurchManager.exe")

    def test_missing_automation_dependency_is_a_nonsecret_skip(self):
        with mock.patch("run_gui_packaged_profile.importlib.util.find_spec", return_value=None), \
             mock.patch("run_gui_packaged_profile.read_credential") as credential:
            ready, reason = profile.automation_readiness()
        self.assertFalse(ready)
        self.assertIn("not installed", reason)
        credential.assert_not_called()

    def test_missing_test_credential_is_a_skip_after_dependency_review(self):
        with mock.patch("run_gui_packaged_profile.importlib.util.find_spec", return_value=object()), \
             mock.patch("run_gui_packaged_profile.read_credential", side_effect=KeyError):
            ready, reason = profile.automation_readiness()
        self.assertFalse(ready)
        self.assertIn("unavailable", reason)

    def test_packaged_control_contract_is_stable_and_test_scoped(self):
        self.assertEqual(profile.LOGIN_TITLE, "ChurchManager Login")
        self.assertIn("TEST MODE", profile.MAIN_TITLE_RE)
        self.assertEqual(profile.PROJECTS_TITLE, "Projects and Scheduling")
        self.assertNotIn("Legacy", profile.MAIN_TITLE_RE)

    def test_packaged_configuration_is_nonsecret_and_test_scoped(self):
        with TemporaryDirectory() as folder:
            target = profile.packaged_test_config(Path(folder) / "config.json")
            text = target.read_text(encoding="utf-8")
        self.assertIn('"database": "ChurchDBTest"', text)
        self.assertIn("ChurchManager/LocalTestAdmin", text)
        self.assertNotIn("password", text.casefold())


if __name__ == "__main__":
    unittest.main()
