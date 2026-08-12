"""Secure visual-report boundary for ChurchManager accounting reports."""

from datetime import date
from decimal import Decimal
from pathlib import Path
import tempfile

import JSForm

from process_service import ProcessService
from visual_reports.designer import ensure_user_definition

from .trial_balance_service import TrialBalanceService


ACCOUNTING_DEFINITIONS = Path(__file__).resolve().parent / "report_definitions"
REPORT_OUTPUTS = Path(__file__).resolve().parents[1] / "Reports"


def field(name, label, data_type="text"):
    return JSForm.ReportField(name, label, data_type)


TRIAL_BALANCE_CONTRACT = JSForm.ReportDatasetContract(
    "accounting.trialbalance", 1, "accounting.reports.run", (
        JSForm.ReportCollection("church", "Church", (
            field("ID", "Church ID", "integer"), field("Church", "Church Name"),
            field("Logo", "Church Logo", "image"),
        )),
        JSForm.ReportCollection("organization", "Accounting Organization", (
            field("ID", "Organization ID", "integer"), field("LegalName", "Legal Name"),
            field("ReportingBasis", "Reporting Basis"), field("BaseCurrency", "Base Currency"),
        )),
        JSForm.ReportCollection("parameters", "Parameters", (
            field("AsOfDate", "As-of Date", "date"), field("Display", "Selected Parameters"),
        )),
        JSForm.ReportCollection("accounts", "Trial Balance Accounts", (
            field("Code", "Account Code"), field("Name", "Account Name"),
            field("AccountType", "Account Type"), field("NormalBalance", "Normal Balance"),
            field("DebitActivity", "Debit Activity", "currency"),
            field("CreditActivity", "Credit Activity", "currency"),
            field("DebitBalance", "Debit Balance", "currency"),
            field("CreditBalance", "Credit Balance", "currency"),
        )),
        JSForm.ReportCollection("totals", "Protected Totals", (
            field("DebitBalance", "Total Debit Balance", "currency"),
            field("CreditBalance", "Total Credit Balance", "currency"),
            field("Difference", "Difference", "currency"),
        )),
    ),
)


TRIAL_BALANCE_MANIFEST = JSForm.ReportProtectionManifest(
    required_settings={
        "name": "ACCT-TB", "dataset": "accounting.trialbalance",
        "datasetversion": 1, "classification": "official",
    },
    required_bands=("ReportHeader", "Detail", "ReportFooter", "PageFooter"),
    required_controls={
        "ChurchLogo": {"collection": "church", "field": "Logo"},
        "ChurchName": {"collection": "church", "field": "Church"},
        "OrganizationName": {"collection": "organization", "field": "LegalName"},
        "ReportTitle": {"systemvalue": "report_title"},
        "AsOfLabel": {"label": "As of date:"},
        "AsOfDate": {"collection": "parameters", "field": "AsOfDate"},
        "DebitTotalLabel": {"label": "Debit balances"},
        "DebitTotal": {"collection": "totals", "field": "DebitBalance"},
        "CreditTotalLabel": {"label": "Credit balances"},
        "CreditTotal": {"collection": "totals", "field": "CreditBalance"},
        "DifferenceLabel": {"label": "Difference"},
        "Difference": {"collection": "totals", "field": "Difference"},
        "ReportCode": {"systemvalue": "report_code"},
        "Classification": {"systemvalue": "classification"},
        "RunUser": {"systemvalue": "run_user"},
        "PageNumber": {"systemvalue": "page_number"},
    },
)


class TrialBalanceDatasetProvider:
    def __init__(self, connection, authorization, service=None):
        self.connection = connection
        self.authorization = authorization
        self.service = service or TrialBalanceService(connection)
        self.marker = "%s" if "mysql.connector" in type(connection).__module__ else "?"

    def build(self, organization_id, as_of_date):
        self.authorization.require(
            TRIAL_BALANCE_CONTRACT.required_permission,
            operation="Create Trial Balance report dataset",
        )
        if not isinstance(as_of_date, date):
            raise ValueError("Trial Balance as-of date must be a date.")
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT o.ID,o.LegalName,o.ReportingBasis,o.BaseCurrency,c.ID,c.Church,c.Logo "
                "FROM tblAccountingOrganization o LEFT JOIN rpt_church_identity c ON c.ID=o.ChurchID "
                f"WHERE o.ID={self.marker}", (organization_id,),
            )
            identity = cursor.fetchone()
        finally:
            cursor.close()
        if identity is None:
            raise ValueError("The selected accounting organization is unavailable.")
        rows = self.service.rows(organization_id, as_of_date)
        accounts = [{
            "Code": row[0], "Name": row[1], "AccountType": row[2],
            "NormalBalance": row[3], "DebitActivity": row[4],
            "CreditActivity": row[5], "DebitBalance": row[6], "CreditBalance": row[7],
        } for row in rows]
        debit = sum((row["DebitBalance"] for row in accounts), Decimal("0"))
        credit = sum((row["CreditBalance"] for row in accounts), Decimal("0"))
        return JSForm.ReportDataset.create(TRIAL_BALANCE_CONTRACT, {
            "church": [{
                "ID": identity[4] or 0,
                "Church": identity[5] or identity[1],
                "Logo": identity[6],
            }],
            "organization": [{
                "ID": identity[0], "LegalName": identity[1],
                "ReportingBasis": identity[2], "BaseCurrency": identity[3],
            }],
            "parameters": [{
                "AsOfDate": as_of_date,
                "Display": f"As of {as_of_date.strftime('%B %d, %Y')}",
            }],
            "accounts": accounts,
            "totals": [{"DebitBalance": debit, "CreditBalance": credit, "Difference": debit-credit}],
        })


class AccountingVisualReportService:
    def __init__(
        self, connection, authorization, session, processes=None, output_directory=None,
        local_app_data=None, trial_balance_provider=None,
    ):
        self.connection = connection
        self.authorization = authorization
        self.session = session
        self.processes = processes or ProcessService()
        self.output_directory = Path(output_directory or REPORT_OUTPUTS)
        self.local_app_data = local_app_data
        self.trial_balance_provider = trial_balance_provider

    def run_trial_balance(self, organization_id, as_of_date):
        self.authorization.require("accounting.reports.run", "run the Trial Balance report")
        definition_path = ensure_user_definition(
            "ACCT-TB", local_app_data=self.local_app_data,
            starter_directory=ACCOUNTING_DEFINITIONS,
        )
        definition = JSForm.ReportDefinitionLoader().load(definition_path)
        TRIAL_BALANCE_MANIFEST.validate(definition)
        provider = self.trial_balance_provider or TrialBalanceDatasetProvider(
            self.connection, self.authorization,
        )
        dataset = provider.build(organization_id, as_of_date)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        output = self.output_directory / "ACCT-TB.pdf"
        rendered = JSForm.PDFReportRenderer().render(
            definition, dataset, output,
            context={"run_user": self.session.display_name},
        )
        self.processes.open_file(rendered)
        return rendered

    def design_trial_balance(self, organization_id, as_of_date):
        self.authorization.require("accounting.reports.run", "view Trial Balance data")
        self.authorization.require(
            "accounting.reports.design", "customize accounting report layouts",
        )
        definition_path = ensure_user_definition(
            "ACCT-TB", local_app_data=self.local_app_data,
            starter_directory=ACCOUNTING_DEFINITIONS,
        )

        def preview(definition):
            TRIAL_BALANCE_MANIFEST.validate(definition)
            provider = self.trial_balance_provider or TrialBalanceDatasetProvider(
                self.connection, self.authorization,
            )
            dataset = provider.build(organization_id, as_of_date)
            output = Path(tempfile.gettempdir()) / "ChurchManager-ACCT-TB-preview.pdf"
            return JSForm.PDFReportRenderer().render(
                definition, dataset, output,
                context={"run_user": self.session.display_name},
            )

        return JSForm.open_report_designer(
            definition_path,
            dataset_contract=TRIAL_BALANCE_CONTRACT,
            preview_handler=preview,
            starter_definition_path=ACCOUNTING_DEFINITIONS / "ACCT-TB.json",
            export_directory=self.output_directory,
            protection_manifest=TRIAL_BALANCE_MANIFEST,
        )
