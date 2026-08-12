"""ChurchManager storage boundary for user-customized visual report designs."""

import os
from pathlib import Path
import shutil
import tempfile

import JSForm
import mariadb

from churchmanager_mode import load_config, resolve_database
from visual_reports.directory_dataset import DIRECTORY_CONTRACT
from visual_reports.directory_dataset import DirectoryDatasetProvider
from visual_reports.report_inventory import REPORTS_BY_CODE
from visual_reports.tabular_dataset import TabularDatasetProvider, contract_for


ROOT = Path(__file__).resolve().parent
STARTERS = ROOT / "definitions"


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
        "jsform_database": None,
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
    output = Path(tempfile.gettempdir()) / "ChurchManager-CMMD01-preview.pdf"
    return JSForm.PDFReportRenderer().render(definition, dataset, output)


def build_tabular_preview(definition, authorization):
    code = definition.report_id
    config = load_config()
    database = config["database_settings"]
    settings = resolve_database({
        "server": database["host"], "database": database["database"],
        "user": database["user"], "password": None, "test_mode": True,
        "jsform_database": None,
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
        dataset = TabularDatasetProvider(connection, authorization).build(code, rows[0][0])
    finally:
        connection.close()
    output = Path(tempfile.gettempdir()) / f"ChurchManager-{code}-preview.pdf"
    return JSForm.PDFReportRenderer().render(definition, dataset, output)


def user_definition_path(report_code, local_app_data=None):
    return user_definition_directory(local_app_data) / f"{report_code}.json"


def user_definition_directory(local_app_data=None):
    base = Path(local_app_data or os.environ["LOCALAPPDATA"])
    return base / "ChurchManager" / "ReportDefinitions"


def ensure_user_definition(report_code, local_app_data=None, starter_directory=None):
    starter = Path(starter_directory or STARTERS) / f"{report_code}.json"
    if not starter.is_file():
        raise FileNotFoundError(f"Starter report definition not found: {report_code}")
    target = user_definition_path(report_code, local_app_data)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(".json.tmp")
        shutil.copyfile(starter, temporary)
        temporary.replace(target)
    JSForm.ReportDefinitionLoader().load(target)
    return target


def open_directory_designer(local_app_data=None, authorization=None):
    authorization = authorization or DirectoryDesignerAuthorization()
    authorization.require("reports.design", operation="Open Report Designer")

    def preview(definition):
        return build_directory_preview(definition, authorization)

    for report_code in ("CMMD01", *REPORTS_BY_CODE):
        ensure_user_definition(report_code, local_app_data)

    def open_definition(path):
        starter = STARTERS / path.name
        definition = JSForm.ReportDefinitionLoader().load(path)
        if definition.report_id == "CMMD01":
            contract = DIRECTORY_CONTRACT
            preview_handler = preview
        else:
            contract = contract_for(definition.report_id)
            preview_handler = lambda value: build_tabular_preview(value, authorization)
        JSForm.open_report_designer(
            path,
            dataset_contract=contract,
            preview_handler=preview_handler,
            starter_definition_path=starter if starter.is_file() else None,
            export_directory=ROOT.parent / "Reports",
        )

    return JSForm.open_report_catalog(
        user_definition_directory(local_app_data), STARTERS, open_definition,
    )
