"""Contract tests for approved giving-purpose maintenance."""

import unittest
from pathlib import Path


class GivingPurposeTests(unittest.TestCase):
    def test_main_menu_protects_approved_purpose_maintenance(self):
        menu = Path("Forms/frmMain.json").read_text(encoding="utf-8")
        permissions = Path("permission_catalog.py").read_text(encoding="utf-8")
        self.assertIn('"lblGivingPurposes"', menu)
        self.assertIn('"giving.purposes.manage"', menu)
        self.assertIn('"lblGivingPurposes": "giving.purposes.manage"', permissions)

    def test_purpose_editor_requires_approval_and_control_facts(self):
        source = Path("giving/purpose_dialog.py").read_text(encoding="utf-8")
        self.assertIn("Approving authority is required", source)
        self.assertIn("retains control and discretion", source)
        self.assertIn("AccountType='REVENUE'", source)
        self.assertIn("functional classification", source)
        self.assertIn("FunctionRequirement", source)
        self.assertIn("StatementTreatment", source)


if __name__ == "__main__":
    unittest.main()
