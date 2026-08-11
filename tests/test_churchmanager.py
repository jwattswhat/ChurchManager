"""Safe automated checks for ChurchManager-owned code and assets.

These tests deliberately do not import ChurchManager application modules because
several of them connect to the database, create a wx application, write output,
or launch another program at import time.  They also do not inspect or test the
neighboring JSForm package.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import py_compile
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
FORMS = ROOT / "Forms"
REPORTS = ROOT / "LimeReportPattern"

# ChurchManager-owned operational modules. Archived code, saved copies,
# conversion utilities, and JSForm are intentionally absent.
OPERATIONAL_MODULES = (
    "cm.py",
    "fnCMargParse.py",
    "churchmanager_mode.py",
    "application_context.py",
    "authentication.py",
    "authorization.py",
    "bootstrap_test_master.py",
    "form_factory.py",
    "main_menu.py",
    "startup.py",
    "login_dialog.py",
    "user_admin.py",
    "process_service.py",
    "backup_service.py",
    "report_service.py",
    "report_support.py",
    "fnSchedule.py",
    "fnUtil.py",
    "network.py",
    "liccalendar.py",
    "rptAnnouncement.py",
    "rptOrderofService.py",
    "rptPrayers.py",
    "rptMemberDirectory.py",
    "sermon2blogger.py",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_function_without_importing(module_path: Path, function_name: str, globals_: dict):
    """Compile one pure function from a module without executing module setup."""
    tree = ast.parse(module_path.read_text(encoding="utf-8-sig"), filename=str(module_path))
    function = next(
        (node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name),
        None,
    )
    if function is None:
        raise AssertionError(f"{function_name} not found in {module_path.name}")
    isolated = ast.Module(body=[function], type_ignores=[])
    ast.fix_missing_locations(isolated)
    namespace = dict(globals_)
    exec(compile(isolated, str(module_path), "exec"), namespace)
    return namespace[function_name]


class TestChurchManagerPython(unittest.TestCase):
    def test_cm_has_guarded_main_entrypoint(self):
        tree = ast.parse((ROOT / "cm.py").read_text(encoding="utf-8-sig"))
        main_functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
        guards = [
            node for node in tree.body
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "__name__"
        ]
        self.assertEqual(len(main_functions), 1)
        self.assertEqual(len(guards), 1)

    def test_jsform_child_cleanup_ignores_deleted_panels(self):
        close_children = load_function_without_importing(
            Path(r"C:\Users\Pastor\Documents\JSForm\clsForm.py"),
            "_close_child_forms",
            {},
        )

        class LivePanel:
            def __init__(self):
                self.closed = False

            def IsBeingDeleted(self):
                return False

            def Close(self):
                self.closed = True

        class DeletedPanel:
            def IsBeingDeleted(self):
                raise RuntimeError("wrapped C/C++ object has been deleted")

        live = type("Child", (), {"FORM": LivePanel()})()
        deleted = type("Child", (), {"FORM": DeletedPanel()})()
        children = {"live": live, "deleted": deleted}

        close_children(object(), children)

        self.assertEqual(children, {})
        self.assertTrue(live.FORM.closed)

    def test_operational_modules_compile(self):
        with tempfile.TemporaryDirectory(prefix="churchmanager_compile_") as cache_dir:
            for relative in OPERATIONAL_MODULES:
                source = ROOT / relative
                with self.subTest(module=relative):
                    self.assertTrue(source.is_file(), f"Missing ChurchManager module: {relative}")
                    target = Path(cache_dir) / f"{source.stem}.pyc"
                    py_compile.compile(str(source), cfile=str(target), doraise=True)

    def test_report_week_calculation_boundaries(self):
        expected = {
            date(2026, 8, 1): 1,
            date(2026, 8, 2): 1,
            date(2026, 8, 8): 2,
            date(2026, 8, 9): 2,
            date(2026, 8, 30): 5,
            date(2026, 9, 1): 1,
            date(2026, 9, 7): 2,
        }
        function = load_function_without_importing(
            ROOT / "report_support.py", "get_week_of_month", {}
        )
        for value, week in expected.items():
            with self.subTest(value=value):
                self.assertEqual(function(value), week)

    def test_report_date_override(self):
        function = load_function_without_importing(
            ROOT / "report_support.py", "get_today",
            {"datetime": datetime, "date": date},
        )
        self.assertEqual(
            function({"testing": {"override_today": "2026-08-09"}}),
            date(2026, 8, 9),
        )

    def test_command_line_reports_have_guarded_entrypoints(self):
        for module_name in ("rptAnnouncement.py", "rptPrayers.py"):
            source = (ROOT / module_name).read_text(encoding="utf-8-sig")
            with self.subTest(module=module_name):
                self.assertIn('if __name__ == "__main__":', source)

    def test_schedule_serialized_list_conversion(self):
        function = load_function_without_importing(ROOT / "fnSchedule.py", "strtolist", {})
        self.assertIsNone(function(None))
        self.assertEqual(function("Reader"), "Reader")
        self.assertEqual(function("[Reader\rUsher\rAcolyte]"), ["Reader", "Usher", "Acolyte"])
        self.assertEqual(function("[Reader\rUsher\n]"), ["Reader", "Usher"])

    def test_order_of_service_placeholder_helpers(self):
        get_name = load_function_without_importing(ROOT / "rptOrderofService.py", "getimbedname", {})
        search_records = load_function_without_importing(ROOT / "rptOrderofService.py", "searchrecrods", {})
        self.assertEqual(get_name("Hymn: {Entrance}"), "Entrance")
        self.assertEqual(get_name("{Gospel}"), "Gospel")
        self.assertIsNone(get_name("No placeholder"))
        records = [(1, "Entrance", 14), (2, "Closing", 22)]
        self.assertEqual(search_records("Closing", records), records[1])
        self.assertIsNone(search_records("Communion", records))

    def test_sermon_docx_conversion_uses_expected_html_markers(self):
        function = load_function_without_importing(
            ROOT / "sermon2blogger.py", "convert_docx_to_text", {"Document": Document}
        )
        with tempfile.TemporaryDirectory(prefix="churchmanager_sermon_") as folder:
            source = Path(folder) / "sample.docx"
            output = Path(folder) / "sample.txt"
            document = Document()
            document.add_paragraph("Opening paragraph")
            quote_style = document.styles.add_style("Bible Quote", 1)
            quote_style.base_style = document.styles["Normal"]
            document.add_paragraph("For God so loved the world", style="Bible Quote")
            document.add_paragraph("")
            document.save(source)
            function(source, output)
            converted = output.read_text(encoding="utf-8")
            self.assertIn("Opening paragraph<br><br>", converted)
            self.assertIn("<blockquote>For God so loved the world</blockquote>", converted)


class TestChurchManagerConfiguration(unittest.TestCase):
    def test_main_menu_router_dispatches_forms_and_special_actions(self):
        from main_menu import MainMenuRouter

        opened = []
        special = []
        factory = type("Factory", (), {"open": lambda self, name: opened.append(name) or name})()
        router = MainMenuRouter(factory, {"lblBackupDB": lambda: special.append("backup")})
        self.assertEqual(router.dispatch("lblSermon"), "frmSermon")
        router.dispatch("lblBackupDB")
        self.assertEqual(opened, ["frmSermon"])
        self.assertEqual(special, ["backup"])

    def test_form_factory_preserves_parent_connection_and_controls(self):
        from form_factory import ChurchManagerFormFactory

        created = []

        class Form:
            def __init__(self, *arguments):
                created.append(arguments)
                self.shown = False

            def show(self):
                self.shown = True

        factory = ChurchManagerFormFactory(Form, "connection", "parent")
        form = factory.open("frmExample", ["Close"])
        self.assertEqual(created, [("parent", "connection", "frmExample", ["Close"])])
        self.assertTrue(form.shown)
    def test_configuration_has_required_sections(self):
        config = load_json(ROOT / "churchmanager.json")
        self.assertIn("database_settings", config)
        self.assertIn("testing", config)
        self.assertTrue({"host", "database", "user", "credential_target"}.issubset(config["database_settings"]))
        self.assertNotIn("password", config["database_settings"])

    def test_testing_override_is_blank_or_iso_date(self):
        config = load_json(ROOT / "churchmanager.json")
        override = config.get("testing", {}).get("override_today")
        if override:
            datetime.strptime(override, "%Y-%m-%d")

    def test_test_mode_selects_an_isolated_database(self):
        from churchmanager_mode import resolve_database

        config = load_json(ROOT / "churchmanager.json")
        resolved = resolve_database(
            {"database": "ChurchDB", "test_mode": True, "password": None},
            config,
            lambda target: ("church", "not-a-real-password"),
        )
        self.assertEqual(resolved["database"], "ChurchDBTest")
        self.assertEqual(resolved["jsform_database"], "JSFormTest")
        self.assertEqual(resolved["server"], "127.0.0.1")
        self.assertEqual(resolved["credential_target"], "ChurchManager/LocalTestAdmin")
        self.assertNotEqual(
            resolved["database"].casefold(),
            config["database_settings"]["database"].casefold(),
        )

    def test_test_mode_refuses_production_database(self):
        from churchmanager_mode import resolve_database

        unsafe_config = {
            "database_settings": {"database": "ChurchDB"},
            "testing": {"host": "127.0.0.1", "database": "churchdb"},
        }
        with self.assertRaisesRegex(RuntimeError, "production database"):
            resolve_database(
                {"database": "ChurchDB", "test_mode": True}, unsafe_config,
                lambda target: ("church", "not-a-real-password"),
            )

    def test_test_mode_refuses_production_jsform_database(self):
        from churchmanager_mode import resolve_database

        unsafe_config = {
            "database_settings": {
                "database": "ChurchDB",
                "jsform_database": "JSForm",
            },
            "testing": {
                "host": "127.0.0.1",
                "database": "ChurchDBTest",
                "jsform_database": "jsform",
            },
        }
        with self.assertRaisesRegex(RuntimeError, "JSForm test database"):
            resolve_database(
                {"database": "ChurchDB", "test_mode": True}, unsafe_config,
                lambda target: ("church", "not-a-real-password"),
            )

    def test_database_password_comes_from_credential_store(self):
        from churchmanager_mode import resolve_database

        config = load_json(ROOT / "churchmanager.json")
        requested = []

        def fake_reader(target):
            requested.append(target)
            return "church", "stored-secret"

        resolved = resolve_database(
            {
                "database": "ChurchDB",
                "user": "church",
                "password": None,
                "test_mode": False,
                "jsform_database": None,
            },
            config,
            fake_reader,
        )
        self.assertEqual(requested, ["ChurchManager/Production"])
        self.assertEqual(resolved["password"], "stored-secret")

    def test_argument_parser_accepts_test_switch(self):
        import fnCMargParse

        parsed = fnCMargParse.CMargs(
            "ChurchManager", "test", ["database", "test_mode"], ["--test"]
        )
        self.assertTrue(parsed["test_mode"])

    def test_test_mode_title_is_applied_to_window_not_panel(self):
        source = (ROOT / "startup.py").read_text(encoding="utf-8-sig")
        self.assertIn("main_form.FRAME.SetTitle(", source)
        self.assertNotIn("main_form.FORM.SetTitle", source)

    def test_user_security_is_enabled_only_for_development_test_mode(self):
        from startup import security_enabled

        config = {
            "security": {"testing_enabled": True, "production_enabled": False}
        }
        self.assertTrue(security_enabled({"test_mode": True}, config))
        self.assertFalse(security_enabled({"test_mode": False}, config))

    def test_test_mode_uses_relaxed_password_length_only_at_composition_root(self):
        source = (ROOT / "startup.py").read_text(encoding="utf-8-sig")
        self.assertIn('minimum_length=4 if arguments["test_mode"] else 12', source)


class TestChurchManagerForms(unittest.TestCase):
    def test_service_propers_lookup_displays_text_and_stores_id(self):
        definition = load_json(FORMS / "frmService.json")["frmServiceFORM"]
        control = definition["CONTROLS"]["PropersID"]
        lookup = control["lookupchoices"]
        self.assertEqual(control["type"], "ComboBox")
        self.assertEqual(lookup["name"], "vwPropersLookup")
        self.assertEqual(lookup["fields"], ["ID", "DisplayName"])
        self.assertNotIn("condition", lookup)
        self.assertNotIn("btnChangeLectionary", definition["CONTROLS"])
        self.assertNotIn("frmOptions", definition["FORM"]["linkedform"])

    def test_propers_use_reusable_lectionary_system_and_optional_cycle(self):
        definition = load_json(FORMS / "frmPropers.json")["frmPropersFORM"]
        controls = definition["CONTROLS"]
        self.assertIn("LectionarySystemID", controls)
        self.assertEqual(controls["Cycle"]["choices"], ["A", "B", "C"])
        self.assertNotIn("Lectionary", controls)
        self.assertEqual(
            controls["LectionarySystemID"]["lookupchoices"]["name"],
            "tblLectionarySystem",
        )
        self.assertIn("frmLectionarySystem", definition["FORM"]["linkedform"])

    def test_schedule_reads_season_by_name_not_propers_column_position(self):
        source = (ROOT / "fnSchedule.py").read_text(encoding="utf-8-sig")
        self.assertIn("SELECT Season FROM tblPropers", source)
        self.assertNotIn("SELECT * FROM tblPropers WHERE ID=%s", source)

    def test_user_administration_is_a_protected_main_menu_action(self):
        definition = next(iter(load_json(FORMS / "frmMain.json").values()))
        control = definition["CONTROLS"]["lblUsers"]
        self.assertEqual(control["security"]["invoke"], "security.users.manage")
        from main_menu import MENU_CONTROLS
        self.assertIn("lblUsers", MENU_CONTROLS)

    def test_every_main_menu_action_declares_its_catalog_permission(self):
        from main_menu import MENU_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS

        controls = load_json(FORMS / "frmMain.json")["frmMainFORM"]["CONTROLS"]
        self.assertEqual(set(MENU_CONTROLS), set(MAIN_MENU_PERMISSIONS))
        for control_name, permission in MAIN_MENU_PERMISSIONS.items():
            self.assertEqual(
                controls[control_name]["security"]["invoke"], permission,
                control_name,
            )

    def test_main_menu_dispatch_rechecks_permissions(self):
        source = (ROOT / "cm.py").read_text(encoding="utf-8-sig")
        self.assertIn("MAIN_MENU_PERMISSIONS[select]", source)
        self.assertIn("context.authorization.require(", source)

    def test_main_menu_provides_current_user_password_change_and_logout(self):
        from main_menu import SESSION_CONTROLS

        controls = load_json(FORMS / "frmMain.json")["frmMainFORM"]["CONTROLS"]
        self.assertEqual(SESSION_CONTROLS, {"lblChangePassword", "lblLogout"})
        self.assertIn("lblCurrentUser", controls)
        self.assertIn("LOGOUT", (ROOT / "cm.py").read_text(encoding="utf-8-sig"))

    def test_chart_of_accounts_is_a_protected_jsform_route(self):
        from main_menu import FORM_ROUTES

        self.assertEqual(FORM_ROUTES["lblAccountingAccounts"], "frmAccountingAccount")
        definition = load_json(FORMS / "frmAccountingAccount.json")[
            "frmAccountingAccountFORM"
        ]
        security = definition["FORM"]["security"]
        self.assertEqual(
            set(security.values()), {"accounting.master_data.manage"}
        )
        fields = definition["FORM"]["table"]["fields"]
        self.assertEqual(fields, ["*"])

    def test_funds_are_a_protected_jsform_route(self):
        from main_menu import FORM_ROUTES

        self.assertEqual(FORM_ROUTES["lblAccountingFunds"], "frmAccountingFund")
        definition = load_json(FORMS / "frmAccountingFund.json")[
            "frmAccountingFundFORM"
        ]
        self.assertEqual(
            set(definition["FORM"]["security"].values()),
            {"accounting.master_data.manage"},
        )
        controls = definition["CONTROLS"]
        self.assertIn("WITH_DONOR_RESTRICTIONS", controls["NetAssetClass"]["choices"])
        self.assertIn("BoardDesignated", controls)

    def test_functions_are_a_protected_jsform_route(self):
        from main_menu import FORM_ROUTES

        self.assertEqual(
            FORM_ROUTES["lblAccountingFunctions"], "frmAccountingFunction"
        )
        definition = load_json(FORMS / "frmAccountingFunction.json")[
            "frmAccountingFunctionFORM"
        ]
        self.assertEqual(
            set(definition["FORM"]["security"].values()),
            {"accounting.master_data.manage"},
        )
        choices = definition["CONTROLS"]["FunctionClass"]["choices"]
        self.assertEqual(
            choices, ["PROGRAM", "MANAGEMENT_GENERAL", "FUNDRAISING"]
        )

    def test_fiscal_years_and_periods_protect_status_overrides(self):
        from main_menu import FORM_ROUTES

        expected = {
            "lblAccountingYears": "frmAccountingFiscalYear",
            "lblAccountingPeriods": "frmAccountingFiscalPeriod",
        }
        for control_name, form_name in expected.items():
            self.assertEqual(FORM_ROUTES[control_name], form_name)
            definition = load_json(FORMS / (form_name + ".json"))[
                form_name + "FORM"
            ]
            self.assertEqual(
                definition["CONTROLS"]["Status"]["security"]["edit"],
                "accounting.periods.override",
            )
            self.assertEqual(
                set(definition["FORM"]["security"].values()),
                {"accounting.master_data.manage"},
            )
        main_controls = load_json(FORMS / "frmMain.json")["frmMainFORM"]["CONTROLS"]
        box = main_controls["FundAccountingBox"]
        left, top = box["posch"]
        width, height = box["sizech"]
        for name in ("lblAccountingYears", "lblAccountingPeriods"):
            x, y = main_controls[name]["posch"]
            self.assertTrue(left < x < left + width, name)
            self.assertTrue(top < y < top + height, name)

    def test_transaction_entry_is_a_protected_special_workflow(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS

        self.assertIn("lblAccountingTransactions", SPECIAL_CONTROLS)
        self.assertEqual(
            MAIN_MENU_PERMISSIONS["lblAccountingTransactions"],
            "accounting.transactions.create",
        )
        controls = load_json(FORMS / "frmMain.json")["frmMainFORM"]["CONTROLS"]
        self.assertEqual(
            controls["lblAccountingTransactions"]["security"]["invoke"],
            "accounting.transactions.create",
        )
        source = (ROOT / "cm.py").read_text(encoding="utf-8-sig")
        self.assertIn("show_accounting_draft_entry(", source)

    def test_transaction_review_is_a_protected_special_workflow(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS

        self.assertIn("lblAccountingReview", SPECIAL_CONTROLS)
        self.assertEqual(
            MAIN_MENU_PERMISSIONS["lblAccountingReview"],
            "accounting.transactions.approve",
        )
        controls = load_json(FORMS / "frmMain.json")["frmMainFORM"]["CONTROLS"]
        self.assertEqual(
            controls["lblAccountingReview"]["security"]["invoke"],
            "accounting.transactions.approve",
        )

    def test_transaction_posting_is_a_protected_special_workflow(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS

        self.assertIn("lblAccountingPosting", SPECIAL_CONTROLS)
        self.assertEqual(
            MAIN_MENU_PERMISSIONS["lblAccountingPosting"],
            "accounting.transactions.post",
        )
        controls = load_json(FORMS / "frmMain.json")["frmMainFORM"]["CONTROLS"]
        self.assertEqual(
            controls["lblAccountingPosting"]["security"]["invoke"],
            "accounting.transactions.post",
        )

    def test_posted_register_is_a_protected_special_workflow(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertIn("lblAccountingRegister", SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingRegister"],
                         "accounting.transactions.view")
        controls = load_json(FORMS / "frmMain.json")["frmMainFORM"]["CONTROLS"]
        self.assertEqual(controls["lblAccountingRegister"]["security"]["invoke"],
                         "accounting.transactions.view")

    def test_trial_balance_is_a_protected_special_workflow(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertIn("lblAccountingTrialBalance", SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingTrialBalance"], "accounting.reports.run")
        controls = load_json(FORMS / "frmMain.json")["frmMainFORM"]["CONTROLS"]
        self.assertEqual(controls["lblAccountingTrialBalance"]["security"]["invoke"], "accounting.reports.run")

    def test_financial_position_is_a_protected_special_workflow(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertIn("lblAccountingPosition",SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingPosition"],"accounting.reports.run")
        controls=load_json(FORMS/"frmMain.json")["frmMainFORM"]["CONTROLS"]
        self.assertEqual(controls["lblAccountingPosition"]["security"]["invoke"],"accounting.reports.run")

    def test_statement_of_activities_is_a_protected_special_workflow(self):
        from main_menu import SPECIAL_CONTROLS
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertIn("lblAccountingActivities",SPECIAL_CONTROLS)
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingActivities"],"accounting.reports.run")
        controls=load_json(FORMS/"frmMain.json")["frmMainFORM"]["CONTROLS"]
        self.assertEqual(controls["lblAccountingActivities"]["security"]["invoke"],"accounting.reports.run")

    def test_bank_accounts_are_protected_jsform_master_data(self):
        from main_menu import FORM_ROUTES
        from permission_catalog import MAIN_MENU_PERMISSIONS
        self.assertEqual(FORM_ROUTES["lblAccountingBankAccounts"],"frmAccountingBankAccount")
        self.assertEqual(MAIN_MENU_PERMISSIONS["lblAccountingBankAccounts"],"accounting.master_data.manage")
        form=load_json(FORMS/"frmAccountingBankAccount.json")["frmAccountingBankAccountFORM"]
        self.assertEqual(form["FORM"]["table"]["name"],"tblAccountingBankAccount")
        lookup=form["CONTROLS"]["AccountID"]["lookupchoices"]
        self.assertIn("AccountType = 'ASSET'",lookup["condition"])
        self.assertIn("last four digits",form["CONTROLS"]["AccountLastFour"]["tooltip"])
        controls=load_json(FORMS/"frmMain.json")["frmMainFORM"]["CONTROLS"]
        box=controls["FundAccountingBox"]; top=box["posch"][1]; bottom=top+box["sizech"][1]
        self.assertTrue(top < controls["lblAccountingActivities"]["posch"][1] < bottom)

    def test_forms_match_jsform_canonical_schema(self):
        from jsonschema import validate

        schema_path = Path(r"C:\Users\Pastor\Documents\JSForm\schema\unified_schema.json")
        schema = load_json(schema_path)
        for path in sorted(FORMS.glob("*.json")):
            with self.subTest(form=path.name):
                validate(instance=load_json(path), schema=schema)

    def test_all_application_forms_are_valid_json(self):
        files = sorted(FORMS.glob("*.json"))
        self.assertGreater(files, [], "No ChurchManager form definitions found")
        for path in files:
            with self.subTest(form=path.name):
                load_json(path)

    def test_form_filename_matches_top_level_definition(self):
        for path in sorted(FORMS.glob("*.json")):
            data = load_json(path)
            expected = f"{path.stem}FORM".casefold()
            with self.subTest(form=path.name):
                self.assertIn(expected, {key.casefold() for key in data})

    def test_forms_have_form_and_controls_sections(self):
        for path in sorted(FORMS.glob("*.json")):
            data = load_json(path)
            with self.subTest(form=path.name):
                self.assertEqual(len(data), 1, "Expected one top-level form definition")
                definition = next(iter(data.values()))
                self.assertIsInstance(definition.get("FORM"), dict)
                self.assertIsInstance(definition.get("CONTROLS"), dict)

    def test_open_file_actions_reference_local_controls(self):
        for path in sorted(FORMS.glob("*.json")):
            definition = next(iter(load_json(path).values()))
            controls = definition.get("CONTROLS", {})
            for control_key, control in controls.items():
                action = control.get("action") if isinstance(control, dict) else None
                if isinstance(action, list) and len(action) > 1 and action[0] == "openfile":
                    with self.subTest(form=path.name, control=control_key):
                        self.assertIn(action[1], controls)

    def test_linked_form_actions_reference_churchmanager_form_files(self):
        available = {path.stem.casefold() for path in FORMS.glob("*.json")}
        for path in sorted(FORMS.glob("*.json")):
            definition = next(iter(load_json(path).values()))
            for control_key, control in definition.get("CONTROLS", {}).items():
                action = control.get("action") if isinstance(control, dict) else None
                if isinstance(action, list) and len(action) > 1 and action[0] == "openlinkedform":
                    with self.subTest(form=path.name, control=control_key):
                        self.assertIn(action[1].casefold(), available)

    def test_file_picker_directories_have_section_and_key(self):
        for path in sorted(FORMS.glob("*.json")):
            definition = next(iter(load_json(path).values()))
            for control_key, control in definition.get("CONTROLS", {}).items():
                if isinstance(control, dict) and control.get("type") == "FilePickerCtrl":
                    directory = control.get("directory")
                    with self.subTest(form=path.name, control=control_key):
                        self.assertIsInstance(directory, list)
                        self.assertEqual(len(directory), 2)
                        self.assertTrue(all(isinstance(value, str) and value for value in directory))

    def test_bound_main_menu_controls_exist(self):
        from main_menu import MENU_CONTROLS

        bound = set(MENU_CONTROLS)
        main = next(iter(load_json(FORMS / "frmMain.json").values()))
        controls = set(main["CONTROLS"])
        self.assertGreater(bound, set(), "No ChurchManager main-menu bindings found")
        self.assertEqual(bound - controls, set(), "cm.py binds controls missing from frmMain.json")

    def test_main_menu_has_explicit_three_column_dashboard(self):
        main = next(iter(load_json(FORMS / "frmMain.json").values()))
        controls = main["CONTROLS"]
        expected = {
            "ChurchBox": (0, 0), "ServiceBox": (1, 0), "MemberBox": (2, 0),
            "ReportBox": (0, 1), "AttendanceBox": (1, 1), "ProjectBox": (2, 1),
            "AdministrationBox": (3, 1), "UtilitiesBox": (0, 2),
            "JSFormUtilitiesBox": (1, 2), "EnhancementsBox": (2, 2),
        }
        actual = {
            name: (controls[name]["layout"]["row"], controls[name]["layout"]["column"])
            for name in expected
        }
        self.assertEqual(actual, expected)

    def test_removed_financial_features_are_not_exposed(self):
        removed_forms = {
            "frmBudget", "frmFund", "frmLedger", "frmCheckRegister",
            "frmGivingRegister", "frmEnvelope", "frmDonor", "frmDonorGift",
            "frmPostCheck", "frmPostGiving",
        }
        removed_controls = {
            "AccountingBox", "DonorBox", "lblChartofAccounts", "lblBudget",
            "lblLedger", "lblCheckRegister", "lblGivingRegister", "lblEnvelope",
            "lblDonor", "lblDonorGift",
        }
        removed_reports = {"CFCA01", "CFCR01", "CFGR01", "CMDN01", "CMDN02"}

        from main_menu import FORM_ROUTES

        main = next(iter(load_json(FORMS / "frmMain.json").values()))
        reports = next(iter(load_json(FORMS / "frmReports.json").values()))
        report_filter = reports["CONTROLS"]["ReportID"]["lookupchoices"]["condition"]

        self.assertTrue(removed_forms.isdisjoint({path.stem for path in FORMS.glob("*.json")}))
        self.assertTrue(removed_controls.isdisjoint(main["CONTROLS"]))
        self.assertTrue(removed_forms.isdisjoint(FORM_ROUTES.values()))
        self.assertTrue(removed_reports.isdisjoint({path.stem for path in REPORTS.glob("*.lrxml")}))
        for report_code in removed_reports:
            self.assertIn(report_code, report_filter)


class TestChurchManagerReportAssets(unittest.TestCase):
    def test_lime_report_test_template_changes_database_without_changing_source(self):
        function = load_function_without_importing(
            Path(r"C:\Users\Pastor\Documents\JSForm\fnReport.py"),
            "prepare_lime_report_template",
            {"Path": Path, "re": re, "tempfile": tempfile},
        )
        with tempfile.TemporaryDirectory(prefix="lime_report_mode_") as folder:
            source = Path(folder) / "sample.lrxml"
            original = '<databaseName Type="QString">ChurchDB</databaseName>'
            source.write_text(original, encoding="utf-8")
            staged_name, temporary = function(source, "ChurchDBTest")
            staged = Path(staged_name)
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertIn(">ChurchDBTest</databaseName>", staged.read_text(encoding="utf-8"))
            self.assertIsNotNone(temporary)
            temporary.unlink(missing_ok=True)

    def test_report_patterns_are_well_formed_xml(self):
        files = sorted(REPORTS.glob("*.lrxml")) + sorted(REPORTS.glob("*.lrsml"))
        self.assertGreater(files, [], "No ChurchManager report patterns found")
        for path in files:
            with self.subTest(report=path.name):
                ET.parse(path)

    def test_report_codes_are_unique_ignoring_case(self):
        files = sorted(REPORTS.glob("*.lrxml")) + sorted(REPORTS.glob("*.lrsml"))
        codes = [path.stem.casefold() for path in files]
        self.assertEqual(len(codes), len(set(codes)), "Duplicate ChurchManager report code")


if __name__ == "__main__":
    unittest.main()
