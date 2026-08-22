"""Contracts for guarded contributor merge and directory refresh."""

import inspect
import unittest
from pathlib import Path

from giving.contributor_dialog import ContributorDialog, ContributorRepository


class ContributorAdministrationTests(unittest.TestCase):
    def test_directory_refresh_is_previewed_before_update(self):
        repository = inspect.getsource(ContributorRepository)
        dialog = inspect.getsource(ContributorDialog.on_refresh_directory)
        self.assertIn("refresh_preview", repository)
        self.assertIn("apply_directory_refresh", repository)
        self.assertIn("Preview Directory Refresh", dialog)
        self.assertIn("if wx.MessageBox", dialog)

    def test_merge_rejects_envelope_and_statement_collisions(self):
        source = inspect.getsource(ContributorRepository.merge_preview)
        self.assertIn("tblContributionEnvelopeAssignment", source)
        self.assertIn("tblContributionStatementIssue", source)
        self.assertIn("Resolve that history before merging", source)

    def test_merge_moves_history_and_retains_audit_marker(self):
        source = inspect.getsource(ContributorRepository.merge_contributors)
        for table in ("tblContribution", "tblContributionEnvelopeAssignment",
                      "tblContributionStatementIssue"):
            self.assertIn(table, source)
        self.assertIn("CONTRIBUTOR_MERGED", source)
        self.assertIn("MergedIntoContributorID", source)
        migration = Path("migrations/095_add_contributor_merge_audit.sql").read_text(encoding="utf-8")
        self.assertIn("MergedIntoContributorID bigint", migration)
        self.assertIn("MergeReason varchar(1000)", migration)


if __name__ == "__main__":
    unittest.main()
