"""Previewed stable-key import and privacy-controlled export for custom profiles."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from JSForm.dynamic_fields import DynamicFieldError, normalize_dynamic_value

from custom_profile_fields import CustomProfileValidationError, _descriptor
from csv_safety import csv_safe_row


FORMAT = "churchmanager-custom-profile-values"
FORMAT_VERSION = 1


@dataclass(frozen=True)
class ImportPreviewRow:
    """One non-writing custom-value import decision."""

    row_number: int
    display_name: str
    profile_id: int | None
    changes: dict
    errors: tuple[str, ...]


class CustomProfileExchangeService:
    """Exchange explicitly approved custom values without exposing unrestricted tables."""

    def __init__(self, field_service):
        self.fields = field_service
        self.repository = field_service.repository
        self.session = field_service.session
        self.authorization = field_service.authorization

    def export(self, church_id, entity_type, destination, include_restricted=False):
        """Write a CSV plus metadata manifest using stable definition and option keys."""
        self.authorization.require("profiles.custom_fields.view", "export custom profile fields")
        church_id = int(church_id); entity_type = str(entity_type).upper()
        if include_restricted:
            self.authorization.require("profiles.custom_fields.view_restricted", "export restricted custom fields")
        definitions = [item for item in self.fields.definitions(church_id, entity_type)
                       if item["lifecycle_status"] == "ACTIVE" and item["export_allowed"]
                       and (item["privacy_class"] == "STANDARD" or include_restricted)]
        if not definitions:
            raise CustomProfileValidationError("No Active custom fields are approved for this export.")
        identities = self.repository.profile_catalog(church_id, entity_type)
        core = self._core_headers(entity_type)
        headers = core + ["custom." + item["field_key"] for item in definitions]
        target = Path(destination); manifest = target.with_suffix(target.suffix + ".manifest.json")
        csv_temp = target.with_name(target.name + ".tmp"); manifest_temp = manifest.with_name(manifest.name + ".tmp")
        try:
            with csv_temp.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=headers); writer.writeheader()
                for profile in identities:
                    row = self._identity_row(entity_type, profile)
                    values = self.repository.profile_values(entity_type, profile["id"], definitions)
                    for definition in definitions:
                        row["custom." + definition["field_key"]] = self._format(values.get(definition["field_key"]))
                    writer.writerow(csv_safe_row(row))
            metadata = {
                "format": FORMAT, "version": FORMAT_VERSION, "entity_type": entity_type,
                "restricted_values_included": bool(include_restricted),
                "csv_sha256": hashlib.sha256(csv_temp.read_bytes()).hexdigest(),
                "fields": [self._metadata(item) for item in definitions],
            }
            manifest_temp.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
            csv_temp.replace(target); manifest_temp.replace(manifest)
            self.repository.audit_exchange(church_id, self.session.user_id, "CUSTOM_FIELD_EXPORT_COMPLETED", entity_type, len(identities))
            return len(identities), manifest
        finally:
            csv_temp.unlink(missing_ok=True); manifest_temp.unlink(missing_ok=True)

    def preview_import(self, church_id, entity_type, source):
        """Validate every CSV row and return non-writing match/change decisions."""
        self.authorization.require("profiles.custom_fields.edit", "import custom profile fields")
        church_id = int(church_id); entity_type = str(entity_type).upper(); source = Path(source)
        with source.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream); headers = tuple(reader.fieldnames or ()); raw_rows = list(reader)
        custom_headers = [header for header in headers if header.startswith("custom.")]
        if not custom_headers: raise CustomProfileValidationError("The CSV contains no custom.<stable_key> columns.")
        definitions = {item["field_key"]: item for item in self.fields.definitions(church_id, entity_type)
                       if item["lifecycle_status"] == "ACTIVE"}
        unknown = [header for header in custom_headers if header[7:] not in definitions]
        if unknown: raise CustomProfileValidationError("Unknown or inactive custom field(s): " + ", ".join(unknown))
        selected = [definitions[header[7:]] for header in custom_headers]
        for item in selected:
            if item["privacy_class"] == "RESTRICTED":
                self.authorization.require("profiles.custom_fields.edit_restricted", "import restricted custom fields")
        catalog = self.repository.profile_catalog(church_id, entity_type)
        index = {}
        for profile in catalog: index.setdefault(self._identity_key(entity_type, profile), []).append(profile)
        preview = []
        for number, raw in enumerate(raw_rows, 2):
            key = self._row_identity_key(entity_type, raw); matches = index.get(key, []); errors = []
            if not self._identity_complete(entity_type, key): errors.append("Required profile identity is blank.")
            elif not matches: errors.append("No existing profile matches this identity.")
            elif len(matches) > 1: errors.append("More than one existing profile matches this identity.")
            changes = {}
            if not errors:
                for definition in selected:
                    raw_value = str(raw.get("custom." + definition["field_key"]) or "").strip()
                    try:
                        value = self._parse_value(definition, raw_value)
                        changes[definition["id"]] = (definition, value)
                    except (DynamicFieldError, ValueError) as error: errors.append(f"{definition['label']}: {error}")
            display = self._row_display(entity_type, raw)
            preview.append(ImportPreviewRow(number, display, matches[0]["id"] if len(matches) == 1 else None, changes, tuple(errors)))
        return preview

    def commit_import(self, church_id, entity_type, source, preview):
        """Re-preview and atomically save an unchanged, fully valid source file."""
        fresh = self.preview_import(church_id, entity_type, source)
        signature = lambda rows: [(
            row.row_number, row.profile_id, row.errors,
            tuple((key, repr(value[1])) for key, value in sorted(row.changes.items())),
        ) for row in rows]
        if signature(fresh) != signature(preview):
            raise CustomProfileValidationError("The import preview changed. Preview the file again.")
        errors = [row for row in fresh if row.errors]
        if errors: raise CustomProfileValidationError("Every import row must be Ready before import.")
        profiles = [(row.profile_id, row.changes) for row in fresh]
        self.repository.save_profile_value_batch(str(entity_type).upper(), profiles, self.session.user_id)
        return len(profiles)

    def _parse_value(self, definition, raw):
        options = self.repository.options(definition["id"], active_only=False)
        descriptor = _descriptor(definition, options)
        if not raw: return () if definition["data_type"] == "MULTIPLE_CHOICE" else None
        if definition["data_type"] == "MULTIPLE_CHOICE":
            values = tuple(part.strip() for part in raw.split("|") if part.strip())
            return normalize_dynamic_value(descriptor, values)
        return normalize_dynamic_value(descriptor, raw)

    def _metadata(self, definition):
        return {
            "stable_key": definition["field_key"], "label": definition["label"],
            "data_type": definition["data_type"], "privacy_class": definition["privacy_class"],
            "options": [{"stable_key": item["option_key"], "label": item["label"]}
                        for item in self.repository.options(definition["id"], active_only=False)],
        }

    @staticmethod
    def _core_headers(entity_type):
        return ["First Name", "Middle Name", "Last Name"] if entity_type == "PERSON" else ["Family Name"]

    @staticmethod
    def _identity_row(entity_type, profile):
        if entity_type == "PERSON": return {"First Name": profile["first_name"], "Middle Name": profile["middle_name"], "Last Name": profile["last_name"]}
        return {"Family Name": profile["family_name"]}

    @staticmethod
    def _identity_key(entity_type, profile):
        if entity_type == "PERSON": return tuple(str(profile[name] or "").strip().casefold() for name in ("first_name", "middle_name", "last_name"))
        return (str(profile["family_name"] or "").strip().casefold(),)

    @staticmethod
    def _row_identity_key(entity_type, row):
        names = ("First Name", "Middle Name", "Last Name") if entity_type == "PERSON" else ("Family Name",)
        return tuple(str(row.get(name) or "").strip().casefold() for name in names)

    @staticmethod
    def _row_display(entity_type, row):
        if entity_type == "PERSON": return " ".join(str(row.get(name) or "").strip() for name in ("First Name", "Middle Name", "Last Name") if str(row.get(name) or "").strip())
        return str(row.get("Family Name") or "").strip()

    @staticmethod
    def _identity_complete(entity_type, key):
        return bool(key[0] and key[2]) if entity_type == "PERSON" else bool(key[0])

    @staticmethod
    def _format(value):
        if value is None: return ""
        if isinstance(value, (tuple, list)): return "|".join(str(item) for item in value)
        if isinstance(value, bool): return "yes" if value else "no"
        if isinstance(value, (date, Decimal)): return str(value)
        return str(value)
