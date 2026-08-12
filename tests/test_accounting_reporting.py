from datetime import date
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

import JSForm

from authorization import AuthorizationDenied
from accounting.reporting import (
    AccountingVisualReportService, TRIAL_BALANCE_CONTRACT,
    TRIAL_BALANCE_MANIFEST, TrialBalanceDatasetProvider,
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


class Session:
    display_name = "Jonathan Watt"


class Processes:
    def __init__(self):
        self.opened = []

    def open_file(self, path):
        self.opened.append(Path(path))


class TestAccountingVisualReports(unittest.TestCase):
    def test_trial_balance_contract_and_starter_are_valid_and_protected(self):
        starter = Path(__file__).parents[1] / "accounting" / "report_definitions" / "ACCT-TB.json"
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

    def test_designer_requires_run_and_accounting_design_permissions(self):
        authorization = Authorization(False)
        service = AccountingVisualReportService(
            Connection(), authorization, Session(), processes=Processes(),
        )
        with self.assertRaises(AuthorizationDenied):
            service.design_trial_balance(1, date(2026, 8, 12))
        self.assertEqual(authorization.checked, ["accounting.reports.run"])


if __name__ == "__main__":
    unittest.main()
