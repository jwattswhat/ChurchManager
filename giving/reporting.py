"""Protected PDF generation for Giving reports."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
import tempfile
import hashlib

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
        "name": "CMGV01", "dataset": "giving.batchsummary",
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
        "name": "CMGV04", "dataset": "giving.statement",
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

TRIBUTE_CONTRACT = JSForm.ReportDatasetContract(
    "giving.tributeacknowledgments", 1, "giving.reports.confidential", (
        JSForm.ReportCollection("church", "Church", (
            field("Church", "Church Name"), field("Logo", "Church Logo", "image"),
        )),
        JSForm.ReportCollection("parameters", "Parameters", (field("Display", "Covered Period"),)),
        JSForm.ReportCollection("records", "Memorial and Honor Gifts", (
            field("Date", "Date", "date"), field("Type", "Type"), field("Honoree", "Honoree"),
            field("Donor", "Donor"), field("Amount", "Amount"), field("Contact", "Acknowledgment Contact"),
            field("Purpose", "Purpose"),
        )),
    ),
)

TRIBUTE_MANIFEST = JSForm.ReportProtectionManifest(
    required_settings={"name": "CMGV08", "dataset": "giving.tributeacknowledgments",
                       "datasetversion": 1, "classification": "confidential"},
    required_bands=("ReportHeader", "Detail", "PageFooter"),
    required_controls={
        "ChurchLogo": {"collection": "church", "field": "Logo"},
        "ChurchName": {"collection": "church", "field": "Church"},
        "ReportTitle": {"systemvalue": "report_title"},
        "Period": {"collection": "parameters", "field": "Display"},
        "Records": {"repeatcollection": "records"},
        "RunUser": {"systemvalue": "run_user"}, "ReportCode": {"systemvalue": "report_code"},
        "Classification": {"systemvalue": "classification"}, "PageNumber": {"systemvalue": "page_number"},
    },
)

DIRECTED_GIFT_CONTRACT = JSForm.ReportDatasetContract(
    "giving.directedgiftreviews", 1, "giving.reports.confidential", (
        JSForm.ReportCollection("church", "Church", (
            field("Church", "Church Name"), field("Logo", "Church Logo", "image"),
        )),
        JSForm.ReportCollection("parameters", "Parameters", (field("Display", "Covered Period"),)),
        JSForm.ReportCollection("records", "Directed Gift Reviews", (
            field("Date", "Date", "date"), field("Contributor", "Contributor"),
            field("Direction", "Donor Direction"), field("Status", "Disposition"),
            field("Resolution", "Resolution"), field("ResolvedBy", "Resolved By"),
            field("ResolvedAt", "Resolved At", "datetime"), field("Batch", "Batch"),
        )),
    ),
)

DIRECTED_GIFT_MANIFEST = JSForm.ReportProtectionManifest(
    required_settings={"name": "CMGV07", "dataset": "giving.directedgiftreviews",
                       "datasetversion": 1, "classification": "confidential"},
    required_bands=("ReportHeader", "Detail", "PageFooter"),
    required_controls={
        "ChurchLogo": {"collection": "church", "field": "Logo"},
        "ChurchName": {"collection": "church", "field": "Church"},
        "ReportTitle": {"systemvalue": "report_title"},
        "Period": {"collection": "parameters", "field": "Display"},
        "Records": {"repeatcollection": "records"},
        "RunUser": {"systemvalue": "run_user"}, "ReportCode": {"systemvalue": "report_code"},
        "Classification": {"systemvalue": "classification"}, "PageNumber": {"systemvalue": "page_number"},
    },
)

OPERATIONAL_CONTRACT = JSForm.ReportDatasetContract(
    "giving.operationalreview", 1, "giving.reports.confidential", (
        JSForm.ReportCollection("church", "Church", (
            field("Church", "Church Name"), field("Logo", "Church Logo", "image"),
        )),
        JSForm.ReportCollection("parameters", "Parameters", (field("Display", "Selection"),)),
        JSForm.ReportCollection("records", "Review Records", (
            field("Date", "Date", "date"), field("Group", "Group"),
            field("Description", "Description"), field("Status", "Status"),
            field("Amount", "Amount", "currency"), field("Detail", "Detail"),
            field("Reference", "Reference"), field("Note", "Note"),
        )),
    ),
)


def operational_manifest(code):
    """Return the shared protection requirements for a named operational report."""
    return JSForm.ReportProtectionManifest(
        required_settings={"name": code, "dataset": "giving.operationalreview",
                           "datasetversion": 1, "classification": "confidential"},
        required_bands=("ReportHeader", "Detail", "PageFooter"),
        required_controls={
            "ChurchLogo": {"collection": "church", "field": "Logo"},
            "ChurchName": {"collection": "church", "field": "Church"},
            "ReportTitle": {"systemvalue": "report_title"},
            "Period": {"collection": "parameters", "field": "Display"},
            "Records": {"repeatcollection": "records"},
            "RunUser": {"systemvalue": "run_user"}, "ReportCode": {"systemvalue": "report_code"},
            "Classification": {"systemvalue": "classification"},
            "PageNumber": {"systemvalue": "page_number"},
        },
    )


ENVELOPE_LABEL_CONTRACT = JSForm.ReportDatasetContract(
    "giving.envelopelabels", 1, "giving.reports.confidential", (
        JSForm.ReportCollection("labelrows", "Envelope Label Rows", tuple(
            field(f"{name}{column}", f"Label {column} {name}")
            for column in range(1, 4) for name in ("Box", "Name", "Church")
        )),
    ),
)


ENVELOPE_LABEL_MANIFEST = JSForm.ReportProtectionManifest(
    required_settings={
        "name": "CMGV09", "dataset": "giving.envelopelabels",
        "datasetversion": 1, "classification": "confidential",
    },
    required_bands=("Detail",),
    required_controls={"Labels": {"repeatcollection": "labelrows"}},
)


ENVELOPE_REGISTER_CONTRACT = JSForm.ReportDatasetContract(
    "giving.enveloperegister", 1, "giving.reports.confidential", (
        JSForm.ReportCollection("church", "Church", (
            field("Church", "Church Name"), field("Logo", "Church Logo", "image"),
        )),
        JSForm.ReportCollection("parameters", "Parameters", (
            field("Year", "Assignment Year", "integer"), field("Display", "Selection"),
        )),
        JSForm.ReportCollection("records", "Envelope Assignments", (
            field("Box", "Box Number"), field("Name", "Contributor"),
            field("Type", "Contributor Type"), field("Active", "Active"),
            field("From", "Effective From", "date"), field("Through", "Effective Through", "date"),
        )),
    ),
)


ENVELOPE_REGISTER_MANIFEST = JSForm.ReportProtectionManifest(
    required_settings={
        "name": "CMGV10", "dataset": "giving.enveloperegister",
        "datasetversion": 1, "classification": "confidential",
    },
    required_bands=("ReportHeader", "Detail", "PageFooter"),
    required_controls={
        "ChurchLogo": {"collection": "church", "field": "Logo"},
        "ChurchName": {"collection": "church", "field": "Church"},
        "Records": {"repeatcollection": "records"},
        "RunUser": {"systemvalue": "run_user"},
        "ReportCode": {"systemvalue": "report_code"},
        "Classification": {"systemvalue": "classification"},
        "PageNumber": {"systemvalue": "page_number"},
    },
)


class GivingBatchSummaryProvider:
    """Build a donor-free report dataset from Giving batch controls."""

    def __init__(self, connection, authorization):
        self.service = GivingReportService(connection, authorization)
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
        "summarizes ChurchManager records and does not determine tax deductibility. "
        "Non-cash gifts are described without a value; donors are responsible for "
        "determining any value used for their own records."
    )

    def __init__(self, connection, authorization):
        self.service = GivingReportService(connection, authorization)
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
            method = str(row[2]).upper()
            statement_amount = None if method == "NON_CASH" else amount
            if statement_amount is not None:
                total += statement_amount
            records.append({
                "Date": row[0], "Purpose": row[1], "Method": method.replace("_", " ").title(),
                "Description": row[4] or "", "Amount": statement_amount,
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


class TributeAcknowledgmentProvider:
    """Build a consent-limited memorial and honor acknowledgment dataset."""

    def __init__(self, connection, authorization):
        self.service = GivingReportService(connection, authorization)

    def build(self, start_date, end_date):
        church = self.service.all("SELECT Church,Logo FROM tblChurch ORDER BY ID LIMIT 1")
        if not church:
            raise ValueError("Church information must be created first.")
        rows = self.service.tribute_acknowledgments(start_date, end_date)
        return JSForm.ReportDataset.create(TRIBUTE_CONTRACT, {
            "church": [{"Church": church[0][0], "Logo": church[0][1]}],
            "parameters": [{"Display": f"{start_date:%B %d, %Y} through {end_date:%B %d, %Y}"}],
            "records": [{
                "Date": row[0], "Type": "In memory of" if row[1] == "IN_MEMORY_OF" else "In honor of",
                "Honoree": row[2], "Donor": row[3],
                "Amount": "" if row[4] is None else f"${Decimal(row[4]):,.2f}",
                "Contact": row[5], "Purpose": row[6],
            } for row in rows],
        })


class DirectedGiftReviewProvider:
    """Build the restricted donor-direction review and disposition dataset."""

    def __init__(self, connection, authorization):
        self.service = GivingReportService(connection, authorization)

    def build(self, start_date, end_date):
        church = self.service.all("SELECT Church,Logo FROM tblChurch ORDER BY ID LIMIT 1")
        if not church:
            raise ValueError("Church information must be created first.")
        rows = self.service.directed_gift_reviews(start_date, end_date)
        return JSForm.ReportDataset.create(DIRECTED_GIFT_CONTRACT, {
            "church": [{"Church": church[0][0], "Logo": church[0][1]}],
            "parameters": [{"Display": f"{start_date:%B %d, %Y} through {end_date:%B %d, %Y}"}],
            "records": [{
                "Date": row[0], "Contributor": row[1], "Direction": row[2],
                "Status": str(row[3]).replace("_", " ").title(), "Resolution": row[4],
                "ResolvedBy": row[5], "ResolvedAt": row[6], "Batch": row[7],
            } for row in rows],
        })


class OperationalGivingReportProvider:
    """Build one of the protected operational Giving review datasets."""

    def __init__(self, connection, authorization):
        self.service = GivingReportService(connection, authorization)

    def build(self, report_kind, start_date, end_date, contributor_id=None):
        church = self.service.all("SELECT Church,Logo FROM tblChurch ORDER BY ID LIMIT 1")
        if not church:
            raise ValueError("Church information must be created first.")
        if report_kind == "envelope-exceptions":
            rows = self.service.envelope_exceptions(start_date, end_date)
        elif report_kind == "batch-detail":
            rows = self.service.batch_detail(start_date, end_date)
        elif report_kind == "fund-period":
            rows = self.service.giving_by_fund(start_date, end_date)
        elif report_kind == "statement-exceptions":
            rows = self.service.statement_exceptions(start_date, end_date)
        elif report_kind == "accounting-reconciliation":
            rows = self.service.accounting_reconciliation(start_date, end_date)
        elif report_kind == "contributor-history":
            if contributor_id is None:
                raise ValueError("Select a contributor for printable history.")
            rows = [
                (row[0], row[1], row[4], str(row[6]).title(), row[5],
                 str(row[2]).replace("_", " ").title(), row[3] or "", str(row[7]).title())
                for row in self.service.contributor_history(contributor_id, start_date, end_date)
            ]
        else:
            raise ValueError("Unknown Giving operational report.")
        return JSForm.ReportDataset.create(OPERATIONAL_CONTRACT, {
            "church": [{"Church": church[0][0], "Logo": church[0][1]}],
            "parameters": [{"Display": f"{start_date:%B %d, %Y} through {end_date:%B %d, %Y}"}],
            "records": [{
                "Date": row[0], "Group": row[1] or "", "Description": row[2] or "",
                "Status": row[3] or "", "Amount": row[4], "Detail": row[5] or "",
                "Reference": row[6] or "", "Note": row[7] or "",
            } for row in rows],
        })


class EnvelopeBoxReportProvider:
    """Build protected label-sheet and assignment-register datasets."""

    def __init__(self, connection, authorization):
        self.service = GivingReportService(connection, authorization)
        self.authorization = authorization

    def _rows(self, year, include_inactive, include_outside):
        self.authorization.require("giving.reports.confidential", "create envelope-box reports")
        rows = self.service.envelope_assignments(
            year, include_inactive=include_inactive, include_outside=include_outside,
        )
        if not rows:
            raise ValueError("No envelope assignments match the selected year and options.")
        return rows

    def labels(self, year, include_inactive, include_outside, include_church):
        """Arrange assignments into three labels per physical sheet row."""
        assignments = self._rows(year, include_inactive, include_outside)
        church = self.service.all("SELECT Church FROM tblChurch ORDER BY ID LIMIT 1")
        church_name = church[0][0] if include_church and church else ""
        rows = []
        for start in range(0, len(assignments), 3):
            record = {}
            for column, assignment in enumerate(assignments[start:start + 3], 1):
                record[f"Box{column}"] = f"Envelope Box {assignment[0]}"
                record[f"Name{column}"] = assignment[1]
                record[f"Church{column}"] = church_name
            for column in range(1, 4):
                for name in ("Box", "Name", "Church"):
                    record.setdefault(f"{name}{column}", "")
            rows.append(record)
        return JSForm.ReportDataset.create(ENVELOPE_LABEL_CONTRACT, {"labelrows": rows})

    def register(self, year, include_inactive, include_outside):
        """Build the human-verifiable assignment register for the same selection."""
        assignments = self._rows(year, include_inactive, include_outside)
        church = self.service.all("SELECT Church,Logo FROM tblChurch ORDER BY ID LIMIT 1")
        if not church:
            raise ValueError("Church information must be created first.")
        selection = [f"Envelope assignments overlapping {year}"]
        if include_inactive:
            selection.append("including inactive contributors")
        if not include_outside:
            selection.append("excluding outside contributors")
        return JSForm.ReportDataset.create(ENVELOPE_REGISTER_CONTRACT, {
            "church": [{"Church": church[0][0], "Logo": church[0][1]}],
            "parameters": [{"Year": int(year), "Display": "; ".join(selection)}],
            "records": [{
                "Box": row[0], "Name": row[1], "Type": str(row[2]).title(),
                "Active": "Yes" if row[3] else "No", "From": row[4], "Through": row[5],
            } for row in assignments],
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
        definition = JSForm.ReportDefinitionLoader().load(DEFINITIONS / "CMGV01.json")
        BATCH_SUMMARY_MANIFEST.validate(definition)
        dataset = GivingBatchSummaryProvider(self.connection, self.authorization).build(start_date, end_date)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        output = self.output_directory / "CMGV01.pdf"
        if output.exists():
            try:
                with output.open("ab"):
                    pass
            except PermissionError:
                output = self.output_directory / f"CMGV01-{datetime.now():%Y%m%d-%H%M%S}.pdf"
        rendered = JSForm.PDFReportRenderer().render(
            definition, dataset, output, context={"run_user": self.session.display_name},
        )
        self.processes.open_file(rendered)
        return rendered

    def run_statements(self, contributor_ids, start_date, end_date, output_name="CMGV04", *, issue=False):
        """Render statements and optionally record their immutable identifiers."""
        self.authorization.require("giving.statements.generate", "preview contribution statements")
        contributor_ids = tuple(contributor_ids)
        if not contributor_ids:
            raise ValueError("Select at least one contributor for the statement preview.")
        definition = JSForm.ReportDefinitionLoader().load(DEFINITIONS / "CMGV04.json")
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
            issue_records = []
            for contributor_id in contributor_ids:
                dataset = provider.build(contributor_id, start_date, end_date)
                target = Path(temporary) / f"statement-{contributor_id}.pdf"
                rendered_path = JSForm.PDFReportRenderer().render(
                    definition, dataset, target,
                    context={"run_user": self.session.display_name},
                )
                rendered.append(rendered_path)
                issue_records.append((
                    contributor_id, start_date, end_date, str(STATEMENT_CONTRACT.version),
                    hashlib.sha256(Path(rendered_path).read_bytes()).hexdigest(), output.name,
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
            if issue:
                GivingReportService(self.connection, self.authorization).record_statement_issuances(
                    issue_records, self.session.user_id,
                )
        self.processes.open_file(output)
        return output

    def _available_output(self, name):
        self.output_directory.mkdir(parents=True, exist_ok=True)
        output = self.output_directory / name
        if output.exists():
            try:
                with output.open("ab"):
                    pass
            except PermissionError:
                output = self.output_directory / f"{output.stem}-{datetime.now():%Y%m%d-%H%M%S}.pdf"
        return output

    def run_envelope_labels(self, year, include_inactive=False, include_outside=True,
                            include_church=True):
        """Render three-column, 30-up envelope-box labels on US Letter paper."""
        self.authorization.require("giving.reports.confidential", "print envelope-box labels")
        definition = JSForm.ReportDefinitionLoader().load(
            DEFINITIONS / "CMGV09.json"
        )
        ENVELOPE_LABEL_MANIFEST.validate(definition)
        dataset = EnvelopeBoxReportProvider(self.connection, self.authorization).labels(
            year, include_inactive, include_outside, include_church,
        )
        output = self._available_output(f"CMGV09-{year}.pdf")
        rendered = JSForm.PDFReportRenderer().render(definition, dataset, output)
        self.processes.open_file(rendered)
        return rendered

    def run_envelope_register(self, year, include_inactive=False, include_outside=True):
        """Render the protected annual envelope assignment register."""
        self.authorization.require("giving.reports.confidential", "print the envelope register")
        definition = JSForm.ReportDefinitionLoader().load(
            DEFINITIONS / "CMGV10.json"
        )
        ENVELOPE_REGISTER_MANIFEST.validate(definition)
        dataset = EnvelopeBoxReportProvider(self.connection, self.authorization).register(
            year, include_inactive, include_outside,
        )
        output = self._available_output(f"CMGV10-{year}.pdf")
        rendered = JSForm.PDFReportRenderer().render(
            definition, dataset, output, context={"run_user": self.session.display_name},
        )
        self.processes.open_file(rendered)
        return rendered

    def run_tribute_acknowledgments(self, start_date, end_date):
        """Render the protected memorial and honor acknowledgment list."""
        self.authorization.require("giving.reports.confidential", "print memorial and honor gifts")
        definition = JSForm.ReportDefinitionLoader().load(DEFINITIONS / "CMGV08.json")
        TRIBUTE_MANIFEST.validate(definition)
        dataset = TributeAcknowledgmentProvider(self.connection, self.authorization).build(start_date, end_date)
        output = self._available_output("CMGV08.pdf")
        rendered = JSForm.PDFReportRenderer().render(
            definition, dataset, output, context={"run_user": self.session.display_name},
        )
        self.processes.open_file(rendered)
        return rendered

    def run_directed_gift_reviews(self, start_date, end_date):
        """Render the restricted directed-gift review and disposition list."""
        self.authorization.require("giving.reports.confidential", "print directed gift reviews")
        definition = JSForm.ReportDefinitionLoader().load(DEFINITIONS / "CMGV07.json")
        DIRECTED_GIFT_MANIFEST.validate(definition)
        dataset = DirectedGiftReviewProvider(self.connection, self.authorization).build(
            start_date, end_date
        )
        output = self._available_output("CMGV07.pdf")
        rendered = JSForm.PDFReportRenderer().render(
            definition, dataset, output, context={"run_user": self.session.display_name},
        )
        self.processes.open_file(rendered)
        return rendered

    def run_operational(self, code, report_kind, start_date, end_date, contributor_id=None):
        """Render one protected operational Giving report through shared plumbing."""
        self.authorization.require("giving.reports.confidential", "print a protected Giving report")
        definition = JSForm.ReportDefinitionLoader().load(DEFINITIONS / f"{code}.json")
        operational_manifest(code).validate(definition)
        dataset = OperationalGivingReportProvider(self.connection, self.authorization).build(
            report_kind, start_date, end_date, contributor_id,
        )
        output = self._available_output(f"{code}.pdf")
        rendered = JSForm.PDFReportRenderer().render(
            definition, dataset, output, context={"run_user": self.session.display_name},
        )
        self.processes.open_file(rendered)
        return rendered
