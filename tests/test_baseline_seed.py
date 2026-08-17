import tempfile
import unittest
from pathlib import Path

from baseline_seed import SEED_TABLES, build_seed_artifact, mutation_table, write_seed_artifact


class BaselineSeedTests(unittest.TestCase):
    def test_identifies_supported_mutation_targets(self):
        self.assertEqual(mutation_table("INSERT IGNORE INTO tblPermission (Name) VALUES ('x')"), "tblpermission")
        self.assertEqual(mutation_table("UPDATE tblReports r SET Available=0"), "tblreports")
        self.assertEqual(mutation_table("DELETE FROM tblChoices WHERE ID=1"), "tblchoices")
        self.assertEqual(mutation_table("DELETE rp FROM tblRolePermission rp JOIN x"), "tblrolepermission")
        self.assertIsNone(mutation_table("DROP TABLE tblReports"))

    def test_extracts_only_approved_seed_tables(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "001_seed.sql").write_text(
                "INSERT INTO tblRole (Name) VALUES ('Master Administrator');\n"
                "INSERT INTO tblUser (Username) VALUES ('person');\n",
                encoding="utf-8",
            )
            artifact = build_seed_artifact(root, "0.2.0-dev")
        self.assertIn("tblRole", artifact.sql)
        self.assertNotIn("tblUser", artifact.sql)
        self.assertEqual(artifact.manifest["statement_count"], 2)
        self.assertNotIn("LegacyRoleID", artifact.sql)
        self.assertIn("INSERT INTO tblWorshipRole (Name,Description,DisplayOrder,Active)", artifact.sql)
        self.assertEqual(set(artifact.manifest["tables"]), set(SEED_TABLES))

    def test_written_artifact_is_stable(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            migrations = root / "migrations"; migrations.mkdir()
            (migrations / "001_seed.sql").write_text(
                "INSERT INTO tblRole (Name) VALUES ('Master Administrator');\n",
                encoding="utf-8",
            )
            artifact = build_seed_artifact(migrations, "0.2.0-dev")
            sql, manifest = write_seed_artifact(artifact, root / "out")
            self.assertEqual(sql.read_text(encoding="utf-8"), artifact.sql)
            self.assertIn(artifact.manifest["seed_sha256"], manifest.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
