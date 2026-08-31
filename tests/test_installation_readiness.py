import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from installation_readiness import (
    ReadinessCheck,
    ReadinessReport,
    MARIADB_DOWNLOAD_URL,
    blocking_message,
    catalog_inventory,
    inspect_readiness,
)


class InstallationReadinessTests(unittest.TestCase):
    def test_included_lectionary_is_available(self):
        matches = [item for item in catalog_inventory() if item.code == "cm-historic-one-year"]
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0].valid)
        self.assertTrue(matches[0].installable)

    def test_included_lsb_hymnal_satisfies_order_of_service_dependency(self):
        hymnals = [item for item in catalog_inventory() if item.code == "lsb"]
        self.assertEqual(len(hymnals), 1)
        self.assertTrue(hymnals[0].valid)
        self.assertTrue(hymnals[0].installable)
        matches = [item for item in catalog_inventory() if item.code == "lsb-service-outlines"]
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0].valid)
        self.assertTrue(matches[0].installable)
        self.assertEqual(matches[0].dependency_code, "lsb")

    def test_bad_package_is_reported_without_raising(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "packages" / "lectionary"
            target.mkdir(parents=True)
            (target / "bad.json").write_text(json.dumps({"package_code": "bad"}), encoding="utf-8")
            packages = catalog_inventory(root)
        self.assertEqual(len(packages), 1)
        self.assertFalse(packages[0].valid)

    @patch("installation_readiness.system_checks", return_value=())
    @patch("installation_readiness.catalog_inventory", return_value=())
    def test_inspection_returns_structured_result(self, _inventory, _checks):
        report = inspect_readiness()
        self.assertTrue(report.ready)
        self.assertEqual(report.checks, ())
        self.assertEqual(report.packages, ())

    def test_missing_mariadb_tools_names_required_product_and_tools(self):
        report = ReadinessReport((
            ReadinessCheck("mariadb_client", False, "client missing"),
            ReadinessCheck("database_backup", False, "backup missing"),
        ), ())
        message = blocking_message(report)
        self.assertIn("MariaDB Server is required", message)
        self.assertIn("mariadb.exe", message)
        self.assertIn("mariadb-dump.exe", message)
        self.assertIn(MARIADB_DOWNLOAD_URL, message)
        self.assertNotIn("client missing", message)

    def test_non_database_failures_retain_corrective_details(self):
        report = ReadinessReport((
            ReadinessCheck("disk_space", False, "Only 1 GB is free."),
        ), ())
        message = blocking_message(report)
        self.assertIn("requirements are corrected", message)
        self.assertIn("Only 1 GB is free.", message)


if __name__ == "__main__":
    unittest.main()
