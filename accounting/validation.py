"""Pure double-entry and per-fund validation rules."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from .models import JournalTransaction, ZERO


class AccountingValidationError(ValueError):
    """A journal transaction cannot safely enter the ledger."""


def _money(value):
    return Decimal(value).quantize(Decimal("0.01"))


def validate_transaction(transaction: JournalTransaction) -> None:
    errors = []
    if not transaction.description.strip():
        errors.append("Transaction description is required.")
    if len(transaction.lines) < 2:
        errors.append("A transaction must contain at least two lines.")

    seen_numbers = set()
    debit_total = ZERO
    credit_total = ZERO
    fund_totals = defaultdict(lambda: [ZERO, ZERO])
    for line in transaction.lines:
        debit = _money(line.debit)
        credit = _money(line.credit)
        if line.line_number in seen_numbers:
            errors.append("Line number {} is duplicated.".format(line.line_number))
        seen_numbers.add(line.line_number)
        if debit < ZERO or credit < ZERO:
            errors.append("Line {} cannot contain a negative amount.".format(line.line_number))
        elif (debit > ZERO) == (credit > ZERO):
            errors.append(
                "Line {} must contain either a debit or a credit.".format(
                    line.line_number
                )
            )
        debit_total += debit
        credit_total += credit
        fund_totals[line.fund_id][0] += debit
        fund_totals[line.fund_id][1] += credit

    difference = _money(debit_total - credit_total)
    if difference:
        errors.append("Transaction is out of balance by ${:.2f}.".format(abs(difference)))
    for fund_id, (debits, credits) in sorted(fund_totals.items()):
        difference = _money(debits - credits)
        if difference:
            errors.append(
                "Fund {} is out of balance by ${:.2f}.".format(
                    fund_id, abs(difference)
                )
            )
    if errors:
        raise AccountingValidationError("\n".join(errors))
