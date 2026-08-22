"""Structural tests for the safe pastoral-care workflow."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PastoralCareDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "pastoral_care_dialog.py").read_text()

    def test_main_menu_is_permission_controlled(self):
        menu = json.loads((ROOT / "Forms" / "frmMain.json").read_text())
        controls = menu["frmMainFORM"]["CONTROLS"]
        self.assertEqual(
            controls["lblPastoralCare"]["security"]["invoke"],
            "pastoral.care.view.assigned",
        )
        self.assertEqual(controls["PastoralCareBox"]["layout"], {"row": 2, "column": 2})

    def test_restricted_note_entry_is_not_exposed(self):
        self.assertNotIn("PastoralRestrictedNoteService", self.source)
        self.assertNotIn("pastoral.notes.edit", self.source)
        self.assertIn("not available in this workflow yet", self.source)

    def test_dashboard_supports_assigned_and_authorized_all_scope(self):
        self.assertIn("service.work_list(scope)", self.source)
        self.assertIn('authorization.has_permission("pastoral.care.view.all")', self.source)

    def test_history_supports_safe_operational_actions(self):
        self.assertIn("Record Action...", self.source)
        self.assertIn("Close - Not Needed", self.source)
        self.assertIn("self.service.assign", self.source)
        self.assertIn("self.service.change_status", self.source)

    def test_native_dialog_buttons_belong_to_their_panel(self):
        self.assertNotIn("CreateStdDialogButtonSizer", self.source)


if __name__ == "__main__":
    unittest.main()
