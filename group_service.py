"""Authorization and validation boundary for congregational Groups."""

from __future__ import annotations

from datetime import date
import re


class GroupValidationError(ValueError):
    """Raised when Group or membership data violates the approved contract."""


class GroupService:
    """Authorize Group operations before invoking parameterized persistence."""

    STATUSES = {"DRAFT", "ACTIVE", "INACTIVE", "CLOSED"}
    PRIVACY = {"STANDARD", "RESTRICTED"}

    def __init__(self, repository, session, authorization):
        self.repository = repository
        self.session = session
        self.authorization = authorization

    def list_groups(self, church_id, status=None):
        """Return only Groups visible under standard and restricted permissions."""

        self.authorization.require("groups.view", "view Groups")
        return self.repository.list_groups(
            _identifier(church_id, "church"), status,
            self.authorization.has_permission("groups.view_restricted"),
        )

    def create_group(self, values):
        """Validate and create one Group with stable identity and audit attribution."""

        self.authorization.require("groups.edit", "create a Group")
        item = _group_values(values)
        if item["privacy_class"] == "RESTRICTED":
            self.authorization.require("groups.edit_restricted", "create a restricted Group")
        item["created_by_user_id"] = self.session.user_id
        return self.repository.create_group(item)

    def update_group(self, group_id, values, version):
        """Update a Group after authorizing its current privacy class and changes."""

        self.authorization.require("groups.edit", "update a Group")
        current = self.repository.group(_identifier(group_id, "Group"))
        if current is None:
            raise GroupValidationError("The selected Group is unavailable.")
        if current["privacy_class"] == "RESTRICTED":
            self.authorization.require("groups.edit_restricted", "update a restricted Group")
        item = _group_values({**current, **dict(values or {})})
        if item["privacy_class"] == "RESTRICTED":
            self.authorization.require("groups.edit_restricted", "make a Group restricted")
        item["updated_by_user_id"] = self.session.user_id
        return self.repository.update_group(current, item, _identifier(version, "version"))

    def add_membership(self, group_id, person_id, start_date, end_date=None, notes=None):
        """Create a same-Church, non-overlapping membership term."""

        self.authorization.require("groups.membership.edit", "add Group membership")
        group = self._editable_group(group_id)
        person_id = _identifier(person_id, "person")
        if self.repository.person_church_id(person_id) != group["church_id"]:
            raise GroupValidationError("The Person and Group must belong to the same church.")
        start_date = _date(start_date, "start date")
        end_date = None if end_date in (None, "") else _date(end_date, "end date")
        if end_date is not None and end_date < start_date:
            raise GroupValidationError("The membership end date cannot precede its start date.")
        if self.repository.membership_overlaps(group["id"], person_id, start_date, end_date):
            raise GroupValidationError("This Person already has an overlapping membership term.")
        return self.repository.create_membership({
            "group_id": group["id"], "person_id": person_id,
            "start_date": start_date, "end_date": end_date,
            "notes": _optional_text(notes, 500), "user_id": self.session.user_id,
        })

    def _editable_group(self, group_id):
        group = self.repository.group(_identifier(group_id, "Group"))
        if group is None:
            raise GroupValidationError("The selected Group is unavailable.")
        if group["privacy_class"] == "RESTRICTED":
            self.authorization.require("groups.edit_restricted", "edit restricted Group membership")
        return group


def _group_values(values):
    values = dict(values or {})
    status = str(values.get("status") or "DRAFT").strip().upper()
    privacy = str(values.get("privacy_class") or "STANDARD").strip().upper()
    if status not in GroupService.STATUSES:
        raise GroupValidationError("Choose a valid Group status.")
    if privacy not in GroupService.PRIVACY:
        raise GroupValidationError("Choose a valid Group privacy class.")
    start = None if values.get("start_date") in (None, "") else _date(values["start_date"], "start date")
    end = None if values.get("end_date") in (None, "") else _date(values["end_date"], "end date")
    if end is not None and start is not None and end < start:
        raise GroupValidationError("The Group end date cannot precede its start date.")
    if status == "CLOSED" and end is None:
        raise GroupValidationError("A closed Group requires an end date.")
    key = str(values.get("group_key") or "").strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key):
        raise GroupValidationError("Group key must use lowercase letters, numbers, and single hyphens.")
    return {
        "church_id": _identifier(values.get("church_id"), "church"),
        "group_key": key, "name": _required_text(values.get("name"), "Group name", 150),
        "group_type_id": _identifier(values.get("group_type_id"), "Group type"),
        "description": _optional_text(values.get("description"), 500),
        "status": status, "start_date": start, "end_date": end,
        "privacy_class": privacy, "notes": _optional_text(values.get("notes"), 1000),
    }


def _identifier(value, label):
    try: result = int(value)
    except (TypeError, ValueError) as error: raise GroupValidationError(f"A valid {label} ID is required.") from error
    if result <= 0: raise GroupValidationError(f"A valid {label} ID is required.")
    return result


def _date(value, label):
    if isinstance(value, date): return value
    try: return date.fromisoformat(str(value))
    except (TypeError, ValueError) as error: raise GroupValidationError(f"The {label} is invalid.") from error


def _required_text(value, label, limit):
    text = str(value or "").strip()
    if not text: raise GroupValidationError(f"{label} is required.")
    if len(text) > limit: raise GroupValidationError(f"{label} cannot exceed {limit} characters.")
    return text


def _optional_text(value, limit):
    text = str(value or "").strip()
    if len(text) > limit: raise GroupValidationError(f"Text cannot exceed {limit} characters.")
    return text or None
