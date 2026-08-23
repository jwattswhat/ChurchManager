"""ChurchManager report orchestration."""

from pathlib import Path

from configuration_paths import writable_directory
from visual_reports.designer import (
    STARTERS, resolve_report_definition, user_definition_directory,
)
from visual_reports.report_inventory import OFFICIAL_CODES
from visual_reports.tabular_dataset import TabularDatasetProvider
from visual_reports.worship_planning_dataset import WorshipPlanningDatasetProvider


class ChurchManagerReportService:
    def __init__(self, jsform, process_service, access=None, connection_settings=None):
        self.jsform = jsform
        self.processes = process_service
        self.access = access
        self.connection_settings = connection_settings

    def run_catalog_report(self, report_id, form, connection):
        """Authorize and render one registered JSForm visual report."""
        if self.access is None:
            raise RuntimeError("Report authorization is not configured.")
        authorized = self.access.require_report(report_id)
        code = authorized[0] if authorized else None
        if code not in OFFICIAL_CODES:
            raise ValueError(
                "Report {} has no approved JSForm visual definition.".format(code)
            )
        return self._run_visual_report(code, form, connection)

    def _run_visual_report(self, code, form, connection):
        definition_path = resolve_report_definition(code)
        definition = self.jsform.ReportDefinitionLoader().load(definition_path)
        controls = form.CONTROLID
        church_id = controls["ChurchID"].GetValue()
        parameters = {}
        for name in (
            "ServiceID", "PersonID", "HymnID", "HymnalID", "StartDate", "EndDate",
            "AttendanceType", "Detail", "MissedWeeks",
        ):
            if name not in controls:
                continue
            try:
                parameters[name] = controls[name].GetValue()
            except (TypeError, ValueError):
                parameters[name] = controls[name].GetValue(format="%Y-%m-%d")
        if definition.dataset_name == "membership.directory":
            from visual_reports.directory_dataset import DirectoryDatasetProvider
            dataset = DirectoryDatasetProvider(connection, self.access.authorization).build(church_id)
        elif code == "CMWP01":
            return self.render_worship_planning(
                church_id, parameters.get("ServiceID"), connection, open_output=True,
            )
        else:
            dataset = TabularDatasetProvider(connection, self.access.authorization).build(
                code, church_id, parameters,
            )
        output = writable_directory("Reports") / f"{code}.pdf"
        rendered = self.jsform.PDFReportRenderer().render(definition, dataset, output)
        self.processes.open_file(rendered)
        return rendered

    def render_worship_planning(
        self, church_id, service_id, connection, *, open_output=False, output=None,
    ):
        """Render a fresh planner for one service, optionally without opening it."""
        definition_path = resolve_report_definition("CMWP01")
        definition = self.jsform.ReportDefinitionLoader().load(definition_path)
        dataset = WorshipPlanningDatasetProvider(
            connection, self.access.authorization,
        ).build(church_id, service_id)
        output = Path(output or (writable_directory("Reports") / "CMWP01.pdf"))
        rendered = self.jsform.PDFReportRenderer().render(definition, dataset, output)
        if open_output:
            self.processes.open_file(rendered)
        return rendered

    def configure_catalog_picker(self, control):
        if self.access is None:
            raise RuntimeError("Report authorization is not configured.")
        customized = set()
        loader = self.jsform.ReportDefinitionLoader()
        for custom in user_definition_directory().glob("*.json"):
            starter = STARTERS / custom.name
            if not starter.is_file():
                customized.add(custom.stem)
                continue
            try:
                if loader.load(custom).to_dict() != loader.load(starter).to_dict():
                    customized.add(custom.stem)
            except Exception:
                customized.add(custom.stem)
        return self.access.configure_picker(control, customized)

    def start_python_report(self, script, settings, extra_arguments=()):
        from churchmanager_mode import connection_arguments

        arguments = connection_arguments(settings) + list(extra_arguments)
        return self.processes.start_python(script, arguments)
