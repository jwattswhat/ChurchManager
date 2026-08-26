from pathlib import Path
import json
import unittest

import JSForm

from visual_reports.report_inventory import (
    CONSOLIDATED_CODES, DISABLED_CODES, LAUNCHER_CODES, OFFICIAL_CODES,
    RETIRED_CODES, SPECS,
)
from visual_reports.tabular_dataset import TabularDatasetProvider, contract_for
from visual_reports.worship_planning_dataset import WORSHIP_PLANNING_CONTRACT


ROOT = Path(__file__).resolve().parents[1]


class TestVisualReportInventory(unittest.TestCase):
    def test_inventory_includes_every_starter_and_declared_exceptions(self):
        starter_codes = {
            path.stem for path in (ROOT / "visual_reports" / "definitions").glob("*.json")
        }
        self.assertTrue(starter_codes.issubset(OFFICIAL_CODES))
        self.assertEqual(CONSOLIDATED_CODES, {"CMAD01", "CMPH01"})
        self.assertEqual(DISABLED_CODES, {"CMSM01"})
        self.assertEqual(LAUNCHER_CODES, {"CMBATCH00"})
        self.assertTrue(RETIRED_CODES.isdisjoint(OFFICIAL_CODES))

    def test_every_official_report_has_a_valid_starter(self):
        loader = JSForm.ReportDefinitionLoader()
        for code in OFFICIAL_CODES:
            with self.subTest(code=code):
                definition = loader.load(ROOT / "visual_reports" / "definitions" / f"{code}.json")
                self.assertEqual(definition.report_id, code)
                if code == "CMWS01":
                    WORSHIP_PLANNING_CONTRACT.validate_definition(definition)
                elif definition.dataset_name == "membership.directory":
                    from visual_reports.directory_dataset import DIRECTORY_CONTRACT
                    DIRECTORY_CONTRACT.validate_definition(definition)
                else:
                    contract_for(code).validate_definition(definition)

    def test_mailing_labels_are_json_only_directory_reports(self):
        loader = JSForm.ReportDefinitionLoader()
        for code, collection in (("CMMB09", "directory_entries"), ("CMMB10", "directory_people")):
            definition = loader.load(ROOT / "visual_reports" / "definitions" / f"{code}.json")
            repeater = next(
                control for control in definition.controls.values()
                if control["type"] == "repeater"
            )
            self.assertEqual(definition.dataset_name, "membership.directory")
            self.assertEqual(repeater["repeatcollection"], collection)
            self.assertEqual(repeater["repeatcolumns"], 3)

    def test_tabular_definitions_use_standard_metadata_and_empty_message(self):
        loader = JSForm.ReportDefinitionLoader()
        for spec in SPECS:
            if spec.code == "CMWS01":
                continue
            definition = loader.load(ROOT / "visual_reports" / "definitions" / f"{spec.code}.json")
            controls = definition.controls
            self.assertEqual(definition.settings["emptytext"], "No records match the selected criteria.")
            self.assertEqual(controls["RunDate"]["systemvalue"], "run_date")
            self.assertEqual(controls["PageNumber"]["systemvalue"], "page_number")

    def test_worship_planner_uses_specialized_service_collections(self):
        definition = JSForm.ReportDefinitionLoader().load(
            ROOT / "visual_reports" / "definitions" / "CMWS01.json"
        )
        WORSHIP_PLANNING_CONTRACT.validate_definition(definition)
        self.assertEqual(definition.controls["OrderLines"]["repeatcollection"], "order_lines")
        self.assertEqual(definition.controls["Readings"]["repeatcollection"], "readings")
        self.assertEqual(definition.controls["Hymns"]["repeatcollection"], "hymns")
        self.assertEqual(definition.controls["Participants"]["repeatcollection"], "participants")
        self.assertEqual(definition.controls["ColorSwatch"]["collection"], "service")
        self.assertEqual(definition.controls["ColorSwatch"]["field"], "ColorHex")
        self.assertIn(
            "ColorHex", {field.name for field in WORSHIP_PLANNING_CONTRACT.collection("service").fields}
        )

    def test_worship_planner_checklist_contract_includes_completion_source(self):
        checklist = WORSHIP_PLANNING_CONTRACT.collection("checklist")
        self.assertIn("CompletionSource", {field.name for field in checklist.fields})

    def test_worship_planner_hymns_expose_stanzas_and_separate_reference(self):
        fields = {field.name for field in WORSHIP_PLANNING_CONTRACT.collection("hymns").fields}
        self.assertTrue({"HymnNumber", "Title", "Stanzas", "ReferenceText"}.issubset(fields))

    def test_worship_planner_provider_reads_only_report_views(self):
        source = (ROOT / "visual_reports" / "worship_planning_dataset.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("FROM tbl", source)
        self.assertNotIn("JOIN tbl", source)
        for view in (
            "rpt_worship_planner_service", "rpt_worship_planner_order",
            "rpt_worship_planner_reading", "rpt_worship_planner_hymn",
            "rpt_worship_planner_participant", "rpt_worship_planner_required_position",
        ):
            self.assertIn(view, source)

    def test_worship_planner_lists_required_open_and_declined_positions(self):
        from visual_reports.worship_planning_dataset import WorshipPlanningDatasetProvider

        from worship_scheduling_rules import report_participant_rows

        rows = report_participant_rows(
            [{"WorshipRoleID": 6, "Role": "Acolyte", "RequiredCount": 2}],
            [{
                "WorshipRoleID": 6, "Role": "Acolyte", "Name": "Sam",
                "Status": "DECLINED",
            }],
        )
        self.assertEqual(rows, [
            {"Role": "Acolyte 1", "Name": "Unfilled", "Status": "Open"},
            {"Role": "Acolyte 2", "Name": "Unfilled", "Status": "Open"},
            {"Role": "Acolyte", "Name": "Sam", "Status": "Declined"},
        ])

    def test_sensitive_contact_sources_are_safe_views(self):
        source = (ROOT / "visual_reports" / "report_inventory.py").read_text(encoding="utf-8")
        self.assertNotIn('"tblPersonContact"', source)
        self.assertNotIn('"tblFamilyContact"', source)
        self.assertNotIn('"tblPersonAddress"', source)
        self.assertNotIn('"tblFamilyAddress"', source)

    def test_every_tabular_report_view_is_approved_by_the_provider(self):
        provider = TabularDatasetProvider(object(), None)
        for spec in SPECS:
            if spec.code == "CMWS01":
                continue
            with self.subTest(code=spec.code, view=spec.view):
                source, _where, _values = provider._scope(spec.view, 1)
                self.assertIn(spec.view, source)

    def test_asset_report_filters_have_reports_screen_controls(self):
        form = json.loads((ROOT / "Forms" / "frmReports.json").read_text(encoding="utf-8"))
        controls = set(form["frmReportsFORM"]["CONTROLS"])
        for spec in (item for item in SPECS if item.code.startswith("CMAM")):
            with self.subTest(code=spec.code):
                self.assertTrue(set(spec.filter_fields).issubset(controls))

    def test_favorite_hymns_report_requires_a_hymnal_and_exact_tag_view(self):
        spec = next(item for item in SPECS if item.code == "CMWS07")
        self.assertEqual(spec.filter_fields, ("HymnalID",))
        migration = (ROOT / "migrations" / "075_add_favorite_hymns_report.sql").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("rpt_favorite_hymn", migration)
        self.assertIn("#favorite", migration)
        self.assertIn("HymnalID=2 AND EntrySlot=363", migration)
        naming = (ROOT / "migrations" / "110_standardize_report_names.sql").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("'CMHU05' THEN 'CMWS07'", naming)
        self.assertIn("'Worship - Favorite Hymns'", naming)

    def test_codes_and_titles_follow_the_subsystem_standard(self):
        subsystem_names = {
            "GN": "General", "AT": "Attendance", "WS": "Worship",
            "MB": "Membership", "GR": "Groups", "PC": "Pastoral Care",
            "AM": "Asset Management",
            "PS": "Projects",
        }
        for code in OFFICIAL_CODES:
            with self.subTest(code=code):
                self.assertRegex(code, r"^CM[A-Z]{2}\d{2}$")
                definition = JSForm.ReportDefinitionLoader().load(
                    ROOT / "visual_reports" / "definitions" / f"{code}.json"
                )
                self.assertTrue(
                    definition.title.startswith(subsystem_names[code[2:4]] + " - ")
                )


if __name__ == "__main__":
    unittest.main()
