"""Protected PDF generation for Giving reports."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import JSForm

from configuration_paths import writable_directory
from process_service import ProcessService
from giving.report_service import GivingReportService


DEFINITIONS = Path(__file__).resolve().parent / "report_definitions"
OUTPUTS = writable_directory("Reports")


def field(name, label, data_type="text"):
    return JSForm.ReportField(name, label, data_type)


BATCH_SUMMARY_CONTRACT = JSForm.ReportDatasetContract(
    "giving.batchsummary", 1, "giving.reports.summary", (
        JSForm.ReportCollection("church", "Church", (
            field("ID", "Church ID", "integer"),
            field("Church", "Church Name"),
            field("Logo", "Church Logo", "image"),
        )),
        JSForm.ReportCollection("parameters", "Parameters", (
            field("FromDate", "From Date", "date"),
            field("ThroughDate", "Through Date", "date"),
            field("Display", "Selected Period"),
        )),
        JSForm.ReportCollection("records", "Batch Controls", (
            field("Date", "Date", "date"), field("Description", "Description"),
            field("Organization", "Organization"), field("Status", "Status"),
            field("Control", "Control", "currency"),
            field("Entered", "Entered", "currency"),
            field("Difference", "Difference", "currency"),
            field("Accounting", "Accounting Transaction"),
        )),
        JSForm.ReportCollection("totals", "Protected Totals", (
            field("Control", "Control Total", "currency"),
            field("Entered", "Entered Total", "currency"),
            field("Difference", "Difference", "currency"),
        )),
    ),
)


BATCH_SUMMARY_MANIFEST = JSForm.ReportProtectionManifest(
    required_settings={
        "name": "GIVE-BATCH", "dataset": "giving.batchsummary",
        "datasetversion": 1, "classification": "confidential",
    },
    required_bands=("ReportHeader", "Detail", "ReportFooter", "PageFooter"),
    required_controls={
        "ChurchLogo": {"collection": "church", "field": "Logo"},
        "ChurchName": {"collection": "church", "field": "Church"},
        "ReportTitle": {"systemvalue": "report_title"},
        "Period": {"collection": "parameters", "field": "Display"},
        "Records": {"repeatcollection": "records"},
        "ControlTotal": {"collection": "totals", "field": "Control"},
        "EnteredTotal": {"collection": "totals", "field": "Entered"},
        "DifferenceTotal": {"collection": "totals", "field": "Difference"},
        "RunUser": {"systemvalue": "run_user"},
        "ReportCode": {"systemvalue": "report_code"},
        "Classification": {"systemvalue": "classification"},
        "PageNumber": {"systemvalue": "page_number"},
    },
)


class GivingBatchSummaryProvider:
    """Build a donor-free report dataset from Giving batch controls."""

    def __init__(self, connection, authorization):
        self.service = GivingReportService(connection)
        self.authorization = authorization

    def build(self, start_date, end_date):
        self.authorization.require("giving.reports.summary", "create the Giving batch summary")
        church = self.service.all("SELECT ID,Church,Logo FROM tblChurch ORDER BY ID LIMIT 1")
        if not church:
            raise ValueError("Church information must be created first.")
        source = self.service.batch_summary(start_date, end_date)
        records = []
        control = Decimal("0.00"); entered = Decimal("0.00")
        for row in source:
            records.append({
                "Date": row[0], "Description": row[1], "Organization": row[2],
                "Status": str(row[3]).title(), "Control": row[4], "Entered": row[5],
                "Difference": row[6], "Accounting": "" if row[7] is None else str(row[7]),
            })
            control += Decimal(row[4] if row[4] is not None else row[5])
            entered += Decimal(row[5])
        return JSForm.ReportDataset.create(BATCH_SUMMARY_CONTRACT, {
            "church": [{"ID": church[0][0], "Church": church[0][1], "Logo": church[0][2]}],
            "parameters": [{
                "FromDate": start_date, "ThroughDate": end_date,
                "Display": f"{start_date.strftime('%B %d, %Y')} through {end_date.strftime('%B %d, %Y')}",
            }],
            "records": records,
            "totals": [{"Control": control, "Entered": entered, "Difference": control-entered}],
        })


class GivingVisualReportService:
    """Render protected Giving PDFs outside the unrestricted report catalog."""

    def __init__(self, connection, authorization, session, processes=None, output_directory=None):
        self.connection = connection
        self.authorization = authorization
        self.session = session
        self.processes = processes or ProcessService()
        self.output_directory = Path(output_directory or OUTPUTS)

    def run_batch_summary(self, start_date, end_date):
        self.authorization.require("giving.reports.summary", "run the Giving batch summary")
        definition = JSForm.ReportDefinitionLoader().load(DEFINITIONS / "GIVE-BATCH.json")
        BATCH_SUMMARY_MANIFEST.validate(definition)
        dataset = GivingBatchSummaryProvider(self.connection, self.authorization).build(start_date, end_date)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        output = self.output_directory / "GIVE-BATCH.pdf"
        if output.exists():
            try:
                with output.open("ab"):
                    pass
            except PermissionError:
                output = self.output_directory / f"GIVE-BATCH-{datetime.now():%Y%m%d-%H%M%S}.pdf"
        rendered = JSForm.PDFReportRenderer().render(
            definition, dataset, output, context={"run_user": self.session.display_name},
        )
        self.processes.open_file(rendered)
        return rendered
