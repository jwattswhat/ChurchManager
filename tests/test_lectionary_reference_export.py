"""Tests for the disposable-current-catalog reconciliation export."""

from datetime import date
import unittest

from export_current_lectionary_reference import ALLOWED, build_inventory


class LectionaryReferenceExportTests(unittest.TestCase):
    def test_export_is_metadata_only_sorted_and_does_not_preserve_unknown_fields(self):
        value = build_inventory(
            [{"ID": 2, "Name": "Zed"}, {"ID": 1, "Name": "Alpha", "Unexpected": "drop"}],
            [{"ID": 4, "LectionarySystemID": 2, "Cycle": "B", "Sort": 2,
              "LiturgicalDate": "Second Sunday", "FullText": "drop"}],
            [{"ID": 8, "PropersID": 4, "Reading": "Gospel", "Reference": "John 3:16",
              "Date": date(2026, 1, 1)}],
            [{"ID": 9, "PropersID": 4, "HymnID": 10331, "SuggestedAs": "Closing",
              "Lyrics": "drop"}],
        )
        self.assertEqual([row["Name"] for row in value["systems"]], ["Alpha", "Zed"])
        self.assertNotIn("Unexpected", value["systems"][0])
        self.assertNotIn("FullText", value["propers"][0])
        self.assertNotIn("Date", value["readings"][0])
        self.assertNotIn("Lyrics", value["hymn_suggestions"][0])
        self.assertEqual(value["purpose"], "Reference-only comparison source; not an installable package.")

    def test_allowlist_contains_no_content_bearing_fields(self):
        names = {field.casefold() for fields in ALLOWED.values() for field in fields}
        for forbidden in ("scripturetext", "fulltext", "lyrics", "music", "image", "html"):
            self.assertNotIn(forbidden, names)

    def test_binary_values_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Binary content"):
            build_inventory([{"ID": 1, "Name": b"bad"}], [], [], [])


if __name__ == "__main__":
    unittest.main()
