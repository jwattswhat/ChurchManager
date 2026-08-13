from pathlib import Path
import json
import tempfile
import unittest

from visual_reports.designer import (
    ensure_user_definition, open_directory_designer, resolve_report_definition, user_definition_directory,
    user_definition_path,
)


class TestVisualReportDesignerStorage(unittest.TestCase):
    def test_current_starter_is_used_until_a_custom_definition_exists(self):
        with tempfile.TemporaryDirectory() as folder:
            starter=resolve_report_definition("CMMD01",folder)
            self.assertEqual(starter.name,"CMMD01.json")
            self.assertNotEqual(starter.parent,user_definition_directory(folder))
            custom=ensure_user_definition("CMMD01",folder)
            self.assertEqual(resolve_report_definition("CMMD01",folder),custom)

    def test_starter_is_copied_without_being_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            first = ensure_user_definition("CMMD01", folder)
            original = first.read_text(encoding="utf-8")
            first.write_text(original.replace("Member Directory", "Custom Directory", 1), encoding="utf-8")
            second = ensure_user_definition("CMMD01", folder)
            self.assertEqual(first, second)
            self.assertIn("Custom Directory", second.read_text(encoding="utf-8"))
            self.assertEqual(first, user_definition_path("CMMD01", folder))
            self.assertEqual(first.parent, user_definition_directory(folder))

    def test_incompatible_custom_dataset_is_backed_up_and_upgraded(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as starters:
            source = Path(__file__).resolve().parents[1] / "visual_reports" / "definitions" / "CMWP01.json"
            starter = Path(starters) / "CMWP01.json"
            starter.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            custom = ensure_user_definition("CMWP01", folder, starters)
            data = json.loads(custom.read_text(encoding="utf-8"))
            data["CMWP01REPORT"]["REPORT"]["datasetversion"] = 1
            data["CMWP01REPORT"]["REPORT"]["title"] = "Older Custom Planner"
            custom.write_text(json.dumps(data), encoding="utf-8")

            self.assertEqual(resolve_report_definition("CMWP01", folder, starters), starter)
            upgraded = ensure_user_definition("CMWP01", folder, starters)
            self.assertEqual(json.loads(upgraded.read_text(encoding="utf-8"))[
                "CMWP01REPORT"
            ]["REPORT"]["datasetversion"], 2)
            self.assertTrue(upgraded.with_suffix(".v1.json.bak").is_file())

    def test_designer_requires_design_permission_before_opening(self):
        class DeniedAuthorization:
            def __init__(self):
                self.checked = []

            def require(self, permission, operation=None):
                self.checked.append(permission)
                raise PermissionError(permission)

        authorization = DeniedAuthorization()
        with self.assertRaises(PermissionError):
            open_directory_designer(authorization=authorization)
        self.assertEqual(authorization.checked, ["reports.design"])


if __name__ == "__main__":
    unittest.main()
