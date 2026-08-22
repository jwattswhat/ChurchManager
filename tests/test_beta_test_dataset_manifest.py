"""Contract checks for the optional fictional beta dataset package."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BetaTestDatasetManifestTests(unittest.TestCase):
    def test_manifest_is_guarded_and_covers_every_required_subsystem(self):
        manifest = json.loads(
            (ROOT / "TestData" / "BetaDataset" / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["dataset_id"], "churchmanager-beta-test-data")
        self.assertEqual(manifest["target_database"], "ChurchDBTest")
        self.assertTrue(manifest["safety"]["local_only"])
        self.assertEqual(manifest["safety"]["production_database_forbidden"], "ChurchDB")
        self.assertTrue(manifest["safety"]["backup_before_destructive_reset"])
        self.assertEqual(
            set(manifest["coverage"]),
            {"people_and_families", "worship_and_attendance", "accounting", "giving", "reports_and_designers"},
        )

    def test_every_stage_has_a_maintained_service(self):
        manifest = json.loads(
            (ROOT / "TestData" / "BetaDataset" / "manifest.json").read_text(encoding="utf-8")
        )
        for stage in manifest["stages"]:
            self.assertTrue((ROOT / f"{stage}.py").is_file(), stage)
