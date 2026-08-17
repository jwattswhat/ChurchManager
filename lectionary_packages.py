"""Validate checksum-protected, metadata-only lectionary packages."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from lectionary_calendar import LectionaryCalendarError, rule_date, validate_cycle_rule


_KEY = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_CHECKSUM = re.compile(r"^[0-9a-f]{64}$")
_CITATION = re.compile(
    r"^[1-3]?[A-Za-z][A-Za-z .'-]*\s+\d+[A-Za-z]?(?::\d+[A-Za-z]?(?:[-–]\d+[A-Za-z]?)?)?"
    r"(?:\s*[,;]\s*(?:[1-3]?[A-Za-z][A-Za-z .'-]*\s+)?\d+[A-Za-z]?(?::\d+[A-Za-z]?(?:[-–]\d+[A-Za-z]?)?)?)*$"
)
_MARKUP = re.compile(
    r"(?:<\s*/?\s*[a-z][^>]*>|\bdata:|\bfile:|\\rtf|!\[[^]]*\]\(|"
    r"\.(?:png|jpe?g|gif|svg|mp3|wav|pdf)\b)", re.IGNORECASE,
)


class LectionaryPackageError(ValueError):
    """Raised when lectionary package data is unsafe or inconsistent."""


def canonical_lectionary_checksum(package):
    """Return the SHA-256 hash of canonical package data without checksum."""
    if not isinstance(package, dict):
        raise LectionaryPackageError("The lectionary package manifest must be an object.")
    content = dict(package)
    content.pop("checksum", None)
    encoded = json.dumps(
        content, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_lectionary_package(path, maximum_bytes=10_000_000):
    """Load bounded UTF-8 JSON while rejecting duplicate fields and tampering."""
    path = Path(path)
    if not path.is_file() or path.stat().st_size > maximum_bytes:
        raise LectionaryPackageError("The lectionary package is unavailable or too large.")

    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise LectionaryPackageError(f"Duplicate JSON field: {key}.")
            value[key] = item
        return value

    try:
        package = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise LectionaryPackageError("The lectionary package is not valid UTF-8 JSON.") from error
    expected = str(package.get("checksum") or "").casefold() if isinstance(package, dict) else ""
    actual = canonical_lectionary_checksum(package)
    if expected != actual:
        raise LectionaryPackageError("The lectionary package checksum does not match its contents.")
    return package, actual


@dataclass(frozen=True)
class ValidatedLectionaryPackage:
    """Safe summary produced after full package validation."""

    package_code: str
    package_version: str
    distribution_scope: str
    system_count: int
    edition_count: int
    cycle_count: int
    proper_count: int
    appointment_count: int


class LectionaryPackageValidator:
    """Validate stable identities and the hard metadata-only boundary."""

    MANIFEST_FIELDS = frozenset({
        "package_code", "package_version", "schema_version", "checksum", "title",
        "source_name", "source_reference", "package_notice", "distribution_scope",
        "systems",
    })
    SYSTEM_FIELDS = frozenset({"system_key", "name", "note", "editions"})
    EDITION_FIELDS = frozenset({
        "edition_key", "name", "edition_year", "status", "valid_from",
        "valid_through", "source_note", "resolver_version", "cycle_rule",
        "cycles", "propers",
    })
    CYCLE_FIELDS = frozenset({"cycle_key", "display_name", "sequence", "is_active"})
    PROPER_FIELDS = frozenset({
        "proper_key", "cycle_key", "liturgical_date", "season", "sort",
        "default_color", "alternate_color", "calendar_rule", "note", "appointments",
    })
    APPOINTMENT_FIELDS = frozenset({
        "appointment_key", "role", "display_role", "display_citation",
        "normalized_citation", "track_code", "option_group_code", "option_type",
        "paired_appointment_key", "sequence", "is_default", "note",
    })
    STATUSES = frozenset({"STABLE", "TRIAL", "RETIRED", "LOCAL"})
    ROLES = frozenset({"FIRST_READING", "PSALM_CANTICLE", "SECOND_READING", "GOSPEL"})
    OPTION_TYPES = frozenset({"DEFAULT", "ALTERNATE", "OPTIONAL_EXTENSION", "VARIANT"})
    DISTRIBUTION_SCOPES = frozenset({"REDISTRIBUTABLE", "LOCAL_ONLY"})
    FORBIDDEN_FIELD_PARTS = (
        "scripture_text", "full_text", "body", "prayer", "collect_text", "rubric",
        "lyrics", "music", "notation", "score", "audio", "recording", "image",
        "artwork", "attachment", "binary", "blob", "media", "file_path",
        "content_url", "html", "rtf", "markdown",
    )

    def __init__(self, supported_schema=1):
        self.supported_schema = int(supported_schema)

    def validate(self, package, actual_checksum=None):
        """Validate the complete package and return non-sensitive counts."""
        self._object(package, self.MANIFEST_FIELDS, "manifest")
        code = self._key(package.get("package_code"), "package code")
        if code.startswith("local-"):
            raise LectionaryPackageError("A distributed package cannot claim the local namespace.")
        version = self._text(package.get("package_version"), 50, "package version")
        distribution_scope = str(package.get("distribution_scope") or "").upper()
        if distribution_scope not in self.DISTRIBUTION_SCOPES:
            raise LectionaryPackageError(
                "Distribution scope must be REDISTRIBUTABLE or LOCAL_ONLY."
            )
        if package.get("schema_version") != self.supported_schema:
            raise LectionaryPackageError("The lectionary package schema version is not supported.")
        checksum = str(package.get("checksum") or "").casefold()
        if not _CHECKSUM.fullmatch(checksum) or (
            actual_checksum is not None and checksum != str(actual_checksum).casefold()
        ):
            raise LectionaryPackageError("The lectionary package checksum is invalid.")
        for field, maximum in (
            ("title", 255), ("source_name", 255), ("source_reference", 500),
            ("package_notice", 500),
        ):
            self._text(package.get(field), maximum, field.replace("_", " "))
        systems = package.get("systems")
        if not isinstance(systems, list) or not systems:
            raise LectionaryPackageError("The lectionary package must contain at least one system.")
        identities = {"system": set(), "edition": set(), "proper": set(), "appointment": set()}
        counts = [0, 0, 0, 0, 0]
        for system in systems:
            self._system(system, code, identities, counts)
        return ValidatedLectionaryPackage(code, version, distribution_scope, *counts)

    def _system(self, system, package_code, identities, counts):
        self._object(system, self.SYSTEM_FIELDS, "system")
        system_key = self._owned_key(system.get("system_key"), package_code, "system key")
        self._unique(system_key, identities["system"], "system key")
        self._text(system.get("name"), 255, "system name")
        self._text(system.get("note", ""), 1000, "system note", required=False)
        editions = system.get("editions")
        if not isinstance(editions, list) or not editions:
            raise LectionaryPackageError("Every lectionary system must contain an edition.")
        counts[0] += 1
        for edition in editions:
            self._edition(edition, package_code, identities, counts)

    def _edition(self, edition, package_code, identities, counts):
        self._object(edition, self.EDITION_FIELDS, "edition")
        edition_key = self._owned_key(edition.get("edition_key"), package_code, "edition key")
        self._unique(edition_key, identities["edition"], "edition key")
        self._text(edition.get("name"), 255, "edition name")
        if str(edition.get("status") or "").upper() not in self.STATUSES:
            raise LectionaryPackageError("An edition has an unsupported status.")
        if edition.get("edition_year") is not None and not isinstance(edition["edition_year"], int):
            raise LectionaryPackageError("Edition year must be an integer or null.")
        self._date_range(edition.get("valid_from"), edition.get("valid_through"))
        self._text(edition.get("source_note", ""), 1000, "source note", required=False)
        self._text(edition.get("resolver_version", "1"), 20, "resolver version")
        self._text(edition.get("cycle_rule", "none"), 100, "cycle rule")
        cycles = edition.get("cycles", [])
        propers = edition.get("propers")
        if not isinstance(cycles, list) or not isinstance(propers, list) or not propers:
            raise LectionaryPackageError("Edition cycles must be a list and Propers must be a nonempty list.")
        cycle_keys = set()
        sequences = set()
        for cycle in cycles:
            self._object(cycle, self.CYCLE_FIELDS, "cycle")
            key = self._key(cycle.get("cycle_key"), "cycle key")
            self._unique(key, cycle_keys, "cycle key")
            sequence = self._positive_integer(cycle.get("sequence"), "cycle sequence")
            self._unique(sequence, sequences, "cycle sequence")
            self._text(cycle.get("display_name"), 100, "cycle display name")
            if not isinstance(cycle.get("is_active"), bool):
                raise LectionaryPackageError("Cycle active values must be true or false.")
        try:
            validate_cycle_rule(
                edition.get("cycle_rule", "none"),
                [(item["cycle_key"], item["display_name"], item["sequence"], item["is_active"])
                 for item in cycles],
            )
        except LectionaryCalendarError as error:
            raise LectionaryPackageError(str(error)) from error
        counts[1] += 1
        counts[2] += len(cycles)
        for proper in propers:
            self._proper(proper, package_code, cycle_keys, identities, counts)

    def _proper(self, proper, package_code, cycle_keys, identities, counts):
        self._object(proper, self.PROPER_FIELDS, "Proper")
        proper_key = self._owned_key(proper.get("proper_key"), package_code, "Proper key")
        self._unique(proper_key, identities["proper"], "Proper key")
        cycle_key = str(proper.get("cycle_key") or "").strip().casefold()
        if cycle_key and cycle_key not in cycle_keys:
            raise LectionaryPackageError("A Proper references an unknown cycle.")
        self._text(proper.get("liturgical_date"), 255, "liturgical date")
        self._text(proper.get("season", ""), 100, "season", required=False)
        self._positive_integer(proper.get("sort"), "Proper sort", allow_zero=True)
        for field in ("default_color", "alternate_color", "calendar_rule"):
            self._text(proper.get(field, ""), 255, field.replace("_", " "), required=False)
        if proper.get("calendar_rule"):
            try:
                rule_date(proper["calendar_rule"], 2024)
            except LectionaryCalendarError as error:
                raise LectionaryPackageError(str(error)) from error
        self._text(proper.get("note", ""), 1000, "Proper note", required=False)
        appointments = proper.get("appointments")
        if not isinstance(appointments, list) or not appointments:
            raise LectionaryPackageError("Every Proper must contain at least one appointment.")
        local_keys = set()
        option_defaults = {}
        pairs = []
        for appointment in appointments:
            self._appointment(
                appointment, package_code, identities, local_keys, option_defaults, pairs,
            )
        for paired_key in pairs:
            if paired_key not in local_keys:
                raise LectionaryPackageError("A paired appointment key is not in the same Proper.")
        if any(count != 1 for count in option_defaults.values()):
            raise LectionaryPackageError("Every option group must have exactly one default appointment.")
        counts[3] += 1
        counts[4] += len(appointments)

    def _appointment(self, item, package_code, identities, local_keys, option_defaults, pairs):
        self._object(item, self.APPOINTMENT_FIELDS, "appointment")
        key = self._owned_key(item.get("appointment_key"), package_code, "appointment key")
        self._unique(key, identities["appointment"], "appointment key")
        local_keys.add(key)
        if str(item.get("role") or "").upper() not in self.ROLES:
            raise LectionaryPackageError("An appointment has an unsupported reading role.")
        self._text(item.get("display_role"), 100, "display role")
        display = self._text(item.get("display_citation"), 500, "display citation")
        normalized = self._text(item.get("normalized_citation"), 500, "normalized citation")
        if not _CITATION.fullmatch(display) or not _CITATION.fullmatch(normalized):
            raise LectionaryPackageError("A biblical citation is not in an approved reference format.")
        option_type = str(item.get("option_type") or "").upper()
        if option_type not in self.OPTION_TYPES:
            raise LectionaryPackageError("An appointment has an unsupported option type.")
        self._positive_integer(item.get("sequence"), "appointment sequence")
        if not isinstance(item.get("is_default"), bool):
            raise LectionaryPackageError("Appointment default values must be true or false.")
        self._optional_key(item.get("track_code"), "track code")
        group = self._optional_key(item.get("option_group_code"), "option group code")
        paired = self._optional_owned_key(item.get("paired_appointment_key"), package_code)
        if paired:
            pairs.append(paired)
        if group:
            option_defaults[group] = option_defaults.get(group, 0) + int(item["is_default"])
        elif option_type != "DEFAULT" or not item["is_default"]:
            raise LectionaryPackageError("Ungrouped appointments must be default appointments.")
        self._text(item.get("note", ""), 1000, "appointment note", required=False)

    def _object(self, value, allowed, location):
        if not isinstance(value, dict):
            raise LectionaryPackageError(f"The {location} must be an object.")
        unknown = set(value) - allowed
        if unknown:
            field = sorted(unknown)[0]
            if any(part in field.casefold() for part in self.FORBIDDEN_FIELD_PARTS):
                raise LectionaryPackageError(f"Prohibited content field in {location}: {field}.")
            raise LectionaryPackageError(f"Unknown field in {location}: {field}.")

    @staticmethod
    def _key(value, label):
        value = str(value or "").strip().casefold()
        if not _KEY.fullmatch(value):
            raise LectionaryPackageError(f"The {label} is not a valid stable key.")
        return value

    def _owned_key(self, value, package_code, label):
        value = self._key(value, label)
        if not value.startswith(package_code + "-"):
            raise LectionaryPackageError(f"The {label} is outside the package namespace.")
        return value

    def _optional_key(self, value, label):
        return "" if value in (None, "") else self._key(value, label)

    def _optional_owned_key(self, value, package_code):
        return "" if value in (None, "") else self._owned_key(value, package_code, "paired appointment key")

    @staticmethod
    def _unique(value, seen, label):
        if value in seen:
            raise LectionaryPackageError(f"Duplicate {label}: {value}.")
        seen.add(value)

    @staticmethod
    def _positive_integer(value, label, allow_zero=False):
        minimum = 0 if allow_zero else 1
        if not isinstance(value, int) or value < minimum:
            raise LectionaryPackageError(f"The {label} must be an integer of at least {minimum}.")
        return value

    @staticmethod
    def _text(value, maximum, label, required=True):
        value = str(value or "").strip()
        if required and not value:
            raise LectionaryPackageError(f"The {label} is required.")
        if len(value) > maximum or _MARKUP.search(value):
            raise LectionaryPackageError(f"The {label} is too long or contains prohibited content.")
        return value

    @staticmethod
    def _date_range(start, end):
        parsed = []
        for value in (start, end):
            if value in (None, ""):
                parsed.append(None)
                continue
            try:
                parsed.append(date.fromisoformat(str(value)))
            except ValueError as error:
                raise LectionaryPackageError("Edition validity dates must use YYYY-MM-DD.") from error
        if parsed[0] and parsed[1] and parsed[0] > parsed[1]:
            raise LectionaryPackageError("Edition valid-through date precedes its valid-from date.")
