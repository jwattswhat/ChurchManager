from pathlib import Path
import unittest

import JSForm

from visual_reports.report_inventory import (
    CONSOLIDATED_CODES, DISABLED_CODES, LAUNCHER_CODES, OFFICIAL_CODES, SPECS,
)
from visual_reports.tabular_dataset import contract_for


ROOT = Path(__file__).resolve().parents[1]


class TestVisualReportInventory(unittest.TestCase):
    def test_inventory_has_27_official_reports_and_declared_exceptions(self):
        self.assertEqual(len(OFFICIAL_CODES), 27)
        self.assertEqual(CONSOLIDATED_CODES, {"CMAD01", "CMPH01"})
        self.assertEqual(DISABLED_CODES, {"CMSM01"})
        self.assertEqual(LAUNCHER_CODES, {"CMBATCH00"})

    def test_every_official_report_has_a_valid_starter(self):
        loader = JSForm.ReportDefinitionLoader()
        for code in OFFICIAL_CODES:
            with self.subTest(code=code):
                definition = loader.load(ROOT / "visual_reports" / "definitions" / f"{code}.json")
                self.assertEqual(definition.report_id, code)
                if code != "CMMD01":
                    contract_for(code).validate_definition(definition)

    def test_tabular_definitions_use_standard_metadata_and_empty_message(self):
        loader = JSForm.ReportDefinitionLoader()
        for spec in SPECS:
            definition = loader.load(ROOT / "visual_reports" / "definitions" / f"{spec.code}.json")
            controls = definition.controls
            self.assertEqual(definition.settings["emptytext"], "No records match the selected criteria.")
            self.assertEqual(controls["RunDate"]["systemvalue"], "run_date")
            self.assertEqual(controls["PageNumber"]["systemvalue"], "page_number")

    def test_sensitive_contact_sources_are_safe_views(self):
        source = (ROOT / "visual_reports" / "report_inventory.py").read_text(encoding="utf-8")
        self.assertNotIn('"tblPersonContact"', source)
        self.assertNotIn('"tblFamilyContact"', source)
        self.assertNotIn('"tblPersonAddress"', source)
        self.assertNotIn('"tblFamilyAddress"', source)


if __name__ == "__main__":
    unittest.main()
