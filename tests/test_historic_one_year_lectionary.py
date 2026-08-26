"""Tests for the maintained public-domain historic one-year package."""

import unittest

from build_historic_one_year_lectionary import build_draft
from build_lectionary_package import build_package


class HistoricOneYearLectionaryTests(unittest.TestCase):
    def test_catalog_has_complete_core_cycle_and_metadata_only_readings(self):
        draft = build_draft()
        propers = draft["systems"][0]["editions"][0]["propers"]
        self.assertEqual(len(propers), 62)
        self.assertEqual(sum(len(item["appointments"]) for item in propers), 124)
        self.assertEqual(propers[0]["liturgical_date"], "First Sunday in Advent")
        self.assertEqual(propers[-1]["liturgical_date"], "Twenty-Seventh Sunday after Trinity")
        self.assertTrue(all("text" not in key.casefold()
                            for proper in propers for reading in proper["appointments"]
                            for key in reading))

    def test_public_domain_provenance_builds_redistributable_package(self):
        draft = build_draft()
        provenance = {
            "package_code": draft["package_code"], "package_version": "1.0.0",
            "approval_status": "APPROVED", "reviewed_by": "Jonathan C. Watt",
            "reviewed_date": "2026-08-17", "source_owner": "Public domain",
            "redistribution_basis": "United States public-domain publication from 1919",
            "distribution_scope": "REDISTRIBUTABLE", "metadata_only_confirmed": True,
            "notes": "Citation index only.",
        }
        package, summary = build_package(draft, provenance)
        self.assertEqual(summary.proper_count, 62)
        self.assertEqual(package["distribution_scope"], "REDISTRIBUTABLE")


if __name__ == "__main__":
    unittest.main()
