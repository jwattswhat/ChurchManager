"""Tests for explicit, denomination-neutral lectionary date resolution."""

from datetime import date
import unittest

from lectionary_calendar import (
    LectionaryCalendarError, LectionaryCalendarResolver, advent_start,
    cycle_for_date, gregorian_easter, rule_date, validate_cycle_rule,
)


class LectionaryCalendarTests(unittest.TestCase):
    def test_easter_and_advent_dates(self):
        self.assertEqual(gregorian_easter(2026), date(2026, 4, 5))
        self.assertEqual(advent_start(2025), date(2025, 11, 30))
        self.assertEqual(rule_date("easter:-2", 2026), date(2026, 4, 3))
        self.assertEqual(rule_date("advent-sunday:4", 2025), date(2025, 12, 21))

    def test_fixed_and_strict_sunday_after_rules(self):
        self.assertEqual(rule_date("fixed:12-25", 2026), date(2026, 12, 25))
        self.assertEqual(rule_date("sunday-after:07-04", 2026), date(2026, 7, 5))
        self.assertEqual(rule_date("sunday-after:07-05", 2026), date(2026, 7, 12))

    def test_cycle_changes_at_advent_boundary(self):
        cycles = [("a", "Year A", 1, True), ("b", "Year B", 2, True),
                  ("c", "Year C", 3, True)]
        rule = "advent-cycle:2025:a"
        self.assertEqual(cycle_for_date(date(2025, 11, 29), rule, cycles), "c")
        self.assertEqual(cycle_for_date(date(2025, 11, 30), rule, cycles), "a")
        self.assertEqual(cycle_for_date(date(2026, 12, 1), rule, cycles), "b")

    def test_resolver_returns_all_ambiguous_matches_with_explanations(self):
        edition = {"resolver_version": "1", "cycle_rule": "none"}
        propers = [
            {"id": 1, "proper_key": "one", "liturgical_date": "Christmas Day",
             "season": "Christmas", "cycle_key": None, "calendar_rule": "fixed:12-25"},
            {"id": 2, "proper_key": "local", "liturgical_date": "Local Festival",
             "season": "Christmas", "cycle_key": None, "calendar_rule": "fixed:12-25"},
        ]
        result = LectionaryCalendarResolver().resolve(date(2026, 12, 25), edition, [], propers)
        self.assertEqual([item.proper_id for item in result], [1, 2])
        self.assertTrue(all("Matched fixed:12-25" in item.explanation for item in result))

    def test_names_are_never_interpreted_as_rules(self):
        with self.assertRaises(LectionaryCalendarError):
            rule_date("First Sunday after Pentecost", 2026)

    def test_cycle_anchor_must_be_declared_and_active(self):
        with self.assertRaises(LectionaryCalendarError):
            validate_cycle_rule("advent-cycle:2025:a", [("a", "A", 1, False)])


if __name__ == "__main__":
    unittest.main()
