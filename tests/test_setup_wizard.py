import json
import tempfile
import unittest
from pathlib import Path

from setup_wizard import application_account_name, save_installed_configuration


class SetupWizardSupportTests(unittest.TestCase):
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
            self.assertEqual(value["database_settings"]["jsform_database"], "ChurchManager_Grace")
            self.assertEqual(value["testing"]["database"], "ChurchDBTest")
            self.assertTrue(value["security"]["production_enabled"])
            self.assertTrue(value["security"]["testing_enabled"])


if __name__ == "__main__":
    unittest.main()
