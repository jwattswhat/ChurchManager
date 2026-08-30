"""Privacy-safe domain validation for the ChurchManager giving subledger."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Iterable


class GivingValidationError(ValueError):
    """Report a giving rule violation without embedding confidential data."""


def require_giving_organization(cursor, church_id: int, organization_id: int) -> None:
    """Require an active accounting organization owned by the Giving church."""
    cursor.execute(
        "SELECT ID FROM tblAccountingOrganization "
        "WHERE ID=? AND ChurchID=? AND Active=1 FOR UPDATE",
        (organization_id, church_id),
    )
    if cursor.fetchone() is None:
        raise GivingValidationError(
            "Select an active accounting organization belonging to this church."
        )


def require_giving_bank_account(cursor, organization_id: int, bank_account_id: int | None) -> None:
    """Require a bank account and ledger account owned by the organization."""
    if bank_account_id is None:
        return
    cursor.execute(
        "SELECT ba.ID FROM tblAccountingBankAccount ba "
        "JOIN tblAccountingAccount a ON a.ID=ba.AccountID "
        "WHERE ba.ID=? AND ba.OrganizationID=? AND ba.Active=1 "
        "AND a.OrganizationID=ba.OrganizationID AND a.Active=1 FOR UPDATE",
        (bank_account_id, organization_id),
    )
    if cursor.fetchone() is None:
        raise GivingValidationError(
            "Select an active bank account belonging to this accounting organization."
        )


def require_giving_contributor(cursor, church_id: int, contributor_id: int | None) -> None:
    """Require an optional contributor identity owned by the Giving church."""
    if contributor_id is None:
        return
    cursor.execute(
        "SELECT ID FROM tblContributionContributor WHERE ID=? AND ChurchID=?",
        (contributor_id, church_id),
    )
    if cursor.fetchone() is None:
        raise GivingValidationError("Select a contributor belonging to this church.")


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


def validate_contribution_amounts(
    method: str,
    gift_amount: object,
    allocations: Iterable[object],
    non_cash_description: str | None = None,
) -> tuple[Decimal, str | None]:
    """Validate monetary or description-only non-cash contribution amounts."""
    normalized_method = str(method or "").strip().upper()
    values = list(allocations)
    if normalized_method != "NON_CASH":
        if non_cash_description not in (None, ""):
            raise GivingValidationError(
                "Remove the non-cash property description for a monetary contribution."
            )
        return validate_allocations(gift_amount, values), None

    description = str(non_cash_description or "").strip()
    if not description:
        raise GivingValidationError("Describe the donated property.")
    if len(description) > 1000:
        raise GivingValidationError("The donated-property description cannot exceed 1000 characters.")
    amount = _money(gift_amount, "Gift amount")
    if amount != Decimal("0.00"):
        raise GivingValidationError(
            "A non-cash gift must not contain a ChurchManager-assigned monetary value."
        )
    allocation_values = [_money(value, "Allocation amount") for value in values]
    if not allocation_values:
        raise GivingValidationError("A non-cash gift requires an approved purpose.")
    if any(value != Decimal("0.00") for value in allocation_values):
        raise GivingValidationError("Non-cash purpose allocations must remain zero dollars.")
    return amount, description


def validate_donor_estimated_value(method: str, value: object | None) -> Decimal | None:
    """Accept an optional donor estimate only for a non-cash contribution."""
    if value in (None, ""):
        return None
    if str(method or "").strip().upper() != "NON_CASH":
        raise GivingValidationError(
            "A donor-provided estimated value may be recorded only for donated property."
        )
    amount = _money(value, "Donor-provided estimated value")
    if amount <= 0:
        raise GivingValidationError("A donor-provided estimated value must be greater than zero.")
    return amount


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


def validate_tribute(
    *,
    tribute_type: str | None,
    honoree_name: str | None,
    acknowledgment_contact: str | None,
    donor_disclosure_authorized: bool,
    amount_disclosure_authorized: bool,
) -> tuple[str | None, str | None, str | None]:
    """Validate optional memorial or honor facts without inferring consent."""
    normalized = str(tribute_type or "").strip().upper() or None
    honoree = str(honoree_name or "").strip() or None
    contact = str(acknowledgment_contact or "").strip() or None
    if normalized not in {None, "IN_MEMORY_OF", "IN_HONOR_OF"}:
        raise GivingValidationError("Select a valid memorial or honor type.")
    if normalized is None:
        if honoree or contact or donor_disclosure_authorized or amount_disclosure_authorized:
            raise GivingValidationError(
                "Select In Memory Of or In Honor Of before entering tribute details."
            )
        return None, None, None
    if not honoree:
        raise GivingValidationError("Enter the person being remembered or honored.")
    if len(honoree) > 255:
        raise GivingValidationError("The memorial or honor name cannot exceed 255 characters.")
    if contact and len(contact) > 1000:
        raise GivingValidationError("The acknowledgment contact cannot exceed 1000 characters.")
    return normalized, honoree, contact
