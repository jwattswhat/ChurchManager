import unittest

from weekly_worship_plan_dialog import match_suggestions_to_slots, suggestion_role_key


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

    def test_legacy_slot_aliases_match_full_suggestion_names(self):
        self.assertEqual(suggestion_role_key("Entrance"), "hymn of invocation")
        self.assertEqual(suggestion_role_key("Of the Day"), "hymn of the day")
        self.assertEqual(suggestion_role_key("Communion"), "distribution hymn")


if __name__ == "__main__":
    unittest.main()
