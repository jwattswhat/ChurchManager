import unittest

from weekly_worship_plan_dialog import duplicate_hymn_line_ids, match_suggestions_to_slots


class WeeklyWorshipPlanMatchingTests(unittest.TestCase):
    def test_distribution_suggestions_fill_repeated_slots_in_order(self):
        slots = [
            (30, "Distribution Hymn", "", ""),
            (31, "Distribution Hymn", "", ""),
            (32, "Distribution Hymn", "", ""),
        ]
        suggestions = [
            (501, "618", "First", "Distribution Hymn"),
            (502, "619", "Second", "Distribution Hymn"),
            (503, "620", "Third", "Distribution Hymn"),
            (504, "621", "Excess", "Distribution Hymn"),
        ]
        self.assertEqual(
            match_suggestions_to_slots(slots, suggestions),
            [(30, "Distribution Hymn", 501),
             (31, "Distribution Hymn", 502),
             (32, "Distribution Hymn", 503)],
        )

    def test_same_hymn_can_fill_different_service_positions(self):
        slots = [(10, "Hymn of Invocation", "", ""), (20, "Closing", "", "")]
        suggestions = [
            (777, "777", "Same hymn", "Hymn of Invocation"),
            (777, "777", "Same hymn", "Closing"),
        ]
        self.assertEqual(
            match_suggestions_to_slots(slots, suggestions),
            [(10, "Hymn of Invocation", 777), (20, "Closing", 777)],
        )

    def test_each_duplicate_suggestion_record_is_used_only_once(self):
        slots = [
            (10, "Distribution Hymn", "", ""),
            (20, "Distribution Hymn", "", ""),
            (30, "Distribution Hymn", "", ""),
        ]
        suggestions = [
            (777, "777", "Same hymn", "Distribution Hymn"),
            (777, "777", "Same hymn", "Distribution Hymn"),
        ]
        self.assertEqual(
            match_suggestions_to_slots(slots, suggestions),
            [(10, "Distribution Hymn", 777), (20, "Distribution Hymn", 777)],
        )

    def test_unmatched_slot_is_left_without_an_assignment(self):
        slots = [(10, "Hymn of Invocation", "", ""), (20, "Closing", "", "")]
        suggestions = [(501, "501", "Opening hymn", "Hymn of Invocation")]
        self.assertEqual(
            match_suggestions_to_slots(slots, suggestions),
            [(10, "Hymn of Invocation", 501)],
        )

    def test_nonexact_suggested_use_is_skipped(self):
        slots = [(10, "Hymn of Invocation", "", ""), (20, "Distribution Hymn", "", "")]
        suggestions = [
            (501, "501", "Opening", "Entrance"),
            (502, "502", "Distribution", "distribution hymn"),
        ]
        self.assertEqual(match_suggestions_to_slots(slots, suggestions), [])

    def test_every_occurrence_of_a_duplicate_hymn_is_flagged(self):
        slots = [
            (10, "Hymn of Invocation", "100", "A Hymn", 501),
            (20, "Hymn of the Day", "200", "Another Hymn", 502),
            (30, "Closing", "100", "A Hymn", 501),
        ]
        self.assertEqual(duplicate_hymn_line_ids(slots), {10, 30})

    def test_unselected_hymn_lines_are_not_duplicates(self):
        slots = [
            (10, "Distribution Hymn", "", "", None),
            (20, "Distribution Hymn", "", "", None),
        ]
        self.assertEqual(duplicate_hymn_line_ids(slots), set())


if __name__ == "__main__":
    unittest.main()
