"""ChurchManager report orchestration."""

from pathlib import Path

from visual_reports.designer import ensure_user_definition, resolve_report_definition
from visual_reports.report_inventory import OFFICIAL_CODES
from visual_reports.tabular_dataset import TabularDatasetProvider


class ChurchManagerReportService:
    def __init__(self, jsform, process_service, access=None, connection_settings=None):
        self.jsform = jsform
        self.processes = process_service
        self.access = access
        self.connection_settings = connection_settings

    def run_catalog_report(self, report_id, form, connection):
        if self.access is None:
            raise RuntimeError("Report authorization is not configured.")
        authorized = self.access.require_report(report_id)
        code = authorized[0] if authorized else None
        if code in OFFICIAL_CODES:
            return self._run_visual_report(code, form, connection)
        return self.jsform.RunReport(
            report_id, form, connection, self.connection_settings
        )

    def _run_visual_report(self, code, form, connection):
        definition_path = resolve_report_definition(code)
        definition = self.jsform.ReportDefinitionLoader().load(definition_path)
        controls = form.CONTROLID
        church_id = controls["ChurchID"].GetValue()
        parameters = {}
        for name in (
            "ServiceID", "PersonID", "HymnID", "ProjectID", "StartDate", "EndDate",
            "AttendanceType", "Detail",
        ):
            if name not in controls:
                continue
            try:
                parameters[name] = controls[name].GetValue()
            except (TypeError, ValueError):
                parameters[name] = controls[name].GetValue(format="%Y-%m-%d")
        if code == "CMMD01":
            from visual_reports.directory_dataset import DirectoryDatasetProvider
            dataset = DirectoryDatasetProvider(connection, self.access.authorization).build(church_id)
        else:
            dataset = TabularDatasetProvider(connection, self.access.authorization).build(
                code, church_id, parameters,
            )
        output = Path(__file__).resolve().parent / "Reports" / f"{code}.pdf"
        rendered = self.jsform.PDFReportRenderer().render(definition, dataset, output)
        self.processes.open_file(rendered)
        return rendered

    def configure_catalog_picker(self, control):
        if self.access is None:
            raise RuntimeError("Report authorization is not configured.")
        return self.access.configure_picker(control)

    def start_python_report(self, script, settings, extra_arguments=()):
        from churchmanager_mode import connection_arguments

        arguments = connection_arguments(settings) + list(extra_arguments)
        return self.processes.start_python(script, arguments)

    def run_lime_report(self, template, output, database_name, lime_directory):
        staged, temporary = self.jsform.prepare_lime_report_template(
            template, database_name
        )
        runner = self.jsform.LimeReportProcess(lime_directory)
        try:
            runner.generate(staged, output)
        finally:
            if temporary:
                temporary.unlink(missing_ok=True)
        runner.open_output(output)
        return Path(output)
