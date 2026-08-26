import hashlib
import tempfile
import unittest
from pathlib import Path

from migration_service import MigrationService, MigrationServiceError


class Cursor:
    def __init__(self, history=None):
        self.history = history
        self.executed = []
        self.response = None
        self.closed = False

    def execute(self, sql, values=None):
        self.executed.append((sql, values))
        if "information_schema.TABLES" in sql:
            self.response = (1 if self.history is not None else 0,)
        elif sql == "SELECT version, checksum FROM schema_migrations":
            self.response = list((self.history or {}).items())

    def fetchone(self):
        return self.response

    def fetchall(self):
        return self.response

    def close(self):
        self.closed = True


class Connection:
    def __init__(self, history=None):
        self.cursor_value = Cursor(history)

    def cursor(self):
        return self.cursor_value


class MigrationServiceTests(unittest.TestCase):
    def migration_directory(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "001_first.sql").write_text(
            "CREATE TABLE example (ID integer);", encoding="utf-8",
        )
        return temporary, root

    def test_preview_reports_pending_without_executing_it(self):
        temporary, root = self.migration_directory()
        self.addCleanup(temporary.cleanup)
        connection = Connection()
        result = MigrationService(connection, root).run()
        self.assertEqual(result.pending, ("001_first.sql",))
        self.assertEqual(result.newly_applied, ())
        self.assertFalse(any("CREATE TABLE example" in sql for sql, _ in connection.cursor_value.executed))
        self.assertTrue(connection.cursor_value.closed)

    def test_apply_executes_and_records_pending_migration(self):
        temporary, root = self.migration_directory()
        self.addCleanup(temporary.cleanup)
        connection = Connection()
        before = []
        after = []
        result = MigrationService(
            connection, root,
            before_apply=lambda _cursor, record: before.append(record.version),
            after_apply=lambda _cursor, record: after.append(record.version),
        ).run(apply=True)
        sql = [statement for statement, _values in connection.cursor_value.executed]
        self.assertIn("CREATE TABLE example (ID integer)", sql)
        self.assertEqual(result.newly_applied, ("001_first.sql",))
        self.assertEqual(before, ["001_first.sql"])
        self.assertEqual(after, ["001_first.sql"])

    def test_changed_applied_migration_is_rejected(self):
        temporary, root = self.migration_directory()
        self.addCleanup(temporary.cleanup)
        wrong = hashlib.sha256(b"different").hexdigest()
        with self.assertRaisesRegex(MigrationServiceError, "checksum changed"):
            MigrationService(Connection({"001_first.sql": wrong}), root).run()

    def test_database_failure_names_migration_and_statement(self):
        class DatabaseFailure(Exception):
            pass

        class FailingCursor(Cursor):
            def execute(self, sql, values=None):
                if sql.startswith("CREATE TABLE example"):
                    raise DatabaseFailure("failed")
                super().execute(sql, values)

        temporary, root = self.migration_directory()
        self.addCleanup(temporary.cleanup)
        connection = Connection()
        connection.cursor_value = FailingCursor()
        with self.assertRaisesRegex(MigrationServiceError, "001_first.sql failed at"):
            MigrationService(
                connection, root, database_errors=(DatabaseFailure,),
            ).run(apply=True)


if __name__ == "__main__":
    unittest.main()
