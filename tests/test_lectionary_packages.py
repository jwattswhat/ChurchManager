"""Contract tests for metadata-only lectionary packages."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from lectionary_packages import (
    LectionaryPackageError, LectionaryPackageValidator,
    canonical_lectionary_checksum, load_lectionary_package,
)


def package():
    value = {
        "package_code": "sample-lectionary", "package_version": "1.0.0",
        "schema_version": 1, "checksum": "a" * 64, "title": "Sample Lectionary",
        "source_name": "Approved source", "source_reference": "Metadata reference",
        "package_notice": "Biblical citations and planning metadata only.",
        "distribution_scope": "REDISTRIBUTABLE",
        "systems": [{
            "system_key": "sample-lectionary-system", "name": "Sample System", "note": "",
            "editions": [{
                "edition_key": "sample-lectionary-1992", "name": "1992 Edition",
                "edition_year": 1992, "status": "STABLE", "valid_from": None,
                "valid_through": None, "source_note": "Reviewed metadata",
                "cycles": [
                    {"cycle_key": "a", "display_name": "Year A", "sequence": 1, "is_active": True},
                    {"cycle_key": "b", "display_name": "Year B", "sequence": 2, "is_active": True},
                    {"cycle_key": "c", "display_name": "Year C", "sequence": 3, "is_active": True},
                ],
                "propers": [{
                    "proper_key": "sample-lectionary-a-advent-1", "cycle_key": "a",
                    "liturgical_date": "First Sunday in Advent", "season": "Advent", "sort": 10,
                    "default_color": "Blue", "alternate_color": "Violet",
                    "calendar_rule": "advent-sunday-1", "note": "", "appointments": [{
                        "appointment_key": "sample-lectionary-a-advent-1-first",
                        "role": "FIRST_READING", "display_role": "Old Testament",
                        "display_citation": "Isaiah 2:1-5", "normalized_citation": "Isaiah 2:1-5",
                        "track_code": None, "option_group_code": None, "option_type": "DEFAULT",
                        "paired_appointment_key": None, "sequence": 1, "is_default": True, "note": "",
                    }],
                }],
            }],
        }],
    }
    return value


class LectionaryPackageTests(unittest.TestCase):
    def test_valid_package_supports_data_defined_cycles(self):
        result = LectionaryPackageValidator().validate(package(), "a" * 64)
        self.assertEqual(
            (result.system_count, result.edition_count, result.cycle_count,
             result.proper_count, result.appointment_count),
            (1, 1, 3, 1, 1),
        )
        self.assertEqual(result.distribution_scope, "REDISTRIBUTABLE")
        value = package(); value["systems"][0]["editions"][0]["cycles"] = []
        value["systems"][0]["editions"][0]["propers"][0]["cycle_key"] = None
        self.assertEqual(LectionaryPackageValidator().validate(value).cycle_count, 0)

    def test_unknown_and_content_bearing_fields_are_rejected(self):
        for field in ("scripture_text", "prayer_body", "music_notation", "image"):
            with self.subTest(field=field):
                value = package(); value["systems"][0]["editions"][0]["propers"][0]["appointments"][0][field] = "content"
                with self.assertRaisesRegex(LectionaryPackageError, "Prohibited content"):
                    LectionaryPackageValidator().validate(value)
        value = package(); value["unexpected"] = "anything"
        with self.assertRaisesRegex(LectionaryPackageError, "Unknown field"):
            LectionaryPackageValidator().validate(value)

    def test_namespace_duplicate_cycle_and_relationship_errors_fail_closed(self):
        value = package(); value["systems"][0]["system_key"] = "someone-elses-system"
        with self.assertRaisesRegex(LectionaryPackageError, "namespace"):
            LectionaryPackageValidator().validate(value)
        value = package(); value["systems"][0]["editions"][0]["cycles"][1]["cycle_key"] = "a"
        with self.assertRaisesRegex(LectionaryPackageError, "Duplicate cycle key"):
            LectionaryPackageValidator().validate(value)
        value = package(); value["systems"][0]["editions"][0]["propers"][0]["cycle_key"] = "d"
        with self.assertRaisesRegex(LectionaryPackageError, "unknown cycle"):
            LectionaryPackageValidator().validate(value)

    def test_option_groups_require_one_default_and_pairs_stay_in_proper(self):
        value = package(); item = value["systems"][0]["editions"][0]["propers"][0]["appointments"][0]
        item["option_group_code"] = "first"; item["is_default"] = False; item["option_type"] = "ALTERNATE"
        with self.assertRaisesRegex(LectionaryPackageError, "exactly one default"):
            LectionaryPackageValidator().validate(value)
        value = package(); item = value["systems"][0]["editions"][0]["propers"][0]["appointments"][0]
        item["paired_appointment_key"] = "sample-lectionary-missing"
        with self.assertRaisesRegex(LectionaryPackageError, "same Proper"):
            LectionaryPackageValidator().validate(value)

    def test_roles_citations_dates_and_local_namespace_are_guarded(self):
        value = package(); value["systems"][0]["editions"][0]["propers"][0]["appointments"][0]["role"] = "OLD_TESTAMENT_ONLY"
        with self.assertRaisesRegex(LectionaryPackageError, "reading role"):
            LectionaryPackageValidator().validate(value)
        value = package(); value["systems"][0]["editions"][0]["propers"][0]["appointments"][0]["display_citation"] = "Here is the whole passage"
        with self.assertRaisesRegex(LectionaryPackageError, "citation"):
            LectionaryPackageValidator().validate(value)
        value = package(); value["systems"][0]["editions"][0]["valid_from"] = "2027-01-01"; value["systems"][0]["editions"][0]["valid_through"] = "2026-01-01"
        with self.assertRaisesRegex(LectionaryPackageError, "precedes"):
            LectionaryPackageValidator().validate(value)
        value = package(); value["package_code"] = "local-user"
        with self.assertRaisesRegex(LectionaryPackageError, "local namespace"):
            LectionaryPackageValidator().validate(value)

    def test_numbered_books_and_cross_chapter_ranges_are_valid_citations(self):
        for citation in ("1 Corinthians 4:1-5", "Isaiah 52:13-53:12",
                         "John 15:26-16:4"):
            with self.subTest(citation=citation):
                value = package()
                item = value["systems"][0]["editions"][0]["propers"][0]["appointments"][0]
                item["display_citation"] = citation
                item["normalized_citation"] = citation
                LectionaryPackageValidator().validate(value)

    def test_distribution_scope_is_explicit_and_bounded(self):
        for scope in (None, "PRIVATE", ""):
            with self.subTest(scope=scope):
                value = package(); value["distribution_scope"] = scope
                with self.assertRaisesRegex(LectionaryPackageError, "Distribution scope"):
                    LectionaryPackageValidator().validate(value)
        value = package(); value["distribution_scope"] = "LOCAL_ONLY"
        self.assertEqual(
            LectionaryPackageValidator().validate(value).distribution_scope,
            "LOCAL_ONLY",
        )

    def test_loader_verifies_checksum_and_duplicate_fields(self):
        value = package(); value["checksum"] = canonical_lectionary_checksum(value)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "lectionary.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            loaded, checksum = load_lectionary_package(path)
            self.assertEqual(loaded["package_code"], "sample-lectionary")
            self.assertEqual(checksum, value["checksum"])
            path.write_text('{"checksum":"x","checksum":"y"}', encoding="utf-8")
            with self.assertRaisesRegex(LectionaryPackageError, "Duplicate"):
                load_lectionary_package(path)


if __name__ == "__main__":
    unittest.main()
