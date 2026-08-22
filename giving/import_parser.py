"""Pure parsing and validation for confidential contribution CSV imports."""

from __future__ import annotations

import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation


class ContributionImportError(ValueError):
    """Describe a CSV problem without exposing unrelated donor rows."""


@dataclass(frozen=True)
class ContributionCsvMapping:
    """Map provider-specific CSV headings to ChurchManager contribution fields."""

    date_column: str
    amount_column: str
    date_format: str = "%m/%d/%Y"
    envelope_column: str | None = None
    contributor_column: str | None = None
    method_column: str | None = None
    reference_column: str | None = None
    purpose_column: str | None = None
    description_column: str | None = None


@dataclass(frozen=True)
class ContributionImportRow:
    """One normalized, still-uncommitted contribution import row."""

    row_number: int
    received_date: object
    amount: Decimal
    envelope_number: str
    contributor: str
    method: str
    reference: str
    purpose: str
    description: str
    fingerprint: str


def file_hash(content: bytes) -> str:
    """Return the SHA-256 fingerprint of the original import bytes."""
    return hashlib.sha256(content).hexdigest()


def _text(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            return content.decode("cp1252")
        except UnicodeDecodeError as error:
            raise ContributionImportError("The CSV text encoding is not supported.") from error


def csv_headers(content: bytes) -> tuple[str, ...]:
    """Return validated, unique CSV headings."""
    reader = csv.reader(io.StringIO(_text(content)))
    try:
        headings = tuple(value.strip() for value in next(reader))
    except StopIteration as error:
        raise ContributionImportError("The CSV file has no header row.") from error
    if not headings or any(not value for value in headings):
        raise ContributionImportError("Every CSV column must have a heading.")
    if len(set(headings)) != len(headings):
        raise ContributionImportError("CSV column headings must be unique.")
    return headings


def _amount(value: str, row_number: int) -> Decimal:
    clean = str(value or "").strip().replace(",", "").replace("$", "")
    if clean.startswith("(") and clean.endswith(")"):
        clean = "-" + clean[1:-1]
    try:
        amount = Decimal(clean).quantize(Decimal("0.01"))
    except InvalidOperation as error:
        raise ContributionImportError(f"Row {row_number} has an invalid amount.") from error
    if amount <= 0:
        raise ContributionImportError(f"Row {row_number} must contain a positive contribution amount.")
    return amount


def _method(value: str, row_number: int) -> str:
    normalized = str(value or "").strip().upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "": "ELECTRONIC", "ACH": "ELECTRONIC", "E_GIVING": "ELECTRONIC",
        "EGIVING": "ELECTRONIC", "ONLINE": "ELECTRONIC", "CARD": "ELECTRONIC",
        "CREDIT_CARD": "ELECTRONIC", "DEBIT_CARD": "ELECTRONIC",
        "CASH": "CASH", "CHECK": "CHECK", "CHEQUE": "CHECK", "OTHER": "OTHER",
        "ELECTRONIC": "ELECTRONIC",
    }
    if normalized not in aliases:
        raise ContributionImportError(f"Row {row_number} has an unsupported contribution method.")
    return aliases[normalized]


def parse_csv(content: bytes, mapping: ContributionCsvMapping) -> tuple[ContributionImportRow, ...]:
    """Parse a contribution CSV entirely in memory without changing the database."""
    headings = csv_headers(content)
    mapped = tuple(value for value in mapping.__dict__.values() if value and value != mapping.date_format)
    missing = sorted({value for value in mapped if value not in headings})
    if missing:
        raise ContributionImportError("CSV columns are missing: " + ", ".join(missing))
    if not mapping.envelope_column and not mapping.contributor_column:
        raise ContributionImportError("Map an envelope or contributor column.")
    reader = csv.DictReader(io.StringIO(_text(content)))
    rows = []
    for row_number, source in enumerate(reader, 2):
        try:
            received = datetime.strptime(
                str(source.get(mapping.date_column) or "").strip(), mapping.date_format
            ).date()
        except ValueError as error:
            raise ContributionImportError(f"Row {row_number} has an invalid date.") from error
        amount = _amount(source.get(mapping.amount_column), row_number)
        envelope = str(source.get(mapping.envelope_column) or "").strip() if mapping.envelope_column else ""
        if envelope.isdecimal():
            envelope = str(int(envelope))
        contributor = str(source.get(mapping.contributor_column) or "").strip() if mapping.contributor_column else ""
        if not envelope and not contributor:
            raise ContributionImportError(f"Row {row_number} has no envelope or contributor.")
        method = _method(source.get(mapping.method_column), row_number) if mapping.method_column else "ELECTRONIC"
        reference = str(source.get(mapping.reference_column) or "").strip() if mapping.reference_column else ""
        purpose = str(source.get(mapping.purpose_column) or "").strip() if mapping.purpose_column else ""
        description = str(source.get(mapping.description_column) or "").strip() if mapping.description_column else ""
        key = "|".join((received.isoformat(), str(amount), envelope.casefold(),
                        contributor.casefold(), method, reference.casefold(), purpose.casefold()))
        rows.append(ContributionImportRow(
            row_number, received, amount, envelope, contributor, method, reference,
            purpose, description, hashlib.sha256(key.encode("utf-8")).hexdigest(),
        ))
    if not rows:
        raise ContributionImportError("The CSV file contains no contribution rows.")
    return tuple(rows)
