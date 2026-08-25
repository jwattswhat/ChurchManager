"""Validation and persistence for ChurchManager's small Church event list."""

from __future__ import annotations

from datetime import datetime
import re


class CalendarEventError(ValueError):
    """Raised when an event violates the approved calendar boundary."""


class CalendarEventConflictError(CalendarEventError):
    """Raised when an event changed after it was displayed."""


class MariaDBCalendarEventRepository:
    """Store public-safe standalone events with optimistic concurrency."""

    def __init__(self, connection):
        self.connection = connection
        self.marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    @staticmethod
    def _rows(cursor):
        names = [column[0] for column in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]

    def churches(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT ID,Church FROM tblChurch WHERE ID>0 ORDER BY Church")
            return cursor.fetchall()
        finally: cursor.close()

    def events(self, church_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT ID id,ChurchID church_id,EventKey event_key,Title title,Description description,"
                          "StartDateTime starts_at,EndDateTime ends_at,AllDay all_day,TimeZoneName time_zone,"
                          "Location location,OwnerType owner_type,OwnerID owner_id,Status status,"
                          "CalendarEligible calendar_eligible,Version version FROM tblChurchEvent "
                          "WHERE ChurchID=? ORDER BY StartDateTime DESC,ID DESC", (church_id,))
            return self._rows(cursor)
        finally: cursor.close()

    def create(self, values):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "INSERT INTO tblChurchEvent (ChurchID,EventKey,Title,Description,StartDateTime,"
                          "EndDateTime,AllDay,TimeZoneName,Location,Status,CalendarEligible,CreatedByUserID,UpdatedByUserID) "
                          "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                              values["church_id"], values["event_key"], values["title"], values["description"],
                              values["starts_at"], values["ends_at"], values["all_day"], values["time_zone"],
                              values["location"], values["status"], values["calendar_eligible"],
                              values["user_id"], values["user_id"],
                          ))
            event_id = cursor.lastrowid; self._audit(cursor, values["user_id"], "CHURCH_EVENT_CREATED", event_id)
            self.connection.commit(); return event_id
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def update(self, values):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "UPDATE tblChurchEvent SET Title=?,Description=?,StartDateTime=?,EndDateTime=?,"
                          "AllDay=?,TimeZoneName=?,Location=?,Status=?,CalendarEligible=?,UpdatedByUserID=?,Version=Version+1 "
                          "WHERE ID=? AND ChurchID=? AND Version=?", (
                              values["title"], values["description"], values["starts_at"], values["ends_at"],
                              values["all_day"], values["time_zone"], values["location"], values["status"],
                              values["calendar_eligible"], values["user_id"], values["id"],
                              values["church_id"], values["version"],
                          ))
            if cursor.rowcount != 1: raise CalendarEventConflictError("This event changed. Reopen it and try again.")
            self._audit(cursor, values["user_id"], "CHURCH_EVENT_UPDATED", values["id"])
            self.connection.commit(); return True
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def _audit(self, cursor, user_id, action, event_id):
        self._execute(cursor, "INSERT INTO tblSecurityAuditEvent (UserID,Action,EntityType,EntityID) VALUES (?,?,?,?)",
                      (user_id, action, "ChurchEvent", str(event_id)))


class CalendarEventService:
    """Apply permissions and the safe standalone-event contract."""

    STATUSES = {"PLANNED", "CONFIRMED", "CANCELLED", "COMPLETED"}

    def __init__(self, repository, session, authorization):
        self.repository = repository; self.session = session; self.authorization = authorization

    def events(self, church_id):
        self.authorization.require("calendar.view", "view Church events")
        return self.repository.events(_positive(church_id, "church"))

    def save(self, values):
        self.authorization.require("calendar.events.manage", "maintain Church events")
        item = dict(values or {}); starts = _datetime(item.get("starts_at"), "start")
        ends = None if item.get("ends_at") in (None, "") else _datetime(item["ends_at"], "end")
        if ends and ends < starts: raise CalendarEventError("The event end cannot precede its start.")
        status = str(item.get("status") or "PLANNED").upper()
        if status not in self.STATUSES: raise CalendarEventError("Choose a valid event status.")
        normalized = {
            "church_id": _positive(item.get("church_id"), "church"),
            "event_key": str(item.get("event_key") or "").strip(),
            "title": _text(item.get("title"), "Title", 150, True),
            "description": _text(item.get("description"), "Description", 1000, False),
            "starts_at": starts, "ends_at": ends, "all_day": bool(item.get("all_day")),
            "time_zone": _text(item.get("time_zone") or "America/Chicago", "Time zone", 64, True),
            "location": _text(item.get("location"), "Location", 150, False),
            "status": status, "calendar_eligible": bool(item.get("calendar_eligible")),
            "user_id": self.session.user_id,
        }
        if item.get("id"):
            normalized.update(id=_positive(item["id"], "event"), version=_positive(item.get("version"), "version"))
            return self.repository.update(normalized)
        normalized["event_key"] = normalized["event_key"] or self._new_key(normalized["title"], starts)
        return self.repository.create(normalized)

    def _new_key(self, title, starts):
        slug = re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")[:36] or "event"
        return f"{starts:%Y%m%d%H%M}-{slug}"


def _positive(value, label):
    try: result = int(value)
    except (TypeError, ValueError) as error: raise CalendarEventError(f"A valid {label} is required.") from error
    if result <= 0: raise CalendarEventError(f"A valid {label} is required.")
    return result


def _datetime(value, label):
    if isinstance(value, datetime): return value.replace(microsecond=0)
    try: return datetime.fromisoformat(str(value)).replace(microsecond=0)
    except (TypeError, ValueError) as error: raise CalendarEventError(f"The event {label} is invalid.") from error


def _text(value, label, length, required):
    result = str(value or "").strip()
    if required and not result: raise CalendarEventError(f"{label} is required.")
    if len(result) > length: raise CalendarEventError(f"{label} may not exceed {length} characters.")
    return result or None
