from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import JSForm

from authorization import AuthorizationDenied
from accounting.reporting import (
    AccountingVisualReportService, ACTIVITIES_CONTRACT, ACTIVITIES_MANIFEST,
    ActivitiesDatasetProvider, FUND_CONTRACT, FUND_MANIFEST, FundDatasetProvider,
    FUNCTIONAL_CONTRACT, FUNCTIONAL_MANIFEST, FunctionalExpenseDatasetProvider,
    ADOPTED_BUDGET_CONTRACT, ADOPTED_BUDGET_MANIFEST,
    BUDGET_ACTUAL_CONTRACT, BUDGET_ACTUAL_MANIFEST, BudgetDatasetProvider,
    GENERAL_LEDGER_CONTRACT, GENERAL_LEDGER_MANIFEST, GeneralLedgerDatasetProvider,
    REGISTER_CONTRACT, REGISTER_MANIFEST,
    JOURNAL_CONTRACT, JOURNAL_MANIFEST, JournalEntryDatasetProvider,
    RECONCILIATION_CONTRACT, RECONCILIATION_MANIFEST,
    POSITION_CONTRACT, POSITION_MANIFEST, FinancialPositionDatasetProvider,
    TRIAL_BALANCE_CONTRACT, TRIAL_BALANCE_MANIFEST, TrialBalanceDatasetProvider,
)


class Authorization:
    def __init__(self, allowed=True):
        self.allowed = allowed
        self.checked = []

    def require(self, permission, operation=None):
        self.checked.append(permission)
        if not self.allowed:
            raise AuthorizationDenied(operation or permission)


class Cursor:
    def __init__(self, identity=None):
        self.executed = []
        self.identity = identity or (
            1, "Reformation Lutheran Church", "MODIFIED_CASH", "USD",
            4, "Reformation Lutheran Church", None,
        )

    def execute(self, sql, values=()):
        self.executed.append((sql, values))

    def fetchone(self):
        return self.identity

    def close(self):
        pass


class Connection:
    __module__ = "mariadb.connections"

    def __init__(self, identity=None):
        self.cursors = []
        self.identity = identity

    def cursor(self):
        cursor = Cursor(self.identity)
        self.cursors.append(cursor)
        return cursor


class TrialService:
    @staticmethod
    def rows(organization_id, as_of_date):
        return [
            ("1000", "Cash", "ASSET", "DEBIT", Decimal("125"), Decimal("25"),
             Decimal("100"), Decimal("0")),
            ("4000", "Offerings", "REVENUE", "CREDIT", Decimal("0"), Decimal("100"),
             Decimal("0"), Decimal("100")),
        ]


class PositionService:
    @staticmethod
    def rows(organization_id, as_of_date):
        return (
            [("1000","Cash",Decimal("100"))],
            [("2000","Payable",Decimal("20"))],
            [("3000","Net assets","WITHOUT_DONOR_RESTRICTIONS",Decimal("50"))],
            {"WITHOUT_DONOR_RESTRICTIONS":Decimal("30"),
             "WITH_DONOR_RESTRICTIONS":Decimal("0")},
        )


class ActivitiesServiceStub:
    @staticmethod
    def rows(organization_id, date_from, date_to):
        return [
            ("4000","Offerings","REVENUE",Decimal("1000"),Decimal("500")),
            ("5000","Ministry","EXPENSE",Decimal("250"),Decimal("100")),
        ]


class FundService:
    @staticmethod
    def report(organization_id, date_from, date_to):
        return [("GEN","General","WITHOUT_DONOR_RESTRICTIONS",Decimal("100"),
                 Decimal("50"),Decimal("25"),Decimal("0"),Decimal("5"),Decimal("130"))]


class FunctionalService:
    @staticmethod
    def report(organization_id,date_from,date_to):
        return {"functions":[(1,"Worship"),(2,"Education")],
                "rows":[("5000","Supplies",[Decimal("125"),Decimal("25")],Decimal("150"))],
                "totals":[Decimal("125"),Decimal("25")],"grand_total":Decimal("150")}


class BudgetCursor(Cursor):
    def execute(self,sql,values=()):
        self.executed.append((sql,values));self.sql=sql
    def fetchone(self):
        if "tblAccountingBudget" in self.sql:
            return (1,"Ministry Budget","2027",12,"December","DETAILED")
        return super().fetchone()


class BudgetConnection(Connection):
    def cursor(self):
        cursor=BudgetCursor(self.identity);self.cursors.append(cursor);return cursor


class BudgetActualServiceStub:
    @staticmethod
    def report(budget_id,period_id):
        return {"mode":"DETAILED","rows":[
            ("5000 - Ministry","GEN - General","Worship",Decimal("100"),Decimal("75"),
             Decimal("25"),Decimal("75.0"),Decimal("1200"),Decimal("900"),Decimal("300"),Decimal("75.0"))],
            "details":[("January","5000 - Ministry","GEN - General","Worship",
                        "Altar supplies",Decimal("100"),"Annual plan")]}


class GeneralLedgerServiceStub:
    @staticmethod
    def report(organization_id,account_id,date_from,date_to,fund_id=None):
        return {"account":"1000 - Checking","normal_balance":"DEBIT",
                "opening_balance":Decimal("100"),"rows":[
                    (date(2027,1,5),1,"RECEIPT","Offering","DEP-1","GEN - General","Sunday",
                     Decimal("50"),Decimal("0"),Decimal("150"))]}


class JournalServiceStub:
    @staticmethod
    def report(transaction_id):
        return {"header":(transaction_id,7,"Reformation Lutheran Church",date(2027,1,11),
                "CASH_DISBURSEMENT","POSTED","Test payment","CHK-7",datetime(2027,1,11,9),
                "Jonathan Watt",datetime(2027,1,11,10),"Sarah Johnson",datetime(2027,1,11,11),
                "Jonathan Watt",None,None),
                "lines":[(1,"1000 - Checking","GEN - General","","Vendor","Payment",
                           Decimal("0"),Decimal("25")),
                         (2,"5000 - Expense","GEN - General","","Vendor","Payment",
                           Decimal("25"),Decimal("0"))],
                "attachments":[("receipt.pdf","application/pdf","abc123",datetime(2027,1,11,9,30))]}


class Session:
    display_name = "Jonathan Watt"


class Processes:
    def __init__(self):
        self.opened = []

    def open_file(self, path):
        self.opened.append(Path(path))


class TestAccountingVisualReports(unittest.TestCase):
    def test_trial_balance_contract_and_starter_are_valid_and_protected(self):
        starter = Path(__file__).parents[1] / "accounting" / "report_definitions" / "CMFI01.json"
        definition = JSForm.ReportDefinitionLoader().load(starter)
        self.assertEqual(definition.dataset_name, TRIAL_BALANCE_CONTRACT.name)
        self.assertIs(TRIAL_BALANCE_MANIFEST.validate(definition), definition)

    def test_dataset_rechecks_permission_before_database_read(self):
        connection = Connection()
        provider = TrialBalanceDatasetProvider(
            connection, Authorization(False), service=TrialService(),
        )
        with self.assertRaises(AuthorizationDenied):
            provider.build(1, date(2026, 8, 12))
        self.assertEqual(connection.cursors, [])

    def test_dataset_preserves_native_values_and_locked_totals(self):
        authorization = Authorization()
        dataset = TrialBalanceDatasetProvider(
            Connection(), authorization, service=TrialService(),
        ).build(1, date(2026, 8, 12))
        self.assertEqual(authorization.checked, ["accounting.reports.run"])
        self.assertIsInstance(dataset.collections["accounts"][0]["DebitActivity"], Decimal)
        self.assertIsInstance(dataset.collections["parameters"][0]["AsOfDate"], date)
        self.assertEqual(dataset.collections["totals"][0]["Difference"], Decimal("0"))

    def test_unlinked_accounting_organization_uses_its_legal_name(self):
        connection = Connection((
            1, "ChurchManager Sample Congregation", "MODIFIED_CASH", "USD",
            None, None, None,
        ))
        dataset = TrialBalanceDatasetProvider(
            connection, Authorization(), service=TrialService(),
        ).build(1, date(2027, 8, 12))
        self.assertEqual(
            dataset.collections["church"][0]["Church"],
            "ChurchManager Sample Congregation",
        )
        self.assertIn("LEFT JOIN rpt_church_identity", connection.cursors[0].executed[0][0])

    def test_trial_balance_visual_service_opens_rendered_pdf(self):
        processes = Processes()
        authorization = Authorization()
        with tempfile.TemporaryDirectory() as folder:
            provider = TrialBalanceDatasetProvider(
                Connection(), authorization, service=TrialService(),
            )
            service = AccountingVisualReportService(
                Connection(), authorization, Session(), processes=processes,
                output_directory=folder, local_app_data=folder,
                trial_balance_provider=provider,
            )
            output = service.run_trial_balance(1, date(2026, 8, 12))
            self.assertTrue(output.is_file())
            self.assertEqual(processes.opened, [output])
            self.assertGreater(output.stat().st_size, 500)

    def test_accounting_design_permission_is_sensitive_and_master_only(self):
        sql = (Path(__file__).parents[1] / "migrations" /
               "020_add_accounting_report_designer_permission.sql").read_text(encoding="utf-8")
        self.assertIn("'accounting.reports.design'", sql)
        self.assertIn("IsSensitive,Active", sql)
        self.assertIn("r.Name='Master Administrator'", sql)

    def test_core_statement_starters_validate_against_contracts_and_manifests(self):
        root = Path(__file__).parents[1] / "accounting" / "report_definitions"
        loader = JSForm.ReportDefinitionLoader()
        for code, contract, manifest in (
            ("CMFI03",POSITION_CONTRACT,POSITION_MANIFEST),
            ("CMFI04",ACTIVITIES_CONTRACT,ACTIVITIES_MANIFEST),
            ("CMFI05",FUND_CONTRACT,FUND_MANIFEST),
            ("CMFI08",FUNCTIONAL_CONTRACT,FUNCTIONAL_MANIFEST),
            ("CMFI07",BUDGET_ACTUAL_CONTRACT,BUDGET_ACTUAL_MANIFEST),
            ("CMFI10",ADOPTED_BUDGET_CONTRACT,ADOPTED_BUDGET_MANIFEST),
            ("CMFI02",GENERAL_LEDGER_CONTRACT,GENERAL_LEDGER_MANIFEST),
            ("CMFI13",REGISTER_CONTRACT,REGISTER_MANIFEST),
            ("CMFI12",JOURNAL_CONTRACT,JOURNAL_MANIFEST),
            ("CMFI06",RECONCILIATION_CONTRACT,RECONCILIATION_MANIFEST),
        ):
            definition=loader.load(root / f"{code}.json")
            self.assertEqual(definition.dataset_name,contract.name)
            manifest.validate(definition)

    def test_financial_position_dataset_preserves_accounting_equation(self):
        dataset=FinancialPositionDatasetProvider(
            Connection(),Authorization(),PositionService(),
        ).build(1,date(2027,8,12))
        totals=dataset.collections["totals"][0]
        self.assertEqual(totals["TotalAssets"],Decimal("100"))
        self.assertEqual(totals["LiabilitiesAndNetAssets"],Decimal("100"))
        self.assertEqual(totals["Difference"],Decimal("0"))

    def test_activities_dataset_calculates_change_by_restriction_class(self):
        dataset=ActivitiesDatasetProvider(
            Connection(),Authorization(),ActivitiesServiceStub(),
        ).build(1,date(2027,1,1),date(2027,8,12))
        totals=dataset.collections["totals"][0]
        self.assertEqual(totals["WithoutRestrictions"],Decimal("750"))
        self.assertEqual(totals["WithRestrictions"],Decimal("400"))
        self.assertEqual(totals["Total"],Decimal("1150"))

    def test_fund_dataset_reconciles_beginning_and_ending_totals(self):
        dataset=FundDatasetProvider(
            Connection(),Authorization(),FundService(),
        ).build(1,date(2027,1,1),date(2027,8,12))
        totals=dataset.collections["totals"][0]
        self.assertEqual(totals["Beginning"],Decimal("100"))
        self.assertEqual(totals["Ending"],Decimal("130"))

    def test_functional_expense_dataset_flattens_dynamic_matrix_values(self):
        dataset=FunctionalExpenseDatasetProvider(
            Connection(),Authorization(),FunctionalService(),
        ).build(1,date(2027,1,1),date(2027,8,12))
        self.assertEqual([row["Function"] for row in dataset.collections["records"]],
                         ["Worship","Education"])
        self.assertEqual(dataset.collections["totals"][0]["GrandTotal"],Decimal("150"))

    def test_budget_dataset_keeps_general_summary_and_optional_details(self):
        provider=BudgetDatasetProvider(BudgetConnection(),Authorization(),BudgetActualServiceStub())
        dataset=provider.build(3,12)
        self.assertEqual(dataset.collections["parameters"][0]["Mode"],"DETAILED")
        self.assertTrue(dataset.collections["parameters"][0]["ShowDetails"])
        self.assertEqual(dataset.collections["summary"][0]["YTDVariance"],Decimal("300"))
        self.assertEqual(dataset.collections["details"][0]["LineItem"],"Altar supplies")

    def test_budget_summary_columns_fit_printable_landscape_width(self):
        root=Path(__file__).parents[1]/"accounting"/"report_definitions"
        for code in ("CMFI07","CMFI10"):
            definition=JSForm.ReportDefinitionLoader().load(root/f"{code}.json")
            columns=definition.controls["Records"]["columns"]
            self.assertEqual(sum(column["width"] for column in columns),720)

    def test_audit_report_uses_readable_event_cards_within_legal_width(self):
        definition=JSForm.ReportDefinitionLoader().load(
            Path(__file__).parents[1]/"accounting"/"report_definitions"/"CMFI09.json")
        control=definition.controls["Records"]
        self.assertEqual(control["type"],"repeater")
        self.assertEqual(control["size"][0],936)
        self.assertEqual({item["field"] for item in control["items"]},
                         {"OccurredAt","Organization","User","Action","Entity","EntityID","Reason","Before","After"})
        state_items={item["field"]:item for item in control["items"] if item["field"] in {"Before","After"}}
        self.assertEqual(state_items["Before"]["size"][0],915)
        self.assertEqual(state_items["After"]["size"][0],915)

    def test_general_ledger_dataset_preserves_opening_and_running_balances(self):
        dataset=GeneralLedgerDatasetProvider(
            Connection(),Authorization(),GeneralLedgerServiceStub(),
        ).build(1,10,date(2027,1,1),date(2027,1,31))
        self.assertEqual(dataset.collections["totals"][0]["OpeningBalance"],Decimal("100"))
        self.assertEqual(dataset.collections["totals"][0]["EndingBalance"],Decimal("150"))
        self.assertEqual(dataset.collections["records"][0]["Balance"],Decimal("150"))
        self.assertEqual(dataset.collections["records"][0]["Type"],"Receipt")
        self.assertEqual(dataset.collections["organization"][0]["LegalName"],"")
        definition=JSForm.ReportDefinitionLoader().load(
            Path(__file__).parents[1]/"accounting"/"report_definitions"/"CMFI02.json")
        self.assertEqual(definition.settings["pagesize"],"legal")
        self.assertEqual(sum(column["width"] for column in definition.controls["Records"]["columns"]),900)

    def test_journal_entry_dataset_preserves_attribution_hashes_and_balance(self):
        dataset=JournalEntryDatasetProvider(
            Connection(),Authorization(),JournalServiceStub(),
        ).build(7)
        self.assertIn("Sarah Johnson",dataset.collections["parameters"][0]["Reviewed"])
        self.assertEqual(dataset.collections["attachments"][0]["Hash"],"abc123")
        self.assertEqual(dataset.collections["totals"][0]["Difference"],Decimal("0"))

    def test_core_statement_starters_render_to_pdf(self):
        root=Path(__file__).parents[1]/"accounting"/"report_definitions"
        providers=(
            ("CMFI03",FinancialPositionDatasetProvider(Connection(),Authorization(),PositionService()),
             (1,date(2027,8,12))),
            ("CMFI04",ActivitiesDatasetProvider(Connection(),Authorization(),ActivitiesServiceStub()),
             (1,date(2027,1,1),date(2027,8,12))),
            ("CMFI05",FundDatasetProvider(Connection(),Authorization(),FundService()),
             (1,date(2027,1,1),date(2027,8,12))),
            ("CMFI08",FunctionalExpenseDatasetProvider(Connection(),Authorization(),FunctionalService()),
             (1,date(2027,1,1),date(2027,8,12))),
            ("CMFI07",BudgetDatasetProvider(BudgetConnection(),Authorization(),BudgetActualServiceStub()),
             (3,12)),
            ("CMFI02",GeneralLedgerDatasetProvider(Connection(),Authorization(),GeneralLedgerServiceStub()),
             (1,10,date(2027,1,1),date(2027,1,31))),
            ("CMFI12",JournalEntryDatasetProvider(Connection(),Authorization(),JournalServiceStub()),(7,)),
        )
        with tempfile.TemporaryDirectory() as folder:
            for code,provider,arguments in providers:
                definition=JSForm.ReportDefinitionLoader().load(root/f"{code}.json")
                output=JSForm.PDFReportRenderer().render(
                    definition,provider.build(*arguments),Path(folder)/f"{code}.pdf",
                    context={"run_user":"Jonathan Watt"},
                )
                self.assertGreater(output.stat().st_size,500)

    def test_designer_requires_run_and_accounting_design_permissions(self):
        authorization = Authorization(False)
        service = AccountingVisualReportService(
            Connection(), authorization, Session(), processes=Processes(),
        )
        with self.assertRaises(AuthorizationDenied):
            service.design_trial_balance(1, date(2026, 8, 12))
        self.assertEqual(authorization.checked, ["accounting.reports.run"])

    def test_open_report_uses_timestamped_name_when_previous_pdf_is_locked(self):
        with tempfile.TemporaryDirectory() as folder:
            service=AccountingVisualReportService(Connection(),Authorization(),Session(),
                                                   output_directory=folder)
            original=Path(folder)/"CMFI02.pdf";original.write_bytes(b"open report")
            real_open=Path.open
            def locked(path,*args,**kwargs):
                if path==original and args and args[0]=="ab":raise PermissionError("locked")
                return real_open(path,*args,**kwargs)
            with patch.object(Path,"open",locked),patch(
                "accounting.reporting.datetime"
            ) as clock:
                clock.now.return_value=datetime(2026,8,12,17,6,7)
                self.assertEqual(service._available_output("CMFI02").name,
                                 "CMFI02-20260812-170607.pdf")


if __name__ == "__main__":
    unittest.main()
