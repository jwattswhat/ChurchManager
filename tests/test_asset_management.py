"""Contract tests for the approved simple Asset subsystem."""

import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from asset_exchange import HEADERS, read_csv, write_csv
from asset_service import AssetService, AssetValidationError


class Authorization:
    def __init__(self, permissions): self.permissions=set(permissions)
    def require(self, permission, operation=None):
        if permission not in self.permissions: raise PermissionError(operation or permission)


class Repository:
    def __init__(self): self.saved=None; self.activity=None; self.imported=None
    def scope_id(self, table, item_id): return 4
    def create_asset(self, values, user_id): self.saved=(values,user_id); return 9
    def asset(self, asset_id): return {"id":asset_id,"church_id":4,"status":"Active","version":1}
    def add_activity(self, asset, values, user_id): self.activity=(asset,values,user_id); return 5
    def import_context(self, church_id): return {"locations":[{"id":3,"name":"Sanctuary"}],"numbers":[{"value":"AST-0001"}],"serials":[{"value":"SERIAL-1"}]}
    def import_assets(self, rows, user_id): self.imported=(rows,user_id); return len(rows)
    def export_assets(self, church_id): return [{name:"" for name in HEADERS}]


class AssetServiceTests(unittest.TestCase):
    def service(self, permissions=("assets.view","assets.manage","assets.retire")):
        self.repository=Repository(); return AssetService(self.repository,SimpleNamespace(user_id=7),Authorization(permissions))

    @staticmethod
    def values():
        return {"church_id":4,"asset_number":"AST-0001","asset_name":"Sanctuary Piano","category":"Musical Instrument","quantity":1,"status":"Active","condition_name":"Good"}

    def test_create_validates_and_attributes_asset(self):
        self.assertEqual(9,self.service().save_asset(self.values()))
        self.assertEqual(7,self.repository.saved[1])

    def test_retired_asset_requires_date_and_permission(self):
        values=self.values(); values["status"]="Retired"
        with self.assertRaises(AssetValidationError): self.service().save_asset(values)
        values["retired_date"]=date(2026,8,25)
        with self.assertRaises(PermissionError): self.service(("assets.view","assets.manage")).save_asset(values)

    def test_activity_rejects_cross_church_location(self):
        service=self.service(); self.repository.scope_id=lambda table,item_id: 8
        with self.assertRaises(AssetValidationError): service.add_activity(1,{"activity_type":"Transfer","summary":"Moved","location_id":3})

    def test_csv_preview_blocks_duplicate_number_and_matches_location(self):
        service=self.service(); content=("Asset Number,Asset Name,Category,Location,Serial Number\n"
                                        "AST-0001,Mixer,Audio/Visual,Sanctuary,SERIAL-2\n"
                                        "AST-0002,Piano,Musical Instrument,Sanctuary,SERIAL-1\n")
        preview=service.preview_csv(4,content)
        self.assertIn("Duplicate asset number",preview[0]["errors"])
        self.assertEqual(3,preview[1]["values"]["location_id"])
        self.assertIn("Repeated serial number",preview[1]["warnings"])
        with self.assertRaises(AssetValidationError): service.import_preview(preview)

    def test_csv_ready_rows_import_as_one_reviewed_set(self):
        service=self.service(); preview=service.preview_csv(
            4,"Asset Number,Asset Name,Category,Location\nAST-0002,Piano,Musical Instrument,Sanctuary\n")
        self.assertEqual(1,service.import_preview(preview)); self.assertEqual(7,self.repository.imported[1])

    def test_csv_invalid_date_marks_only_that_row_for_attention(self):
        service=self.service(); preview=service.preview_csv(
            4,"Asset Number,Asset Name,Category,Acquisition Date\n"
              "AST-0002,Piano,Musical Instrument,August someday\n"
              "AST-0003,Table,Furniture,2026-08-25\n")
        self.assertIn("Use YYYY-MM-DD",preview[0]["errors"][0])
        self.assertEqual([],preview[1]["errors"])
        self.assertEqual(date(2026,8,25),preview[1]["values"]["acquisition_date"])


class AssetExchangeTests(unittest.TestCase):
    def test_round_trip_uses_approved_headers_only(self):
        row={name:"" for name in HEADERS}; row.update({"Asset Number":"AST-9","Asset Name":"Table","Category":"Furniture"})
        content=write_csv([row]); parsed=read_csv(content)
        self.assertEqual("AST-9",parsed[0]["Asset Number"]); self.assertNotIn("Document",content)

    def test_formula_like_cells_are_exported_as_spreadsheet_text(self):
        row = {name: "" for name in HEADERS}
        row.update({"Asset Number": "AST-10", "Asset Name": "=HYPERLINK(\"bad\")",
                    "Category": "Furniture", "Note": " @SUM(A1:A2)"})
        content = write_csv([row])
        self.assertNotIn(",=HYPERLINK", content)
        parsed = read_csv(content)[0]
        self.assertEqual(parsed["Asset Name"], "'" + row["Asset Name"])
        self.assertEqual(parsed["Note"], "'" + row["Note"])

    def test_required_headers_are_enforced(self):
        with self.assertRaises(ValueError): read_csv("Name\nPiano\n")


class AssetIntegrationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).parents[1]
        cls.sql=(cls.root/"migrations"/"117_add_asset_management.sql").read_text(encoding="utf-8")

    def test_migration_contains_tables_permissions_views_and_reports(self):
        for token in ("tblAssetLocation","tblAssetActivity","CHANGE COLUMN AssetID AssetNumber","assets.view","assets.manage","assets.retire","rpt_asset_register","CMAM01","CMAM02","CMAM03"):
            self.assertIn(token,self.sql)

    def test_asset_register_uses_non_reserved_condition_field(self):
        repair=(self.root/"migrations"/"118_fix_asset_register_condition_name.sql").read_text(encoding="utf-8")
        inventory=(self.root/"visual_reports"/"report_inventory.py").read_text(encoding="utf-8")
        definition=(self.root/"visual_reports"/"definitions"/"CMAM01.json").read_text(encoding="utf-8")
        self.assertIn("ConditionName",repair)
        self.assertIn('c("ConditionName", "Condition"',inventory)
        self.assertIn('"field": "ConditionName"',definition)

    def test_menu_and_dashboard_routes_exist(self):
        menu=(self.root/"Menus"/"main.menu.json").read_text(encoding="utf-8")
        dashboard=(self.root/"Forms"/"frmMain.json").read_text(encoding="utf-8")
        self.assertIn('churchmanager.assets',menu); self.assertIn('"AssetBox"',dashboard)

    def test_visual_report_starters_exist(self):
        for code in ("CMAM01","CMAM02","CMAM03"):
            self.assertTrue((self.root/"visual_reports"/"definitions"/f"{code}.json").exists())


if __name__ == "__main__": unittest.main()
