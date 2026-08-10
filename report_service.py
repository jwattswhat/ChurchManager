"""ChurchManager report orchestration."""

from pathlib import Path


class ChurchManagerReportService:
    def __init__(self, jsform, process_service):
        self.jsform = jsform
        self.processes = process_service

    def run_catalog_report(self, report_id, form, connection):
        return self.jsform.RunReport(report_id, form, connection)

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

