"""Contract tests for permanent-ID metadata-only hymnal packages."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from hymnal_packages import (
    HymnalPackageError, HymnalPackageImporter, HymnalPackageValidator,
    canonical_hymnal_checksum, load_hymnal_package,
)
from local_hymns import LocalHymnCapacityError, LocalHymnIDAllocator


ROOT = Path(__file__).parents[1]


def package():
    value = {
        "package_code": "sample-hymnal", "package_version": "1.0.0",
        "schema_version": 1, "checksum": "a" * 64, "hymnal_id": 3,
        "hymn_id_start": 15001, "hymn_id_end": 19999,
        "abbreviation": "SMP", "title": "Sample Hymnal", "edition": "First",
        "publisher": "Sample Publisher", "publication_year": 2026,
        "isbn": "978-0-0000-0000-0", "source_name": "Approved metadata",
        "source_reference": "Catalog prepared from an owned source",
        "distribution_notice": "Metadata and outline support only; no lyrics or music.",
        "entries": [{
            "hymn_id": 15001, "entry_slot": 1, "printed_reference": "SMP 1",
            "title": "Sample Hymn", "printed_stanza_count": 4, "is_active": True,
            "tune": "SAMPLE", "text_copyright_status": "UNKNOWN",
            "tune_copyright_status": "PUBLIC_DOMAIN",
            "setting_copyright_status": "UNKNOWN",
        }],
    }
    return value


class RecordingCursor:
    def __init__(self, connection):
        self.connection = connection; self.current = None

    def execute(self, sql, values=()):
        if sql.count("?") != len(values):
            raise AssertionError(f"placeholder mismatch: {sql.count('?')} != {len(values)}")
        self.connection.calls.append((sql, values))
        if self.connection.fail_on and self.connection.fail_on in sql:
            raise RuntimeError("fictional database failure")
        if "FROM tblHymnal WHERE ID=? OR PackageCode=?" in sql:
            self.current = self.connection.registry_rows
        elif "SELECT COUNT(*) FROM tblHymnal" in sql:
            self.current = [(self.connection.overlap_count,)]
        elif "FROM tblHymn WHERE ID=?" in sql:
            self.current = self.connection.hymn_row
        elif "FROM tblLocalHymnIDAllocation" in sql:
            self.current = self.connection.allocation_row
        else:
            self.current = None

    def fetchall(self): return list(self.current or [])
    def fetchone(self):
        if isinstance(self.current, list): return self.current[0] if self.current else None
        return self.current
    def close(self): pass


class RecordingConnection:
    def __init__(self, registry_rows=(), hymn_row=None, overlap_count=0, fail_on=None,
                 allocation_row=None):
        self.registry_rows = list(registry_rows); self.hymn_row = hymn_row
        self.overlap_count = overlap_count; self.fail_on = fail_on
        self.allocation_row = allocation_row
        self.calls = []; self.commits = 0; self.rollbacks = 0

    def cursor(self): return RecordingCursor(self)
    def commit(self): self.commits += 1
    def rollback(self): self.rollbacks += 1


class HymnalPackageTests(unittest.TestCase):
    def test_valid_package_uses_permanent_block(self):
        result = HymnalPackageValidator().validate(package(), "a" * 64)
        self.assertEqual((result.hymnal_id, result.entry_count), (3, 1))

    def test_wrong_block_slot_and_duplicate_identity_are_rejected(self):
        value = package(); value["hymn_id_start"] = 10001
        with self.assertRaisesRegex(HymnalPackageError, "block"):
            HymnalPackageValidator().validate(value)
        value = package(); duplicate = deepcopy(value["entries"][0]); duplicate["title"] = "Other"
        value["entries"].append(duplicate)
        with self.assertRaisesRegex(HymnalPackageError, "unique"):
            HymnalPackageValidator().validate(value)

    def test_local_namespace_and_content_fields_are_rejected(self):
        value = package(); value["package_code"] = "local"; value["hymnal_id"] = 1
        value["hymn_id_start"] = 5001; value["hymn_id_end"] = 9999
        with self.assertRaisesRegex(HymnalPackageError, "local"):
            HymnalPackageValidator().validate(value)
        for field in ("lyrics", "music_notation", "image", "audio_recording"):
            with self.subTest(field=field):
                value = package(); value["entries"][0][field] = "prohibited"
                with self.assertRaisesRegex(HymnalPackageError, "Prohibited"):
                    HymnalPackageValidator().validate(value)

    def test_passive_copyright_status_is_bounded_not_enforced(self):
        value = package(); value["entries"][0]["text_copyright_status"] = "LICENSED"
        self.assertEqual(HymnalPackageValidator().validate(value).entry_count, 1)
        value["entries"][0]["text_copyright_status"] = "THE_INTERNET_SAID_SO"
        with self.assertRaisesRegex(HymnalPackageError, "Unsupported passive"):
            HymnalPackageValidator().validate(value)

    def test_loader_verifies_checksum_and_duplicate_json_fields(self):
        value = package(); value["checksum"] = canonical_hymnal_checksum(value)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "hymnal.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            loaded, checksum = load_hymnal_package(path)
            self.assertEqual(loaded["hymnal_id"], 3)
            self.assertEqual(checksum, value["checksum"])
            path.write_text('{"checksum":"x","checksum":"y"}', encoding="utf-8")
            with self.assertRaisesRegex(HymnalPackageError, "Duplicate"):
                load_hymnal_package(path)

    def test_import_is_transactional_and_uses_explicit_ids(self):
        connection = RecordingConnection()
        result = HymnalPackageImporter(connection).install(package(), "a" * 64)
        self.assertEqual(result.entry_count, 1)
        self.assertEqual((connection.commits, connection.rollbacks), (1, 0))
        sql = "\n".join(call[0] for call in connection.calls)
        self.assertIn("INSERT INTO tblHymn (ID,HymnalID", sql)
        self.assertIn("INSERT INTO tblHymnalPackageImport", sql)

    def test_identity_collision_and_failure_roll_back(self):
        connection = RecordingConnection(hymn_row=(4, 1, "OTHER 1"))
        with self.assertRaisesRegex(HymnalPackageError, "different permanent identity"):
            HymnalPackageImporter(connection).install(package())
        self.assertEqual(connection.rollbacks, 1)
        connection = RecordingConnection(fail_on="INSERT INTO tblHymn")
        with self.assertRaisesRegex(RuntimeError, "fictional"):
            HymnalPackageImporter(connection).install(package())
        self.assertEqual((connection.commits, connection.rollbacks), (0, 1))

    def test_migration_converts_lsb_and_protects_history(self):
        source = (ROOT / "migrations" / "074_add_permanent_hymn_catalog.sql").read_text(encoding="utf-8")
        self.assertIn("10001,14999", source)
        self.assertIn("5001,9999", source)
        self.assertIn("tblHymnIDConversionLog", source)
        self.assertIn("UPDATE tblHymnUsage", source)
        self.assertIn("UPDATE tblProperHymnSuggestion", source)
        self.assertEqual(source.count("ON DELETE RESTRICT"), 3)
        self.assertIn("MODIFY COLUMN ID int NOT NULL", source)
        self.assertNotIn("FOREIGN_KEY_CHECKS=0", source)

    def test_local_allocator_never_uses_packaged_block(self):
        connection = RecordingConnection()
        self.assertEqual(LocalHymnIDAllocator(connection).allocate(), (5001, 1))
        connection = RecordingConnection(allocation_row=(5008,))
        self.assertEqual(LocalHymnIDAllocator(connection).allocate(), (5009, 9))
        self.assertEqual(connection.commits, 1)

    def test_local_allocator_stops_at_end_of_reserved_block(self):
        connection = RecordingConnection(allocation_row=(9999,))
        with self.assertRaises(LocalHymnCapacityError):
            LocalHymnIDAllocator(connection).allocate()
        self.assertEqual(connection.rollbacks, 1)

    def test_hymn_screen_assigns_and_retires_permanent_local_ids(self):
        source = (ROOT / "cm.py").read_text(encoding="utf-8")
        form = json.loads((ROOT / "Forms" / "frmHymn.json").read_text(encoding="utf-8"))
        self.assertIn("LocalHymnIDAllocator(self.DBConnection).allocate()", source)
        self.assertIn("LocalHymnIDAllocator(self.DBConnection).retire", source)
        self.assertIn("PrintedStanzaCount", form["frmHymnFORM"]["CONTROLS"])
        self.assertIn("IsActive", form["frmHymnFORM"]["CONTROLS"])


if __name__ == "__main__":
    unittest.main()
