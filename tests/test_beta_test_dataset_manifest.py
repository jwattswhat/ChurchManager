"""Contract checks for the optional fictional beta dataset package."""

import json
import unittest
from pathlib import Path

from churchmanager_version import __version__
from install_beta_test_dataset import BetaDatasetError, load_manifest, stage_commands


ROOT = Path(__file__).resolve().parents[1]


class BetaTestDatasetManifestTests(unittest.TestCase):
    def test_manifest_is_guarded_and_covers_every_required_subsystem(self):
        manifest = json.loads(
            (ROOT / "TestData" / "BetaDataset" / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["dataset_id"], "churchmanager-beta-test-data")
        self.assertEqual(manifest["target_database"], "ChurchDBTest")
        self.assertEqual(manifest["release_version"], __version__)
        self.assertGreaterEqual(manifest["minimum_schema_migration"], 120)
        self.assertTrue(manifest["safety"]["local_only"])
        self.assertEqual(manifest["safety"]["production_database_forbidden"], "ChurchDB")
        self.assertTrue(manifest["safety"]["backup_before_destructive_reset"])
        self.assertTrue({"people_and_families", "worship_and_attendance", "accounting",
                         "giving", "assets", "projects_and_calendar",
                         "documents_and_journal", "reports_and_designers"}.issubset(manifest["coverage"]))

    def test_every_stage_has_a_maintained_service(self):
        manifest = json.loads(
            (ROOT / "TestData" / "BetaDataset" / "manifest.json").read_text(encoding="utf-8")
        )
        for stage in manifest["stages"]:
            self.assertTrue((ROOT / f"{stage['service']}.py").is_file(), stage)

    def test_coordinator_builds_only_explicit_local_stage_commands(self):
        manifest = load_manifest()
        commands = stage_commands(manifest, python="python", root=ROOT)
        self.assertEqual(len(commands), len(manifest["stages"]))
        self.assertTrue(all("--apply" in command or "--seed" in command for command in commands))
        self.assertIn("--skip-login-users", next(command for command in commands if "seed_nonaccounting" in command[1]))

    def test_release_mismatch_is_rejected(self):
        value = json.loads((ROOT / "TestData" / "BetaDataset" / "manifest.json").read_text())
        value["release_version"] = "0.0.0-wrong"
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "manifest.json"
            path.write_text(json.dumps(value))
            with self.assertRaises(BetaDatasetError):
                load_manifest(path)
