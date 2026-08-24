"""Authorization and validation boundary for Group meetings and attendance."""

from __future__ import annotations

from datetime import date, datetime

from group_service import GroupValidationError, _identifier, _optional_text, _required_text


class GroupMeetingService:
    """Apply privacy, congregation, lifecycle, and attendance rules."""

    STATUSES = {"SCHEDULED", "HELD", "CANCELLED", "RESCHEDULED"}
    MODES = {"ROSTER", "HEADCOUNT", "BOTH"}
    ATTENDANCE_STATUSES = {"PRESENT", "ABSENT", "EXCUSED", "UNKNOWN"}

    def __init__(self, repository, group_service, session, authorization):
        self.repository = repository
        self.groups = group_service
        self.session = session
        self.authorization = authorization

    def meetings(self, group_id):
        """List meetings only after the Group itself is authorized."""
        self.authorization.require("groups.meetings.view", "view Group meetings")
        group = self.groups.group(group_id)
        if group is None: raise GroupValidationError("The selected Group is unavailable.")
        return self.repository.meetings(group["id"])

    def create_meeting(self, group_id, values):
        """Create a meeting for an active or draft authorized Group."""
        self.authorization.require("groups.meetings.edit", "create a Group meeting")
        group = self.groups.group(group_id)
        if group is None: raise GroupValidationError("The selected Group is unavailable.")
        if group["status"] in {"INACTIVE", "CLOSED"}:
            raise GroupValidationError("New meetings require a Draft or Active Group.")
        item = dict(values or {})
        starts = _datetime(item.get("starts_at"), "meeting start")
        ends = None if item.get("ends_at") in (None, "") else _datetime(item["ends_at"], "meeting end")
        if ends and ends < starts: raise GroupValidationError("The meeting end cannot precede its start.")
        status = str(item.get("status") or "SCHEDULED").upper()
        mode = str(item.get("attendance_mode") or "ROSTER").upper()
        if status not in self.STATUSES or status == "RESCHEDULED":
            raise GroupValidationError("A new meeting must be Scheduled, Held, or Cancelled.")
        if mode not in self.MODES: raise GroupValidationError("Choose a valid attendance mode.")
        count = _count(item.get("total_head_count"))
        return self.repository.create_meeting({
            "group_id": group["id"], "starts_at": starts, "ends_at": ends,
            "title": _required_text(item.get("title"), "Meeting title", 150),
            "location": _optional_text(item.get("location"), 150), "status": status,
            "attendance_mode": mode, "total_head_count": count,
            "notes": _optional_text(item.get("notes"), 1000), "user_id": self.session.user_id,
        })

    def attendance_rows(self, meeting_id):
        """Combine the effective roster with saved guest and attendance status."""
        self.authorization.require("groups.attendance.view", "view Group attendance")
        meeting = self._meeting(meeting_id)
        roster = self.repository.roster_for_date(
            meeting["group_id"], meeting["id"], meeting["starts_at"].date()
        )
        saved = {row["person_id"]: row for row in self.repository.attendance(meeting["id"])}
        result = []
        for person in roster:
            attendance = saved.get(person["person_id"], {})
            result.append({**person, "attendance_status": attendance.get("attendance_status", "UNKNOWN")})
        return meeting, result

    def add_guest(self, meeting_id, person_id):
        """Add an existing same-congregation Person without creating membership."""
        self.authorization.require("groups.attendance.record", "add a Group meeting guest")
        meeting = self._meeting(meeting_id)
        person_id = _identifier(person_id, "person")
        people = self.repository.available_people(meeting["church_id"])
        if person_id not in {row["id"] for row in people}:
            raise GroupValidationError("The guest and Group must belong to the same church.")
        return self.repository.add_guest(meeting["id"], person_id, self.session.user_id)

    def record_attendance(self, meeting_id, entries, total_head_count=None):
        """Record one supported status per displayed Person and optional head count."""
        self.authorization.require("groups.attendance.record", "record Group attendance")
        meeting = self._meeting(meeting_id)
        valid_people = {row["person_id"] for row in self.repository.roster_for_date(
            meeting["group_id"], meeting["id"], meeting["starts_at"].date()
        )}
        normalized = []
        for person_id, status in entries:
            person_id = _identifier(person_id, "person")
            status = str(status or "UNKNOWN").upper()
            if person_id not in valid_people: raise GroupValidationError("Attendance contains an unavailable Person.")
            if status not in self.ATTENDANCE_STATUSES: raise GroupValidationError("Choose a valid attendance status.")
            normalized.append((person_id, status))
        if len({person_id for person_id, _status in normalized}) != len(normalized):
            raise GroupValidationError("A Person may be recorded only once per meeting.")
        return self.repository.replace_attendance(meeting, normalized, _count(total_head_count), self.session.user_id)

    def available_guests(self, meeting_id):
        """Return same-congregation people not already displayed for the meeting."""
        meeting, rows = self.attendance_rows(meeting_id)
        shown = {row["person_id"] for row in rows}
        return [row for row in self.repository.available_people(meeting["church_id"]) if row["id"] not in shown]

    def _meeting(self, meeting_id):
        meeting = self.repository.meeting(_identifier(meeting_id, "meeting"))
        if meeting is None: raise GroupValidationError("The selected meeting is unavailable.")
        self.groups.group(meeting["group_id"])
        return meeting


def _datetime(value, label):
    if isinstance(value, datetime): return value.replace(microsecond=0)
    try: return datetime.fromisoformat(str(value)).replace(microsecond=0)
    except (TypeError, ValueError) as error: raise GroupValidationError(f"The {label} is invalid.") from error


def _count(value):
    if value in (None, ""): return None
    try: result = int(value)
    except (TypeError, ValueError) as error: raise GroupValidationError("The total head count must be a whole number.") from error
    if result < 0: raise GroupValidationError("The total head count cannot be negative.")
    return result
