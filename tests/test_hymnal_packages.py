"""Contract tests for permanent-ID metadata-only hymnal packages."""

from copy import deepcopy
import csv
import json
from pathlib import Path
import tempfile
import unittest

from hymnal_packages import (
    HymnalPackageError, HymnalPackageImporter, HymnalPackageValidator,
    canonical_hymnal_checksum, load_hymnal_package,
)
from hymn_titles import title_case
from build_lsb_hymnal_package import (
    build_package as build_lsb_package, initialize_review, reviewed_rows,
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
    def test_lsb_review_has_all_printed_hymns_and_fails_closed_while_pending(self):
        with tempfile.TemporaryDirectory() as folder:
            review = Path(folder) / "review.csv"
            self.assertEqual(initialize_review(review_path=review), 636)
            with review.open(encoding="utf-8-sig") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual((rows[0]["HymnNumber"], rows[-1]["HymnNumber"]), ("331", "966"))
            with self.assertRaisesRegex(HymnalPackageError, "636 LSB stanza counts remain unverified"):
                reviewed_rows(review_path=review)

    def test_lsb_builder_uses_permanent_ids_and_requires_review_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            review = Path(folder) / "review.csv"
            initialize_review(review_path=review)
            with review.open(newline="", encoding="utf-8-sig") as stream:
                rows = list(csv.DictReader(stream))
                fields = list(rows[0])
            for row in rows:
                row.update({
                    "PrintedStanzaCount": "4", "VerificationStatus": "VERIFIED",
                    "VerificationSource": "Owned pew edition", "VerifiedBy": "Reviewer",
                    "VerifiedDate": "2026-08-17",
                })
            with review.open("w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader(); writer.writerows(rows)
            value = build_lsb_package(review_path=review)
            self.assertEqual(len(value["entries"]), 636)
            self.assertEqual(
                (value["entries"][0]["hymn_id"], value["entries"][-1]["hymn_id"]),
                (10331, 10966),
            )
            HymnalPackageValidator().validate(value, value["checksum"])

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
        value = package()
        value["title"] = "fictional hymnal"
        result = HymnalPackageImporter(connection).install(value, "a" * 64)
        self.assertEqual(result.entry_count, 1)
        self.assertEqual((connection.commits, connection.rollbacks), (1, 0))
        sql = "\n".join(call[0] for call in connection.calls)
        self.assertIn("INSERT INTO tblHymn (ID,HymnalID", sql)
        self.assertIn("INSERT INTO tblHymnalPackageImport", sql)
        hymnal_insert = next(call for call in connection.calls if "INSERT INTO tblHymnal (ID" in call[0])
        self.assertIn("Fictional Hymnal", hymnal_insert[1])

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
        self.assertIn("Synthetic Test Hymnal", source)
        self.assertIn("DELETE FROM tblService", source)
        self.assertIn("BETWEEN 1 AND 966", source)
        self.assertIn("Publisher='Local Congregation'", source)
        self.assertIn("DROP PROCEDURE IF EXISTS cm_migrate_permanent_lsb_hymn_ids", source)
        self.assertEqual(source.count("ON DELETE RESTRICT"), 3)
        self.assertIn("MODIFY COLUMN ID int NOT NULL", source)
        self.assertNotIn("FOREIGN_KEY_CHECKS=0", source)

    def test_hymn_titles_use_stable_title_case(self):
        self.assertEqual(
            title_case("Savior of the nations, come"),
            "Savior of the Nations, Come",
        )
        self.assertEqual(title_case("O Lord, how shall I meet You"), "O Lord, How Shall I Meet You")
        self.assertEqual(title_case("Hark! A thrilling voice is sounding"), "Hark! A Thrilling Voice Is Sounding")
        self.assertEqual(title_case("LSB service-builder index"), "LSB Service-Builder Index")

    def test_migration_runner_applies_title_case_conversion(self):
        source = (ROOT / "run_churchdb_migrations.py").read_text(encoding="utf-8")
        self.assertIn("normalize_hymn_catalog_titles(cursor)", source)
        self.assertIn("PERMANENT_HYMN_CATALOG", source)

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
