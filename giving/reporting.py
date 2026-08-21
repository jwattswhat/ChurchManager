"""Protected PDF generation for Giving reports."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
import tempfile

import JSForm
from pypdf import PdfWriter

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


STATEMENT_CONTRACT = JSForm.ReportDatasetContract(
    "giving.statement", 1, "giving.statements.generate", (
        JSForm.ReportCollection("church", "Church", (
            field("Church", "Church Name"), field("Logo", "Church Logo", "image"),
            field("Address", "Church Address"), field("Contact", "Church Contact"),
        )),
        JSForm.ReportCollection("contributor", "Statement Recipient", (
            field("ID", "Contributor ID", "integer"), field("Name", "Statement Name"),
            field("Address", "Statement Address"),
        )),
        JSForm.ReportCollection("parameters", "Statement Parameters", (
            field("FromDate", "From Date", "date"), field("ThroughDate", "Through Date", "date"),
            field("Display", "Covered Period"), field("Acknowledgment", "Acknowledgment"),
        )),
        JSForm.ReportCollection("records", "Contributions", (
            field("Date", "Date", "date"), field("Purpose", "Purpose"),
            field("Method", "Method"), field("Description", "Description"),
            field("Amount", "Amount", "currency"), field("Benefit", "Goods or Services"),
        )),
        JSForm.ReportCollection("totals", "Statement Totals", (
            field("EligibleAmount", "Eligible Monetary Contributions", "currency"),
        )),
    ),
)


STATEMENT_MANIFEST = JSForm.ReportProtectionManifest(
    required_settings={
        "name": "GIVE-STMT", "dataset": "giving.statement",
        "datasetversion": 1, "classification": "confidential",
    },
    required_bands=("ReportHeader", "Detail", "ReportFooter", "PageFooter"),
    required_controls={
        "ChurchLogo": {"collection": "church", "field": "Logo"},
        "ChurchName": {"collection": "church", "field": "Church"},
        "ContributorName": {"collection": "contributor", "field": "Name"},
        "ContributorAddress": {"collection": "contributor", "field": "Address"},
        "Period": {"collection": "parameters", "field": "Display"},
        "Records": {"repeatcollection": "records"},
        "EligibleTotal": {"collection": "totals", "field": "EligibleAmount"},
        "Acknowledgment": {"collection": "parameters", "field": "Acknowledgment"},
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


class ContributionStatementProvider:
    """Build one contributor's confidential posted-contribution statement."""

    ACKNOWLEDGMENT = (
        "Thank you for supporting the congregation's ministry. This statement "
        "summarizes ChurchManager records and does not determine tax deductibility."
    )

    def __init__(self, connection, authorization):
        self.service = GivingReportService(connection)
        self.authorization = authorization

    @staticmethod
    def _address(row):
        locality = " ".join(value for value in (row[4], row[5], row[6]) if value)
        return "\n".join(value for value in (row[2], row[3], locality) if value)

    @staticmethod
    def _benefit(row):
        if row[8]:
            return "Intangible religious benefits only"
        if row[5]:
            description = row[6] or "Goods or services provided"
            if row[7] is not None:
                return f"{description}; value ${Decimal(row[7]):,.2f}"
            return description
        return "No goods or services"

    def build(self, contributor_id, start_date, end_date):
        self.authorization.require("giving.statements.generate", "create contribution statements")
        church = self.service.all(
            "SELECT Church,Logo,Address,Address2,City,State,ZIP,Phone,Email "
            "FROM tblChurch ORDER BY ID LIMIT 1"
        )
        if not church:
            raise ValueError("Church information must be created first.")
        identity = self.service.statement_identity(contributor_id)
        source = self.service.statement_lines(contributor_id, start_date, end_date)
        records = []
        total = Decimal("0.00")
        for row in source:
            amount = Decimal(row[3])
            total += amount
            records.append({
                "Date": row[0], "Purpose": row[1], "Method": str(row[2]).title(),
                "Description": row[4] or "", "Amount": amount,
                "Benefit": self._benefit(row),
            })
        church_locality = " ".join(value for value in (church[0][4], church[0][5], church[0][6]) if value)
        church_address = "\n".join(value for value in (church[0][2], church[0][3], church_locality) if value)
        contact = " | ".join(value for value in (church[0][7], church[0][8]) if value)
        return JSForm.ReportDataset.create(STATEMENT_CONTRACT, {
            "church": [{"Church": church[0][0], "Logo": church[0][1],
                        "Address": church_address, "Contact": contact}],
            "contributor": [{"ID": identity[0], "Name": identity[1],
                             "Address": self._address(identity)}],
            "parameters": [{
                "FromDate": start_date, "ThroughDate": end_date,
                "Display": f"{start_date.strftime('%B %d, %Y')} through {end_date.strftime('%B %d, %Y')}",
                "Acknowledgment": self.ACKNOWLEDGMENT,
            }],
            "records": records,
            "totals": [{"EligibleAmount": total}],
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

    def run_statements(self, contributor_ids, start_date, end_date, output_name="GIVE-STMT"):
        """Preview one statement or merge several statements into one PDF."""
        self.authorization.require("giving.statements.generate", "preview contribution statements")
        contributor_ids = tuple(contributor_ids)
        if not contributor_ids:
            raise ValueError("Select at least one contributor for the statement preview.")
        definition = JSForm.ReportDefinitionLoader().load(DEFINITIONS / "GIVE-STMT.json")
        STATEMENT_MANIFEST.validate(definition)
        provider = ContributionStatementProvider(self.connection, self.authorization)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        output = self.output_directory / f"{output_name}.pdf"
        if output.exists():
            try:
                with output.open("ab"):
                    pass
            except PermissionError:
                output = self.output_directory / f"{output_name}-{datetime.now():%Y%m%d-%H%M%S}.pdf"
        with tempfile.TemporaryDirectory(prefix="churchmanager-statements-") as temporary:
            rendered = []
            for contributor_id in contributor_ids:
                dataset = provider.build(contributor_id, start_date, end_date)
                target = Path(temporary) / f"statement-{contributor_id}.pdf"
                rendered.append(JSForm.PDFReportRenderer().render(
                    definition, dataset, target,
                    context={"run_user": self.session.display_name},
                ))
            if len(rendered) == 1:
                Path(rendered[0]).replace(output)
            else:
                writer = PdfWriter()
                for source in rendered:
                    writer.append(str(source))
                with output.open("wb") as stream:
                    writer.write(stream)
                writer.close()
        self.processes.open_file(output)
        return output
