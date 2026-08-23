"""Contract tests for minimum-necessary pastoral-care reports."""

import unittest
from pathlib import Path

from visual_reports.report_inventory import REPORTS_BY_CODE


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "104_add_pastoral_care_reports.sql"


class PastoralCareReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MIGRATION.read_text(encoding="utf-8")

    def test_reports_use_the_dedicated_sensitive_permission(self):
        for code in ("CMPC01", "CMPC02"):
            self.assertEqual(REPORTS_BY_CODE[code].permission, "pastoral.care.report")
            self.assertIn(f"'{code}'", self.source)

    def test_work_list_exposes_only_operational_fields(self):
        view = self.source.split("VIEW rpt_pastoral_care_work_list", 1)[1]
        view = view.split("CREATE OR REPLACE", 1)[0]
        self.assertIn("tblPastoralCareNeed", view)
        self.assertNotIn("tblPastoralRestrictedNote", view)
        for forbidden in ("Ciphertext", "Nonce", "AuthenticationTag", "SafeSummary", "SafeOutcome"):
            self.assertNotIn(forbidden, view)

    def test_activity_summary_is_aggregate_and_non_identifying(self):
        view = self.source.split("VIEW rpt_pastoral_care_activity_summary", 1)[1]
        view = view.split("INSERT INTO", 1)[0]
        self.assertIn("COUNT(*) AS ActionCount", view)
        for forbidden in ("PersonID", "FamilyID", "DisplaySubject", "SafeOutcome", "tblPastoralRestrictedNote"):
            self.assertNotIn(forbidden, view)


if __name__ == "__main__":
    unittest.main()
