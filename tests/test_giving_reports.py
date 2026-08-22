"""Contracts for permission-separated Giving report screens."""

import inspect
import json
import unittest
from pathlib import Path

from giving.report_dialog import (
    GivingReportsDialog, quarter_bounds, statement_period_bounds, show_giving_reports,
)
from giving.report_service import GivingReportService
from giving.reporting import (
    BATCH_SUMMARY_CONTRACT, BATCH_SUMMARY_MANIFEST, DEFINITIONS,
    GivingBatchSummaryProvider, STATEMENT_CONTRACT, STATEMENT_MANIFEST,
    ContributionStatementProvider, TRIBUTE_CONTRACT, TRIBUTE_MANIFEST,
    TributeAcknowledgmentProvider,
)
import JSForm
from datetime import date


class GivingReportTests(unittest.TestCase):
    def test_summary_query_contains_no_contributor_identity(self):
        source = inspect.getsource(GivingReportService.batch_summary)
        self.assertIn("tblContributionBatch", source)
        self.assertNotIn("tblContributionContributor", source)
        self.assertNotIn("ContributorID", source)

    def test_history_is_limited_to_reviewed_or_posted_giving(self):
        source = inspect.getsource(GivingReportService.contributor_history)
        self.assertIn("g.ContributorID=?", source)
        self.assertIn("b.Status IN ('READY','POSTED')", source)

    def test_tabs_are_permission_separated(self):
        source = inspect.getsource(GivingReportsDialog)
        self.assertIn('has_permission("giving.reports.summary")', source)
        self.assertIn('has_permission("giving.history.view")', source)
        entry = inspect.getsource(show_giving_reports)
        self.assertIn('require("giving.reports.summary"', entry)

    def test_run_actions_provide_visible_refresh_feedback(self):
        source = inspect.getsource(GivingReportsDialog)
        self.assertIn("Refreshed {_run_time()}", source)
        self.assertIn('label="Refresh Batch Summary"', source)
        self.assertIn('label="Refresh Contributor History"', source)
        self.assertIn("GetParent().Layout()", source)
        self.assertIn("No contribution batches match", source)
        self.assertIn("No Ready or Posted contributions match", source)

    def test_main_menu_routes_giving_reports(self):
        menu = json.loads(Path("forms/frmMain.json").read_text(encoding="utf-8"))
        control = menu["frmMainFORM"]["CONTROLS"]["lblGivingReports"]
        self.assertEqual(control["label"], "Giving Reports")
        self.assertEqual(control["security"]["invoke"], "giving.reports.summary")
        self.assertIn('"lblGivingReports": "giving.reports.summary"',
                      Path("permission_catalog.py").read_text(encoding="utf-8"))

    def test_batch_summary_pdf_is_protected_and_donor_free(self):
        definition = JSForm.ReportDefinitionLoader().load(DEFINITIONS / "GIVE-BATCH.json")
        BATCH_SUMMARY_MANIFEST.validate(definition)
        self.assertEqual(BATCH_SUMMARY_CONTRACT.required_permission, "giving.reports.summary")
        source = inspect.getsource(GivingBatchSummaryProvider)
        self.assertNotIn("tblContributionContributor", source)
        self.assertNotIn("ContributorID", source)
        self.assertIn('label="Preview PDF"', inspect.getsource(GivingReportsDialog))

    def test_quarter_bounds_include_the_complete_calendar_quarter(self):
        self.assertEqual(quarter_bounds(2026, 1), (date(2026, 1, 1), date(2026, 3, 31)))
        self.assertEqual(quarter_bounds(2026, 4), (date(2026, 10, 1), date(2026, 12, 31)))

    def test_statement_periods_support_quarter_annual_and_custom(self):
        self.assertEqual(
            statement_period_bounds("Calendar Year", 2027, 1)[:2],
            (date(2027, 1, 1), date(2027, 12, 31)),
        )
        self.assertEqual(
            statement_period_bounds(
                "Custom Date Range", 2027, 1, date(2027, 2, 3), date(2027, 8, 9),
            )[:2],
            (date(2027, 2, 3), date(2027, 8, 9)),
        )
        with self.assertRaisesRegex(ValueError, "cannot be before"):
            statement_period_bounds(
                "Custom Date Range", 2027, 1, date(2027, 8, 9), date(2027, 2, 3),
            )

    def test_all_contributors_tolerates_initial_choice_state(self):
        source = inspect.getsource(GivingReportsDialog._statement_selection)
        self.assertIn("if selected <= 0:", source)
        self.assertIn("No statement-enabled contributors have eligible Posted", source)

    def test_contribution_statement_is_confidential_and_posted_only(self):
        definition = JSForm.ReportDefinitionLoader().load(DEFINITIONS / "GIVE-STMT.json")
        STATEMENT_MANIFEST.validate(definition)
        self.assertEqual(STATEMENT_CONTRACT.required_permission, "giving.statements.generate")
        query = inspect.getsource(GivingReportService.statement_lines)
        self.assertIn("b.Status='POSTED'", query)
        self.assertIn("g.StatementEligibility='ELIGIBLE'", query)
        self.assertIn("p.StatementTreatment='ELIGIBLE'", query)
        self.assertIn('require("giving.statements.generate"', inspect.getsource(ContributionStatementProvider))

    def test_statement_issuance_records_hash_revision_and_safe_audit(self):
        migration = Path("migrations/087_add_contribution_statement_issuance.sql").read_text(encoding="utf-8")
        self.assertIn("tblContributionStatementIssue", migration)
        self.assertIn("DocumentHash char(64)", migration)
        source = inspect.getsource(GivingReportService.record_statement_issuances)
        self.assertIn("RevisionNumber DESC", source)
        self.assertIn("STATEMENT_ISSUED", source)
        reporting = __import__("giving.reporting", fromlist=["GivingVisualReportService"])
        renderer = inspect.getsource(reporting.GivingVisualReportService.run_statements)
        self.assertIn("hashlib.sha256", renderer)
        self.assertIn("issue=False", renderer)

    def test_tribute_report_honors_separate_disclosure_consent(self):
        definition = JSForm.ReportDefinitionLoader().load(DEFINITIONS / "GIVE-TRIBUTE.json")
        TRIBUTE_MANIFEST.validate(definition)
        self.assertEqual(TRIBUTE_CONTRACT.required_permission, "giving.reports.confidential")
        query = inspect.getsource(GivingReportService.tribute_acknowledgments)
        self.assertIn("b.Status='POSTED'", query)
        self.assertIn("CASE WHEN g.DonorDisclosureAuthorized=1", query)
        self.assertIn("CASE WHEN g.AmountDisclosureAuthorized=1", query)
        provider = inspect.getsource(TributeAcknowledgmentProvider)
        self.assertIn('"Amount": "" if row[4] is None', provider)
        dialog = inspect.getsource(GivingReportsDialog)
        self.assertIn('"Memorial / Honor Gifts"', dialog)
        self.assertIn("run_tribute_acknowledgments", dialog)

    def test_report_providers_have_a_public_read_boundary(self):
        self.assertTrue(callable(getattr(GivingReportService, "all", None)))
        source = inspect.getsource(GivingReportService.all)
        self.assertIn("return self._all(sql, values)", source)


if __name__ == "__main__":
    unittest.main()
