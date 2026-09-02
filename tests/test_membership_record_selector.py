"""Tests for selecting a membership record before opening its edit form."""

import unittest

from membership_record_selector import (
    MembershipRecordChoice, MembershipRecordRepository,
    distinguish_duplicate_labels, filter_choices, position_form_at_record,
    resolve_typed_choice,
)


class Cursor:
    def __init__(self, rows):
        self.rows = rows
        self.sql = None
        self.closed = False

    def execute(self, sql):
        self.sql = sql

    def fetchall(self):
        return self.rows

    def close(self):
        self.closed = True


class Connection:
    def __init__(self, rows):
        self.cursor_value = Cursor(rows)

    def cursor(self):
        return self.cursor_value


class Records:
    def __init__(self, rows):
        self._record = rows
        self._position = 0
        self.selected = None

    def _select(self, position):
        self._position = position
        self.selected = position

    def current(self):
        return self._record[self._position]


class Form:
    def __init__(self, rows):
        self.RECORDS = Records(rows)
        self.NavControlsPresent = True
        self.filled = None
        self.navigation_enabled = False

    def fill_form(self, record):
        self.filled = record

    def enable_navigation_buttons(self):
        self.navigation_enabled = True


class MembershipRecordSelectorTests(unittest.TestCase):
    def test_filter_matches_all_typed_words_in_any_case(self):
        choices = [MembershipRecordChoice(1, "Anderson, Mary Jane"),
                   MembershipRecordChoice(2, "Andrews, John")]
        self.assertEqual(filter_choices(choices, "MARY and"), [choices[0]])

    def test_duplicate_names_are_distinguished(self):
        choices = distinguish_duplicate_labels([
            MembershipRecordChoice(10, "Smith, John"),
            MembershipRecordChoice(11, "Smith, John"),
            MembershipRecordChoice(12, "Smith, Jane"),
        ])
        self.assertEqual(choices[0].label, "Smith, John (record 10)")
        self.assertEqual(choices[1].label, "Smith, John (record 11)")
        self.assertEqual(choices[2].label, "Smith, Jane")

    def test_typed_name_resolves_exact_or_single_partial_match(self):
        choices = [MembershipRecordChoice(1, "Anderson, Mary"),
                   MembershipRecordChoice(2, "Andrews, John")]
        self.assertEqual(resolve_typed_choice(choices, "Anderson, Mary"), choices[0])
        self.assertEqual(resolve_typed_choice(choices, "mary"), choices[0])
        self.assertIsNone(resolve_typed_choice(choices, "and"))

    def test_person_repository_formats_names_and_uses_form_order(self):
        connection = Connection([(7, "John", "Q", "Public")])
        choices = MembershipRecordRepository(connection).choices("person")
        self.assertEqual(choices, [MembershipRecordChoice(7, "Public, John Q")])
        self.assertIn("ORDER BY LastName, FirstName, MiddleName, ID", connection.cursor_value.sql)
        self.assertTrue(connection.cursor_value.closed)

    def test_family_repository_returns_family_names(self):
        connection = Connection([(4, "Public Family")])
        choices = MembershipRecordRepository(connection).choices("family")
        self.assertEqual(choices, [MembershipRecordChoice(4, "Public Family")])
        self.assertIn("FROM tblFamily", connection.cursor_value.sql)

    def test_positioning_keeps_complete_record_set_for_navigation(self):
        form = Form([{"ID": 2}, {"ID": 5}, {"ID": 9}])
        self.assertTrue(position_form_at_record(form, 5))
        self.assertEqual(form.RECORDS.selected, 1)
        self.assertEqual(len(form.RECORDS._record), 3)
        self.assertEqual(form.filled, {"ID": 5})
        self.assertTrue(form.navigation_enabled)

    def test_positioning_reports_a_missing_record(self):
        self.assertFalse(position_form_at_record(Form([{"ID": 2}]), 99))


if __name__ == "__main__":
    unittest.main()
