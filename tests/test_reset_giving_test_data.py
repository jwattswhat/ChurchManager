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

    def test_dataset_covers_draft_ready_split_and_anonymous_gifts(self):
        for value in ("TEST - Sunday Offering Entry", "TEST - Ready Deposit",
                      "General Ministry", "Building and Property", "Student Support"):
            self.assertIn(value, self.source)
        self.assertIn('(None, None, "CASH"', self.source)
        self.assertIn('"tblContributionAllocation": 8', self.source)
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


if __name__ == "__main__": unittest.main()
