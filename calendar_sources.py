"""Privacy-safe provider-neutral calendar descriptors and source adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from event_schedule_rules import event_occurrences


class CalendarSourceError(ValueError):
    """Raised when a calendar source violates the public-safe contract."""


@dataclass(frozen=True)
class CalendarEventDescriptor:
    """Bounded event data that may be handed to an external calendar adapter."""

    source_type: str
    source_id: int
    church_id: int
    uid: str
    title: str
    starts_at: datetime
    ends_at: datetime | None = None
    all_day: bool = False
    time_zone: str = "America/Chicago"
    location: str = ""
    description: str = ""
    status: str = "CONFIRMED"
    version: str = "1"

    def __post_init__(self):
        if self.source_type not in {"CHURCH_EVENT", "WORSHIP_SERVICE", "GROUP_MEETING"}:
            raise CalendarSourceError("The calendar source type is not approved.")
        if int(self.source_id) <= 0 or int(self.church_id) <= 0:
            raise CalendarSourceError("Calendar descriptors require positive source and church IDs.")
        if not self.uid or not self.title.strip():
            raise CalendarSourceError("Calendar descriptors require a stable UID and title.")
        if self.ends_at is not None and self.ends_at < self.starts_at:
            raise CalendarSourceError("A calendar event cannot end before it starts.")
        if self.status not in {"CONFIRMED", "CANCELLED"}:
            raise CalendarSourceError("Calendar descriptors expose only confirmed or cancelled status.")


class MariaDBCalendarSourceRepository:
    """Read only fields explicitly approved for calendar publication."""

    def __init__(self, connection):
        self.connection = connection
        self.marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"

    def _all(self, sql, values):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql.replace("?", self.marker), values)
            names = [column[0] for column in cursor.description]
            return [dict(zip(names, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def church_events(self, church_id, through_date):
        return self._all(
            "SELECT ID id,ChurchID church_id,Title title,COALESCE(Description,'') description,"
            "StartDateTime starts_at,EndDateTime ends_at,AllDay all_day,TimeZoneName time_zone,"
            "COALESCE(Location,'') location,Status status,ScheduleRule schedule_rule,Version version "
            "FROM tblChurchEvent WHERE ChurchID=? AND CalendarEligible=1 "
            "AND Status IN ('PLANNED','CONFIRMED','CANCELLED') AND DATE(StartDateTime)<=?",
            (church_id, through_date),
        )

    def worship_services(self, church_id, from_date, through_date):
        return self._all(
            "SELECT ID id,ChurchID church_id,DateTime starts_at,COALESCE(Location,'') location,"
            "COALESCE(NULLIF(TRIM(LiturgicalDate),''),'Worship Service') title "
            "FROM tblService WHERE ChurchID=? AND DATE(DateTime) BETWEEN ? AND ? ORDER BY DateTime,ID",
            (church_id, from_date, through_date),
        )

    def group_meetings(self, church_id, from_date, through_date):
        return self._all(
            "SELECT m.ID id,g.ChurchID church_id,m.StartsAt starts_at,m.EndsAt ends_at,m.Title title,"
            "COALESCE(m.Location,'') location,m.Status status,m.Version version "
            "FROM tblGroupMeeting m JOIN tblGroup g ON g.ID=m.GroupID "
            "WHERE g.ChurchID=? AND g.PrivacyClass='STANDARD' "
            "AND DATE(m.StartsAt) BETWEEN ? AND ? AND m.Status<>'RESCHEDULED' ORDER BY m.StartsAt,m.ID",
            (church_id, from_date, through_date),
        )


class CalendarSourceService:
    """Authorize sources and translate them into the common safe contract."""

    def __init__(self, repository, authorization):
        self.repository = repository
        self.authorization = authorization

    def descriptors(self, source_type, church_id, from_date, through_date):
        self.authorization.require("calendar.view", "view calendar information")
        source = str(source_type or "").upper()
        church_id = _positive(church_id, "church")
        start, end = _date(from_date, "from date"), _date(through_date, "through date")
        if end < start:
            raise CalendarSourceError("The through date cannot precede the from date.")
        if source == "CHURCH_EVENT":
            return self._church_events(church_id, start, end)
        if source == "WORSHIP_SERVICE":
            self.authorization.require("worship.manage", "view Worship Services")
            return self._worship(church_id, start, end)
        if source == "GROUP_MEETING":
            self.authorization.require("groups.view", "view Groups")
            self.authorization.require("groups.meetings.view", "view Group meetings")
            return self._groups(church_id, start, end)
        raise CalendarSourceError("The requested calendar source is not approved.")

    def _church_events(self, church_id, start, end):
        result = []
        for row in self.repository.church_events(church_id, end):
            first = row["starts_at"]
            occurrence_start = max(start, first.date())
            duration = row["ends_at"] - first if row.get("ends_at") else None
            maximum_occurrences = (end - occurrence_start).days + 1
            for occurrence in event_occurrences(row["schedule_rule"], occurrence_start, maximum_occurrences):
                if occurrence > end:
                    break
                if occurrence < first.date():
                    continue
                begins = datetime.combine(occurrence, first.time())
                result.append(CalendarEventDescriptor(
                    "CHURCH_EVENT", row["id"], row["church_id"],
                    f"event-{row['id']}-{occurrence:%Y%m%d}@churchmanager.local",
                    row["title"], begins, begins + duration if duration else None,
                    bool(row["all_day"]), row["time_zone"], row["location"], row["description"],
                    "CANCELLED" if row["status"] == "CANCELLED" else "CONFIRMED", str(row["version"]),
                ))
        return result

    def _worship(self, church_id, start, end):
        return [CalendarEventDescriptor(
            "WORSHIP_SERVICE", row["id"], row["church_id"],
            f"worship-{row['id']}@churchmanager.local", row["title"], row["starts_at"],
            location=row["location"], version=row["starts_at"].isoformat(),
        ) for row in self.repository.worship_services(church_id, start, end)]

    def _groups(self, church_id, start, end):
        return [CalendarEventDescriptor(
            "GROUP_MEETING", row["id"], row["church_id"],
            f"group-meeting-{row['id']}@churchmanager.local", row["title"], row["starts_at"],
            row["ends_at"], location=row["location"],
            status="CANCELLED" if row["status"] == "CANCELLED" else "CONFIRMED",
            version=str(row["version"]),
        ) for row in self.repository.group_meetings(church_id, start, end)]


def _positive(value, label):
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise CalendarSourceError(f"A valid {label} is required.") from error
    if result <= 0:
        raise CalendarSourceError(f"A valid {label} is required.")
    return result


def _date(value, label):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError) as error:
        raise CalendarSourceError(f"The {label} is invalid.") from error
