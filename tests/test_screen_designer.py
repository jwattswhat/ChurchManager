from pathlib import Path
import tempfile
import unittest

from authorization import AuthorizationDenied, UserSession
from churchmanager_screen_designer import (
    ensure_user_screen, open_churchmanager_screen_designer,
    security_audit_hook, user_screen_directory,
)


class Authorization:
    def __init__(self, allowed): self.allowed = allowed; self.checked = []
    def require(self, permission, operation=None):
        self.checked.append(permission)
        if permission not in self.allowed: raise AuthorizationDenied(permission)


class TestChurchManagerScreenDesigner(unittest.TestCase):
    def test_every_churchmanager_form_loads_and_round_trips_in_designer_model(self):
        import JSForm

        loader = JSForm.ScreenDefinitionLoader()
        paths = sorted(Path("Forms").glob("*.json"))
        self.assertGreaterEqual(len(paths), 60)
        for path in paths:
            with self.subTest(form=path.name):
                model = JSForm.ScreenDesignerModel(loader.load(path))
                model.validated_definition()
                self.assertEqual(model.form.get("theme"), "churchmanager")

    def test_security_audit_uses_mysql_connector_parameter_markers(self):
        class Cursor:
            def __init__(self): self.call = None
            def execute(self, sql, values): self.call = (sql, values)
            def close(self): pass

        class MySQLConnection:
            __module__ = "mysql.connector.connection_cext"
            def __init__(self): self.cursor_value = Cursor(); self.committed = False
            def cursor(self): return self.cursor_value
            def commit(self): self.committed = True

        class Session:
            user_id = 1
            workstation = "TEST"

        connection = MySQLConnection()
        security_audit_hook(connection, Session())("SCREEN_DESIGN_OPENED", "frmMain.json")
        sql, values = connection.cursor_value.call
        self.assertEqual(sql.count("%s"), 7)
        self.assertNotIn("?", sql)
        self.assertEqual(len(values), 7)
        self.assertTrue(connection.committed)

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

    def test_church_logo_uses_the_open_upper_right_area(self):
        import json

        form = json.loads(Path("Forms/frmChurch.json").read_text(encoding="utf-8"))["frmChurchFORM"]
        label = form["CONTROLS"]["lblLogo"]
        logo = form["CONTROLS"]["Logo"]
        self.assertGreaterEqual(label["posch"][0], 30)
        self.assertGreaterEqual(logo["posch"][0], 30)
        self.assertLess(logo["posch"][1], form["CONTROLS"]["Note"]["posch"][1])


if __name__ == "__main__": unittest.main()
