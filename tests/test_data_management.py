"""Tests for guarded membership data management."""

import json
from pathlib import Path
import unittest

from data_management import duplicate_pairs, normalized_contact, normalized_text


ROOT = Path(__file__).resolve().parents[1]


class DataManagementTests(unittest.TestCase):
    def test_comparison_normalization_is_exact_but_presentation_neutral(self):
        self.assertEqual(normalized_text("  Sarah  O'Neil "), "sarah o neil")
        self.assertEqual(normalized_contact("(218) 555-0100"), "2185550100")
        self.assertEqual(normalized_contact(" Sarah@Example.COM "), "sarah@example.com")

    def test_duplicate_pairs_ignore_blanks_and_do_not_self_match(self):
        rows = [(1, "Sarah Johnson", 1), (2, "Sarah  Johnson", 1), (3, "", 1)]
        found = duplicate_pairs(
            rows, lambda row: (row[2], normalized_text(row[1])), "Person", "Same full name"
        )
        self.assertEqual(len(found), 1)
        self.assertEqual((found[0].first_id, found[0].second_id), (1, 2))

    def test_main_menu_opens_data_management_with_membership_permission(self):
        controls = json.loads((ROOT / "Forms" / "frmMain.json").read_text(encoding="utf-8"))[
            "frmMainFORM"
        ]["CONTROLS"]
        self.assertEqual(
            controls["lblDataManagement"]["security"]["invoke"], "membership.manage"
        )
        menu = (ROOT / "main_menu.py").read_text(encoding="utf-8")
        application = (ROOT / "cm.py").read_text(encoding="utf-8")
        permissions = (ROOT / "permission_catalog.py").read_text(encoding="utf-8")
        self.assertIn('"lblDataManagement"', menu)
        self.assertIn('case "lblDataManagement"', application)
        self.assertIn('"lblDataManagement": "membership.manage"', permissions)

    def test_specification_requires_preview_privacy_and_human_review(self):
        specification = (ROOT / "Documentation" / "ChurchManager.DataManagement.Specification.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Import preview never writes", specification)
        self.assertIn("never silently merges", specification)
        self.assertIn("unlisted contact", specification)
        self.assertIn("Portable archives", specification)


if __name__ == "__main__":
    unittest.main()
