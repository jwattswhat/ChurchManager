"""Secure visual-report boundary for ChurchManager accounting reports."""

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import json
import tempfile

import JSForm

from process_service import ProcessService
from configuration_paths import writable_directory
from visual_reports.designer import ensure_user_definition, resolve_report_definition

from .trial_balance_service import TrialBalanceService
from .position_service import FinancialPositionService
from .activities_service import ActivitiesService
from .fund_balance_service import FundBalanceService
from .functional_expense_service import FunctionalExpenseService
from .budget_actual_service import BudgetActualService
from .general_ledger_service import GeneralLedgerService
from .register_service import AccountingRegisterService
from .journal_entry_service import JournalEntryService
from .reconciliation_report_service import ReconciliationReportService
from .close_checklist_service import CloseChecklistService
from .year_end_service import YearEndService
from .audit_service import AccountingAuditService


ACCOUNTING_DEFINITIONS = Path(__file__).resolve().parent / "report_definitions"
REPORT_OUTPUTS = writable_directory("Reports")


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
        "name": "CMFI01", "dataset": "accounting.trialbalance",
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


POSITION_MANIFEST = _manifest("CMFI03", "accounting.position", {
    "TotalAssets": {"collection": "totals", "field": "TotalAssets"},
    "LiabilitiesAndNetAssets": {"collection": "totals", "field": "LiabilitiesAndNetAssets"},
    "Difference": {"collection": "totals", "field": "Difference"},
})
ACTIVITIES_MANIFEST = _manifest("CMFI04", "accounting.activities", {
    "ChangeWithout": {"collection": "totals", "field": "WithoutRestrictions"},
    "ChangeWith": {"collection": "totals", "field": "WithRestrictions"},
    "ChangeTotal": {"collection": "totals", "field": "Total"},
})
FUND_MANIFEST = _manifest("CMFI05", "accounting.funds", {
    "BeginningTotal": {"collection": "totals", "field": "Beginning"},
    "EndingTotal": {"collection": "totals", "field": "Ending"},
})

FUNCTIONAL_CONTRACT = JSForm.ReportDatasetContract(
    "accounting.functionalexpenses", 1, "accounting.reports.run",
    _common_collections((
        field("Account", "Natural Expense Account"), field("Function", "Ministry Function"),
        field("Amount", "Amount", "currency"),
    ), (field("GrandTotal", "Grand Total", "currency"),), date_range=True),
)
FUNCTIONAL_MANIFEST = _manifest("CMFI08", "accounting.functionalexpenses", {
    "ExpenseMatrix": {"repeatcollection":"records", "rowfield":"Account",
                      "columnfield":"Function", "valuefield":"Amount"},
    "GrandTotal": {"collection":"totals", "field":"GrandTotal"},
})

BUDGET_SUMMARY_FIELDS = (
    field("Account", "General Account"), field("Fund", "Fund"), field("Function", "Function"),
    field("PeriodBudget", "Period Budget", "currency"), field("PeriodActual", "Period Actual", "currency"),
    field("PeriodVariance", "Period Variance", "currency"), field("PeriodPercent", "Period Percent", "decimal"),
    field("YTDBudget", "YTD Budget", "currency"), field("YTDActual", "YTD Actual", "currency"),
    field("YTDVariance", "YTD Variance", "currency"), field("YTDPercent", "YTD Percent", "decimal"),
)
BUDGET_DETAIL_FIELDS = (
    field("Period", "Period"), field("Account", "General Account"), field("Fund", "Fund"),
    field("Function", "Function"), field("LineItem", "Detailed Line Item"),
    field("Budget", "Budget", "currency"), field("Note", "Note"),
)


def _budget_contract(name):
    return JSForm.ReportDatasetContract(name,1,"accounting.reports.run",(
        JSForm.ReportCollection("church","Church",(
            field("ID","Church ID","integer"),field("Church","Church Name"),field("Logo","Church Logo","image"))),
        JSForm.ReportCollection("organization","Accounting Organization",(
            field("ID","Organization ID","integer"),field("LegalName","Legal Name"),
            field("ReportingBasis","Reporting Basis"),field("BaseCurrency","Base Currency"))),
        JSForm.ReportCollection("parameters","Parameters",(
            field("Display","Selected Parameters"),field("Mode","Budget Detail Mode"),
            field("ShowDetails","Show Details","boolean"))),
        JSForm.ReportCollection("summary","General Account Summary",BUDGET_SUMMARY_FIELDS),
        JSForm.ReportCollection("details","Detailed Budget Lines",BUDGET_DETAIL_FIELDS),
        JSForm.ReportCollection("totals","Protected Totals",(
            field("PeriodBudget","Total Period Budget","currency"),field("PeriodActual","Total Period Actual","currency"),
            field("PeriodVariance","Total Period Variance","currency"),field("YTDBudget","Total YTD Budget","currency"),
            field("YTDActual","Total YTD Actual","currency"),field("YTDVariance","Total YTD Variance","currency"))),
    ))


BUDGET_ACTUAL_CONTRACT=_budget_contract("accounting.budgetactual")
ADOPTED_BUDGET_CONTRACT=_budget_contract("accounting.adoptedbudget")


def _budget_manifest(code,dataset):
    return _manifest(code,dataset,{
        "PeriodBudgetTotal":{"collection":"totals","field":"PeriodBudget"},
        "PeriodActualTotal":{"collection":"totals","field":"PeriodActual"},
        "YTDBudgetTotal":{"collection":"totals","field":"YTDBudget"},
        "YTDActualTotal":{"collection":"totals","field":"YTDActual"},
    })


BUDGET_ACTUAL_MANIFEST=_budget_manifest("CMFI07","accounting.budgetactual")
ADOPTED_BUDGET_MANIFEST=_budget_manifest("CMFI10","accounting.adoptedbudget")

GENERAL_LEDGER_CONTRACT=JSForm.ReportDatasetContract(
    "accounting.generalledger",1,"accounting.reports.run",
    _common_collections((
        field("Date","Transaction Date","date"),field("Number","Transaction Number","integer"),
        field("Type","Transaction Type"),field("Transaction","Transaction Description"),
        field("Reference","Reference"),field("Fund","Fund"),field("Description","Line Description"),
        field("Debit","Debit","currency"),field("Credit","Credit","currency"),
        field("Balance","Running Normal Balance","currency"),
    ),(
        field("OpeningBalance","Opening Balance","currency"),field("DebitTotal","Total Debits","currency"),
        field("CreditTotal","Total Credits","currency"),field("EndingBalance","Ending Balance","currency"),
    ),date_range=True),
)
GENERAL_LEDGER_MANIFEST=_manifest("CMFI02","accounting.generalledger",{
    "OpeningBalance":{"collection":"totals","field":"OpeningBalance"},
    "DebitTotal":{"collection":"totals","field":"DebitTotal"},
    "CreditTotal":{"collection":"totals","field":"CreditTotal"},
    "EndingBalance":{"collection":"totals","field":"EndingBalance"},
})

REGISTER_CONTRACT=JSForm.ReportDatasetContract(
    "accounting.register",1,"accounting.transactions.view",(
        JSForm.ReportCollection("church","Church",(
            field("ID","Church ID","integer"),field("Church","Church Name"),field("Logo","Church Logo","image"))),
        JSForm.ReportCollection("organization","Accounting Organization",(
            field("ID","Organization ID","integer"),field("LegalName","Legal Name"),
            field("ReportingBasis","Reporting Basis"),field("BaseCurrency","Base Currency"))),
        JSForm.ReportCollection("parameters","Parameters",(field("Display","Selected Parameters"),)),
        JSForm.ReportCollection("records","Posted Transactions",(
            field("Number","Number","integer"),field("Organization","Organization"),field("Date","Date","date"),
            field("Type","Type"),field("Status","Status"),field("Description","Description"),
            field("Reference","Reference"),field("Total","Total","currency"))),
        JSForm.ReportCollection("totals","Protected Totals",(
            field("TransactionCount","Transaction Count","integer"),field("Total","Register Total","currency"))),
    ))
REGISTER_MANIFEST=_manifest("CMFI13","accounting.register",{
    "TransactionCount":{"collection":"totals","field":"TransactionCount"},
    "RegisterTotal":{"collection":"totals","field":"Total"},
})

JOURNAL_CONTRACT=JSForm.ReportDatasetContract(
    "accounting.journalentry",1,"accounting.transactions.view",(
        JSForm.ReportCollection("church","Church",(
            field("ID","Church ID","integer"),field("Church","Church Name"),field("Logo","Church Logo","image"))),
        JSForm.ReportCollection("organization","Accounting Organization",(
            field("ID","Organization ID","integer"),field("LegalName","Legal Name"),field("ReportingBasis","Reporting Basis"),field("BaseCurrency","Base Currency"))),
        JSForm.ReportCollection("parameters","Transaction Metadata",(
            field("Display","Transaction"),field("Number","Number","integer"),field("Date","Date","date"),
            field("TypeStatus","Type and Status"),field("Description","Description"),field("Reference","Reference"),
            field("Created","Created Attribution"),field("Reviewed","Reviewed Attribution"),field("Posted","Posted Attribution"),
            field("ReversalLinks","Original and Reversal Links"),field("HasAttachments","Has Attachments","boolean"))),
        JSForm.ReportCollection("records","Journal Lines",(
            field("Line","Line","integer"),field("Account","Account"),field("Fund","Fund"),field("Function","Function"),
            field("Payee","Payee"),field("Description","Description"),field("Debit","Debit","currency"),field("Credit","Credit","currency"))),
        JSForm.ReportCollection("attachments","Attachments",(
            field("Name","File Name"),field("Type","Document Type"),field("Hash","SHA-256 Hash"),field("AddedAt","Added","datetime"))),
        JSForm.ReportCollection("totals","Protected Totals",(
            field("Debit","Total Debits","currency"),field("Credit","Total Credits","currency"),field("Difference","Difference","currency"))),
    ))
JOURNAL_MANIFEST=_manifest("CMFI12","accounting.journalentry",{
    "Created":{"collection":"parameters","field":"Created"},
    "Reviewed":{"collection":"parameters","field":"Reviewed"},
    "Posted":{"collection":"parameters","field":"Posted"},
    "DebitTotal":{"collection":"totals","field":"Debit"},
    "CreditTotal":{"collection":"totals","field":"Credit"},
    "Difference":{"collection":"totals","field":"Difference"},
})

RECONCILIATION_CONTRACT=JSForm.ReportDatasetContract(
    "accounting.reconciliation",1,"accounting.reports.run",(
        JSForm.ReportCollection("church","Church",(
            field("ID","Church ID","integer"),field("Church","Church Name"),field("Logo","Church Logo","image"))),
        JSForm.ReportCollection("organization","Accounting Organization",(
            field("ID","Organization ID","integer"),field("LegalName","Legal Name"),field("ReportingBasis","Reporting Basis"),field("BaseCurrency","Base Currency"))),
        JSForm.ReportCollection("parameters","Reconciliation Metadata",(
            field("Display","Selection"),field("BankAccount","Bank Account"),field("StatementDate","Statement Date","date"),
            field("PreparedBy","Prepared By"),field("CompletedAt","Completed At","datetime"))),
        JSForm.ReportCollection("records","Reconciliation Items",(
            field("Status","Status"),field("Date","Transaction Date","date"),field("Number","Number","integer"),
            field("Description","Description"),field("Reference","Reference"),field("Amount","Amount","currency"),
            field("ClearedDate","Cleared Date","date"))),
        JSForm.ReportCollection("totals","Protected Reconciliation Proof",(
            field("Beginning","Beginning Balance","currency"),field("Cleared","Cleared Activity","currency"),
            field("Ending","Statement Ending Balance","currency"),field("Difference","Difference","currency"),
            field("Outstanding","Outstanding Total","currency"))),
    ))
RECONCILIATION_MANIFEST=_manifest("CMFI06","accounting.reconciliation",{
    "PreparedBy":{"collection":"parameters","field":"PreparedBy"},
    "CompletedAt":{"collection":"parameters","field":"CompletedAt"},
    "Beginning":{"collection":"totals","field":"Beginning"},"Cleared":{"collection":"totals","field":"Cleared"},
    "Ending":{"collection":"totals","field":"Ending"},"Difference":{"collection":"totals","field":"Difference"},
    "Outstanding":{"collection":"totals","field":"Outstanding"},
})

CLOSE_CONTRACT=JSForm.ReportDatasetContract(
    "accounting.closechecklist",1,"accounting.reports.run",(
        JSForm.ReportCollection("church","Church",(
            field("ID","Church ID","integer"),field("Church","Church Name"),field("Logo","Church Logo","image"))),
        JSForm.ReportCollection("organization","Accounting Organization",(
            field("ID","Organization ID","integer"),field("LegalName","Legal Name"),field("ReportingBasis","Reporting Basis"),field("BaseCurrency","Base Currency"))),
        JSForm.ReportCollection("parameters","Close Period",(
            field("Display","Fiscal Period"),field("Start","Start","date"),field("End","End","date"),
            field("PeriodStatus","Period Status"),field("Conclusion","Conclusion"))),
        JSForm.ReportCollection("records","Readiness Checks",(
            field("Check","Check"),field("Status","Status"),field("Detail","Explanation"))),
        JSForm.ReportCollection("totals","Protected Conclusion",(
            field("Conclusion","Conclusion"),field("Ready","Ready","boolean"))),
    ))
CLOSE_MANIFEST=_manifest("CMFI11","accounting.closechecklist",{
    "PeriodStatus":{"collection":"parameters","field":"PeriodStatus"},
    "Conclusion":{"collection":"totals","field":"Conclusion"},
})

YEAR_END_CONTRACT=JSForm.ReportDatasetContract(
    "accounting.yearend",1,"accounting.periods.override",(
        JSForm.ReportCollection("church","Church",(field("ID","Church ID","integer"),field("Church","Church Name"),field("Logo","Church Logo","image"))),
        JSForm.ReportCollection("organization","Accounting Organization",(field("ID","Organization ID","integer"),field("LegalName","Legal Name"),field("ReportingBasis","Reporting Basis"),field("BaseCurrency","Base Currency"))),
        JSForm.ReportCollection("parameters","Fiscal Year",(field("Display","Fiscal Year"),field("Status","Status"),field("Conclusion","Conclusion"),field("ClosingTransaction","Closing Transaction"),field("HasBlockers","Has Blockers","boolean"))),
        JSForm.ReportCollection("records","Fund Close Summary",(
            field("Fund","Fund"),field("Revenue","Revenue","currency"),field("Expense","Expense","currency"),
            field("Transfers","Transfers","currency"),field("Change","Change","currency"),field("NetAssetAccount","Net Asset Account"))),
        JSForm.ReportCollection("blockers","Close Blockers",(field("Blocker","Blocker"),)),
        JSForm.ReportCollection("totals","Protected Conclusion",(
            field("Revenue","Total Revenue","currency"),field("Expense","Total Expense","currency"),
            field("Transfers","Total Transfers","currency"),field("Change","Total Change","currency"),field("Conclusion","Conclusion"))),
    ))
YEAR_END_MANIFEST=_manifest("CMFI14","accounting.yearend",{
    "Status":{"collection":"parameters","field":"Status"},"ClosingTransaction":{"collection":"parameters","field":"ClosingTransaction"},
    "ChangeTotal":{"collection":"totals","field":"Change"},"Conclusion":{"collection":"totals","field":"Conclusion"},
})

AUDIT_CONTRACT=JSForm.ReportDatasetContract(
    "accounting.audithistory",1,"accounting.audit.view",(
        JSForm.ReportCollection("church","Church",(field("ID","Church ID","integer"),field("Church","Church Name"),field("Logo","Church Logo","image"))),
        JSForm.ReportCollection("organization","Accounting Organization",(field("ID","Organization ID","integer"),field("LegalName","Legal Name"),field("ReportingBasis","Reporting Basis"),field("BaseCurrency","Base Currency"))),
        JSForm.ReportCollection("parameters","Filters",(field("Display","Applied Filters"),)),
        JSForm.ReportCollection("records","Audit Events",(
            field("OccurredAt","Date and Time","datetime"),field("Organization","Organization"),field("User","User"),
            field("Action","Action"),field("Entity","Entity"),field("EntityID","Entity ID"),field("Reason","Reason"),
            field("Before","Before JSON"),field("After","After JSON"))),
        JSForm.ReportCollection("totals","Protected Audit Count",(field("Count","Event Count","integer"),)),
    ))
AUDIT_MANIFEST=_manifest("CMFI09","accounting.audithistory",{
    "ConfidentialLabel":{"label":"CONFIDENTIAL ACCOUNTING AUDIT RECORD"},
    "EventCount":{"collection":"totals","field":"Count"},
})
AUDIT_MANIFEST=JSForm.ReportProtectionManifest(
    required_settings={**AUDIT_MANIFEST.required_settings,"classification":"confidential"},
    required_bands=AUDIT_MANIFEST.required_bands,
    required_controls=AUDIT_MANIFEST.required_controls,
)


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
            "organization": [{"ID": row[0],
                              "LegalName": "" if (row[5] or row[1]) == row[1] else row[1],
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


class FunctionalExpenseDatasetProvider(_AccountingDatasetProvider):
    def __init__(self, connection, authorization, service=None):
        super().__init__(connection, authorization)
        self.service=service or FunctionalExpenseService(connection)

    def build(self, organization_id, date_from, date_to):
        self.authorization.require("accounting.reports.run", "Create Functional Expense dataset")
        collections=self._identity(organization_id)
        result=self.service.report(organization_id,date_from,date_to)
        records=[]
        for code,name,values,total in result["rows"]:
            for index,(_,function_name) in enumerate(result["functions"]):
                records.append({"Account":f"{code} - {name}","Function":function_name,
                                "Amount":values[index]})
        collections.update({
            "parameters":[{"FromDate":date_from,"ThroughDate":date_to,
                           "Display":f"{date_from.strftime('%B %d, %Y')} through {date_to.strftime('%B %d, %Y')}"}],
            "records":records,"totals":[{"GrandTotal":result["grand_total"]}],
        })
        return JSForm.ReportDataset.create(FUNCTIONAL_CONTRACT,collections)


class BudgetDatasetProvider(_AccountingDatasetProvider):
    def __init__(self,connection,authorization,service=None):
        super().__init__(connection,authorization);self.service=service or BudgetActualService(connection)

    def _selection(self,budget_id,period_id=None):
        cursor=self.connection.cursor()
        try:
            if period_id is None:
                cursor.execute(
                    "SELECT b.OrganizationID,b.Name,y.Name,p.ID,p.Name,b.DetailMode "
                    "FROM tblAccountingBudget b JOIN tblAccountingFiscalYear y ON y.ID=b.FiscalYearID "
                    "JOIN tblAccountingFiscalPeriod p ON p.FiscalYearID=b.FiscalYearID "
                    f"WHERE b.ID={self.marker} AND b.Status='ADOPTED' ORDER BY p.PeriodNumber DESC LIMIT 1",
                    (budget_id,),)
            else:
                cursor.execute(
                    "SELECT b.OrganizationID,b.Name,y.Name,p.ID,p.Name,b.DetailMode "
                    "FROM tblAccountingBudget b JOIN tblAccountingFiscalYear y ON y.ID=b.FiscalYearID "
                    "JOIN tblAccountingFiscalPeriod p ON p.FiscalYearID=b.FiscalYearID "
                    f"WHERE b.ID={self.marker} AND b.Status='ADOPTED' AND p.ID={self.marker}",
                    (budget_id,period_id),)
            row=cursor.fetchone()
        finally:cursor.close()
        if row is None:raise ValueError("Select a period from an adopted budget.")
        return row

    def build(self,budget_id,period_id=None,adopted_budget=False):
        self.authorization.require("accounting.reports.run","Create adopted budget report dataset")
        selected=self._selection(budget_id,period_id)
        collections=self._identity(selected[0]);result=self.service.report(budget_id,selected[3])
        summary=[{
            "Account":r[0],"Fund":r[1],"Function":r[2],"PeriodBudget":r[3],"PeriodActual":r[4],
            "PeriodVariance":r[5],"PeriodPercent":r[6],"YTDBudget":r[7],"YTDActual":r[8],
            "YTDVariance":r[9],"YTDPercent":r[10],
        } for r in result["rows"]]
        details=[{"Period":r[0],"Account":r[1],"Fund":r[2],"Function":r[3],
                  "LineItem":r[4],"Budget":r[5],"Note":r[6] or ""} for r in result["details"]]
        def total(name):return sum((row[name] for row in summary),Decimal("0"))
        label=(f"{selected[2]} - {selected[1]} (Adopted Budget)" if adopted_budget
               else f"{selected[2]} - {selected[1]} through {selected[4]}")
        collections.update({
            "parameters":[{"Display":label,"Mode":result["mode"],"ShowDetails":bool(details)}],
            "summary":summary,"details":details,
            "totals":[{name:total(name) for name in (
                "PeriodBudget","PeriodActual","PeriodVariance","YTDBudget","YTDActual","YTDVariance")}],
        })
        contract=ADOPTED_BUDGET_CONTRACT if adopted_budget else BUDGET_ACTUAL_CONTRACT
        return JSForm.ReportDataset.create(contract,collections)


class GeneralLedgerDatasetProvider(_AccountingDatasetProvider):
    def __init__(self,connection,authorization,service=None):
        super().__init__(connection,authorization);self.service=service or GeneralLedgerService(connection)

    def build(self,organization_id,account_id,date_from,date_to,fund_id=None):
        self.authorization.require("accounting.reports.run","Create General Ledger report dataset")
        collections=self._identity(organization_id)
        result=self.service.report(organization_id,account_id,date_from,date_to,fund_id)
        records=[{"Date":r[0],"Number":r[1],"Type":str(r[2]).replace("_"," ").title(),"Transaction":r[3] or "",
                  "Reference":r[4] or "","Fund":r[5],
                  "Description":"" if str(r[6] or "").strip().casefold()==str(r[3] or "").strip().casefold() else (r[6] or ""),
                  "Debit":r[7],"Credit":r[8],"Balance":r[9]} for r in result["rows"]]
        debit=sum((row["Debit"] for row in records),Decimal("0"));credit=sum((row["Credit"] for row in records),Decimal("0"))
        ending=records[-1]["Balance"] if records else result["opening_balance"]
        collections.update({
            "parameters":[{"FromDate":date_from,"ThroughDate":date_to,
                           "Display":f"{result['account']} - {date_from.strftime('%B %d, %Y')} through {date_to.strftime('%B %d, %Y')}"}],
            "records":records,"totals":[{"OpeningBalance":result["opening_balance"],
                "DebitTotal":debit,"CreditTotal":credit,"EndingBalance":ending}],
        })
        return JSForm.ReportDataset.create(GENERAL_LEDGER_CONTRACT,collections)


class RegisterDatasetProvider(_AccountingDatasetProvider):
    def __init__(self,connection,authorization,service=None):
        super().__init__(connection,authorization);self.service=service or AccountingRegisterService(connection)

    def build(self):
        self.authorization.require("accounting.transactions.view","Create Posted Transaction Register dataset")
        source=self.service.transactions()
        cursor=self.connection.cursor()
        try:
            cursor.execute("SELECT ID FROM tblAccountingOrganization WHERE Active=1 ORDER BY ID LIMIT 1")
            selected=cursor.fetchone()
        finally:cursor.close()
        if selected is None:raise ValueError("No active accounting organization is available.")
        collections=self._identity(selected[0])
        if len({str(row[2]) for row in source})>1:
            collections["organization"][0]["LegalName"]="All accounting organizations"
        records=[{"Number":r[1],"Organization":r[2],"Date":r[3],
                  "Type":str(r[4]).replace("_"," ").title(),"Status":str(r[5]).title(),
                  "Description":r[6] or "","Reference":r[7] or "","Total":r[8]} for r in source]
        collections.update({"parameters":[{"Display":"Posted and reversed transactions"}],
                            "records":records,"totals":[{"TransactionCount":len(records),
                            "Total":sum((r["Total"] for r in records),Decimal("0"))}]})
        return JSForm.ReportDataset.create(REGISTER_CONTRACT,collections)


class JournalEntryDatasetProvider(_AccountingDatasetProvider):
    def __init__(self,connection,authorization,service=None):
        super().__init__(connection,authorization);self.service=service or JournalEntryService(connection)

    def build(self,transaction_id):
        self.authorization.require("accounting.transactions.view","Create Journal Entry report dataset")
        result=self.service.report(transaction_id);header=result["header"]
        cursor=self.connection.cursor()
        try:
            cursor.execute(f"SELECT ID FROM tblAccountingOrganization WHERE LegalName={self.marker}",(header[2],))
            selected=cursor.fetchone()
        finally:cursor.close()
        if selected is None:raise ValueError("The transaction organization is unavailable.")
        collections=self._identity(selected[0])
        def attribution(at,name):return f"{at or '(not recorded)'} by {name or '(none)'}"
        metadata={"Display":f"Journal Entry #{header[1]}","Number":header[1],"Date":header[3],
                  "TypeStatus":f"{str(header[4]).replace('_',' ').title()} / {str(header[5]).title()}",
                  "Description":header[6] or "","Reference":header[7] or "",
                  "Created":attribution(header[8],header[9]),"Reviewed":attribution(header[10],header[11]),
                  "Posted":attribution(header[12],header[13]),
                  "ReversalLinks":f"Original: {header[14] or '(none)'}    Reversal: {header[15] or '(none)'}",
                  "HasAttachments":bool(result["attachments"])}
        records=[{"Line":r[0],"Account":r[1],"Fund":r[2],"Function":r[3],"Payee":r[4],
                  "Description":r[5],"Debit":r[6],"Credit":r[7]} for r in result["lines"]]
        attachments=[{"Name":r[0],"Type":r[1],"Hash":r[2],"AddedAt":r[3]} for r in result["attachments"]]
        debit=sum((r["Debit"] for r in records),Decimal("0"));credit=sum((r["Credit"] for r in records),Decimal("0"))
        collections.update({"parameters":[metadata],"records":records,"attachments":attachments,
                            "totals":[{"Debit":debit,"Credit":credit,"Difference":debit-credit}]})
        return JSForm.ReportDataset.create(JOURNAL_CONTRACT,collections)


class ReconciliationDatasetProvider(_AccountingDatasetProvider):
    def __init__(self,connection,authorization,service=None):
        super().__init__(connection,authorization);self.service=service or ReconciliationReportService(connection)

    def build(self,reconciliation_id):
        self.authorization.require("accounting.reports.run","Create Bank Reconciliation report dataset")
        cursor=self.connection.cursor()
        try:
            cursor.execute(
                "SELECT b.OrganizationID,u.DisplayName,r.CompletedAt FROM tblAccountingReconciliation r "
                "JOIN tblAccountingBankAccount b ON b.ID=r.BankAccountID JOIN tblUser u ON u.ID=r.PreparedByUserID "
                f"WHERE r.ID={self.marker} AND r.Status='COMPLETED'",(reconciliation_id,))
            metadata=cursor.fetchone()
        finally:cursor.close()
        if metadata is None:raise ValueError("Select a completed reconciliation.")
        result=self.service.detail(reconciliation_id);collections=self._identity(metadata[0])
        records=[{"Status":r[0],"Date":r[1],"Number":r[2],"Description":r[3] or "",
                  "Reference":r[4] or "","Amount":r[5],"ClearedDate":r[6]} for r in result["items"]]
        collections.update({
            "parameters":[{"Display":f"{result['bank_account']} - statement date {result['statement_date']}",
                           "BankAccount":result["bank_account"],"StatementDate":result["statement_date"],
                           "PreparedBy":metadata[1],"CompletedAt":metadata[2]}],
            "records":records,"totals":[{"Beginning":result["beginning"],"Cleared":result["cleared_total"],
                "Ending":result["ending"],"Difference":result["difference"],
                "Outstanding":result["outstanding_total"]}],
        })
        return JSForm.ReportDataset.create(RECONCILIATION_CONTRACT,collections)


class CloseChecklistDatasetProvider(_AccountingDatasetProvider):
    def __init__(self,connection,authorization,service=None):
        super().__init__(connection,authorization);self.service=service or CloseChecklistService(connection)

    def build(self,organization_id,period_id):
        self.authorization.require("accounting.reports.run","Create Fiscal Period Close Checklist dataset")
        collections=self._identity(organization_id);result=self.service.run(organization_id,period_id)
        conclusion=("PERIOD CLOSED" if result["status"]=="CLOSED" else
                    "READY TO CLOSE" if result["ready"] else "NOT READY TO CLOSE")
        collections.update({
            "parameters":[{"Display":f"{result['period']} ({result['start']} through {result['end']})",
                           "Start":result["start"],"End":result["end"],
                           "PeriodStatus":result["status"],"Conclusion":conclusion}],
            "records":[{"Check":r["check"],"Status":r["status"],"Detail":r["detail"]}
                       for r in result["checks"]],
            "totals":[{"Conclusion":conclusion,"Ready":result["ready"]}],
        })
        return JSForm.ReportDataset.create(CLOSE_CONTRACT,collections)


class YearEndDatasetProvider(_AccountingDatasetProvider):
    def __init__(self,connection,authorization,service=None):
        super().__init__(connection,authorization);self.service=service or YearEndService(connection)
    def build(self,organization_id,year_id):
        self.authorization.require("accounting.periods.override","Create Year-End Close report dataset")
        collections=self._identity(organization_id);result=self.service.preview(organization_id,year_id);year=result["year"]
        conclusion=("YEAR CLOSED" if year[3]=="CLOSED" else "READY TO CLOSE" if result["ready"] else "NOT READY TO CLOSE")
        records=[{"Fund":f"{r[1]} - {r[2]}","Revenue":r[3],"Expense":r[4],"Transfers":r[5],
                  "Change":r[6],"NetAssetAccount":r[7]} for r in result["rows"]]
        def total(name):return sum((r[name] for r in records),Decimal("0"))
        collections.update({"parameters":[{"Display":f"{year[0]} ({year[1]} through {year[2]})",
            "Status":year[3],"Conclusion":conclusion,"ClosingTransaction":str(year[4] or "(none)"),
            "HasBlockers":bool(result["blockers"])}],"records":records,
            "blockers":[{"Blocker":b} for b in result["blockers"]],
            "totals":[{"Revenue":total("Revenue"),"Expense":total("Expense"),"Transfers":total("Transfers"),
                       "Change":total("Change"),"Conclusion":conclusion}]})
        return JSForm.ReportDataset.create(YEAR_END_CONTRACT,collections)


class AuditDatasetProvider(_AccountingDatasetProvider):
    def __init__(self,connection,authorization,service=None):
        super().__init__(connection,authorization);self.service=service or AccountingAuditService(connection)
    def build(self,organization_id=None,user_text="",action_text="",entity_text="",date_from=None,date_to=None):
        self.authorization.require("accounting.audit.view","Create Accounting Audit History dataset")
        rows=self.service.events(organization_id,user_text,action_text,entity_text,date_from,date_to)
        selected=organization_id
        if selected is None:
            cursor=self.connection.cursor()
            try:cursor.execute("SELECT ID FROM tblAccountingOrganization ORDER BY ID LIMIT 1");row=cursor.fetchone()
            finally:cursor.close()
            if row is None:raise ValueError("No accounting organization is available.")
            selected=row[0]
        collections=self._identity(selected)
        if organization_id is None:collections["organization"][0]["LegalName"]="All accounting organizations"
        display="; ".join(x for x in (f"User: {user_text}" if user_text else "",f"Action: {action_text}" if action_text else "",
            f"Entity: {entity_text}" if entity_text else "",f"From: {date_from}" if date_from else "",f"Through: {date_to}" if date_to else "") if x) or "All audit events"
        def readable_json(value):
            if not value:return "(none)"
            try:return json.dumps(json.loads(value),ensure_ascii=False,separators=(", ",": "))
            except (TypeError,ValueError):return str(value)
        records=[{"OccurredAt":r[1],"Organization":r[2],"User":r[3],
                  "Action":str(r[4]).replace("_"," ").title(),
                  "Entity":str(r[5]).replace("_"," ").title(),
                  "EntityID":r[6],"Reason":"Reason: "+(r[7] or "(none)"),
                  "Before":"Before:\n"+readable_json(r[8]),"After":"After:\n"+readable_json(r[9])} for r in rows]
        collections.update({"parameters":[{"Display":display}],"records":records,"totals":[{"Count":len(records)}]})
        return JSForm.ReportDataset.create(AUDIT_CONTRACT,collections)


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
            "CMFI01", local_app_data=self.local_app_data,
            starter_directory=ACCOUNTING_DEFINITIONS,
        )
        definition = JSForm.ReportDefinitionLoader().load(definition_path)
        TRIAL_BALANCE_MANIFEST.validate(definition)
        provider = self.trial_balance_provider or TrialBalanceDatasetProvider(
            self.connection, self.authorization,
        )
        dataset = provider.build(organization_id, as_of_date)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        output = self.output_directory / "CMFI01.pdf"
        rendered = JSForm.PDFReportRenderer().render(
            definition, dataset, output,
            context={"run_user": self.session.display_name},
        )
        self.processes.open_file(rendered)
        return rendered

    def _run(self, code, contract, manifest, provider, *parameters):
        self.authorization.require(contract.required_permission, f"run the {code} report")
        definition_path = resolve_report_definition(
            code, local_app_data=self.local_app_data, starter_directory=ACCOUNTING_DEFINITIONS,
        )
        definition = JSForm.ReportDefinitionLoader().load(definition_path)
        manifest.validate(definition)
        dataset = provider.build(*parameters)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        output = self._available_output(code)
        rendered = JSForm.PDFReportRenderer().render(
            definition, dataset, output, context={"run_user": self.session.display_name},
        )
        self.processes.open_file(rendered)
        return rendered

    def _available_output(self, code):
        output=self.output_directory/f"{code}.pdf"
        if not output.exists():return output
        try:
            with output.open("ab"):
                pass
            return output
        except PermissionError:
            stamp=datetime.now().strftime("%Y%m%d-%H%M%S")
            return self.output_directory/f"{code}-{stamp}.pdf"

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
            "CMFI03", POSITION_CONTRACT, POSITION_MANIFEST,
            FinancialPositionDatasetProvider(self.connection, self.authorization),
            organization_id, as_of_date,
        )

    def design_financial_position(self, organization_id, as_of_date):
        return self._design(
            "CMFI03", POSITION_CONTRACT, POSITION_MANIFEST,
            FinancialPositionDatasetProvider(self.connection,self.authorization),
            organization_id,as_of_date,
        )

    def run_activities(self, organization_id, date_from, date_to):
        return self._run(
            "CMFI04", ACTIVITIES_CONTRACT, ACTIVITIES_MANIFEST,
            ActivitiesDatasetProvider(self.connection, self.authorization),
            organization_id, date_from, date_to,
        )

    def design_activities(self, organization_id, date_from, date_to):
        return self._design(
            "CMFI04", ACTIVITIES_CONTRACT, ACTIVITIES_MANIFEST,
            ActivitiesDatasetProvider(self.connection,self.authorization),
            organization_id,date_from,date_to,
        )

    def run_funds(self, organization_id, date_from, date_to):
        return self._run(
            "CMFI05", FUND_CONTRACT, FUND_MANIFEST,
            FundDatasetProvider(self.connection, self.authorization),
            organization_id, date_from, date_to,
        )

    def design_funds(self, organization_id, date_from, date_to):
        return self._design(
            "CMFI05", FUND_CONTRACT, FUND_MANIFEST,
            FundDatasetProvider(self.connection,self.authorization),
            organization_id,date_from,date_to,
        )

    def run_functional_expenses(self, organization_id, date_from, date_to):
        return self._run(
            "CMFI08",FUNCTIONAL_CONTRACT,FUNCTIONAL_MANIFEST,
            FunctionalExpenseDatasetProvider(self.connection,self.authorization),
            organization_id,date_from,date_to,
        )

    def design_functional_expenses(self, organization_id, date_from, date_to):
        return self._design(
            "CMFI08",FUNCTIONAL_CONTRACT,FUNCTIONAL_MANIFEST,
            FunctionalExpenseDatasetProvider(self.connection,self.authorization),
            organization_id,date_from,date_to,
        )

    def run_budget_actual(self,budget_id,period_id):
        return self._run("CMFI07",BUDGET_ACTUAL_CONTRACT,BUDGET_ACTUAL_MANIFEST,
                         BudgetDatasetProvider(self.connection,self.authorization),budget_id,period_id)

    def design_budget_actual(self,budget_id,period_id):
        return self._design("CMFI07",BUDGET_ACTUAL_CONTRACT,BUDGET_ACTUAL_MANIFEST,
                            BudgetDatasetProvider(self.connection,self.authorization),budget_id,period_id)

    def run_adopted_budget(self,budget_id):
        provider=BudgetDatasetProvider(self.connection,self.authorization)
        class Adopted:
            def build(inner,*arguments):return provider.build(*arguments,adopted_budget=True)
        return self._run("CMFI10",ADOPTED_BUDGET_CONTRACT,ADOPTED_BUDGET_MANIFEST,Adopted(),budget_id)

    def run_general_ledger(self,organization_id,account_id,date_from,date_to,fund_id=None):
        return self._run("CMFI02",GENERAL_LEDGER_CONTRACT,GENERAL_LEDGER_MANIFEST,
                         GeneralLedgerDatasetProvider(self.connection,self.authorization),
                         organization_id,account_id,date_from,date_to,fund_id)

    def design_general_ledger(self,organization_id,account_id,date_from,date_to,fund_id=None):
        return self._design("CMFI02",GENERAL_LEDGER_CONTRACT,GENERAL_LEDGER_MANIFEST,
                            GeneralLedgerDatasetProvider(self.connection,self.authorization),
                            organization_id,account_id,date_from,date_to,fund_id)

    def run_register(self):
        return self._run("CMFI13",REGISTER_CONTRACT,REGISTER_MANIFEST,
                         RegisterDatasetProvider(self.connection,self.authorization))

    def design_register(self):
        return self._design("CMFI13",REGISTER_CONTRACT,REGISTER_MANIFEST,
                            RegisterDatasetProvider(self.connection,self.authorization))

    def run_journal_entry(self,transaction_id):
        return self._run("CMFI12",JOURNAL_CONTRACT,JOURNAL_MANIFEST,
                         JournalEntryDatasetProvider(self.connection,self.authorization),transaction_id)

    def design_journal_entry(self,transaction_id):
        return self._design("CMFI12",JOURNAL_CONTRACT,JOURNAL_MANIFEST,
                            JournalEntryDatasetProvider(self.connection,self.authorization),transaction_id)

    def run_reconciliation(self,reconciliation_id):
        return self._run("CMFI06",RECONCILIATION_CONTRACT,RECONCILIATION_MANIFEST,
                         ReconciliationDatasetProvider(self.connection,self.authorization),reconciliation_id)

    def design_reconciliation(self,reconciliation_id):
        return self._design("CMFI06",RECONCILIATION_CONTRACT,RECONCILIATION_MANIFEST,
                            ReconciliationDatasetProvider(self.connection,self.authorization),reconciliation_id)

    def run_close_checklist(self,organization_id,period_id):
        return self._run("CMFI11",CLOSE_CONTRACT,CLOSE_MANIFEST,
                         CloseChecklistDatasetProvider(self.connection,self.authorization),organization_id,period_id)

    def design_close_checklist(self,organization_id,period_id):
        return self._design("CMFI11",CLOSE_CONTRACT,CLOSE_MANIFEST,
                            CloseChecklistDatasetProvider(self.connection,self.authorization),organization_id,period_id)

    def run_year_end(self,organization_id,year_id):
        return self._run("CMFI14",YEAR_END_CONTRACT,YEAR_END_MANIFEST,
                         YearEndDatasetProvider(self.connection,self.authorization),organization_id,year_id)

    def run_audit(self,organization_id=None,user_text="",action_text="",entity_text="",date_from=None,date_to=None):
        return self._run("CMFI09",AUDIT_CONTRACT,AUDIT_MANIFEST,
                         AuditDatasetProvider(self.connection,self.authorization),organization_id,user_text,action_text,entity_text,date_from,date_to)

    def design_trial_balance(self, organization_id, as_of_date):
        self.authorization.require("accounting.reports.run", "view Trial Balance data")
        self.authorization.require(
            "accounting.reports.design", "customize accounting report layouts",
        )
        definition_path = ensure_user_definition(
            "CMFI01", local_app_data=self.local_app_data,
            starter_directory=ACCOUNTING_DEFINITIONS,
        )

        def preview(definition):
            TRIAL_BALANCE_MANIFEST.validate(definition)
            provider = self.trial_balance_provider or TrialBalanceDatasetProvider(
                self.connection, self.authorization,
            )
            dataset = provider.build(organization_id, as_of_date)
            output = Path(tempfile.gettempdir()) / "ChurchManager-CMFI01-preview.pdf"
            return JSForm.PDFReportRenderer().render(
                definition, dataset, output,
                context={"run_user": self.session.display_name},
            )

        return JSForm.open_report_designer(
            definition_path,
            dataset_contract=TRIAL_BALANCE_CONTRACT,
            preview_handler=preview,
            starter_definition_path=ACCOUNTING_DEFINITIONS / "CMFI01.json",
            export_directory=self.output_directory,
            protection_manifest=TRIAL_BALANCE_MANIFEST,
        )
