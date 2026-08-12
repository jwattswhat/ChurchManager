"""ChurchManager report orchestration."""

from pathlib import Path


class ChurchManagerReportService:
    def __init__(self, jsform, process_service, access=None, connection_settings=None):
        self.jsform = jsform
        self.processes = process_service
        self.access = access
        self.connection_settings = connection_settings

    def run_catalog_report(self, report_id, form, connection):
        if self.access is None:
            raise RuntimeError("Report authorization is not configured.")
        self.access.require_report(report_id)
        return self.jsform.RunReport(
            report_id, form, connection, self.connection_settings
        )

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
