"""Contract tests for the protected lectionary package manager."""

import json
from pathlib import Path
import unittest

from main_menu import SPECIAL_CONTROLS
from permission_catalog import MAIN_MENU_PERMISSIONS


class LectionaryPackageDialogTests(unittest.TestCase):
    def test_package_manager_is_protected_and_routed(self):
        form = json.loads(Path("Forms/frmMain.json").read_text(encoding="utf-8"))
        control = form["frmMainFORM"]["CONTROLS"]["lblLectionaryPackages"]
        self.assertEqual(control["security"]["invoke"], "application.config.manage")
        self.assertIn("lblLectionaryPackages", SPECIAL_CONTROLS)
        self.assertEqual(
            MAIN_MENU_PERMISSIONS["lblLectionaryPackages"], "application.config.manage",
        )

    def test_dialog_requires_preview_and_confirmation(self):
        source = Path("lectionary_package_dialog.py").read_text(encoding="utf-8")
        self.assertIn("LectionaryPackageValidator().validate", source)
        self.assertIn("Install / Upgrade", source)
        self.assertIn("wx.NO_DEFAULT", source)
        self.assertIn("application.config.manage", source)


if __name__ == "__main__":
    unittest.main()
