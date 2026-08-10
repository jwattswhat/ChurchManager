from datetime import date
import unittest

from accounting.setup_service import (
    FundClassification, calendar_periods, validated_fund_classifications,
)
from accounting.setup_dialog import CLASSIFICATION_CHOICES


def classified_special_funds():
    restricted = FundClassification("WITH_DONOR_RESTRICTIONS", "PURPOSE")
    return {
        "BUILDING": restricted,
        "MISSIONS": restricted,
        "BENEVOLENCE": restricted,
        "MEMORIALS": restricted,
        "ENDOWMENT": restricted,
    }


class TestAccountingSetup(unittest.TestCase):
    def test_calendar_year_has_twelve_exact_periods(self):
        periods = calendar_periods(2028)
        self.assertEqual(len(periods), 12)
        self.assertEqual(periods[0], (1, "January", date(2028, 1, 1), date(2028, 1, 31)))
        self.assertEqual(periods[1][3], date(2028, 2, 29))
        self.assertEqual(periods[-1][3], date(2028, 12, 31))

    def test_every_special_fund_requires_explicit_classification(self):
        choices = classified_special_funds()
        choices.pop("MEMORIALS")
        with self.assertRaisesRegex(ValueError, "MEMORIALS"):
            validated_fund_classifications(choices)

    def test_donor_restricted_fund_cannot_be_board_designated(self):
        choices = classified_special_funds()
        choices["BUILDING"] = FundClassification(
            "WITH_DONOR_RESTRICTIONS", "PURPOSE", True
        )
        with self.assertRaisesRegex(ValueError, "both donor-restricted"):
            validated_fund_classifications(choices)

    def test_unrestricted_fund_cannot_claim_donor_restriction_type(self):
        choices = classified_special_funds()
        choices["BUILDING"] = FundClassification(
            "WITHOUT_DONOR_RESTRICTIONS", "PURPOSE"
        )
        with self.assertRaisesRegex(ValueError, "without donor restrictions"):
            validated_fund_classifications(choices)

    def test_fixed_general_and_reserve_classifications_are_preserved(self):
        result = validated_fund_classifications(classified_special_funds())
        self.assertEqual(result["GENERAL"].net_asset_class, "WITHOUT_DONOR_RESTRICTIONS")
        self.assertTrue(result["RESERVE"].board_designated)

    def test_setup_dialog_offers_explicit_safe_classifications(self):
        labels = {label for label, unused in CLASSIFICATION_CHOICES}
        self.assertIn("Board-designated", labels)
        self.assertIn("Unrestricted", labels)
        self.assertTrue(any("purpose and time" in label for label in labels))

    def test_setup_dialog_uses_a_growing_two_column_grid(self):
        from pathlib import Path

        source = (
            Path(__file__).parents[1] / "accounting" / "setup_dialog.py"
        ).read_text(encoding="utf-8-sig")
        self.assertIn("wx.FlexGridSizer(cols=2", source)
        self.assertNotIn("wx.FlexGridSizer(2, 2", source)


if __name__ == "__main__":
    unittest.main()
