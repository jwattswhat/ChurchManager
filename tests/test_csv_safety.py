"""Regression tests for shared spreadsheet-safe CSV cell encoding."""

from decimal import Decimal
import unittest

from csv_safety import SAFE_PREFIX, csv_safe_row, csv_safe_value


class CsvSafetyTests(unittest.TestCase):
    def test_formula_prefixes_and_spreadsheet_ignored_leaders_are_neutralized(self):
        for value in ("=1+1", "+cmd", "-1+2", "@SUM(A1:A2)",
                      " =1+1", "\t@cmd", "\r\n-2", "\ufeff+3"):
            encoded = csv_safe_value(value)
            self.assertTrue(encoded.startswith(SAFE_PREFIX), value)

    def test_safe_text_numbers_and_existing_text_markers_are_unchanged(self):
        for value in ("ordinary text", "1-2", 42, Decimal("-12.50"), SAFE_PREFIX + "=note"):
            self.assertEqual(csv_safe_value(value), value)
        self.assertEqual(csv_safe_row({"name": "=x", "count": 2})["count"], 2)


if __name__ == "__main__":
    unittest.main()
