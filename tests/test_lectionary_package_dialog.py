"""Contract tests for the protected lectionary package manager."""

import json
from pathlib import Path
import unittest

from main_menu import SPECIAL_CONTROLS
from permission_catalog import MAIN_MENU_PERMISSIONS


class LectionaryPackageDialogTests(unittest.TestCase):
    def test_package_manager_is_protected_and_routed(self):
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
        self.assertIn("Retire Selected", source)
        self.assertIn('("Scope", 120)', source)
        self.assertIn("summary.distribution_scope", source)
        self.assertIn('INCLUDED_PACKAGE_DIRECTORY', source)
        self.assertIn('defaultDir=str(INCLUDED_PACKAGE_DIRECTORY)', source)
        self.assertIn("PrimaryLectionaryEditionID", source)
        self.assertIn("WHERE PackageID=?", source)
        self.assertNotIn("DELETE FROM tblLectionary", source)


if __name__ == "__main__":
    unittest.main()
