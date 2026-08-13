import unittest

from convert_legacy_hymn_suggestions import (
    HYMN_GUESSES,
    IGNORED_NUMBER_TOKENS,
    catalog_number,
    suggestion_tokens,
)


class LegacyHymnSuggestionConversionTests(unittest.TestCase):
    def test_catalog_number_reads_lsb_labels_only(self):
        self.assertEqual(catalog_number("LSB 343"), "343")
        self.assertEqual(catalog_number("LSB1021"), "1021")
        self.assertIsNone(catalog_number("ELW 343"))

    def test_roles_follow_legacy_section_headings(self):
        text = (
            "Entrance: 343 Prepare the Royal Highway\r340/1 Lift Up Your Heads\r"
            "Of the Day: 332 Savior of the Nations\rDistribution: 516 Wake, Awake\r"
            "Closing: 331 The Advent of Our King"
        )
        self.assertEqual(
            suggestion_tokens(text),
            [
                ("343", "Hymn of Invocation"), ("340", "Hymn of Invocation"),
                ("332", "Hymn of the Day"), ("516", "Communion"),
                ("331", "Closing"),
            ],
        )

    def test_unsectioned_hymn_remains_general_suggestion(self):
        self.assertEqual(
            suggestion_tokens("Consider using LSB357 in place of the Gloria"),
            [("357", "")],
        )

    def test_reviewed_missing_hymns_and_date_token_are_explicit(self):
        self.assertEqual(set(HYMN_GUESSES), {"341", "407", "499", "530", "576", "824", "879"})
        self.assertEqual(IGNORED_NUMBER_TOKENS, {"2020"})


if __name__ == "__main__":
    unittest.main()
