"""Tests for deterministic annual envelope-box assignment planning."""

from __future__ import annotations

import unittest

from giving.annual_envelopes import (
    ASSIGN_NEW_SEQUENCE,
    KEEP_CURRENT_NUMBERS,
    assign_annual_numbers,
)
from giving.validation import GivingValidationError


class AnnualEnvelopeAssignmentTests(unittest.TestCase):
    def setUp(self):
        self.contributors = [(1, "Alpha Family"), (2, "Beta Family"), (3, "Gamma Family")]

    def test_new_sequence_ignores_prior_numbers(self):
        rows = assign_annual_numbers(
            self.contributors, {1: "8", 2: "2"}, ASSIGN_NEW_SEQUENCE, 10
        )
        self.assertEqual([row.proposed_number for row in rows], ["10", "11", "12"])
        self.assertTrue(all(row.result == "Assigned" for row in rows))

    def test_keep_current_fills_lowest_numeric_gaps(self):
        rows = assign_annual_numbers(
            self.contributors, {1: "1", 3: "3"}, KEEP_CURRENT_NUMBERS, 1
        )
        self.assertEqual([row.proposed_number for row in rows], ["1", "2", "3"])
        self.assertEqual([row.result for row in rows], ["Retained", "Assigned", "Retained"])

    def test_leading_zeroes_do_not_reserve_distinct_numbers(self):
        with self.assertRaisesRegex(GivingValidationError, "duplicate"):
            assign_annual_numbers(
                self.contributors[:2], {1: "01", 2: "1"}, KEEP_CURRENT_NUMBERS, 1
            )

    def test_invalid_strategy_and_start_are_rejected(self):
        with self.assertRaises(GivingValidationError):
            assign_annual_numbers(self.contributors, {}, "UNKNOWN", 1)
        with self.assertRaises(GivingValidationError):
            assign_annual_numbers(self.contributors, {}, ASSIGN_NEW_SEQUENCE, 0)


if __name__ == "__main__":
    unittest.main()
