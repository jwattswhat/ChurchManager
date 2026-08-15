import unittest
from pathlib import Path

from hymn_stanzas import (
    StanzaSelectionError, format_hymn_reference, format_stanza_notation,
    normalize_stanzas,
)
from weekly_worship_plan_dialog import duplicate_hymn_line_ids, match_suggestions_to_slots
from unified_worship_service_dialog import normalize_line_sequences


class WeeklyWorshipPlanMatchingTests(unittest.TestCase):
    def test_displayed_order_is_resequenced_with_simple_increments(self):
        lines = [{"sequence": 30, "label": "Third"}, {"sequence": 10, "label": "First"}]
        self.assertEqual(
            normalize_line_sequences(lines),
            [{"sequence": 1, "label": "Third"}, {"sequence": 2, "label": "First"}],
        )

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


class HymnStanzaTests(unittest.TestCase):
    def test_blank_means_whole_hymn(self):
        self.assertIsNone(normalize_stanzas("  "))
        self.assertEqual(format_hymn_reference("LSB 656", None), "LSB 656")

    def test_input_is_normalized_and_printed_readably(self):
        self.assertEqual(normalize_stanzas("sts. 1, 3, 11–12"), "1,3,11-12")
        self.assertEqual(format_stanza_notation("1,3,11-12"), "sts. 1, 3, 11–12")
        self.assertEqual(
            format_hymn_reference("LSB 581", "1,3,11-12"),
            "LSB 581, sts. 1, 3, 11–12",
        )

    def test_single_stanza_uses_singular_label(self):
        self.assertEqual(format_stanza_notation("3"), "st. 3")

    def test_invalid_and_duplicate_values_are_rejected(self):
        for value in ("0", "4-2", "1,,3", "three", "3-", "1-3,3"):
            with self.subTest(value=value), self.assertRaises(StanzaSelectionError):
                normalize_stanzas(value)

    def test_guarded_migration_adds_stanzas_and_report_fields(self):
        migration = (Path(__file__).resolve().parents[1] / "migrations" /
                     "067_add_hymn_stanza_selections.sql").read_text(encoding="utf-8")
        self.assertIn("ADD COLUMN IF NOT EXISTS Stanzas varchar(100) NULL", migration)
        self.assertIn("CREATE SQL SECURITY DEFINER VIEW rpt_worship_planner_hymn", migration)
        self.assertIn("u.Stanzas", migration)

    def test_compatible_combined_report_field_includes_formatted_reference(self):
        migration = (Path(__file__).resolve().parents[1] / "migrations" /
                     "068_include_stanzas_in_compatible_hymn_report_field.sql").read_text(
                         encoding="utf-8"
                     )
        self.assertIn("COALESCE(l.ReferenceText,h.Hymn)", migration)
        self.assertIn("AS Hymn", migration)

    def test_unified_planner_exposes_stanza_column_and_editor(self):
        source = (Path(__file__).resolve().parents[1] /
                  "unified_worship_service_dialog.py").read_text(encoding="utf-8")
        self.assertIn('(\"Reference\", 145), (\"Stanzas\", 90)', source)
        self.assertIn('(\"Edit Stanzas...\", self.on_edit_stanzas)', source)
        self.assertIn("def on_edit_stanzas", source)


if __name__ == "__main__":
    unittest.main()
