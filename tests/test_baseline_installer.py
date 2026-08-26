import json
import tempfile
import unittest
from pathlib import Path

from baseline_installer import (
    BaselineInstallationError,
    BaselineInstaller,
    load_baseline,
)
from baseline_schema import build_baseline_artifact, write_baseline_artifact


class Cursor:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.response = None
        self.executed = []
        self.closed = False

    def execute(self, sql, values=None):
        self.executed.append((sql, values))
        if sql.startswith("SELECT COUNT"):
            self.response = next(self.responses)

    def fetchone(self):
        return self.response

    def close(self):
        self.closed = True


class Connection:
    def __init__(self, responses):
        self.value = Cursor(responses)
        self.committed = False

    def cursor(self):
        return self.value

    def commit(self):
        self.committed = True


class BaselineInstallerTests(unittest.TestCase):
    def artifact(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        migrations = root / "migrations"
        migrations.mkdir()
        (migrations / "001_sample.sql").write_text("CREATE TABLE source (ID int);", encoding="utf-8")
        artifact = build_baseline_artifact(
            "CREATE TABLE schema_migrations (version varchar(100), checksum char(64));\n"
            "CREATE TABLE sample (ID int);",
            "ChurchDBTest", migrations, "0.1.0",
        )
        schema, manifest = write_baseline_artifact(artifact, root)
        return temporary, migrations, schema, manifest

    def test_loads_matching_artifact(self):
        temporary, migrations, schema, manifest = self.artifact()
        self.addCleanup(temporary.cleanup)
        loaded, value = load_baseline(schema, manifest, migrations)
        self.assertIn("CREATE TABLE sample", loaded)
        self.assertEqual(len(value["represented_migrations"]), 1)

    def test_rejects_changed_schema(self):
        temporary, migrations, schema, manifest = self.artifact()
        self.addCleanup(temporary.cleanup)
        schema.write_text(schema.read_text(encoding="utf-8") + "\nCREATE TABLE changed (ID int);", encoding="utf-8")
        with self.assertRaisesRegex(BaselineInstallationError, "checksum"):
            load_baseline(schema, manifest, migrations)

    def test_rejects_changed_migration_ledger(self):
        temporary, migrations, schema, manifest = self.artifact()
        self.addCleanup(temporary.cleanup)
        value = json.loads(manifest.read_text(encoding="utf-8"))
        value["represented_migrations"] = []
        manifest.write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(BaselineInstallationError, "migration ledger"):
            load_baseline(schema, manifest, migrations)

    def test_installs_only_into_empty_database(self):
        connection = Connection(((1,),))
        with self.assertRaisesRegex(BaselineInstallationError, "empty database"):
            BaselineInstaller(connection).install("CREATE TABLE x (ID int);", {
                "represented_migrations": [], "schema_sha256": "a" * 64,
            }, "INSERT INTO tblRole VALUES (1);")

    def test_installs_and_verifies(self):
        connection = Connection(((0,), (1,), (2,), (1,), (5,)))
        manifest = {
            "represented_migrations": [{"version": "001.sql", "checksum": "a" * 64}],
            "schema_sha256": "b" * 64,
        }
        result = BaselineInstaller(connection).install(
            "CREATE TABLE schema_migrations (version varchar(100), checksum char(64));",
            manifest, "INSERT INTO tblRole VALUES (1);",
        )
        self.assertEqual(result["represented_migrations"], 1)
        self.assertEqual(result["database_objects"], 2)
        self.assertEqual(result["active_permissions"], 5)
        self.assertTrue(connection.committed)
        self.assertTrue(connection.value.closed)


if __name__ == "__main__":
    unittest.main()
