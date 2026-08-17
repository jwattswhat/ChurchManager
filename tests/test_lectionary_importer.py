"""Tests for transactional lectionary package importing."""

from pathlib import Path
import unittest

from lectionary_importer import LectionaryPackageImporter, _key


class FailingCursor:
    __module__ = "mariadb.cursors"

    def __init__(self):
        self.calls = []

    def execute(self, sql, values=()):
        self.calls.append((sql, values))
        if sql.startswith("SELECT ID FROM tblLectionaryPackage"):
            raise RuntimeError("database failure")

    def close(self):
        pass


class FailingConnection:
    def __init__(self):
        self.cursor_value = FailingCursor()
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.cursor_value

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class RecordingCursor:
    __module__ = "mariadb.cursors"

    def __init__(self):
        self.calls = []
        self.lastrowid = 0
        self.rowcount = 1

    def execute(self, sql, values=()):
        if sql.count("?") != len(values):
            raise AssertionError(f"placeholder mismatch: {sql}")
        self.calls.append((sql, values))
        if sql.startswith("INSERT"):
            self.lastrowid += 1

    def fetchone(self):
        return None

    def close(self):
        pass


class RecordingConnection(FailingConnection):
    def __init__(self):
        super().__init__()
        self.cursor_value = RecordingCursor()


def valid_package():
    from lectionary_packages import canonical_lectionary_checksum

    package = {
        "package_code": "sample", "package_version": "1.0", "schema_version": 1,
        "checksum": "0" * 64, "title": "Sample", "source_name": "Source",
        "source_reference": "Citation index", "package_notice": "Metadata only",
        "systems": [{
            "system_key": "sample-system", "name": "Sample", "note": "",
            "editions": [{
                "edition_key": "sample-edition", "name": "Sample Edition",
                "edition_year": 2026, "status": "STABLE", "valid_from": None,
                "valid_through": None, "source_note": "", "cycles": [],
                "propers": [{
                    "proper_key": "sample-proper", "cycle_key": None,
                    "liturgical_date": "Sample Sunday", "season": "Sample", "sort": 1,
                    "default_color": "Green", "alternate_color": None,
                    "calendar_rule": None, "note": "", "appointments": [{
                        "appointment_key": "sample-reading", "role": "GOSPEL",
                        "display_role": "Gospel", "display_citation": "John 1:1-5",
                        "normalized_citation": "John 1:1-5", "track_code": None,
                        "option_group_code": None, "option_type": "DEFAULT",
                        "paired_appointment_key": None, "sequence": 1,
                        "is_default": True, "note": "",
                    }],
                }],
            }],
        }],
    }
    package["checksum"] = canonical_lectionary_checksum(package)
    return package


class LectionaryImporterTests(unittest.TestCase):
    def test_keys_are_case_and_whitespace_stable(self):
        self.assertEqual(_key(" Sample-Key "), "sample-key")

    def test_database_failure_rolls_back_complete_transaction(self):
        connection = FailingConnection()
        package = valid_package()
        with self.assertRaisesRegex(RuntimeError, "database failure"):
            LectionaryPackageImporter(connection).install(package, package["checksum"])
        self.assertEqual(connection.commits, 0)
        self.assertEqual(connection.rollbacks, 1)
        self.assertEqual(connection.cursor_value.calls[0][0], "START TRANSACTION")

    def test_importer_contains_no_content_download_or_text_fields(self):
        source = Path("lectionary_importer.py").read_text(encoding="utf-8").casefold()
        for forbidden in ("requests.", "urllib", "scripturetext", "fulltext", "lyrics"):
            self.assertNotIn(forbidden, source)

    def test_complete_new_install_commits_and_records_import_last(self):
        connection = RecordingConnection()
        package = valid_package()
        result = LectionaryPackageImporter(connection).install(
            package, package["checksum"],
        )
        self.assertEqual(result.action, "INSTALL")
        self.assertEqual(connection.commits, 1)
        self.assertEqual(connection.rollbacks, 0)
        writes = [sql for sql, _values in connection.cursor_value.calls]
        self.assertTrue(writes[-1].startswith("INSERT INTO tblLectionaryPackageImport"))
        self.assertIn("INSERT INTO tblReading", "\n".join(writes))


if __name__ == "__main__":
    unittest.main()
