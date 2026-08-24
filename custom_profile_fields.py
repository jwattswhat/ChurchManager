"""ChurchManager policy boundary for custom profile fields and controlled tags."""

from __future__ import annotations

import re

from JSForm.dynamic_fields import (
    DynamicFieldDescriptor, DynamicFieldError, DynamicFieldOption,
    normalize_dynamic_value,
)


class CustomProfileValidationError(ValueError):
    """Raised when custom profile metadata or values violate ChurchManager policy."""


class CustomProfileFieldService:
    """Authorize and validate church-scoped Person and Family custom data."""

    ENTITY_TYPES = {"PERSON", "FAMILY"}
    DATA_TYPES = {
        "SHORT_TEXT", "LONG_TEXT", "INTEGER", "DECIMAL", "DATE", "BOOLEAN",
        "SINGLE_CHOICE", "MULTIPLE_CHOICE",
    }
    MAX_ACTIVE_FIELDS = 25
    MAX_OPTIONS = 50
    MAX_TAGS = 25

    def __init__(self, repository, session, authorization):
        self.repository = repository
        self.session = session
        self.authorization = authorization

    def definitions(self, church_id, entity_type, include_drafts=False):
        """Return authorized definitions without revealing restricted metadata."""
        self.authorization.require("profiles.custom_fields.view", "view custom profile fields")
        restricted = self.authorization.has_permission("profiles.custom_fields.view_restricted")
        return self.repository.definitions(
            _identifier(church_id, "church"), _entity(entity_type),
            bool(include_drafts and self.authorization.has_permission("profiles.custom_fields.define")),
            restricted,
        )

    def create_definition(self, values):
        """Create one bounded Draft definition after explicit prohibited-use confirmation."""
        self.authorization.require("profiles.custom_fields.define", "define custom profile fields")
        item = _definition_values(values)
        if not bool(values.get("content_boundary_confirmed")):
            raise CustomProfileValidationError(
                "Confirm that this field will not store prohibited or already-supported information."
            )
        if self.repository.definition_key_exists(item["church_id"], item["entity_type"], item["field_key"]):
            raise CustomProfileValidationError("That custom field key is already in use.")
        item["user_id"] = self.session.user_id
        return self.repository.create_definition(item)

    def activate_definition(self, definition_id):
        """Activate a Draft only when limits and choice catalogs are complete."""
        self.authorization.require("profiles.custom_fields.define", "activate custom profile fields")
        current = self._definition(definition_id)
        if current["lifecycle_status"] != "DRAFT":
            raise CustomProfileValidationError("Only a Draft custom field can be activated.")
        if self.repository.active_definition_count(current["church_id"], current["entity_type"]) >= self.MAX_ACTIVE_FIELDS:
            raise CustomProfileValidationError(
                f"No more than {self.MAX_ACTIVE_FIELDS} active custom fields are allowed per profile type."
            )
        if current["data_type"] in {"SINGLE_CHOICE", "MULTIPLE_CHOICE"}:
            if not self.repository.options(current["id"], active_only=True):
                raise CustomProfileValidationError("Add at least one active choice before activation.")
        return self.repository.set_definition_status(current, "ACTIVE", self.session.user_id)

    def retire_definition(self, definition_id):
        """Retire a definition while preserving values and stable identity."""
        self.authorization.require("profiles.custom_fields.define", "retire custom profile fields")
        current = self._definition(definition_id)
        if current["lifecycle_status"] != "ACTIVE":
            raise CustomProfileValidationError("Only an Active custom field can be retired.")
        return self.repository.set_definition_status(current, "RETIRED", self.session.user_id)

    def add_option(self, definition_id, option_key, label):
        """Add a stable option to an unretired choice definition."""
        self.authorization.require("profiles.custom_fields.define", "define custom-field choices")
        current = self._definition(definition_id)
        if current["data_type"] not in {"SINGLE_CHOICE", "MULTIPLE_CHOICE"}:
            raise CustomProfileValidationError("Only a choice field can contain options.")
        if current["lifecycle_status"] == "RETIRED":
            raise CustomProfileValidationError("A retired custom field cannot receive new choices.")
        if len(self.repository.options(current["id"], active_only=False)) >= self.MAX_OPTIONS:
            raise CustomProfileValidationError(f"A custom field may contain at most {self.MAX_OPTIONS} choices.")
        key = _key(option_key, "Option key")
        return self.repository.create_option(
            current, key, _text(label, "Option label", 100), self.session.user_id,
        )

    def profile(self, church_id, entity_type, profile_id):
        """Return JSForm descriptors and values authorized for one profile."""
        church_id = _identifier(church_id, "church")
        entity_type = _entity(entity_type)
        profile_id = _identifier(profile_id, entity_type.lower())
        self.authorization.require("profiles.custom_fields.view", "view custom profile fields")
        if self.repository.profile_church_id(entity_type, profile_id) != church_id:
            raise CustomProfileValidationError("The selected profile is unavailable.")
        include_restricted = self.authorization.has_permission("profiles.custom_fields.view_restricted")
        rows = self.repository.profile_definitions(church_id, entity_type, profile_id, include_restricted)
        descriptors = tuple(_descriptor(row, self.repository.options(row["id"], active_only=False)) for row in rows)
        return descriptors, self.repository.profile_values(entity_type, profile_id, rows)

    def save_profile_values(self, church_id, entity_type, profile_id, proposed):
        """Validate and atomically save authorized typed values."""
        self.authorization.require("profiles.custom_fields.edit", "edit custom profile fields")
        church_id = _identifier(church_id, "church")
        entity_type = _entity(entity_type)
        profile_id = _identifier(profile_id, "profile")
        if self.repository.profile_church_id(entity_type, profile_id) != church_id:
            raise CustomProfileValidationError("The selected profile is unavailable.")
        include_restricted = self.authorization.has_permission("profiles.custom_fields.view_restricted")
        rows = self.repository.profile_definitions(
            church_id, entity_type, profile_id, include_restricted,
        )
        descriptors = tuple(
            _descriptor(row, self.repository.options(row["id"], active_only=False))
            for row in rows
        )
        by_key = {item.key: item for item in descriptors}
        rows_by_key = {item["field_key"]: item for item in rows}
        changes = {}
        for key, raw in dict(proposed or {}).items():
            descriptor = by_key.get(key)
            if descriptor is None or descriptor.readonly:
                raise CustomProfileValidationError("A custom field is unavailable for editing.")
            row = rows_by_key[key]
            if row["privacy_class"] == "RESTRICTED":
                self.authorization.require(
                    "profiles.custom_fields.edit_restricted", "edit restricted custom profile fields"
                )
            try:
                changes[row["id"]] = (row, normalize_dynamic_value(descriptor, raw))
            except DynamicFieldError as error:
                raise CustomProfileValidationError(str(error)) from error
        return self.repository.save_profile_values(
            entity_type, profile_id, changes, self.session.user_id,
        )

    def create_tag(self, values):
        """Create one controlled profile tag in the selected church."""
        self.authorization.require("profiles.tags.define", "define profile tags")
        item = dict(values or {})
        item = {
            "church_id": _identifier(item.get("church_id"), "church"),
            "entity_type": _entity(item.get("entity_type")),
            "tag_key": _key(item.get("tag_key"), "Tag key"),
            "label": _text(item.get("label"), "Tag label", 100),
            "description": _optional_text(item.get("description"), 500),
            "privacy_class": str(item.get("privacy_class") or "STANDARD").upper(),
            "display_color": _optional_text(item.get("display_color"), 20),
            "display_order": max(0, int(item.get("display_order") or 0)),
            "user_id": self.session.user_id,
        }
        if item["privacy_class"] not in {"STANDARD", "RESTRICTED"}:
            raise CustomProfileValidationError("Choose a valid privacy class.")
        if item["display_color"] and not re.fullmatch(r"#[0-9A-Fa-f]{6}", item["display_color"]):
            raise CustomProfileValidationError("Display color must use #RRGGBB format.")
        if self.repository.tag_key_exists(item["church_id"], item["entity_type"], item["tag_key"]):
            raise CustomProfileValidationError("That tag key is already in use.")
        return self.repository.create_tag(item)

    def set_tag_active(self, tag_id, active):
        """Activate or retire a controlled tag without deleting history."""
        self.authorization.require("profiles.tags.define", "maintain profile tags")
        tag = self.repository.tag(_identifier(tag_id, "tag"))
        if not tag:
            raise CustomProfileValidationError("The selected tag is unavailable.")
        return self.repository.set_tag_active(tag, bool(active), self.session.user_id)

    def available_tags(self, church_id, entity_type):
        """Return authorized active controlled tags."""
        self.authorization.require("profiles.tags.view", "view profile tags")
        return self.repository.tags(
            _identifier(church_id, "church"), _entity(entity_type),
            self.authorization.has_permission("profiles.custom_fields.view_restricted"),
        )

    def tag_catalog(self, church_id, entity_type):
        """Return all tags for authorized administration, including retired tags."""
        self.authorization.require("profiles.tags.define", "maintain profile tags")
        return self.repository.tags(
            _identifier(church_id, "church"), _entity(entity_type), True, active_only=False,
        )

    def assign_tag(self, church_id, entity_type, profile_id, tag_id, assigned):
        """Assign or remove one same-church controlled tag."""
        self.authorization.require("profiles.tags.assign", "assign profile tags")
        entity_type = _entity(entity_type); profile_id = _identifier(profile_id, "profile")
        church_id = _identifier(church_id, "church"); tag = self.repository.tag(_identifier(tag_id, "tag"))
        if not tag or (assigned and not tag["active"]) or tag["church_id"] != church_id or tag["entity_type"] != entity_type:
            raise CustomProfileValidationError("The selected tag is unavailable.")
        if self.repository.profile_church_id(entity_type, profile_id) != church_id:
            raise CustomProfileValidationError("The selected profile is unavailable.")
        if tag["privacy_class"] == "RESTRICTED":
            self.authorization.require("profiles.custom_fields.edit_restricted", "assign restricted profile tags")
        if assigned and self.repository.profile_tag_count(entity_type, profile_id) >= self.MAX_TAGS:
            raise CustomProfileValidationError(f"A profile may contain at most {self.MAX_TAGS} tags.")
        return self.repository.set_tag(entity_type, profile_id, tag, bool(assigned), self.session.user_id)

    def profile_tags(self, church_id, entity_type, profile_id):
        """Return authorized active tags plus retired tags already assigned."""
        self.authorization.require("profiles.tags.view", "view profile tags")
        church_id = _identifier(church_id, "church"); entity_type = _entity(entity_type)
        profile_id = _identifier(profile_id, "profile")
        if self.repository.profile_church_id(entity_type, profile_id) != church_id:
            raise CustomProfileValidationError("The selected profile is unavailable.")
        assigned = self.repository.assigned_tag_ids(entity_type, profile_id)
        restricted = self.authorization.has_permission("profiles.custom_fields.view_restricted")
        catalog = self.repository.tags(church_id, entity_type, restricted, active_only=False)
        return tuple(item for item in catalog if item["active"] or item["id"] in assigned), assigned

    def _definition(self, definition_id):
        current = self.repository.definition(_identifier(definition_id, "custom field"))
        if current is None:
            raise CustomProfileValidationError("The selected custom field is unavailable.")
        return current


def _definition_values(values):
    values = dict(values or {}); data_type = str(values.get("data_type") or "").upper()
    if data_type not in CustomProfileFieldService.DATA_TYPES:
        raise CustomProfileValidationError("Choose a supported custom field type.")
    maximum = values.get("max_length")
    if maximum not in (None, ""):
        maximum = _identifier(maximum, "maximum length")
        limit = 255 if data_type == "SHORT_TEXT" else 2000 if data_type == "LONG_TEXT" else 0
        if not limit or maximum > limit:
            raise CustomProfileValidationError("Choose a valid maximum length for the selected field type.")
    privacy = str(values.get("privacy_class") or "STANDARD").upper()
    if privacy not in {"STANDARD", "RESTRICTED"}:
        raise CustomProfileValidationError("Choose a valid privacy class.")
    return {
        "church_id": _identifier(values.get("church_id"), "church"),
        "entity_type": _entity(values.get("entity_type")),
        "field_key": _key(values.get("field_key"), "Field key"),
        "label": _text(values.get("label"), "Label", 100),
        "help_text": _optional_text(values.get("help_text"), 500),
        "section_label": _text(values.get("section_label") or "Additional Information", "Section", 100),
        "data_type": data_type, "privacy_class": privacy,
        "display_order": max(0, int(values.get("display_order") or 0)),
        "required": int(bool(values.get("required"))), "searchable": int(bool(values.get("searchable"))),
        "report_allowed": int(bool(values.get("report_allowed"))),
        "export_allowed": int(bool(values.get("export_allowed"))), "max_length": maximum,
        "minimum_value": values.get("minimum_value") or None, "maximum_value": values.get("maximum_value") or None,
        "decimal_places": int(values.get("decimal_places") if values.get("decimal_places") is not None else 2),
    }


def _descriptor(row, options):
    return DynamicFieldDescriptor(
        key=row["field_key"], label=row["label"], data_type=row["data_type"].lower(),
        section=row["section_label"], order=row["display_order"], required=bool(row["required"]),
        readonly=row["lifecycle_status"] == "RETIRED", help_text=row.get("help_text") or "",
        max_length=row.get("max_length"), minimum=row.get("minimum_value"), maximum=row.get("maximum_value"),
        decimal_places=row.get("decimal_places", 2),
        options=tuple(DynamicFieldOption(item["option_key"], item["label"], bool(item["active"])) for item in options),
    )


def _entity(value):
    result = str(value or "").strip().upper()
    if result not in CustomProfileFieldService.ENTITY_TYPES:
        raise CustomProfileValidationError("Choose Person or Family.")
    return result


def _identifier(value, label):
    try: result = int(value)
    except (TypeError, ValueError) as error: raise CustomProfileValidationError(f"A valid {label} ID is required.") from error
    if result <= 0: raise CustomProfileValidationError(f"A valid {label} ID is required.")
    return result


def _key(value, label):
    result = str(value or "").strip().lower()
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", result):
        raise CustomProfileValidationError(f"{label} must use lowercase letters, numbers, and underscores.")
    return result


def _text(value, label, limit):
    result = str(value or "").strip()
    if not result: raise CustomProfileValidationError(f"{label} is required.")
    if len(result) > limit: raise CustomProfileValidationError(f"{label} cannot exceed {limit} characters.")
    return result


def _optional_text(value, limit):
    result = str(value or "").strip()
    if len(result) > limit: raise CustomProfileValidationError(f"Text cannot exceed {limit} characters.")
    return result or None
