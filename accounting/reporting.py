"""Secure visual-report boundary for ChurchManager accounting reports."""

from datetime import date
from decimal import Decimal
from pathlib import Path
import tempfile

import JSForm

from process_service import ProcessService
from visual_reports.designer import ensure_user_definition

from .trial_balance_service import TrialBalanceService
from .position_service import FinancialPositionService
from .activities_service import ActivitiesService
from .fund_balance_service import FundBalanceService


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


def _common_collections(records, totals, date_range=False):
    parameter_fields = [field("Display", "Selected Parameters")]
    if date_range:
        parameter_fields.extend((field("FromDate", "From Date", "date"),
                                 field("ThroughDate", "Through Date", "date")))
    else:
        parameter_fields.append(field("AsOfDate", "As-of Date", "date"))
    return (
        JSForm.ReportCollection("church", "Church", (
            field("ID", "Church ID", "integer"), field("Church", "Church Name"),
            field("Logo", "Church Logo", "image"),
        )),
        JSForm.ReportCollection("organization", "Accounting Organization", (
            field("ID", "Organization ID", "integer"), field("LegalName", "Legal Name"),
            field("ReportingBasis", "Reporting Basis"), field("BaseCurrency", "Base Currency"),
        )),
        JSForm.ReportCollection("parameters", "Parameters", tuple(parameter_fields)),
        JSForm.ReportCollection("records", "Statement Lines", records),
        JSForm.ReportCollection("totals", "Protected Totals", totals),
    )


POSITION_CONTRACT = JSForm.ReportDatasetContract(
    "accounting.position", 1, "accounting.reports.run",
    _common_collections((
        field("Section", "Section"), field("Code", "Account Code"),
        field("Name", "Account Name"), field("Amount", "Amount", "currency"),
    ), (
        field("TotalAssets", "Total Assets", "currency"),
        field("LiabilitiesAndNetAssets", "Liabilities and Net Assets", "currency"),
        field("Difference", "Difference", "currency"),
    )),
)

ACTIVITIES_CONTRACT = JSForm.ReportDatasetContract(
    "accounting.activities", 1, "accounting.reports.run",
    _common_collections((
        field("Section", "Section"), field("Code", "Account Code"),
        field("Name", "Account Name"),
        field("WithoutRestrictions", "Without Donor Restrictions", "currency"),
        field("WithRestrictions", "With Donor Restrictions", "currency"),
        field("Total", "Total", "currency"),
    ), (
        field("WithoutRestrictions", "Change Without Restrictions", "currency"),
        field("WithRestrictions", "Change With Restrictions", "currency"),
        field("Total", "Change in Net Assets", "currency"),
    ), date_range=True),
)

FUND_CONTRACT = JSForm.ReportDatasetContract(
    "accounting.funds", 1, "accounting.reports.run",
    _common_collections((
        field("Code", "Fund Code"), field("Name", "Fund Name"),
        field("NetAssetClass", "Restriction Class"),
        field("Beginning", "Beginning Balance", "currency"),
        field("Revenue", "Revenue", "currency"), field("Expense", "Expense", "currency"),
        field("Transfers", "Transfers and Releases", "currency"),
        field("Other", "Other Activity", "currency"),
        field("Ending", "Ending Balance", "currency"),
    ), tuple(field(name, label, "currency") for name, label in (
        ("Beginning", "Total Beginning Balance"), ("Revenue", "Total Revenue"),
        ("Expense", "Total Expense"), ("Transfers", "Total Transfers and Releases"),
        ("Other", "Total Other Activity"), ("Ending", "Total Ending Balance"),
    )), date_range=True),
)


def _manifest(code, dataset, total_bindings):
    controls = {
        "ChurchLogo": {"collection": "church", "field": "Logo"},
        "ChurchName": {"collection": "church", "field": "Church"},
        "OrganizationName": {"collection": "organization", "field": "LegalName"},
        "ReportTitle": {"systemvalue": "report_title"},
        "Period": {"collection": "parameters", "field": "Display"},
        "ReportCode": {"systemvalue": "report_code"},
        "Classification": {"systemvalue": "classification"},
        "RunUser": {"systemvalue": "run_user"},
        "PageNumber": {"systemvalue": "page_number"},
    }
    controls.update(total_bindings)
    return JSForm.ReportProtectionManifest(
        required_settings={"name": code, "dataset": dataset, "datasetversion": 1,
                           "classification": "official"},
        required_bands=("ReportHeader", "Detail", "ReportFooter", "PageFooter"),
        required_controls=controls,
    )


POSITION_MANIFEST = _manifest("ACCT-FP", "accounting.position", {
    "TotalAssets": {"collection": "totals", "field": "TotalAssets"},
    "LiabilitiesAndNetAssets": {"collection": "totals", "field": "LiabilitiesAndNetAssets"},
    "Difference": {"collection": "totals", "field": "Difference"},
})
ACTIVITIES_MANIFEST = _manifest("ACCT-ACT", "accounting.activities", {
    "ChangeWithout": {"collection": "totals", "field": "WithoutRestrictions"},
    "ChangeWith": {"collection": "totals", "field": "WithRestrictions"},
    "ChangeTotal": {"collection": "totals", "field": "Total"},
})
FUND_MANIFEST = _manifest("ACCT-FUND", "accounting.funds", {
    "BeginningTotal": {"collection": "totals", "field": "Beginning"},
    "EndingTotal": {"collection": "totals", "field": "Ending"},
})


class _AccountingDatasetProvider:
    def __init__(self, connection, authorization):
        self.connection = connection
        self.authorization = authorization
        self.marker = "%s" if "mysql.connector" in type(connection).__module__ else "?"

    def _identity(self, organization_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT o.ID,o.LegalName,o.ReportingBasis,o.BaseCurrency,c.ID,c.Church,c.Logo "
                "FROM tblAccountingOrganization o LEFT JOIN rpt_church_identity c ON c.ID=o.ChurchID "
                f"WHERE o.ID={self.marker}", (organization_id,),
            )
            row = cursor.fetchone()
        finally:
            cursor.close()
        if row is None:
            raise ValueError("The selected accounting organization is unavailable.")
        return {
            "church": [{"ID": row[4] or 0, "Church": row[5] or row[1], "Logo": row[6]}],
            "organization": [{"ID": row[0], "LegalName": row[1],
                              "ReportingBasis": row[2], "BaseCurrency": row[3]}],
        }


class FinancialPositionDatasetProvider(_AccountingDatasetProvider):
    def __init__(self, connection, authorization, service=None):
        super().__init__(connection, authorization)
        self.service = service or FinancialPositionService(connection)

    def build(self, organization_id, as_of_date):
        self.authorization.require("accounting.reports.run", "Create Financial Position dataset")
        collections = self._identity(organization_id)
        assets, liabilities, net_accounts, activity = self.service.rows(organization_id, as_of_date)
        records = ([{"Section": "Assets", "Code": c, "Name": n, "Amount": a} for c,n,a in assets]
                   + [{"Section": "Liabilities", "Code": c, "Name": n, "Amount": a} for c,n,a in liabilities])
        without = activity["WITHOUT_DONOR_RESTRICTIONS"]
        with_restrictions = activity["WITH_DONOR_RESTRICTIONS"]
        for code, name, net_class, amount in net_accounts:
            section = ("Net assets - with donor restrictions" if net_class == "WITH_DONOR_RESTRICTIONS"
                       else "Net assets - without donor restrictions")
            records.append({"Section": section, "Code": code, "Name": name, "Amount": amount})
            if net_class == "WITH_DONOR_RESTRICTIONS": with_restrictions += amount
            else: without += amount
        records.extend((
            {"Section": "Current activity", "Code": "", "Name": "Without donor restrictions",
             "Amount": activity["WITHOUT_DONOR_RESTRICTIONS"]},
            {"Section": "Current activity", "Code": "", "Name": "With donor restrictions",
             "Amount": activity["WITH_DONOR_RESTRICTIONS"]},
        ))
        total_assets = sum((row[2] for row in assets), Decimal("0"))
        total_liabilities = sum((row[2] for row in liabilities), Decimal("0"))
        right_side = total_liabilities + without + with_restrictions
        collections.update({
            "parameters": [{"AsOfDate": as_of_date,
                            "Display": f"As of {as_of_date.strftime('%B %d, %Y')}"}],
            "records": records,
            "totals": [{"TotalAssets": total_assets, "LiabilitiesAndNetAssets": right_side,
                        "Difference": total_assets-right_side}],
        })
        return JSForm.ReportDataset.create(POSITION_CONTRACT, collections)


class ActivitiesDatasetProvider(_AccountingDatasetProvider):
    def __init__(self, connection, authorization, service=None):
        super().__init__(connection, authorization)
        self.service = service or ActivitiesService(connection)

    def build(self, organization_id, date_from, date_to):
        self.authorization.require("accounting.reports.run", "Create Activities dataset")
        collections = self._identity(organization_id)
        rows = self.service.rows(organization_id, date_from, date_to)
        sums = {kind: [Decimal("0"), Decimal("0")] for kind in ("REVENUE","EXPENSE","TRANSFER")}
        labels = {"REVENUE":"Revenue", "EXPENSE":"Expenses", "TRANSFER":"Transfers"}
        records = []
        for code, name, kind, without, with_restrictions in rows:
            records.append({"Section": labels[kind], "Code": code, "Name": name,
                            "WithoutRestrictions": without, "WithRestrictions": with_restrictions,
                            "Total": without+with_restrictions})
            sums[kind][0] += without; sums[kind][1] += with_restrictions
        change = [sums["REVENUE"][i]-sums["EXPENSE"][i]+sums["TRANSFER"][i] for i in (0,1)]
        collections.update({
            "parameters": [{"FromDate": date_from, "ThroughDate": date_to,
                            "Display": f"{date_from.strftime('%B %d, %Y')} through {date_to.strftime('%B %d, %Y')}"}],
            "records": records,
            "totals": [{"WithoutRestrictions": change[0], "WithRestrictions": change[1],
                        "Total": sum(change)}],
        })
        return JSForm.ReportDataset.create(ACTIVITIES_CONTRACT, collections)


class FundDatasetProvider(_AccountingDatasetProvider):
    def __init__(self, connection, authorization, service=None):
        super().__init__(connection, authorization)
        self.service = service or FundBalanceService(connection)

    def build(self, organization_id, date_from, date_to):
        self.authorization.require("accounting.reports.run", "Create Fund Activity dataset")
        collections = self._identity(organization_id)
        source = self.service.report(organization_id, date_from, date_to)
        labels = {"WITH_DONOR_RESTRICTIONS":"With donor restrictions",
                  "WITHOUT_DONOR_RESTRICTIONS":"Without donor restrictions"}
        records = [{"Code": r[0], "Name": r[1], "NetAssetClass": labels.get(r[2],r[2]),
                    "Beginning": r[3], "Revenue": r[4], "Expense": r[5],
                    "Transfers": r[6], "Other": r[7], "Ending": r[8]} for r in source]
        names = ("Beginning","Revenue","Expense","Transfers","Other","Ending")
        totals = {name: sum((row[name] for row in records), Decimal("0")) for name in names}
        collections.update({
            "parameters": [{"FromDate": date_from, "ThroughDate": date_to,
                            "Display": f"{date_from.strftime('%B %d, %Y')} through {date_to.strftime('%B %d, %Y')}"}],
            "records": records, "totals": [totals],
        })
        return JSForm.ReportDataset.create(FUND_CONTRACT, collections)


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

    def _run(self, code, contract, manifest, provider, *parameters):
        self.authorization.require(contract.required_permission, f"run the {code} report")
        definition_path = ensure_user_definition(
            code, local_app_data=self.local_app_data, starter_directory=ACCOUNTING_DEFINITIONS,
        )
        definition = JSForm.ReportDefinitionLoader().load(definition_path)
        manifest.validate(definition)
        dataset = provider.build(*parameters)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        output = self.output_directory / f"{code}.pdf"
        rendered = JSForm.PDFReportRenderer().render(
            definition, dataset, output, context={"run_user": self.session.display_name},
        )
        self.processes.open_file(rendered)
        return rendered

    def _design(self, code, contract, manifest, provider, *parameters):
        self.authorization.require(contract.required_permission, f"view {code} report data")
        self.authorization.require("accounting.reports.design", "customize accounting report layouts")
        definition_path = ensure_user_definition(
            code, local_app_data=self.local_app_data, starter_directory=ACCOUNTING_DEFINITIONS,
        )
        def preview(definition):
            manifest.validate(definition)
            dataset = provider.build(*parameters)
            output = Path(tempfile.gettempdir()) / f"ChurchManager-{code}-preview.pdf"
            return JSForm.PDFReportRenderer().render(
                definition, dataset, output, context={"run_user":self.session.display_name},
            )
        return JSForm.open_report_designer(
            definition_path, dataset_contract=contract, preview_handler=preview,
            starter_definition_path=ACCOUNTING_DEFINITIONS / f"{code}.json",
            export_directory=self.output_directory, protection_manifest=manifest,
        )

    def run_financial_position(self, organization_id, as_of_date):
        return self._run(
            "ACCT-FP", POSITION_CONTRACT, POSITION_MANIFEST,
            FinancialPositionDatasetProvider(self.connection, self.authorization),
            organization_id, as_of_date,
        )

    def design_financial_position(self, organization_id, as_of_date):
        return self._design(
            "ACCT-FP", POSITION_CONTRACT, POSITION_MANIFEST,
            FinancialPositionDatasetProvider(self.connection,self.authorization),
            organization_id,as_of_date,
        )

    def run_activities(self, organization_id, date_from, date_to):
        return self._run(
            "ACCT-ACT", ACTIVITIES_CONTRACT, ACTIVITIES_MANIFEST,
            ActivitiesDatasetProvider(self.connection, self.authorization),
            organization_id, date_from, date_to,
        )

    def design_activities(self, organization_id, date_from, date_to):
        return self._design(
            "ACCT-ACT", ACTIVITIES_CONTRACT, ACTIVITIES_MANIFEST,
            ActivitiesDatasetProvider(self.connection,self.authorization),
            organization_id,date_from,date_to,
        )

    def run_funds(self, organization_id, date_from, date_to):
        return self._run(
            "ACCT-FUND", FUND_CONTRACT, FUND_MANIFEST,
            FundDatasetProvider(self.connection, self.authorization),
            organization_id, date_from, date_to,
        )

    def design_funds(self, organization_id, date_from, date_to):
        return self._design(
            "ACCT-FUND", FUND_CONTRACT, FUND_MANIFEST,
            FundDatasetProvider(self.connection,self.authorization),
            organization_id,date_from,date_to,
        )

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
