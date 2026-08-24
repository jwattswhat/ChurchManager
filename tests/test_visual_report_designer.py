from pathlib import Path
import json
import tempfile
import unittest

from visual_reports.designer import (
    contract_for_definition, ensure_user_definition, open_directory_designer, resolve_report_definition, source_code_for_definition, user_definition_directory,
    user_definition_path,
)
import JSForm


class TestVisualReportDesignerStorage(unittest.TestCase):
    def test_custom_report_code_uses_its_inherited_dataset_contract(self):
        source = Path(__file__).resolve().parents[1] / "visual_reports" / "definitions" / "CMAT01.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        root = data.pop("CMAT01REPORT")
        root["REPORT"]["name"] = "test"
        definition = JSForm.ReportDefinitionLoader().from_dict({"testREPORT": root})
        contract, kind = contract_for_definition(definition)
        self.assertEqual(contract.name, definition.dataset_name)
        self.assertEqual(kind, "tabular")
        self.assertEqual(source_code_for_definition(definition), "CMAT01")

    def test_current_starter_is_used_until_a_custom_definition_exists(self):
        with tempfile.TemporaryDirectory() as folder:
            starter=resolve_report_definition("CMMB01",folder)
            self.assertEqual(starter.name,"CMMB01.json")
            self.assertNotEqual(starter.parent,user_definition_directory(folder))
            custom=ensure_user_definition("CMMB01",folder)
            self.assertEqual(resolve_report_definition("CMMB01",folder),custom)

    def test_starter_is_copied_without_being_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            first = ensure_user_definition("CMMB01", folder)
            original = first.read_text(encoding="utf-8")
            first.write_text(original.replace("Member Directory", "Custom Directory", 1), encoding="utf-8")
            second = ensure_user_definition("CMMB01", folder)
            self.assertEqual(first, second)
            self.assertIn("Custom Directory", second.read_text(encoding="utf-8"))
            self.assertEqual(first, user_definition_path("CMMB01", folder))
            self.assertEqual(first.parent, user_definition_directory(folder))

    def test_saved_layout_under_prior_code_is_migrated_once(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = user_definition_directory(folder)
            directory.mkdir(parents=True)
            source = Path(__file__).resolve().parents[1] / "visual_reports" / "definitions" / "CMGN01.json"
            old_text = source.read_text(encoding="utf-8")
            old_text = old_text.replace("CMGN01", "CMAS01").replace("cmgn01", "cmas01")
            (directory / "CMAS01.json").write_text(old_text, encoding="utf-8")

            migrated = resolve_report_definition("CMGN01", folder)

            self.assertEqual(migrated, directory / "CMGN01.json")
            definition = JSForm.ReportDefinitionLoader().load(migrated)
            self.assertEqual(definition.dataset_name, "churchmanager.cmgn01")

    def test_incompatible_custom_dataset_is_backed_up_and_upgraded(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as starters:
            source = Path(__file__).resolve().parents[1] / "visual_reports" / "definitions" / "CMWS01.json"
            starter = Path(starters) / "CMWS01.json"
            starter.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            custom = ensure_user_definition("CMWS01", folder, starters)
            data = json.loads(custom.read_text(encoding="utf-8"))
            data["CMWS01REPORT"]["REPORT"]["datasetversion"] = 1
            data["CMWS01REPORT"]["REPORT"]["title"] = "Older Custom Planner"
            custom.write_text(json.dumps(data), encoding="utf-8")

            self.assertEqual(resolve_report_definition("CMWS01", folder, starters), starter)
            upgraded = ensure_user_definition("CMWS01", folder, starters)
            self.assertEqual(json.loads(upgraded.read_text(encoding="utf-8"))[
                "CMWS01REPORT"
            ]["REPORT"]["datasetversion"], 4)
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
