import unittest

from import_lsb_from_production import is_lsb_hymn, is_lsb_hymnal, mapped_value


class LSBImportTests(unittest.TestCase):
    def test_lsb_hymnal_requires_abbreviation_or_full_title(self):
        self.assertTrue(is_lsb_hymnal({"Hymnal": "LSB", "Title": ""}))
        self.assertTrue(is_lsb_hymnal({"Hymnal": "", "Title": "Lutheran Service Book"}))
        self.assertFalse(is_lsb_hymnal({"Hymnal": "ELW", "Title": "Evangelical Lutheran Worship"}))

    def test_legacy_hymn_fields_map_to_current_columns(self):
        row = {"HymnalCategory": "Advent", "Notes": "Favorite"}
        self.assertEqual(mapped_value(row, "Category"), "Advent")
        self.assertEqual(mapped_value(row, "Note"), "Favorite")

    def test_hymns_use_relation_when_available_and_prefix_as_legacy_fallback(self):
        self.assertTrue(is_lsb_hymn({"HymnalID": 4, "Hymn": "500"}, 4, True))
        self.assertFalse(is_lsb_hymn({"HymnalID": 3, "Hymn": "LSB 500"}, 4, True))
        self.assertTrue(is_lsb_hymn({"Hymn": "LSB 500"}, 4, False))


if __name__ == "__main__":
    unittest.main()
