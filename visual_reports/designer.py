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


ROOT = Path(__file__).resolve().parent
STARTERS = ROOT / "definitions"


class DirectoryDesignerAuthorization:
    @staticmethod
    def require(permission, operation=None):
        if permission != DIRECTORY_CONTRACT.required_permission:
            raise PermissionError(operation or permission)


def build_directory_preview(definition):
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
            connection, DirectoryDesignerAuthorization(),
        ).build(rows[0][0])
    finally:
        connection.close()
    output = Path(tempfile.gettempdir()) / "ChurchManager-CMMD01-preview.pdf"
    return JSForm.PDFReportRenderer().render(definition, dataset, output)


def user_definition_path(report_code, local_app_data=None):
    base = Path(local_app_data or os.environ["LOCALAPPDATA"])
    return base / "ChurchManager" / "ReportDefinitions" / f"{report_code}.json"


def ensure_user_definition(report_code, local_app_data=None):
    starter = STARTERS / f"{report_code}.json"
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


def open_directory_designer(local_app_data=None):
    return JSForm.open_report_designer(
        ensure_user_definition("CMMD01", local_app_data),
        dataset_contract=DIRECTORY_CONTRACT,
        preview_handler=build_directory_preview,
        starter_definition_path=STARTERS / "CMMD01.json",
    )
