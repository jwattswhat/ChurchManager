"""Shared display colors for worship screens and reports."""

import re


LITURGICAL_COLOR_HEX = {
    "black": "#202124",
    "blue": "#1565C0",
    "gold": "#D4AF37",
    "green": "#2E7D32",
    "red": "#C62828",
    "rose": "#D76C8A",
    "violet": "#6A1B9A",
    "white": "#FFFFFF",
}

ALIASES = {
    "pink": "rose",
    "purple": "violet",
    "scarlet": "red",
}


def liturgical_color_hex(value):
    """Return a safe display color, or blank when no known color is selected."""
    text = str(value or "").strip()
    if re.fullmatch(r"#[0-9a-fA-F]{6}", text):
        return text.upper()
    for word in re.findall(r"[A-Za-z]+", text.casefold()):
        name = ALIASES.get(word, word)
        if name in LITURGICAL_COLOR_HEX:
            return LITURGICAL_COLOR_HEX[name]
    return ""
