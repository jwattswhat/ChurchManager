"""Regression tests for the normalized Groups database foundation."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class GroupFoundationTests(unittest.TestCase):
    """Protect the approved first-increment schema and security boundary."""

    @classmethod
    def setUpClass(cls):
        cls.sql = (ROOT / "Migrations" / "106_add_normalized_groups_foundation.sql").read_text(
            encoding="utf-8"
        )

    def test_normalized_tables_are_created(self):
        for table in (
            "tblGroupType", "tblGroupRole", "tblGroup",
            "tblGroupMembership", "tblGroupMembershipRole",
        ):
            self.assertIn(f"CREATE TABLE {table}", self.sql)

    def test_history_uses_restrictive_foreign_keys(self):
        membership = self.sql.split("CREATE TABLE tblGroupMembership (", 1)[1].split(
            "CREATE TABLE tblGroupMembershipRole (", 1
        )[0]
        self.assertNotIn("ON DELETE CASCADE", membership)

    def test_permissions_include_restricted_group_boundary(self):
        self.assertIn("'groups.view_restricted'", self.sql)
        self.assertIn("'groups.edit_restricted'", self.sql)

    def test_starter_catalogs_are_present(self):
        for label in ("Governance Body", "Committee", "Bible Study", "Service Team"):
            self.assertIn(label, self.sql)
        for label in ("Member", "Chair", "Leader", "Secretary", "Teacher"):
            self.assertIn(label, self.sql)


if __name__ == "__main__":
    unittest.main()
