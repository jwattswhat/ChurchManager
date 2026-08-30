import json
import inspect
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from setup_wizard import (
    ChurchManagerSetupWizard,
    INSTALLATION_TITLE,
    SetupPage,
    application_account_name,
    finalize_installed_connection,
    packaged_resource,
    save_installed_configuration,
)


class SetupWizardSupportTests(unittest.TestCase):
    def test_aligned_row_labels_use_a_positive_native_height(self):
        source = inspect.getsource(SetupPage.row)
        self.assertIn("caption.GetBestSize().GetHeight()", source)
        self.assertNotIn("size=(170, -1)", source)

    def test_wizard_size_is_set_after_supported_constructor_call(self):
        source = inspect.getsource(ChurchManagerSetupWizard.__init__)
        constructor = source.split("self.SetSize", 1)[0]
        self.assertNotIn("size=", constructor)
        self.assertIn("self.SetSize((760, 650))", source)
        self.assertIn("self.SetPageSize((720, 520))", source)

    def test_installer_identity_uses_narrow_installation_title_and_banner(self):
        self.assertEqual(INSTALLATION_TITLE, "ChurchManager Installation")
        self.assertEqual(
            packaged_resource(
                "assets", "brand", "png", "ChurchManager-logo-horizontal-600.png",
            ).name,
            "ChurchManager-logo-horizontal-600.png",
        )

    def test_catalog_controls_fit_supported_page_height(self):
        source = inspect.getsource(ChurchManagerSetupWizard._build_pages)
        self.assertIn("size=(-1, 52)", source)
        self.assertNotIn("size=(-1, 74)", source)

    def test_application_account_is_local_bounded_and_predictable(self):
        self.assertEqual(application_account_name("ChurchManager"), "cm_churchmanager")
        self.assertLessEqual(len(application_account_name("A" * 64)), 32)

    def test_installed_configuration_preserves_testing_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "churchmanager.json"
            path.write_text(json.dumps({
                "database_settings": {"host": "old", "database": "old"},
                "testing": {"database": "ChurchDBTest"},
                "security": {"testing_enabled": True, "production_enabled": False},
            }), encoding="utf-8")
            save_installed_configuration("ChurchManager_Grace", "cm_grace", path)
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(value["database_settings"]["database"], "ChurchManager_Grace")
            self.assertNotIn("jsform_database", value["database_settings"])
            self.assertEqual(value["testing"]["database"], "ChurchDBTest")
            self.assertTrue(value["security"]["production_enabled"])
            self.assertTrue(value["security"]["testing_enabled"])

    def test_installed_configuration_falls_back_when_windows_denies_replace(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "churchmanager.json"
            path.write_text(json.dumps({
                "database_settings": {}, "security": {},
            }), encoding="utf-8")
            with mock.patch.object(Path, "replace", side_effect=PermissionError("locked")):
                save_installed_configuration("ChurchManager_Grace", "cm_grace", path)
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(value["database_settings"]["database"], "ChurchManager_Grace")
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_failed_configuration_save_restores_credential_and_config(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "churchmanager.json"
            original = {"database_settings": {}, "security": {}}
            path.write_text(json.dumps(original), encoding="utf-8")
            writes = []
            result = type("Result", (), {
                "database_name": "ChurchManager_New",
                "application_user": "cm_new",
            })()

            def writer(*values):
                writes.append(values)

            with mock.patch(
                "setup_wizard.save_installed_configuration",
                side_effect=PermissionError("blocked"),
            ):
                with self.assertRaises(PermissionError):
                    finalize_installed_connection(
                        result, "new secret", path=path,
                        credential_reader=lambda _target: ("old_user", "old_secret"),
                        credential_writer=writer,
                        credential_deleter=lambda _target: None,
                    )
            self.assertEqual(json.loads(path.read_text()), original)
            self.assertEqual(writes[-1], (
                "ChurchManager/Production", "old_user", "old_secret",
            ))


if __name__ == "__main__":
    unittest.main()
