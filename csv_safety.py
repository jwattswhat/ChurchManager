"""Shared spreadsheet-formula neutralization for ChurchManager CSV output."""

from __future__ import annotations

from collections.abc import Mapping


FORMULA_PREFIXES = ("=", "+", "-", "@")
SAFE_PREFIX = "'"


def _first_significant(text: str) -> str:
    """Return the first character spreadsheets may treat as significant."""
    for character in text:
        if ord(character) > 0x20 and character != "\ufeff":
            return character
    return ""


def csv_safe_value(value):
    """Prefix formula-like text with an apostrophe while preserving non-text values."""
    if isinstance(value, str) and _first_significant(value) in FORMULA_PREFIXES:
        return SAFE_PREFIX + value
    return value


def csv_safe_row(row):
    """Return a mapping or sequence whose text cells are safe for spreadsheets."""
    if isinstance(row, Mapping):
        return {key: csv_safe_value(value) for key, value in row.items()}
    return tuple(csv_safe_value(value) for value in row)
