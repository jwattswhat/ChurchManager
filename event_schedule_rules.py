"""Controlled natural-language recurrence rules for general Church events."""

from __future__ import annotations

from datetime import date, datetime
import re


_WEEKDAYS = {
    "monday": "MO", "tuesday": "TU", "wednesday": "WE",
    "thursday": "TH", "friday": "FR", "saturday": "SA", "sunday": "SU",
}
_DAY_NAMES = {code: name.title() for name, code in _WEEKDAYS.items()}
_MONTHS = {
    name.lower(): number for number, name in enumerate(
        ("January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"), 1
    )
}
_ORDINALS = {
    "first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "3rd": 3,
    "fourth": 4, "4th": 4, "fifth": 5, "5th": 5, "last": -1,
}
_ORDINAL_NAMES = {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth", -1: "Last"}
_COMMON_TYPOS = {"frist": "first", "tuseday": "tuesday", "tuesay": "tuesday", "thrusday": "thursday"}


def _clean(value):
    text = re.sub(r"[,.;]+", " ", str(value or "").strip().lower())
    words = [_COMMON_TYPOS.get(word, word) for word in re.sub(r"\s+", " ", text).split()]
    return " ".join(words)


def _join(values):
    return values[0] if len(values) == 1 else ", ".join(values[:-1]) + " and " + values[-1]


def _weekday_list(text):
    values = [item.strip() for item in re.split(r"\s*(?:and|&)\s*", text) if item.strip()]
    if not values or any(value not in _WEEKDAYS for value in values):
        raise ValueError("Use full weekday names, such as Tuesday and Thursday.")
    return list(dict.fromkeys(_WEEKDAYS[value] for value in values))


def parse_event_schedule(value):
    """Return canonical display text and an RFC 5545 rule for an event phrase."""
    text = _clean(value)
    if not text:
        raise ValueError("Enter a schedule, such as Every Tuesday.")

    weekly = re.fullmatch(r"(?:every|each|weekly on)\s+(.+)", text)
    if weekly:
        days = _weekday_list(weekly.group(1))
        names = [_DAY_NAMES[day] for day in days]
        return f"Every {_join(names)}", f"RRULE:FREQ=WEEKLY;BYDAY={','.join(days)}"

    monthly = re.fullmatch(
        r"(first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|last)\s+"
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+"
        r"(?:of|in)\s+(?:every|each|the)?\s*month", text)
    if monthly:
        ordinal, day = _ORDINALS[monthly.group(1)], _WEEKDAYS[monthly.group(2)]
        return (f"{_ORDINAL_NAMES[ordinal]} {_DAY_NAMES[day]} of every month",
                f"RRULE:FREQ=MONTHLY;BYDAY={ordinal}{day}")

    yearly = re.fullmatch(
        r"(first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|last)\s+"
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+"
        r"(?:of|in)\s+([a-z]+)", text)
    if yearly and yearly.group(3) in _MONTHS:
        ordinal, day, month = (_ORDINALS[yearly.group(1)], _WEEKDAYS[yearly.group(2)],
                               _MONTHS[yearly.group(3)])
        return (f"{_ORDINAL_NAMES[ordinal]} {_DAY_NAMES[day]} in {date(2000, month, 1):%B}",
                f"RRULE:FREQ=YEARLY;BYMONTH={month};BYDAY={ordinal}{day}")

    once = re.fullmatch(r"(?:once on|on)\s+([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\d{4})", text)
    if once and once.group(1) in _MONTHS:
        occurrence = date(int(once.group(3)), _MONTHS[once.group(1)], int(once.group(2)))
        return f"Once on {occurrence:%B} {occurrence.day}, {occurrence.year}", f"RDATE:{occurrence:%Y%m%d}"

    raise ValueError(
        "Schedule not understood. Try Every Tuesday and Thursday; First Tuesday of every month; "
        "Last Tuesday of the month; First Tuesday in October; or Once on October 1, 2026."
    )


def event_occurrences(rule, after, count=3):
    """Return upcoming dates for a validated stored event rule."""
    from dateutil.rrule import rrulestr
    recurrence = rrulestr(str(rule), dtstart=datetime(1900, 1, 1), forceset=True)
    current = datetime.combine(after, datetime.min.time())
    found = []
    for _index in range(count):
        occurrence = recurrence.after(current, inc=True)
        if occurrence is None:
            break
        found.append(occurrence.date()); current = occurrence.replace(microsecond=1)
    return found
