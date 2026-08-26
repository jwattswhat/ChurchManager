"""Typed, UI-independent accounting data objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


ZERO = Decimal("0.00")


@dataclass(frozen=True)
class JournalLine:
    line_number: int
    account_id: int
    fund_id: int
    debit: Decimal = ZERO
    credit: Decimal = ZERO
    function_id: int | None = None
    payee_id: int | None = None
    description: str = ""


@dataclass(frozen=True)
class JournalTransaction:
    organization_id: int
    transaction_date: date
    description: str
    lines: tuple[JournalLine, ...] = field(default_factory=tuple)
    reference: str = ""
    transaction_type: str = "JOURNAL"
