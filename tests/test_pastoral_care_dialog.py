"""Structural and behavior tests for the safe pastoral-care workflow."""

import json
import unittest
from pathlib import Path

from pastoral_care_dialog import _selected_row_id


ROOT = Path(__file__).resolve().parents[1]


class ChoiceStub:
    def __init__(self, rows, selection):
        self.rows = rows
        self.selection = selection

    def GetSelection(self):
        return self.selection


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
        self.assertEqual(controls["PeopleBox"]["layout"], {"row": 0, "column": 2})

    def test_restricted_note_entry_is_permission_controlled_and_closed_by_default(self):
        self.assertIn("PastoralRestrictedNoteService", self.source)
        self.assertIn('has_permission("pastoral.notes.edit")', self.source)
        self.assertIn("remains closed until explicitly opened", self.source)
        self.assertIn("Restricted Notes...", self.source)

    def test_restricted_note_failures_do_not_enter_support_diagnostics(self):
        restricted = self.source.split("class RestrictedNoteEditorDialog", 1)[1].split(
            "class CareHistoryDialog", 1
        )[0]
        self.assertNotIn("report_exception", restricted)
        self.assertNotIn("safe_context", restricted)

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

    def test_create_failure_logs_only_safe_church_diagnostics(self):
        self.assertIn('operation="pastoral.create_follow_up"', self.source)
        self.assertIn('"church_id_type"', self.source)
        self.assertIn('"church_name"', self.source)
        self.assertNotIn('"safe_summary":', self.source.split("JSForm.report_exception", 1)[1])

    def test_selected_row_is_returned(self):
        self.assertEqual(_selected_row_id(ChoiceStub([(4, "A"), (7, "B")], 1)), 7)

    def test_visible_first_row_is_used_when_wx_loses_selection(self):
        self.assertEqual(_selected_row_id(ChoiceStub([(4, "A"), (7, "B")], -1)), 4)

    def test_empty_choice_has_no_identifier(self):
        self.assertIsNone(_selected_row_id(ChoiceStub([], -1)))


if __name__ == "__main__":
    unittest.main()
