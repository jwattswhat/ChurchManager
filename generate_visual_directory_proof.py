"""Generate the local ChurchDBTest visual Member Directory proof PDF."""

from pathlib import Path

import mariadb
import JSForm

from churchmanager_mode import load_config, resolve_database
from visual_reports.directory_dataset import DirectoryDatasetProvider


ROOT = Path(__file__).resolve().parent


class DirectoryProofAuthorization:
    @staticmethod
    def require(permission, operation=None):
        if permission != "reports.membership.contact":
            raise PermissionError(operation or permission)


def main():
    config = load_config()
    database = config["database_settings"]
    settings = resolve_database({
        "server": database["host"], "database": database["database"],
        "user": database["user"], "password": None, "test_mode": True,
        "jsform_database": None,
    }, config)
    if settings["database"].casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: visual-report proof requires ChurchDBTest.")
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
                "The ChurchDBTest proof requires exactly one Reformation Lutheran Church record."
            )
        dataset = DirectoryDatasetProvider(
            connection, DirectoryProofAuthorization()
        ).build(rows[0][0])
    finally:
        connection.close()
    definition = JSForm.ReportDefinitionLoader().load(
        ROOT / "visual_reports" / "definitions" / "CMMB01.json"
    )
    output = ROOT / "Reports" / "CMMB01.visual-proof.pdf"
    JSForm.PDFReportRenderer().render(definition, dataset, output)
    print(output)


if __name__ == "__main__":
    main()
