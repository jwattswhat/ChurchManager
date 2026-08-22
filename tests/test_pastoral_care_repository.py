"""Structural tests for safe MariaDB pastoral-care persistence."""

import unittest
from pathlib import Path

from pastoral_care_repository import _choice_values


ROOT = Path(__file__).resolve().parents[1]


class PastoralCareRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "pastoral_care_repository.py").read_text()

    def test_operational_reads_never_join_restricted_notes(self):
        work_list = self.source.split("def work_list", 1)[1].split("def need", 1)[0]
        need = self.source.split("def need", 1)[1].split("def create_need", 1)[0]
        self.assertNotIn("tblPastoralRestrictedNote", work_list)
        self.assertNotIn("tblPastoralRestrictedNote", need)
        self.assertNotIn("Ciphertext", work_list + need)

    def test_all_values_are_parameterized(self):
        self.assertIn('sql.replace("?", self.marker)', self.source)
        self.assertNotIn(".format(values", self.source)

    def test_each_write_commits_with_safe_audit_and_rolls_back_on_failure(self):
        for method, audit in (
            ("create_need", "PASTORAL_CARE_CREATED"),
            ("assign", "PASTORAL_CARE_ASSIGNED"),
            ("record_action", "PASTORAL_ACTION_RECORDED"),
            ("change_status", "PASTORAL_STATUS_CHANGED"),
        ):
            section = self.source.split("def " + method, 1)[1]
            self.assertIn(audit, section)
            self.assertIn("self.connection.commit()", section)
            self.assertIn("self.connection.rollback()", section)

    def test_optimistic_updates_reject_stale_versions(self):
        self.assertGreaterEqual(self.source.count("AND Version=?"), 3)
        self.assertIn("PastoralCareConflictError", self.source)

    def test_assignment_rejects_inactive_users(self):
        assign = self.source.split("def assign", 1)[1].split("def record_action", 1)[0]
        self.assertIn("SELECT Active FROM tblUser", assign)
        self.assertIn("selected caregiver is unavailable", assign)

    def test_maintained_category_formats_are_parsed(self):
        self.assertEqual(_choice_values([(1, '["Hospital", "Homebound"]')]),
                         ["Hospital", "Homebound"])
        self.assertEqual(_choice_values([(1, "[Hospital\nHomebound]")]),
                         ["Hospital", "Homebound"])


if __name__ == "__main__":
    unittest.main()
