"""ChurchManager storage boundary for user-customized visual report designs."""

import os
from pathlib import Path
import shutil
import tempfile

import JSForm
import mariadb

from churchmanager_mode import load_config, resolve_database
from configuration_paths import writable_directory
from report_codes import legacy_report_code
from visual_reports.directory_dataset import DIRECTORY_CONTRACT
from visual_reports.directory_dataset import DirectoryDatasetProvider
from visual_reports.report_inventory import REPORTS_BY_CODE
from visual_reports.tabular_dataset import TabularDatasetProvider, contract_for
from visual_reports.worship_planning_dataset import (
    WORSHIP_PLANNING_CONTRACT, WorshipPlanningDatasetProvider,
)


ROOT = Path(__file__).resolve().parent
STARTERS = ROOT / "definitions"


def source_code_for_definition(definition):
    """Return the approved source report code for a custom report definition."""
    if definition.dataset_name == DIRECTORY_CONTRACT.name:
        return "CMMB01"
    if definition.dataset_name == WORSHIP_PLANNING_CONTRACT.name:
        return "CMWS01"
    for code in REPORTS_BY_CODE:
        if definition.dataset_name == contract_for(code).name:
            return code
    raise ValueError(
        "No approved ChurchManager dataset is registered for {}.".format(
            definition.dataset_name
        )
    )


def contract_for_definition(definition):
    """Resolve a designer contract from stable dataset identity, not report code."""
    code = source_code_for_definition(definition)
    if code == "CMMB01":
        return DIRECTORY_CONTRACT, "directory"
    if code == "CMWS01":
        return WORSHIP_PLANNING_CONTRACT, "worship"
    return contract_for(code), "tabular"


class DirectoryDesignerAuthorization:
    """Explicit test-only authorization for the standalone proof launcher."""

    @staticmethod
    def require(permission, operation=None):
        if permission not in {"reports.design", DIRECTORY_CONTRACT.required_permission}:
            raise PermissionError(operation or permission)


def build_directory_preview(definition, authorization):
    config = load_config()
    database = config["database_settings"]
    settings = resolve_database({
        "server": database["host"], "database": database["database"],
        "user": database["user"], "password": None, "test_mode": True,
    }, config)
    if settings["database"].casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: report preview requires local ChurchDBTest.")
    connection = mariadb.connect(
        host=settings["server"], port=settings["port"], database=settings["database"],
        user=settings["user"], password=settings["password"],
    )
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT ID FROM rpt_church_identity WHERE Church=?",
            ("Reformation Lutheran Church",),
        )
        rows = cursor.fetchall()
        cursor.close()
        if len(rows) != 1:
            raise RuntimeError(
                "Preview requires exactly one Reformation Lutheran Church test record."
            )
        dataset = DirectoryDatasetProvider(
            connection, authorization,
        ).build(rows[0][0])
    finally:
        connection.close()
    output = Path(tempfile.gettempdir()) / "ChurchManager-CMMB01-preview.pdf"
    return JSForm.PDFReportRenderer().render(definition, dataset, output)


def build_tabular_preview(definition, authorization):
    code = source_code_for_definition(definition)
    config = load_config()
    database = config["database_settings"]
    settings = resolve_database({
        "server": database["host"], "database": database["database"],
        "user": database["user"], "password": None, "test_mode": True,
    }, config)
    if settings["database"].casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: report preview requires local ChurchDBTest.")
    connection = mariadb.connect(
        host=settings["server"], port=settings["port"], database=settings["database"],
        user=settings["user"], password=settings["password"],
    )
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT ID FROM rpt_church_identity WHERE Church=?", ("Reformation Lutheran Church",))
        rows = cursor.fetchall()
        cursor.close()
        if len(rows) != 1:
            raise RuntimeError("Preview requires exactly one Reformation Lutheran Church test record.")
        if code == "CMWS01":
            cursor = connection.cursor()
            cursor.execute(
                "SELECT ID FROM rpt_worship_planner_service WHERE ChurchID=? "
                "ORDER BY DateTime DESC,ID DESC LIMIT 1", (rows[0][0],),
            )
            service = cursor.fetchone()
            cursor.close()
            if not service:
                raise RuntimeError("Preview requires a saved test Worship Service.")
            dataset = WorshipPlanningDatasetProvider(
                connection, authorization,
            ).build(rows[0][0], service[0])
        else:
            dataset = TabularDatasetProvider(connection, authorization).build(code, rows[0][0])
    finally:
        connection.close()
    output = Path(tempfile.gettempdir()) / f"ChurchManager-{code}-preview.pdf"
    return JSForm.PDFReportRenderer().render(definition, dataset, output)


def user_definition_path(report_code, local_app_data=None):
    return user_definition_directory(local_app_data) / f"{report_code}.json"


def migrate_saved_definition(report_code, local_app_data=None):
    """Copy a saved pre-standardization layout to its canonical report code."""
    target = user_definition_path(report_code, local_app_data)
    legacy_code = legacy_report_code(report_code)
    if target.exists() or not legacy_code:
        return target
    legacy = user_definition_path(legacy_code, local_app_data)
    if not legacy.is_file():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    content = legacy.read_text(encoding="utf-8")
    content = content.replace(legacy_code, report_code)
    content = content.replace(legacy_code.lower(), report_code.lower())
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(target)
    return target


def user_definition_directory(local_app_data=None):
    base = Path(local_app_data or os.environ["LOCALAPPDATA"])
    return base / "ChurchManager" / "ReportDefinitions"


def ensure_user_definition(report_code, local_app_data=None, starter_directory=None):
    starter = Path(starter_directory or STARTERS) / f"{report_code}.json"
    if not starter.is_file():
        raise FileNotFoundError(f"Starter report definition not found: {report_code}")
    target = migrate_saved_definition(report_code, local_app_data)
    replace_incompatible = False
    if target.exists():
        loader = JSForm.ReportDefinitionLoader()
        current = loader.load(target)
        baseline = loader.load(starter)
        replace_incompatible = (
            current.dataset_name != baseline.dataset_name
            or current.dataset_version != baseline.dataset_version
        )
        if replace_incompatible:
            backup = target.with_suffix(f".v{current.dataset_version}.json.bak")
            shutil.copyfile(target, backup)
    if not target.exists() or replace_incompatible:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(".json.tmp")
        shutil.copyfile(starter, temporary)
        temporary.replace(target)
    JSForm.ReportDefinitionLoader().load(target)
    return target


def resolve_report_definition(report_code, local_app_data=None, starter_directory=None):
    """Use a customization when present; otherwise read the current starter directly."""
    starter = Path(starter_directory or STARTERS) / f"{report_code}.json"
    custom = migrate_saved_definition(report_code, local_app_data)
    selected = custom if custom.is_file() else starter
    if custom.is_file() and starter.is_file():
        loader = JSForm.ReportDefinitionLoader()
        custom_definition = loader.load(custom)
        starter_definition = loader.load(starter)
        if (
            custom_definition.dataset_name != starter_definition.dataset_name
            or custom_definition.dataset_version != starter_definition.dataset_version
        ):
            selected = starter
    if not selected.is_file():
        raise FileNotFoundError(f"Report definition not found: {report_code}")
    JSForm.ReportDefinitionLoader().load(selected)
    return selected


def open_directory_designer(local_app_data=None, authorization=None):
    authorization = authorization or DirectoryDesignerAuthorization()
    authorization.require("reports.design", operation="Open Report Designer")

    def preview(definition):
        return build_directory_preview(definition, authorization)

    def open_definition(path):
        starter = STARTERS / path.name
        if starter.is_file():
            path = ensure_user_definition(path.stem, local_app_data)
        definition = JSForm.ReportDefinitionLoader().load(path)
        contract, dataset_kind = contract_for_definition(definition)
        if dataset_kind == "directory":
            preview_handler = preview
        elif dataset_kind == "worship":
            preview_handler = lambda value: build_tabular_preview(value, authorization)
        else:
            preview_handler = lambda value: build_tabular_preview(value, authorization)
        JSForm.open_report_designer(
            path,
            dataset_contract=contract,
            preview_handler=preview_handler,
            starter_definition_path=starter if starter.is_file() else None,
            export_directory=writable_directory("Reports"),
        )

    return JSForm.open_report_catalog(
        user_definition_directory(local_app_data), STARTERS, open_definition,
    )
