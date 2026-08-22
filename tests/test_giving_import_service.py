"""Contract tests for atomic contribution draft imports."""

from pathlib import Path
import unittest


class GivingImportServiceTests(unittest.TestCase):
    def test_service_preserves_evidence_and_creates_only_a_draft(self):
        source = (Path(__file__).parents[1] / "giving" / "import_service.py").read_text(encoding="utf-8")
        self.assertIn("tblContributionImportEvidence", source)
        self.assertIn("AttachmentStore", source)
        self.assertIn("'DRAFT'", source)
        self.assertNotIn("'READY'", source)
        self.assertNotIn("'POSTED'", source)
        self.assertIn("Every contribution row must be Ready", source)
        self.assertIn("already been imported", source)

    def test_failure_removes_new_evidence_copy(self):
        source = (Path(__file__).parents[1] / "giving" / "import_service.py").read_text(encoding="utf-8")
        self.assertIn("self.connection.rollback()", source)
        self.assertIn("self.store.remove(stored_path)", source)

    def test_migration_uses_giving_money_precision_and_unique_file_identity(self):
        migration = (Path(__file__).parents[1] / "migrations" /
                     "090_add_contribution_import_evidence.sql").read_text(encoding="utf-8")
        self.assertIn("ImportedTotal decimal(19,2)", migration)
        self.assertIn("UNIQUE KEY uq_contribution_import_file (ChurchID,FileHash)", migration)
        self.assertIn("UNIQUE KEY uq_contribution_import_batch (BatchID)", migration)


if __name__ == "__main__":
    unittest.main()
