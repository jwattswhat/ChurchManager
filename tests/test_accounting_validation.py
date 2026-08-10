from datetime import date
from decimal import Decimal
import unittest

from accounting import (
    AccountingValidationError, JournalLine, JournalTransaction,
    validate_transaction,
)


def line(number, fund, debit="0.00", credit="0.00"):
    return JournalLine(number, number, fund, Decimal(debit), Decimal(credit))


class TestAccountingValidation(unittest.TestCase):
    def transaction(self, *lines):
        return JournalTransaction(1, date(2027, 1, 1), "Opening entry", lines)

    def test_balanced_transaction_and_each_fund_are_accepted(self):
        validate_transaction(self.transaction(
            line(1, 1, debit="100.00"), line(2, 1, credit="100.00"),
            line(3, 2, debit="25.00"), line(4, 2, credit="25.00"),
        ))

    def test_line_requires_exactly_one_positive_side(self):
        for invalid in (
            line(1, 1), line(1, 1, debit="1.00", credit="1.00"),
            line(1, 1, debit="-1.00"),
        ):
            with self.subTest(line=invalid):
                with self.assertRaisesRegex(AccountingValidationError, "Line 1"):
                    validate_transaction(self.transaction(invalid, line(2, 1, credit="1.00")))

    def test_whole_transaction_difference_is_reported(self):
        with self.assertRaisesRegex(AccountingValidationError, r"\$25.00"):
            validate_transaction(self.transaction(
                line(1, 1, debit="100.00"), line(2, 1, credit="75.00")
            ))

    def test_each_fund_must_balance_even_when_transaction_balances(self):
        with self.assertRaises(AccountingValidationError) as raised:
            validate_transaction(self.transaction(
                line(1, 1, debit="100.00"), line(2, 2, credit="100.00")
            ))
        self.assertIn("Fund 1", str(raised.exception))
        self.assertIn("Fund 2", str(raised.exception))

    def test_description_two_lines_and_unique_line_numbers_are_required(self):
        transaction = JournalTransaction(
            1, date(2027, 1, 1), " ",
            (line(1, 1, debit="10.00"), line(1, 1, credit="10.00")),
        )
        with self.assertRaises(AccountingValidationError) as raised:
            validate_transaction(transaction)
        self.assertIn("description", str(raised.exception))
        self.assertIn("duplicated", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
