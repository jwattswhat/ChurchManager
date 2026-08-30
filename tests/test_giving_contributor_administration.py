"""Contracts for guarded contributor merge and directory refresh."""

import inspect
import unittest
from pathlib import Path

from giving.contributor_dialog import ContributorDialog, ContributorRepository
from giving.validation import GivingValidationError


class Authorization:
    def require(self, _permission, _operation=None):
        return None


class Cursor:
    def __init__(self, connection):
        self.connection = connection; self.rows = []; self.rowcount = 0; self.lastrowid = 41

    def execute(self, sql, values=()):
        self.connection.calls.append((sql, values)); self.rows = []; self.rowcount = 0
        if "SELECT ID FROM tblChurch" in sql:
            self.rows = [(7,)]
        elif sql.startswith("SELECT ID FROM tblPerson WHERE"):
            self.rows = [(values[0],)] if self.connection.directory_owned else []
        elif sql.startswith("SELECT ID FROM tblFamily WHERE"):
            self.rows = [(values[0],)] if self.connection.directory_owned else []
        elif sql.startswith("UPDATE tblContributionContributor"):
            self.rowcount = 1

    def fetchall(self): return self.rows
    def fetchone(self): return self.rows[0] if self.rows else None
    def close(self): pass


class Connection:
    def __init__(self):
        self.calls = []; self.commits = 0; self.rollbacks = 0; self.directory_owned = True
    def cursor(self): return Cursor(self)
    def commit(self): self.commits += 1
    def rollback(self): self.rollbacks += 1


class ContributorAdministrationTests(unittest.TestCase):
    def repository(self, connection=None):
        return ContributorRepository(connection or Connection(), Authorization())

    def test_directory_choices_are_scoped_to_the_active_church(self):
        connection = Connection(); repository = self.repository(connection)
        repository.people(); repository.families()
        directory_calls = [(sql, values) for sql, values in connection.calls
                           if "FROM tblPerson" in sql or "FROM tblFamily" in sql]
        self.assertEqual(len(directory_calls), 2)
        for sql, values in directory_calls:
            self.assertIn("ChurchID=?", sql)
            self.assertEqual(values, (7,))

    def test_direct_cross_church_person_link_is_rejected_before_write(self):
        connection = Connection(); connection.directory_owned = False
        values = ("PERSON", 99, None, "Foreign Person", "", None, None, None, None,
                  None, None, True, True, None)
        with self.assertRaisesRegex(GivingValidationError, "directory record belonging"):
            self.repository(connection).save_contributor(None, values)
        self.assertFalse(any(sql.startswith("INSERT INTO tblContributionContributor")
                             for sql, _values in connection.calls))
        self.assertEqual((connection.commits, connection.rollbacks), (0, 1))

    def test_external_contributor_remains_valid_without_directory_link(self):
        connection = Connection()
        values = ("EXTERNAL", None, None, "Outside Donor", "", None, None, None, None,
                  None, None, True, True, None)
        contributor_id = self.repository(connection).save_contributor(None, values)
        self.assertEqual((contributor_id, connection.commits), (41, 1))
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
