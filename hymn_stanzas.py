"""Validate and format service-specific hymn stanza selections."""

from __future__ import annotations

import re


_PREFIX = re.compile(r"^\s*sts?\.\s*", re.IGNORECASE)
_PART = re.compile(r"^(\d+)(?:-(\d+))?$")


class StanzaSelectionError(ValueError):
    """Raised when a stanza expression cannot be normalized safely."""


def normalize_stanzas(text) -> str | None:
    """Return canonical numeric stanza syntax, or ``None`` for blank input."""
    if text is None:
        return None
    value = _PREFIX.sub("", str(text).strip()).replace("–", "-").replace("—", "-")
    value = re.sub(r"\s+", "", value)
    if not value:
        return None

    seen: set[int] = set()
    normalized: list[str] = []
    for part in value.split(","):
        if not part:
            raise StanzaSelectionError("Enter stanza numbers separated by commas, such as 1,3,5.")
        match = _PART.fullmatch(part)
        if not match:
            raise StanzaSelectionError("Use stanza numbers and closed ranges, such as 1,3,11-12.")
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if start < 1 or end < 1:
            raise StanzaSelectionError("Stanza numbers must be positive whole numbers.")
        if end < start:
            raise StanzaSelectionError("A stanza range must run from the lower number to the higher number.")
        expanded = range(start, end + 1)
        if any(number in seen for number in expanded):
            raise StanzaSelectionError("Each stanza may be listed only once.")
        seen.update(expanded)
        normalized.append(str(start) if start == end else f"{start}-{end}")
    return ",".join(normalized)


def format_stanza_notation(value) -> str:
    """Format canonical syntax for a printed hymn reference."""
    normalized = normalize_stanzas(value)
    if normalized is None:
        return ""
    expanded_count = 0
    for part in normalized.split(","):
        bounds = part.split("-")
        expanded_count += 1 if len(bounds) == 1 else int(bounds[1]) - int(bounds[0]) + 1
    readable = normalized.replace("-", "–").replace(",", ", ")
    return f"st. {readable}" if expanded_count == 1 else f"sts. {readable}"


def format_hymn_reference(reference, stanzas=None) -> str:
    """Append optional stanza notation to an existing hymnal reference."""
    base = str(reference or "").strip()
    notation = format_stanza_notation(stanzas)
    if not notation:
        return base
    return f"{base}, {notation}" if base else notation
