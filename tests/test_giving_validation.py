"""Tests for confidential giving-domain validation."""

from __future__ import annotations

import unittest
from datetime import date
from decimal import Decimal

from giving.validation import (
    GivingValidationError,
    envelope_periods_overlap,
    validate_allocations,
    validate_contributor_links,
    validate_envelope_assignment,
    validate_gift_acknowledgment,
    validate_tribute,
)


class GivingValidationTests(unittest.TestCase):
    def test_contributor_types_enforce_exactly_one_permitted_link(self):
        validate_contributor_links("PERSON", 1, None)
        validate_contributor_links("FAMILY", None, 2)
        validate_contributor_links("EXTERNAL", None, None)
        invalid = [("PERSON", None, None), ("FAMILY", 1, 2), ("EXTERNAL", 1, None)]
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(GivingValidationError):
                validate_contributor_links(*values)

    def test_numeric_envelope_number_discards_leading_zeroes_and_validates_dates(self):
        self.assertEqual(
            validate_envelope_assignment(" 0042 ", date(2027, 1, 1)), "42"
        )
        self.assertEqual(
            {validate_envelope_assignment(value, date(2027, 1, 1))
             for value in ("1", "01", "001")},
            {"1"},
        )
        with self.assertRaises(GivingValidationError):
            validate_envelope_assignment("42", date(2027, 2, 1), date(2027, 1, 31))

    def test_envelope_overlap_uses_inclusive_open_ended_periods(self):
        self.assertTrue(
            envelope_periods_overlap(
                date(2027, 1, 1), date(2027, 12, 31),
                date(2027, 12, 31), None,
            )
        )
        self.assertFalse(
            envelope_periods_overlap(
                date(2027, 1, 1), date(2027, 12, 31),
                date(2028, 1, 1), None,
            )
        )

    def test_allocations_must_be_positive_and_balance_to_the_cent(self):
        self.assertEqual(validate_allocations("25.00", ["20", "5"]), Decimal("25.00"))
        for allocations in ([], ["24.99"], ["25", "-1", "1"]):
            with self.subTest(allocations=allocations), self.assertRaises(GivingValidationError):
                validate_allocations("25.00", allocations)

    def test_acknowledgment_facts_are_mutually_consistent(self):
        self.assertEqual(
            validate_gift_acknowledgment(
                goods_or_services_provided=True,
                goods_or_services_value="12.50",
                intangible_religious_benefit_only=False,
            ),
            Decimal("12.50"),
        )
        with self.assertRaises(GivingValidationError):
            validate_gift_acknowledgment(
                goods_or_services_provided=True,
                goods_or_services_value="12.50",
                intangible_religious_benefit_only=True,
            )

    def test_tribute_requires_type_and_honoree_without_assuming_disclosure(self):
        self.assertEqual(
            validate_tribute(
                tribute_type="IN_MEMORY_OF", honoree_name="Grace Example",
                acknowledgment_contact="Family contact", donor_disclosure_authorized=False,
                amount_disclosure_authorized=False,
            ),
            ("IN_MEMORY_OF", "Grace Example", "Family contact"),
        )
        with self.assertRaises(GivingValidationError):
            validate_tribute(
                tribute_type="IN_HONOR_OF", honoree_name="",
                acknowledgment_contact=None, donor_disclosure_authorized=False,
                amount_disclosure_authorized=False,
            )
        with self.assertRaises(GivingValidationError):
            validate_tribute(
                tribute_type=None, honoree_name="Grace Example",
                acknowledgment_contact=None, donor_disclosure_authorized=False,
                amount_disclosure_authorized=False,
            )


if __name__ == "__main__":
    unittest.main()
