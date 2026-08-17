"""Resolve explicit lectionary calendar rules without inferring from names."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import re

from bulletin_orders import portable_connection


class LectionaryCalendarError(ValueError):
    """Raised when a resolver rule is unsupported or malformed."""


@dataclass(frozen=True)
class LectionaryCandidate:
    """One possible Proper for a date, including its auditable explanation."""

    proper_id: int
    proper_key: str
    liturgical_date: str
    season: str
    cycle_key: str
    rule: str
    explanation: str


def gregorian_easter(year):
    """Return Gregorian Easter Sunday using the standard computus algorithm."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def advent_start(year):
    """Return the First Sunday in Advent occurring in the civil year."""
    december_third = date(year, 12, 3)
    return december_third - timedelta(days=(december_third.weekday() + 1) % 7)


def _month_day(text, year):
    try:
        month, day = (int(part) for part in text.split("-", 1))
        return date(year, month, day)
    except (TypeError, ValueError) as error:
        raise LectionaryCalendarError("A calendar rule contains an invalid month and day.") from error


def rule_date(rule, year):
    """Return the civil date produced by one supported explicit rule."""
    rule = str(rule or "").strip().casefold()
    if match := re.fullmatch(r"fixed:(\d{2}-\d{2})", rule):
        return _month_day(match.group(1), year)
    if match := re.fullmatch(r"easter:([+-]?\d{1,3})", rule):
        return gregorian_easter(year) + timedelta(days=int(match.group(1)))
    if match := re.fullmatch(r"advent-sunday(?::|-)([1-4])", rule):
        return advent_start(year) + timedelta(days=7 * (int(match.group(1)) - 1))
    if match := re.fullmatch(r"sunday-after:(\d{2}-\d{2})", rule):
        anchor = _month_day(match.group(1), year)
        return anchor + timedelta(days=7 - ((anchor.weekday() + 1) % 7))
    raise LectionaryCalendarError(f"Unsupported lectionary calendar rule: {rule or '(blank)' }.")


def validate_cycle_rule(rule, cycles):
    """Validate a cycle rule against the edition's declared active cycle keys."""
    text = str(rule or "none").strip().casefold()
    if text == "none":
        return
    match = re.fullmatch(r"advent-cycle:(\d{4}):([a-z0-9._-]+)", text)
    keys = {str(item[0]).casefold() for item in cycles if bool(item[3])}
    if not match or match.group(2) not in keys:
        raise LectionaryCalendarError("The edition cycle rule or anchor key is invalid.")


def cycle_for_date(value, cycle_rule, cycles):
    """Resolve an explicitly anchored cycle; return blank for noncyclic editions."""
    rule = str(cycle_rule or "none").strip().casefold()
    ordered = sorted(cycles, key=lambda item: (int(item[2]), str(item[0])))
    if rule == "none":
        return ""
    validate_cycle_rule(rule, ordered)
    match = re.fullmatch(r"advent-cycle:(\d{4}):([a-z0-9._-]+)", rule)
    if not ordered:
        raise LectionaryCalendarError("The edition cycle rule is unsupported or has no cycles.")
    anchor_year, anchor_key = int(match.group(1)), match.group(2)
    keys = [str(item[0]).casefold() for item in ordered if bool(item[3])]
    if anchor_key not in keys:
        raise LectionaryCalendarError("The cycle anchor key is not active in this edition.")
    church_year = value.year if value >= advent_start(value.year) else value.year - 1
    return keys[(keys.index(anchor_key) + church_year - anchor_year) % len(keys)]


class LectionaryCalendarResolver:
    """Return every explicit matching Proper and never choose precedence silently."""

    def resolve(self, civil_date, edition, cycles, propers):
        """Resolve candidate dictionaries for one edition and civil date."""
        if not isinstance(civil_date, date):
            raise LectionaryCalendarError("The service date is required.")
        if str(edition.get("resolver_version") or "1") != "1":
            raise LectionaryCalendarError("The edition requires an unsupported resolver version.")
        cycle = cycle_for_date(civil_date, edition.get("cycle_rule"), cycles)
        candidates = []
        for proper in propers:
            proper_cycle = str(proper.get("cycle_key") or "").casefold()
            if proper_cycle and proper_cycle != cycle:
                continue
            rule = str(proper.get("calendar_rule") or "").strip()
            if not rule or rule_date(rule, civil_date.year) != civil_date:
                continue
            candidates.append(LectionaryCandidate(
                int(proper["id"]), str(proper["proper_key"]),
                str(proper["liturgical_date"]), str(proper.get("season") or ""),
                proper_cycle, rule,
                f"Matched {rule}; edition cycle {cycle or 'none'}.",
            ))
        return candidates


class LectionaryCalendarRepository:
    """Load one installed edition and return its explicit date candidates."""

    def __init__(self, connection, resolver=None):
        self.connection = portable_connection(connection)
        self.resolver = resolver or LectionaryCalendarResolver()

    def _all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def resolve(self, edition_id, civil_date):
        """Resolve an active installed edition without interpreting its display names."""
        rows = self._all(
            "SELECT ResolverVersion,CycleRule,ValidFrom,ValidThrough FROM tblLectionaryEdition "
            "WHERE ID=? AND IsActive=1", (edition_id,),
        )
        if not rows:
            raise LectionaryCalendarError("The selected lectionary edition is unavailable.")
        resolver_version, cycle_rule, valid_from, valid_through = rows[0]
        if ((valid_from and civil_date < valid_from)
                or (valid_through and civil_date > valid_through)):
            return []
        cycles = self._all(
            "SELECT CycleCode,DisplayName,Sequence,IsActive FROM tblLectionaryCycle "
            "WHERE LectionaryEditionID=? ORDER BY Sequence,ID", (edition_id,),
        )
        proper_rows = self._all(
            "SELECT p.ID,p.ProperKey,p.LiturgicalDate,COALESCE(p.Season,''),"
            "COALESCE(c.CycleCode,''),p.CalendarRule FROM tblPropers p "
            "LEFT JOIN tblLectionaryCycle c ON c.ID=p.LectionaryCycleID "
            "WHERE p.LectionaryEditionID=? AND p.IsActive=1 AND p.CalendarRule IS NOT NULL "
            "ORDER BY p.Sort,p.ID", (edition_id,),
        )
        propers = [{
            "id": row[0], "proper_key": row[1], "liturgical_date": row[2],
            "season": row[3], "cycle_key": row[4], "calendar_rule": row[5],
        } for row in proper_rows]
        return self.resolver.resolve(
            civil_date,
            {"resolver_version": resolver_version, "cycle_rule": cycle_rule},
            cycles, propers,
        )
