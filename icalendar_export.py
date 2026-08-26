"""Standards-based iCalendar serialization for approved calendar descriptors."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from calendar_sources import CalendarEventDescriptor


class ICalendarExportError(ValueError):
    """Raised when an iCalendar export cannot be created safely."""


def _escape(value):
    return (str(value or "").replace("\\", "\\\\").replace("\r\n", "\\n")
            .replace("\r", "\\n").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;"))


def _fold(line, limit=75):
    """Fold one content line without splitting a UTF-8 character."""
    pieces, current = [], ""
    for character in line:
        candidate = current + character
        allowance = limit if not pieces else limit - 1
        if current and len(candidate.encode("utf-8")) > allowance:
            pieces.append(current); current = character
        else:
            current = candidate
    pieces.append(current)
    return "\r\n ".join(pieces)


def _event_lines(event, stamp):
    lines = ["BEGIN:VEVENT", f"UID:{event.uid}", f"DTSTAMP:{stamp:%Y%m%dT%H%M%SZ}"]
    if event.all_day:
        lines.append(f"DTSTART;VALUE=DATE:{event.starts_at:%Y%m%d}")
        end_date = event.ends_at.date() if event.ends_at else event.starts_at.date() + timedelta(days=1)
        if end_date <= event.starts_at.date(): end_date = event.starts_at.date() + timedelta(days=1)
        lines.append(f"DTEND;VALUE=DATE:{end_date:%Y%m%d}")
    else:
        lines.append(f"DTSTART;TZID={event.time_zone}:{event.starts_at:%Y%m%dT%H%M%S}")
        if event.ends_at:
            lines.append(f"DTEND;TZID={event.time_zone}:{event.ends_at:%Y%m%dT%H%M%S}")
    lines.extend((f"SUMMARY:{_escape(event.title)}", f"STATUS:{event.status}"))
    if event.location: lines.append(f"LOCATION:{_escape(event.location)}")
    if event.description: lines.append(f"DESCRIPTION:{_escape(event.description)}")
    lines.extend((f"X-CHURCHMANAGER-SOURCE:{event.source_type}",
                  f"X-CHURCHMANAGER-SOURCE-ID:{event.source_id}",
                  f"X-CHURCHMANAGER-VERSION:{_escape(event.version)}", "END:VEVENT"))
    return lines


def serialize_calendar(events, product_id="-//ChurchManager//Calendar Export//EN", now=None):
    """Serialize approved descriptors to RFC 5545-style CRLF text."""
    rows = list(events or [])
    if not rows: raise ICalendarExportError("There are no eligible events to export.")
    if any(not isinstance(row, CalendarEventDescriptor) for row in rows):
        raise ICalendarExportError("Only approved calendar descriptors may be exported.")
    stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(tzinfo=None, microsecond=0)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:{product_id}", "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    for event in sorted(rows, key=lambda item: (item.starts_at, item.uid)):
        lines.extend(_event_lines(event, stamp))
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"


class ICalendarExportService:
    """Authorize and write a new portable calendar file."""

    def __init__(self, authorization): self.authorization = authorization

    def write(self, path, events, overwrite=False):
        self.authorization.require("calendar.export", "export calendar events")
        target = Path(path).expanduser()
        if target.suffix.casefold() != ".ics": target = target.with_suffix(".ics")
        if target.exists() and not overwrite:
            raise ICalendarExportError("The selected calendar file already exists.")
        target.parent.mkdir(parents=True, exist_ok=True)
        content = serialize_calendar(events)
        with target.open("w", encoding="utf-8", newline="") as stream:
            stream.write(content)
        return target
