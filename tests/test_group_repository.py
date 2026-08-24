"""Contract tests for parameterized Groups persistence."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class GroupRepositoryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "group_repository.py").read_text(encoding="utf-8")

    def test_restricted_groups_are_filtered_in_sql(self):
        self.assertIn("g.PrivacyClass='STANDARD'", self.source)

    def test_membership_overlap_is_inclusive_and_open_ended(self):
        self.assertIn("StartDate<=COALESCE(?,'9999-12-31')", self.source)
        self.assertIn("COALESCE(EndDate,'9999-12-31')>=?", self.source)

    def test_mutations_are_audited_and_transactional(self):
        self.assertIn('"GROUP_CREATED"', self.source)
        self.assertIn('"GROUP_MEMBERSHIP_CREATED"', self.source)
        self.assertIn('"GROUP_MEMBERSHIP_ENDED"', self.source)
        self.assertIn('"GROUP_ROLE_ASSIGNED"', self.source)
        self.assertIn('"GROUP_CATALOG_CREATED"', self.source)
        self.assertIn('"GROUP_CATALOG_STATUS_CHANGED"', self.source)
        self.assertIn("self.connection.rollback()", self.source)


if __name__ == "__main__":
    unittest.main()
