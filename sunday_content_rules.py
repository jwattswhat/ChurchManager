"""Natural-language recurrence rules shared by prayers and announcements."""

from datetime import date, timedelta


EVERY_SUNDAY = "EVERY_SUNDAY"
MONTHLY_SUNDAYS = "MONTHLY_SUNDAYS"
ANNUAL_DATE = "ANNUAL_DATE"
ANNUAL_FIRST_SUNDAY = "ANNUAL_FIRST_SUNDAY"
ONE_TIME = "ONE_TIME"


def monthly_rule(weeks):
    values = sorted({int(week) for week in weeks if 1 <= int(week) <= 5})
    return f"{MONTHLY_SUNDAYS}:" + ",".join(str(value) for value in values)


def annual_date_rule(month, day):
    date(2000, int(month), int(day))
    return f"{ANNUAL_DATE}:{int(month):02d}-{int(day):02d}"


def one_time_rule(value):
    parsed = value if isinstance(value, date) else date.fromisoformat(str(value))
    return f"{ONE_TIME}:{parsed.isoformat()}"


def normalize_rule(value):
    return str(value or EVERY_SUNDAY).strip().upper()


def _ordinal(value):
    return {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}[value]


def describe_rule(value):
    rule = normalize_rule(value)
    if rule == EVERY_SUNDAY:
        return "Every Sunday"
    if rule == ANNUAL_FIRST_SUNDAY:
        return "First Sunday of each year"
    if rule.startswith(f"{MONTHLY_SUNDAYS}:"):
        weeks = [int(item) for item in rule.split(":", 1)[1].split(",") if item]
        names = [_ordinal(item) for item in weeks]
        if not names:
            return "No Sundays selected"
        joined = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
        return f"{joined.capitalize()} Sunday{'s' if len(names) > 1 else ''} of each month"
    if rule.startswith(f"{ANNUAL_DATE}:"):
        month, day = (int(item) for item in rule.split(":", 1)[1].split("-"))
        return f"Every year on {date(2000, month, day).strftime('%B')} {day}"
    if rule.startswith(f"{ONE_TIME}:"):
        value = date.fromisoformat(rule.split(":", 1)[1])
        return f"Once on {value.strftime('%B')} {value.day}, {value.year}"
    raise ValueError("The Sunday-content schedule rule is not recognized.")


def _first_sunday(year):
    value = date(year, 1, 1)
    return value + timedelta(days=(6 - value.weekday()) % 7)


def matches_rule(value, report_date):
    rule = normalize_rule(value)
    if rule == EVERY_SUNDAY:
        return report_date.weekday() == 6
    if rule == ANNUAL_FIRST_SUNDAY:
        return report_date == _first_sunday(report_date.year)
    if rule.startswith(f"{MONTHLY_SUNDAYS}:"):
        if report_date.weekday() != 6:
            return False
        selected = {int(item) for item in rule.split(":", 1)[1].split(",") if item}
        return ((report_date.day - 1) // 7 + 1) in selected
    if rule.startswith(f"{ANNUAL_DATE}:"):
        month, day = (int(item) for item in rule.split(":", 1)[1].split("-"))
        return (report_date.month, report_date.day) == (month, day)
    if rule.startswith(f"{ONE_TIME}:"):
        return report_date == date.fromisoformat(rule.split(":", 1)[1])
    return False


def is_active(rule, report_date, start_date=None, end_date=None):
    return (
        (start_date is None or report_date >= start_date)
        and (end_date is None or report_date <= end_date)
        and matches_rule(rule, report_date)
    )


def service_week(value):
    """Return the Sunday-through-Saturday week containing value."""
    start = value - timedelta(days=(value.weekday() + 1) % 7)
    return start, start + timedelta(days=6)


def occurs_in_service_week(rule, value, start_date=None, end_date=None):
    """True when a recurrence has an eligible occurrence anywhere in the service week."""
    week_start, _week_end = service_week(value)
    return any(
        is_active(rule, week_start + timedelta(days=offset), start_date, end_date)
        for offset in range(7)
    )
