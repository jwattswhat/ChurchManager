"""Service-layer authorization and validation for pastoral-care operations."""

from __future__ import annotations

from datetime import date, datetime
import re


class PastoralCareValidationError(ValueError):
    """Raised when safe operational pastoral-care data is incomplete or invalid."""


class PastoralCareService:
    """Authorize every pastoral-care operation before invoking its repository.

    The repository is responsible for parameterized persistence and for writing
    the corresponding safe audit event in the same transaction. Restricted-note
    encryption is intentionally a separate service and is not accepted here.
    """

    SOURCES = {
        "MANUAL", "ATTENDANCE_FOLLOWUP", "PRAYER_REQUEST",
        "HOSPITAL_NOTICE", "LIFE_EVENT", "OTHER",
    }
    PRIORITIES = {"NORMAL", "URGENT"}
    RESULTS = {"COMPLETED", "ATTEMPTED", "DEFERRED", "NOT_NEEDED"}
    ACTION_TYPES = {"CALL", "VISIT", "CARD", "MEAL", "EMAIL", "PRAYER", "REFERRAL", "OTHER"}
    STATUSES = {"OPEN", "WAITING", "COMPLETED", "CLOSED_NOT_NEEDED"}

    def __init__(self, repository, session, authorization):
        self.repository = repository
        self.session = session
        self.authorization = authorization

    def work_list(self, scope="assigned"):
        """Return the authorized operational work list without restricted notes."""

        scope = str(scope or "assigned").strip().casefold()
        if scope == "all":
            self.authorization.require("pastoral.care.view.all", "view all pastoral care")
            return self.repository.work_list(assigned_user_id=None)
        self.authorization.require(
            "pastoral.care.view.assigned", "view assigned pastoral care"
        )
        return self.repository.work_list(assigned_user_id=self.session.user_id)

    def need(self, care_need_id):
        """Return one operational record only when its assignment is authorized."""

        record = self.repository.need(_identifier(care_need_id, "care need"))
        self._require_record_access(record)
        return record

    def history(self, care_need_id):
        """Return safe action history after authorizing its care record."""

        record = self.need(care_need_id)
        return record, self.repository.history(record["id"])

    def choices(self):
        """Return maintained editor choices after pastoral access is confirmed."""

        if not (
            self.authorization.has_permission("pastoral.care.create")
            or self.authorization.has_permission("pastoral.care.assign")
        ):
            self.authorization.require("pastoral.care.view.all", "load pastoral care choices")
        return self.repository.choices()

    def create_need(self, values):
        """Validate and create a minimum-necessary care need."""

        self.authorization.require("pastoral.care.create", "create pastoral care")
        values = dict(values or {})
        church_id = None
        church_name = str(values.get("church_name") or "").strip()
        if church_name:
            church_id = self.repository.church_id_for_name(church_name)
        if church_id is None:
            church_id = values.get("church_id")
        if church_id in (None, ""):
            church_id = self.repository.default_church_id()
        values["church_id"] = _identifier(church_id, "church")
        subjects = [
            bool(values.get("person_id")), bool(values.get("family_id")),
            bool(str(values.get("display_subject") or "").strip()),
        ]
        if sum(subjects) != 1:
            raise PastoralCareValidationError(
                "Choose exactly one person, family, or display subject."
            )
        values["category"] = _required_text(values.get("category"), "Category", 100)
        values["source"] = _choice(values.get("source", "MANUAL"), self.SOURCES, "source")
        values["priority"] = _choice(values.get("priority", "NORMAL"), self.PRIORITIES, "priority")
        values["opened_date"] = _date(values.get("opened_date", date.today()), "opened date")
        values["safe_summary"] = _optional_text(values.get("safe_summary"), 500)
        values["created_by_user_id"] = self.session.user_id
        if values.get("assigned_user_id") not in (None, self.session.user_id):
            self.authorization.require("pastoral.care.assign", "assign pastoral care")
        return self.repository.create_need(values)

    def assign(self, care_need_id, assigned_user_id, version):
        """Assign or unassign a care need under the dedicated permission."""

        self.authorization.require("pastoral.care.assign", "assign pastoral care")
        record = self.repository.need(_identifier(care_need_id, "care need"))
        self._require_record_access(record, allow_assigner=True)
        assignee = None if assigned_user_id is None else _identifier(assigned_user_id, "user")
        return self.repository.assign(record, assignee, _identifier(version, "version"), self.session.user_id)

    def record_action(self, care_need_id, values):
        """Record a non-sensitive action for an authorized care need."""

        self.authorization.require("pastoral.care.update", "update pastoral care")
        record = self.repository.need(_identifier(care_need_id, "care need"))
        self._require_record_access(record)
        values = dict(values or {})
        values["action_type"] = _choice(values.get("action_type"), self.ACTION_TYPES, "action type")
        values["result"] = _choice(values.get("result"), self.RESULTS, "result")
        action_at = values.get("action_datetime", datetime.now())
        if not isinstance(action_at, datetime):
            raise PastoralCareValidationError("Action date and time is invalid.")
        values["action_datetime"] = action_at
        values["safe_outcome"] = _optional_text(values.get("safe_outcome"), 500)
        values["caregiver_user_id"] = self.session.user_id
        values["created_by_user_id"] = self.session.user_id
        return self.repository.record_action(record, values)

    def change_status(self, care_need_id, status, version):
        """Complete, reopen, wait, or close a care need with explicit authority."""

        self.authorization.require("pastoral.care.close", "change pastoral care status")
        record = self.repository.need(_identifier(care_need_id, "care need"))
        self._require_record_access(record)
        normalized = _choice(status, self.STATUSES, "status")
        return self.repository.change_status(
            record, normalized, _identifier(version, "version"), self.session.user_id
        )

    def _require_record_access(self, record, allow_assigner=False):
        if record is None:
            raise PastoralCareValidationError("The pastoral care record is unavailable.")
        if self.authorization.has_permission("pastoral.care.view.all"):
            return
        assigned_user_id = (
            record.get("assigned_user_id") if isinstance(record, dict)
            else getattr(record, "assigned_user_id", None)
        )
        if assigned_user_id == self.session.user_id and self.authorization.has_permission(
            "pastoral.care.view.assigned"
        ):
            return
        if allow_assigner and self.authorization.has_permission("pastoral.care.assign"):
            return
        self.authorization.require("pastoral.care.view.all", "access this pastoral care record")


def _identifier(value, label):
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise PastoralCareValidationError("A valid {} ID is required.".format(label)) from error
    if result <= 0:
        raise PastoralCareValidationError("A valid {} ID is required.".format(label))
    return result


def _choice(value, choices, label):
    normalized = re.sub(r"[\s-]+", "_", str(value or "").strip().upper())
    if normalized not in choices:
        raise PastoralCareValidationError("The pastoral care {} is invalid.".format(label))
    return normalized


def _required_text(value, label, maximum):
    result = str(value or "").strip()
    if not result:
        raise PastoralCareValidationError("{} is required.".format(label))
    if len(result) > maximum:
        raise PastoralCareValidationError("{} is too long.".format(label))
    return result


def _optional_text(value, maximum):
    result = str(value or "").strip() or None
    if result and len(result) > maximum:
        raise PastoralCareValidationError("The safe operational summary is too long.")
    return result


def _date(value, label):
    if not isinstance(value, date) or isinstance(value, datetime):
        raise PastoralCareValidationError("The pastoral care {} is invalid.".format(label))
    return value
