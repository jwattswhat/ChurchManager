from pathlib import Path
import tempfile
import unittest

from authorization import AuthorizationDenied, UserSession
from churchmanager_screen_designer import ensure_user_screen, open_churchmanager_screen_designer, user_screen_directory


class Authorization:
    def __init__(self, allowed): self.allowed = allowed; self.checked = []
    def require(self, permission, operation=None):
        self.checked.append(permission)
        if permission not in self.allowed: raise AuthorizationDenied(permission)


class TestChurchManagerScreenDesigner(unittest.TestCase):
    def test_test_and_production_customizations_are_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertNotEqual(user_screen_directory(True, folder), user_screen_directory(False, folder))
            self.assertIn("TestScreenDefinitions", str(user_screen_directory(True, folder)))

    def test_starter_is_copied_without_overwriting_source(self):
        with tempfile.TemporaryDirectory() as folder:
            target = ensure_user_screen("frmMain", True, folder)
            source = Path("Forms/frmMain.json").read_text(encoding="utf-8")
            target.write_text(target.read_text(encoding="utf-8").replace("Church Manager", "Custom", 1), encoding="utf-8")
            self.assertEqual(ensure_user_screen("frmMain", True, folder), target)
            self.assertEqual(Path("Forms/frmMain.json").read_text(encoding="utf-8"), source)

    def test_launch_requires_screen_design_permission_before_catalog(self):
        authorization = Authorization(set())
        with self.assertRaises(AuthorizationDenied):
            open_churchmanager_screen_designer(None, None, authorization, True)
        self.assertEqual(authorization.checked, ["screens.design"])

    def test_main_menu_and_migration_use_sensitive_permission(self):
        import json
        from main_menu import MENU_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        definition = json.loads(Path("Forms/frmMain.json").read_text(encoding="utf-8"))["frmMainFORM"]
        self.assertEqual(definition["CONTROLS"]["lblScreenDesigner"]["security"]["invoke"], "screens.design")
        self.assertIn("lblScreenDesigner", MENU_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblScreenDesigner"], "screens.design")
        sql = Path("migrations/021_add_screen_designer_permission.sql").read_text(encoding="utf-8")
        self.assertIn("'screens.design'", sql)
        self.assertIn("IsSensitive,Active", sql)
        self.assertIn("Master Administrator", sql)


if __name__ == "__main__": unittest.main()
