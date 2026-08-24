"""Keep the Groups workspace connected to permissions and the main menu."""

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]


class GroupDialogContractTests(unittest.TestCase):
    def test_main_menu_exposes_groups_with_groups_permission(self):
        document = json.loads((ROOT / "Forms" / "frmMain.json").read_text(encoding="utf-8"))
        controls = document["frmMainFORM"]["CONTROLS"]
        self.assertEqual("groups.view", controls["lblGroups"]["security"]["invoke"])
        self.assertEqual("groups.attendance.view", controls["lblGroupAttendance"]["security"]["invoke"])

    def test_dialog_uses_native_resizable_workspace(self):
        source = (ROOT / "group_dialog.py").read_text(encoding="utf-8")
        self.assertIn("wx.LC_REPORT", source)
        self.assertIn("wx.RESIZE_BORDER", source)
        self.assertIn("EVT_LIST_ITEM_ACTIVATED", source)
        self.assertIn("Show ended memberships", source)
        self.assertIn('status = "Ends today"', source)


if __name__ == "__main__":
    unittest.main()
