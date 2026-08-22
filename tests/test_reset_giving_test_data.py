"""Safety and content contracts for the Giving test-data reset."""

import unittest
from pathlib import Path


class GivingTestDataResetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path("reset_giving_test_data.py").read_text(encoding="utf-8")

    def test_reset_is_hard_guarded_and_backup_first(self):
        self.assertIn('!= "churchdbtest"', self.source)
        self.assertIn("create_backup", self.source)
        self.assertLess(self.source.index("create_backup(testing"), self.source.index("remove_existing(cursor)"))

    def test_dataset_covers_workflow_statement_history_and_anonymous_gifts(self):
        for value in ("TEST - Sunday Offering Entry", "TEST - Ready Deposit",
                      "TEST - First Quarter Posted", "TEST - Fourth Quarter Posted",
                      "General Ministry", "Building and Property", "Student Support"):
            self.assertIn(value, self.source)
        self.assertIn('(None, None, "CASH"', self.source)
        self.assertIn('"tblContributionAllocation": 17', self.source)
        self.assertIn("statement_test_year=", self.source)
        self.assertIn("statement_q{quarter}_contributors=", self.source)
        self.assertIn("Quarterly contribution statement test data verification failed.", self.source)
        self.assertIn("tribute_consent_combinations=", self.source)
        self.assertIn("Memorial and honor disclosure test data verification failed.", self.source)
        for tribute_type in ('"IN_MEMORY_OF"', '"IN_HONOR_OF"'):
            self.assertIn(tribute_type, self.source)
        for consent in (
            '"donor": False, "amount": False', '"donor": True, "amount": False',
            '"donor": False, "amount": True', '"donor": True, "amount": True',
        ):
            self.assertIn(consent, self.source)
        self.assertIn('"INELIGIBLE"', self.source)
        self.assertIn("giving_test_dataset_verified=true", self.source)

    def test_verification_precedes_commit(self):
        self.assertLess(
            self.source.index('raise RuntimeError("Giving test dataset verification failed.")'),
            self.source.index("connection.commit()"),
        )

    def test_batches_use_an_open_fiscal_period(self):
        self.assertIn("p.Status='OPEN'", self.source)
        self.assertIn("y.Status='OPEN'", self.source)
        self.assertIn("create_batch(draft_date", self.source)
        self.assertIn("create_batch(ready_date", self.source)
        self.assertIn("Four open fiscal quarters are required", self.source)

    def test_posted_statement_batches_have_privacy_safe_accounting_links(self):
        self.assertIn("def post_batch", self.source)
        self.assertIn("Contribution deposit - {description}", self.source)
        self.assertIn("Giving batch {batch_id}", self.source)
        self.assertIn("AccountingTransactionID=?,Status='POSTED'", self.source)
        self.assertNotIn("ContributorID,TransactionID", self.source)

    def test_reset_removes_prior_statement_issues_before_contributors(self):
        issue = self.source.index('"tblContributionStatementIssue", "tblContributionAuditEvent"')
        contributor = self.source.index('"tblContributionPurpose", "tblContributionContributor"')
        self.assertLess(issue, contributor)

    def test_reset_breaks_self_referencing_correction_links_before_deletion(self):
        clear_link = self.source.index(
            'UPDATE tblContribution SET CorrectionOfContributionID=NULL'
        )
        deletion_loop = self.source.index("for table in (", clear_link)
        self.assertLess(clear_link, deletion_loop)

    def test_reset_removes_complete_accounting_reversal_chains(self):
        self.assertIn("ReversalAccountingTransactionID", self.source)
        self.assertIn("while pending:", self.source)
        self.assertIn("OR OriginalTransactionID=?", self.source)
        self.assertIn("OR ReversalTransactionID=?", self.source)
        clear_links = self.source.index(
            'UPDATE tblAccountingTransaction SET OriginalTransactionID=NULL,'
        )
        delete_transaction = self.source.index(
            'DELETE FROM tblAccountingTransaction WHERE ID=?'
        )
        self.assertLess(clear_links, delete_transaction)

    def test_reset_removes_import_evidence_before_batches_and_protected_files_after_commit(self):
        evidence = self.source.index('"tblContributionImportEvidence", "tblContributionStatementIssue"')
        batches = self.source.index('"tblContributionEnvelopeAssignment", "tblContributionBatch"')
        self.assertLess(evidence, batches)
        self.assertLess(self.source.index("connection.commit()"),
                        self.source.index("store.remove(stored_path)"))
        self.assertIn("removed_import_evidence_files=", self.source)


if __name__ == "__main__": unittest.main()
