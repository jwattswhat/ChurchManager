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
        # Development intentionally contains only the active JSON screens;
        # obsolete definitions live solely in the frozen Legacy application.
        self.assertGreaterEqual(len(paths), 34)
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
        self.assertGreaterEqual(logo["layout"]["row_span"], 6)
        self.assertTrue(logo["layout"]["expand"])

    def test_member_forms_expose_database_backed_images(self):
        import json

        person = json.loads(Path("Forms/frmPerson.json").read_text(encoding="utf-8"))["frmPersonFORM"]
        family = json.loads(Path("Forms/frmFamily.json").read_text(encoding="utf-8"))["frmFamilyFORM"]
        self.assertIn("Picture", person["FORM"]["table"]["fields"])
        self.assertEqual(person["CONTROLS"]["Picture"]["type"], "ImagePickerCtrl")
        self.assertEqual(person["FORM"]["layout"]["type"], "legacy")
        linked_person_fields = family["FORM"]["linkedform"]["frmPerson"]["table"]["fields"]
        self.assertIn("Picture", linked_person_fields)
        self.assertIn("Image", family["FORM"]["table"]["fields"])
        self.assertEqual(family["CONTROLS"]["Image"]["type"], "ImagePickerCtrl")

    def test_utility_dialogs_have_correct_identity(self):
        import json

        for name in ("frmNotifyviaeMail",):
            form = json.loads(Path("Forms", name + ".json").read_text(encoding="utf-8"))[name + "FORM"]["FORM"]
            self.assertEqual(form["name"], name)
            self.assertIn("Close", form["controls"])
            self.assertIn("CLOSEBOX", form["stylelist"])

    def test_propers_uses_compact_fixed_two_column_layout(self):
        import json

        propers = json.loads(Path("Forms/frmPropers.json").read_text(encoding="utf-8"))["frmPropersFORM"]
        self.assertEqual(propers["FORM"]["layout"]["type"], "legacy")
        self.assertLessEqual(propers["FORM"]["sizech"][1], 35)
        self.assertLessEqual(propers["CONTROLS"]["Theme"]["sizech"][1], 6)
        self.assertLessEqual(propers["CONTROLS"]["dvlHymnSuggestions"]["sizech"][1], 6)
        self.assertNotIn("HymnSug", propers["CONTROLS"])
        self.assertLessEqual(propers["CONTROLS"]["Note"]["sizech"][1], 8)


if __name__ == "__main__": unittest.main()
