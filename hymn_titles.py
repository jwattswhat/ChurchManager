"""Normalize hymnal and hymn titles to ChurchManager title-case conventions."""

from __future__ import annotations


_LOWERCASE_WORDS = frozenset({
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "in",
    "nor", "of", "on", "or", "the", "to", "with",
})


def title_case(value: str) -> str:
    """Return stable title case while preserving acronyms and hymn apostrophes."""
    words = " ".join(str(value or "").strip().split()).split(" ")
    if not words or words == [""]:
        return ""
    converted = []
    for index, word in enumerate(words):
        follows_break = index > 0 and words[index - 1].rstrip().endswith((":", "!", "?"))
        converted.append(
            _title_word(word, index == 0 or index == len(words) - 1 or follows_break)
        )
    return " ".join(converted)


def _title_word(word: str, is_edge: bool) -> str:
    if not word:
        return word
    if word.isupper() and sum(character.isalpha() for character in word) > 1:
        return word
    lowered = word.casefold()
    if not is_edge and lowered in _LOWERCASE_WORDS:
        return lowered
    return "-".join(_capitalize_segment(segment) for segment in word.split("-"))


def _capitalize_segment(segment: str) -> str:
    characters = list(segment.lower())
    for index, character in enumerate(characters):
        if character.isalpha():
            characters[index] = character.upper()
            break
    return "".join(characters)
