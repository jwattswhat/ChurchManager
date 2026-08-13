import unittest

from hymn_validation import duplicate_selection_status


class HymnValidationTests(unittest.TestCase):
    def test_same_hymn_is_a_duplicate_hymn_not_a_separate_tune_warning(self):
        lines = [
            {"hymn_id": 1, "tune": "FRANCONIA"},
            {"hymn_id": 1, "tune": " franconia "},
        ]
        statuses, hymn_duplicates, tune_duplicates = duplicate_selection_status(lines)
        self.assertEqual(statuses, ["DUPLICATE HYMN", "DUPLICATE HYMN"])
        self.assertEqual((hymn_duplicates, tune_duplicates), (1, 0))

    def test_different_hymns_with_same_known_tune_are_flagged(self):
        lines = [
            {"hymn_id": 10, "tune": "FRANCONIA"},
            {"hymn_id": 20, "tune": "Franconia"},
            {"hymn_id": 30, "tune": "OTHER"},
        ]
        statuses, hymn_duplicates, tune_duplicates = duplicate_selection_status(lines)
        self.assertEqual(statuses, ["DUPLICATE TUNE", "DUPLICATE TUNE", ""])
        self.assertEqual((hymn_duplicates, tune_duplicates), (0, 1))

    def test_missing_tunes_are_not_warnings(self):
        lines = [{"hymn_id": 10, "tune": ""}, {"hymn_id": 20, "tune": None}]
        self.assertEqual(duplicate_selection_status(lines), (["", ""], 0, 0))


if __name__ == "__main__":
    unittest.main()
