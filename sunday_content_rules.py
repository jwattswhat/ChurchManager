"""Controlled natural-language schedules for prayers and announcements."""

from datetime import date, datetime, time, timedelta
import re

from dateutil.rrule import rrulestr


EVERY_SUNDAY = "RRULE:FREQ=WEEKLY;BYDAY=SU"
ANNUAL_FIRST_SUNDAY = "RRULE:FREQ=YEARLY;BYMONTH=1;BYDAY=1SU"

_ORDINALS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "last": -1,
}
_ORDINAL_NAMES = {value: key for key, value in _ORDINALS.items()}
_MONTHS = {
    name.lower(): number
    for number, name in enumerate(
        ("January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"), 1
    )
}
_MONTHS.update({name[:3].lower(): number for name, number in tuple(_MONTHS.items()) if len(name) > 3})
_HOLIDAYS = {
    "new year's day": (1, 1), "new years day": (1, 1),
    "fourth of july": (7, 4), "4th of july": (7, 4), "independence day": (7, 4),
    "christmas eve": (12, 24), "christmas day": (12, 25),
    "new year's eve": (12, 31), "new years eve": (12, 31),
}
_WEEKDAYS = {
    "monday": "MO", "tuesday": "TU", "wednesday": "WE",
    "thursday": "TH", "friday": "FR", "saturday": "SA", "sunday": "SU",
}
_WEEKDAY_NAMES = {value: name.title() for name, value in _WEEKDAYS.items()}
_MOVABLE_WORDS = (
    "advent", "ash wednesday", "easter", "palm sunday", "pentecost",
)


def _month_name(month):
    return date(2000, month, 1).strftime("%B")


def _join_words(values):
    if len(values) == 1:
        return values[0]
    return ", ".join(values[:-1]) + " and " + values[-1]


def monthly_rule(weeks):
    values = sorted({int(week) for week in weeks if int(week) in (-1, 1, 2, 3, 4, 5)})
    return "RRULE:FREQ=MONTHLY;BYDAY=" + ",".join(f"{value}SU" for value in values)


def annual_date_rule(month, day):
    date(2000, int(month), int(day))
    return f"RRULE:FREQ=YEARLY;BYMONTH={int(month)};BYMONTHDAY={int(day)}"


def weekly_rule(weekday):
    """Return a weekly RFC 5545 rule for a weekday name or code."""
    value = str(weekday or "").strip().lower()
    code = _WEEKDAYS.get(value, value.upper())
    if code not in _WEEKDAY_NAMES:
        raise ValueError("Choose a valid weekday.")
    return f"RRULE:FREQ=WEEKLY;BYDAY={code}"


def annual_sunday_after_rule(month, day):
    """Return the first Sunday strictly after a fixed date in the same month."""
    month, day = int(month), int(day)
    date(2000, month, day + 7)
    days = ",".join(str(value) for value in range(day + 1, day + 8))
    return f"RRULE:FREQ=YEARLY;BYMONTH={month};BYDAY=SU;BYMONTHDAY={days}"


def one_time_rule(value):
    parsed = value if isinstance(value, date) else date.fromisoformat(str(value))
    return f"RDATE:{parsed.strftime('%Y%m%d')}"


def normalize_rule(value):
    """Normalize current rules and defensively translate pre-migration codes."""
    text = str(value or EVERY_SUNDAY).strip()
    upper = text.upper()
    if upper == "EVERY_SUNDAY":
        return EVERY_SUNDAY
    if upper == "ANNUAL_FIRST_SUNDAY":
        return ANNUAL_FIRST_SUNDAY
    if upper.startswith("MONTHLY_SUNDAYS:"):
        return monthly_rule(int(item) for item in upper.split(":", 1)[1].split(",") if item)
    if upper.startswith("ANNUAL_DATE:"):
        month, day = (int(item) for item in upper.split(":", 1)[1].split("-"))
        return annual_date_rule(month, day)
    if upper.startswith("ONE_TIME:"):
        return one_time_rule(date.fromisoformat(text.split(":", 1)[1]))
    if upper.startswith(("RRULE:", "RDATE:")):
        return upper
    raise ValueError("The stored schedule rule is not recognized.")


def describe_rule(value):
    rule = normalize_rule(value)
    if rule == EVERY_SUNDAY:
        return "Every Sunday"
    if rule == ANNUAL_FIRST_SUNDAY:
        return "First Sunday of each year"
    if rule.startswith("RDATE:"):
        occurrence = datetime.strptime(rule.split(":", 1)[1], "%Y%m%d").date()
        return f"Once on {occurrence.strftime('%B')} {occurrence.day}, {occurrence.year}"
    body = rule.split(":", 1)[1]
    parts = dict(item.split("=", 1) for item in body.split(";") if "=" in item)
    if parts.get("FREQ") == "WEEKLY" and parts.get("BYDAY") in _WEEKDAY_NAMES:
        return f"Every {_WEEKDAY_NAMES[parts['BYDAY']]}"
    if parts.get("FREQ") == "MONTHLY" and parts.get("BYDAY"):
        numbers = [int(item[:-2]) for item in parts["BYDAY"].split(",")]
        names = [_ORDINAL_NAMES[number] for number in numbers]
        return f"{_join_words(names).capitalize()} Sunday{'s' if len(names) > 1 else ''} of each month"
    if (parts.get("FREQ") == "YEARLY" and parts.get("BYMONTH") and
            parts.get("BYMONTHDAY") and not parts.get("BYDAY")):
        month, day = int(parts["BYMONTH"]), int(parts["BYMONTHDAY"])
        holiday = {(1, 1): "New Year's Day", (12, 24): "Christmas Eve",
                   (12, 25): "Christmas Day", (12, 31): "New Year's Eve"}.get((month, day))
        return f"Every {holiday}" if holiday else f"Every year on {_month_name(month)} {day}"
    if (parts.get("FREQ") == "YEARLY" and parts.get("BYMONTH") and
            parts.get("BYDAY") == "SU" and parts.get("BYMONTHDAY")):
        days = [int(item) for item in parts["BYMONTHDAY"].split(",")]
        if len(days) == 7 and days == list(range(days[0], days[0] + 7)):
            month, day = int(parts["BYMONTH"]), days[0] - 1
            anchor = "the Fourth of July" if (month, day) == (7, 4) else f"{_month_name(month)} {day}"
            return f"First Sunday after {anchor}"
    raise ValueError("This custom recurrence rule cannot be edited as a supported schedule.")


def _clean_text(value):
    text = str(value or "").strip().lower().replace("sinday", "sunday")
    return re.sub(r"\s+", " ", re.sub(r"[,.;]+", " ", text)).strip()


def _parse_month_day(text):
    match = re.fullmatch(r"([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?", text)
    if not match or match.group(1) not in _MONTHS:
        raise ValueError("Enter a month and day, such as October 1.")
    month, day = _MONTHS[match.group(1)], int(match.group(2))
    date(2000, month, day)
    return month, day


def parse_schedule(value):
    """Return ``(canonical_text, standard_rule)`` for supported English input."""
    text = _clean_text(value)
    if not text:
        raise ValueError("Enter a schedule, such as Every Sunday.")
    if any(word in text for word in _MOVABLE_WORDS):
        raise ValueError("Church-year and movable-feast schedules are not supported. Use a fixed date or Sunday schedule.")
    weekly = re.fullmatch(r"(?:every|each|weekly on)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", text)
    if weekly:
        rule = weekly_rule(weekly.group(1))
        return describe_rule(rule), rule

    annual = re.fullmatch(r"(?:every|each|annually on)\s+(.+)", text)
    if annual:
        named = annual.group(1)
        if named.startswith("year on "):
            named = named[8:]
        if named in _HOLIDAYS:
            rule = annual_date_rule(*_HOLIDAYS[named])
            return describe_rule(rule), rule
        try:
            rule = annual_date_rule(*_parse_month_day(named))
            return describe_rule(rule), rule
        except ValueError:
            pass

    if text in ("first sunday of each year", "first sunday of the year"):
        return "First Sunday of each year", ANNUAL_FIRST_SUNDAY

    after = re.fullmatch(r"(?:the )?first sunday after\s+(.+)", text)
    if after:
        anchor = re.sub(r"^the\s+", "", after.group(1))
        month, day = _HOLIDAYS.get(anchor, (None, None))
        if month is None:
            month, day = _parse_month_day(anchor)
        try:
            rule = annual_sunday_after_rule(month, day)
        except ValueError as error:
            raise ValueError(
                "The fixed date must leave seven days in the same month. Use an explicit date for this schedule."
            ) from error
        return describe_rule(rule), rule

    monthly_text = re.sub(r"\s+(?:of each month|of the month|monthly)$", "", text)
    monthly_text = monthly_text.replace("sundays", "sunday")
    if monthly_text.endswith(" sunday"):
        ordinal_text = monthly_text[:-7].strip()
        words = [item.strip() for item in re.split(r"\s*(?:and|&)\s*", ordinal_text) if item.strip()]
        if words and all(word in _ORDINALS for word in words):
            rule = monthly_rule(_ORDINALS[word] for word in words)
            return describe_rule(rule), rule

    once = re.fullmatch(r"(?:once on|on)\s+([a-z]+\s+\d{1,2})(?:\s+(\d{4}))?(?:\s+only)?", text)
    if once and once.group(2):
        month, day = _parse_month_day(once.group(1))
        rule = one_time_rule(date(int(once.group(2)), month, day))
        return describe_rule(rule), rule

    raise ValueError(
        "Schedule not understood. Try Every Tuesday; First and third Sundays of each month; "
        "Every Christmas Eve; Every year on October 1; or Once on December 24, 2026."
    )


def matches_rule(value, report_date):
    rule = normalize_rule(value)
    start = datetime.combine(report_date, time.min)
    end = datetime.combine(report_date, time.max)
    recurrence = rrulestr(rule, dtstart=datetime(1900, 1, 1), forceset=True)
    return bool(recurrence.between(start, end, inc=True))


def next_occurrences(value, after=None, count=3):
    rule = normalize_rule(value)
    after = after or date.today()
    recurrence = rrulestr(rule, dtstart=datetime(1900, 1, 1), forceset=True)
    result = []
    current = datetime.combine(after - timedelta(days=1), time.max)
    for _index in range(count):
        found = recurrence.after(current, inc=False)
        if found is None:
            break
        result.append(found.date())
        current = found
    return result


def is_active(rule, report_date, start_date=None, end_date=None):
    return ((start_date is None or report_date >= start_date)
            and (end_date is None or report_date <= end_date)
            and matches_rule(rule, report_date))


def service_week(value):
    """Return the Sunday-through-Saturday week containing value."""
    start = value - timedelta(days=(value.weekday() + 1) % 7)
    return start, start + timedelta(days=6)


def occurs_in_service_week(rule, value, start_date=None, end_date=None):
    """True when a recurrence has an eligible occurrence anywhere in the service week."""
    week_start, _week_end = service_week(value)
    return any(is_active(rule, week_start + timedelta(days=offset), start_date, end_date)
               for offset in range(7))
