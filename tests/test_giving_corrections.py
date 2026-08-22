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


if __name__ == "__main__":
    unittest.main()
