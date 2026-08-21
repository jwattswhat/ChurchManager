"""Privacy-safe domain validation for the ChurchManager giving subledger."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Iterable


class GivingValidationError(ValueError):
    """Report a giving rule violation without embedding confidential data."""


def _money(value: object, field: str) -> Decimal:
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise GivingValidationError(f"{field} must be a valid monetary amount.") from error
    if not amount.is_finite():
        raise GivingValidationError(f"{field} must be a finite monetary amount.")
    return amount


def validate_contributor_links(
    contributor_type: str, person_id: int | None, family_id: int | None
) -> None:
    """Require the one permitted directory link for a contributor type."""
    normalized = str(contributor_type or "").strip().upper()
    valid = {
        "PERSON": person_id is not None and family_id is None,
        "FAMILY": family_id is not None and person_id is None,
        "EXTERNAL": person_id is None and family_id is None,
    }
    if normalized not in valid:
        raise GivingValidationError("Contributor type must be Person, Family, or External.")
    if not valid[normalized]:
        raise GivingValidationError(
            f"A {normalized.title()} contributor has an invalid directory relationship."
        )


def envelope_periods_overlap(
    first_from: date,
    first_through: date | None,
    second_from: date,
    second_through: date | None,
) -> bool:
    """Return whether two inclusive envelope assignments overlap."""
    maximum = date.max
    return first_from <= (second_through or maximum) and second_from <= (first_through or maximum)


def validate_envelope_assignment(
    envelope_number: str,
    effective_from: date,
    effective_through: date | None = None,
) -> str:
    """Normalize an envelope number while preserving significant zeroes."""
    normalized = str(envelope_number or "").strip()
    if not normalized:
        raise GivingValidationError("Envelope number is required.")
    if len(normalized) > 30:
        raise GivingValidationError("Envelope number cannot exceed 30 characters.")
    if normalized.isdecimal():
        normalized = str(int(normalized))
    if effective_through is not None and effective_from > effective_through:
        raise GivingValidationError("Envelope end date cannot precede its start date.")
    return normalized


def validate_allocations(gift_amount: object, allocations: Iterable[object]) -> Decimal:
    """Require positive allocation lines that exactly equal a monetary gift."""
    gift = _money(gift_amount, "Gift amount")
    if gift <= 0:
        raise GivingValidationError("A monetary gift must be greater than zero.")
    values = [_money(value, "Allocation amount") for value in allocations]
    if not values:
        raise GivingValidationError("A monetary gift requires at least one allocation.")
    if any(value <= 0 for value in values):
        raise GivingValidationError("Every allocation amount must be greater than zero.")
    if sum(values, Decimal("0.00")) != gift:
        raise GivingValidationError("Allocation amounts must equal the gift amount.")
    return gift


def validate_gift_acknowledgment(
    *,
    goods_or_services_provided: bool,
    goods_or_services_value: object | None,
    intangible_religious_benefit_only: bool,
) -> Decimal | None:
    """Validate mutually exclusive acknowledgment facts for a contribution."""
    if goods_or_services_provided and intangible_religious_benefit_only:
        raise GivingValidationError(
            "Goods or services and intangible religious benefit cannot both be selected."
        )
    if goods_or_services_provided:
        if goods_or_services_value is None:
            raise GivingValidationError("Enter the good-faith value of goods or services.")
        value = _money(goods_or_services_value, "Goods or services value")
        if value < 0:
            raise GivingValidationError("Goods or services value cannot be negative.")
        return value
    if goods_or_services_value not in (None, ""):
        raise GivingValidationError(
            "Remove the goods or services value when none were provided."
        )
    return None
