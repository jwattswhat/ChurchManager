"""Contract checks for immutable posted-Giving corrections."""

from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]


class GivingCorrectionContractTests(unittest.TestCase):
    def test_correction_creates_reversal_and_replacement_without_mutating_gifts(self):
        source = (ROOT / "giving" / "correction_service.py").read_text(encoding="utf-8")
        self.assertIn("'REVERSAL','READY'", source)
        self.assertIn("CorrectionOfContributionID", source)
        self.assertIn("CorrectionBatchID=?", source)
        self.assertNotIn("UPDATE tblContribution SET", source)
        self.assertNotIn("DELETE FROM tblContribution", source)

    def test_replacement_waits_for_original_reversal(self):
        source = (ROOT / "giving" / "accounting_handoff.py").read_text(encoding="utf-8")
        self.assertIn("CorrectsBatchID", source)
        self.assertIn("Post the linked accounting reversal", source)

    def test_posting_voids_the_original_giving_batch_atomically(self):
        source = (ROOT / "accounting" / "posting_service.py").read_text(encoding="utf-8")
        self.assertIn("ReversalAccountingTransactionID", source)
        self.assertIn("BATCH_VOIDED_BY_REVERSAL", source)

    def test_catalog_exposes_explicit_correction_action(self):
        source = (ROOT / "giving" / "batch_dialog.py").read_text(encoding="utf-8")
        self.assertIn("Correct Posted Batch...", source)
        self.assertIn("reason for correction", source.lower())
        self.assertIn("Sent to Accounting", source)

    def test_returned_check_uses_reversal_and_omits_only_selected_check(self):
        source = (ROOT / "giving" / "correction_service.py").read_text(encoding="utf-8")
        self.assertIn("create_returned_check", source)
        self.assertIn("gift[0] == returned[0]", source)
        self.assertIn("INSERT INTO tblContributionReturn", source)
        self.assertIn("CONTRIBUTION_CHECK_RETURNED", source)

    def test_returned_check_is_an_explicit_catalog_action(self):
        source = (ROOT / "giving" / "batch_dialog.py").read_text(encoding="utf-8")
        self.assertIn("Returned Check...", source)
        self.assertIn("Record Returned Contribution Check", source)
        self.assertIn("replacement batch without the selected check", source)

    def test_returned_check_schema_links_giving_and_accounting(self):
        source = (ROOT / "migrations" / "094_add_returned_contribution_checks.sql").read_text(
            encoding="utf-8"
        )
        for field in ("OriginalContributionID", "OriginalBatchID", "ReplacementBatchID",
                      "ReversalAccountingTransactionID", "ReturnDate", "Reason"):
            self.assertIn(field, source)


if __name__ == "__main__":
    unittest.main()
