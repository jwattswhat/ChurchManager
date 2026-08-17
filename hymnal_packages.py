"""Validate and transactionally install metadata-only hymnal packages."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from bulletin_orders import portable_connection
from hymn_titles import title_case


_KEY = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_CHECKSUM = re.compile(r"^[0-9a-f]{64}$")
_MARKUP = re.compile(
    r"(?:<\s*/?\s*[a-z][^>]*>|\bdata:|\bfile:|\\rtf|!\[[^]]*\]\(|"
    r"\.(?:png|jpe?g|gif|svg|mp3|wav|pdf)\b)", re.IGNORECASE,
)


class HymnalPackageError(ValueError):
    """Raised when a hymnal package is unsafe, ambiguous, or inconsistent."""


def canonical_hymnal_checksum(package):
    """Return the SHA-256 hash of canonical package data excluding its checksum."""
    if not isinstance(package, dict):
        raise HymnalPackageError("The hymnal package manifest must be an object.")
    content = dict(package); content.pop("checksum", None)
    encoded = json.dumps(
        content, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_hymnal_package(path, maximum_bytes=10_000_000):
    """Load bounded UTF-8 JSON while rejecting duplicate fields and tampering."""
    path = Path(path)
    if not path.is_file() or path.stat().st_size > maximum_bytes:
        raise HymnalPackageError("The hymnal package is unavailable or too large.")

    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise HymnalPackageError(f"Duplicate JSON field: {key}.")
            value[key] = item
        return value

    try:
        package = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise HymnalPackageError("The hymnal package is not valid UTF-8 JSON.") from error
    expected = str(package.get("checksum") or "").casefold() if isinstance(package, dict) else ""
    actual = canonical_hymnal_checksum(package)
    if expected != actual:
        raise HymnalPackageError("The hymnal package checksum does not match its contents.")
    return package, actual


@dataclass(frozen=True)
class ValidatedHymnalPackage:
    package_code: str
    package_version: str
    hymnal_id: int
    entry_count: int
    warning_count: int


class HymnalPackageValidator:
    """Validate permanent IDs and passive metadata without database access."""

    MANIFEST_FIELDS = frozenset({
        "package_code", "package_version", "schema_version", "checksum",
        "hymnal_id", "hymn_id_start", "hymn_id_end", "abbreviation", "title",
        "edition", "publisher", "publication_year", "isbn", "source_name",
        "source_reference", "distribution_notice", "entries",
    })
    ENTRY_FIELDS = frozenset({
        "hymn_id", "entry_slot", "printed_reference", "title",
        "printed_stanza_count", "is_active", "tune", "meter", "category",
        "scripture_references", "first_line", "author", "translator", "composer",
        "text_copyright_status", "tune_copyright_status", "setting_copyright_status",
        "copyright_owner", "copyright_year", "license_source", "license_reference",
        "copyright_note", "copyright_verified_date", "copyright_verified_by", "source_note",
    })
    COPYRIGHT_STATUSES = frozenset({"UNKNOWN", "PUBLIC_DOMAIN", "COPYRIGHTED", "LICENSED"})
    FORBIDDEN_FIELD_PARTS = (
        "lyrics", "stanza_text", "full_text", "music", "notation", "score",
        "audio", "recording", "image", "artwork", "attachment", "binary",
        "blob", "media", "file_path", "content_url", "html", "rtf", "markdown",
    )

    def __init__(self, supported_schema=1):
        self.supported_schema = int(supported_schema)

    def validate(self, package, actual_checksum=None):
        """Return counts only after validating the entire in-memory package."""
        if not isinstance(package, dict):
            raise HymnalPackageError("The hymnal package manifest must be an object.")
        self._known_fields(package, self.MANIFEST_FIELDS, "manifest")
        code = self._key(package.get("package_code"), "package code")
        if code == "local":
            raise HymnalPackageError("The local congregation block cannot be distributed as a package.")
        version = self._short(package.get("package_version"), 50, "package version")
        schema = package.get("schema_version")
        if not isinstance(schema, int) or schema != self.supported_schema:
            raise HymnalPackageError("The hymnal package schema version is not supported.")
        checksum = str(package.get("checksum") or "").casefold()
        if not _CHECKSUM.fullmatch(checksum) or (
            actual_checksum is not None and checksum != str(actual_checksum).casefold()
        ):
            raise HymnalPackageError("The hymnal package checksum is invalid.")
        hymnal_id = package.get("hymnal_id")
        start = package.get("hymn_id_start"); end = package.get("hymn_id_end")
        if not isinstance(hymnal_id, int) or hymnal_id < 2:
            raise HymnalPackageError("A distributed hymnal must have a registered HymnalID of 2 or greater.")
        if start != hymnal_id * 5000 + 1 or end != hymnal_id * 5000 + 4999:
            raise HymnalPackageError("The permanent hymn block does not match its HymnalID.")
        self._short(package.get("abbreviation"), 20, "hymnal abbreviation")
        self._short(package.get("title"), 255, "hymnal title")
        for field, maximum in (
            ("edition", 255), ("publisher", 255), ("isbn", 40),
            ("source_name", 255), ("source_reference", 500),
            ("distribution_notice", 500),
        ):
            self._short(package.get(field), maximum, field.replace("_", " "))
        entries = package.get("entries")
        if not isinstance(entries, list) or not entries:
            raise HymnalPackageError("The hymnal package must contain at least one entry.")
        ids = set(); slots = set(); references = set(); warnings = 0
        for index, entry in enumerate(entries, start=1):
            warnings += self._entry(entry, index, hymnal_id, start, end, ids, slots, references)
        return ValidatedHymnalPackage(code, version, hymnal_id, len(entries), warnings)

    def _entry(self, entry, index, hymnal_id, start, end, ids, slots, references):
        if not isinstance(entry, dict):
            raise HymnalPackageError(f"Entry {index} must be an object.")
        self._known_fields(entry, self.ENTRY_FIELDS, f"entry {index}")
        hymn_id = entry.get("hymn_id"); slot = entry.get("entry_slot")
        if not isinstance(slot, int) or not 1 <= slot <= 4999:
            raise HymnalPackageError("Every entry slot must be from 1 through 4,999.")
        if hymn_id != hymnal_id * 5000 + slot or not start <= hymn_id <= end:
            raise HymnalPackageError("A HymnID does not match its permanent hymnal block and entry slot.")
        reference = self._short(entry.get("printed_reference"), 50, "printed reference")
        if hymn_id in ids or slot in slots or reference.casefold() in references:
            raise HymnalPackageError("Hymn IDs, entry slots, and printed references must be unique.")
        ids.add(hymn_id); slots.add(slot); references.add(reference.casefold())
        self._short(entry.get("title"), 500, "hymn title")
        stanza_count = entry.get("printed_stanza_count")
        if not isinstance(stanza_count, int) or not 0 <= stanza_count <= 99:
            raise HymnalPackageError("Printed stanza count must be from 0 through 99.")
        if not isinstance(entry.get("is_active"), bool):
            raise HymnalPackageError("The active value must be true or false.")
        limits = {
            "tune": 255, "meter": 50, "category": 255,
            "scripture_references": 500, "first_line": 500, "author": 255,
            "translator": 255, "composer": 255, "copyright_owner": 255,
            "license_source": 100, "license_reference": 255,
            "copyright_note": 1000, "copyright_verified_date": 10,
            "copyright_verified_by": 255, "source_note": 1000,
        }
        for field, maximum in limits.items():
            self._short(entry.get(field, ""), maximum, field.replace("_", " "), required=False)
        for field in ("text_copyright_status", "tune_copyright_status", "setting_copyright_status"):
            status = str(entry.get(field, "UNKNOWN")).upper()
            if status not in self.COPYRIGHT_STATUSES:
                raise HymnalPackageError(f"Unsupported passive copyright status: {status}.")
        return int(not entry.get("tune"))

    def _known_fields(self, value, allowed, location):
        unknown = set(value) - allowed
        if unknown:
            field = sorted(unknown)[0]
            if any(part in field.casefold() for part in self.FORBIDDEN_FIELD_PARTS):
                raise HymnalPackageError(f"Prohibited content field in {location}: {field}.")
            raise HymnalPackageError(f"Unknown field in {location}: {field}.")

    @staticmethod
    def _key(value, label):
        value = str(value or "").strip().casefold()
        if not _KEY.fullmatch(value):
            raise HymnalPackageError(f"The {label} is not a valid stable key.")
        return value

    @staticmethod
    def _short(value, maximum, label, required=True):
        value = str(value or "").strip()
        if required and not value:
            raise HymnalPackageError(f"The {label} is required.")
        if len(value) > maximum or _MARKUP.search(value):
            raise HymnalPackageError(f"The {label} is too long or contains prohibited content.")
        return value


class HymnalPackageImporter:
    """Install one validated permanent-ID hymnal package in one transaction."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def install(self, package, actual_checksum=None):
        """Validate, collision-check, install metadata, log, and commit atomically."""
        summary = HymnalPackageValidator().validate(package, actual_checksum)
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ID,PackageCode,HymnIDStart,HymnIDEnd FROM tblHymnal "
                "WHERE ID=? OR PackageCode=? FOR UPDATE",
                (summary.hymnal_id, summary.package_code),
            )
            registry_rows = cursor.fetchall()
            if len(registry_rows) > 1 or (registry_rows and (
                registry_rows[0][0] != summary.hymnal_id
                or str(registry_rows[0][1]).casefold() != summary.package_code
                or registry_rows[0][2] != package["hymn_id_start"]
                or registry_rows[0][3] != package["hymn_id_end"]
            )):
                raise HymnalPackageError("The permanent hymnal registry assignment conflicts with this package.")
            cursor.execute(
                "SELECT COUNT(*) FROM tblHymnal WHERE ID<>? AND HymnIDStart<=? AND HymnIDEnd>=?",
                (summary.hymnal_id, package["hymn_id_end"], package["hymn_id_start"]),
            )
            if cursor.fetchone()[0]:
                raise HymnalPackageError("The permanent hymn block overlaps another hymnal.")
            action = "UPGRADE" if registry_rows else "INSTALL"
            if registry_rows:
                cursor.execute(
                    "UPDATE tblHymnal SET Hymnal=?,Title=?,Publisher=?,PackageVersion=?,Edition=?,"
                    "PublicationYear=?,ISBN=?,IsActive=1 WHERE ID=? AND PackageCode=?",
                    (package["abbreviation"], title_case(package["title"]), package["publisher"],
                     package["package_version"], package["edition"], package.get("publication_year"),
                     package.get("isbn"), summary.hymnal_id, summary.package_code),
                )
            else:
                cursor.execute(
                    "INSERT INTO tblHymnal (ID,Hymnal,Title,Publisher,Note,PackageCode,PackageVersion,"
                    "Edition,PublicationYear,ISBN,HymnIDStart,HymnIDEnd,IsActive) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1)",
                    (summary.hymnal_id, package["abbreviation"], title_case(package["title"]),
                     package["publisher"], package["distribution_notice"], summary.package_code,
                     package["package_version"], package["edition"], package.get("publication_year"),
                     package.get("isbn"), package["hymn_id_start"], package["hymn_id_end"]),
                )
            for entry in package["entries"]:
                self._install_entry(cursor, summary.hymnal_id, entry)
            cursor.execute(
                "INSERT INTO tblHymnalPackageImport "
                "(HymnalID,PackageCode,PackageVersion,Checksum,Action,EntryCount,WarningCount) "
                "VALUES (?,?,?,?,?,?,?)",
                (summary.hymnal_id, summary.package_code, summary.package_version,
                 package["checksum"], action, summary.entry_count, summary.warning_count),
            )
            self.connection.commit()
            return summary
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    @staticmethod
    def _install_entry(cursor, hymnal_id, entry):
        cursor.execute(
            "SELECT HymnalID,EntrySlot,PrintedReference FROM tblHymn WHERE ID=? FOR UPDATE",
            (entry["hymn_id"],),
        )
        existing = cursor.fetchone()
        if existing and (
            existing[0] != hymnal_id or existing[1] != entry["entry_slot"]
            or str(existing[2]).casefold() != entry["printed_reference"].casefold()
        ):
            raise HymnalPackageError("An existing HymnID has a different permanent identity.")
        values = (
            title_case(entry["title"]), entry.get("tune"), entry.get("scripture_references"),
            entry.get("category"), entry["printed_stanza_count"], int(entry["is_active"]),
            entry.get("first_line"), entry.get("meter"), entry.get("author"),
            entry.get("translator"), entry.get("composer"), entry.get("source_note"),
            entry.get("text_copyright_status", "UNKNOWN"),
            entry.get("tune_copyright_status", "UNKNOWN"),
            entry.get("setting_copyright_status", "UNKNOWN"), entry.get("copyright_owner"),
            entry.get("copyright_year"), entry.get("license_source"),
            entry.get("license_reference"), entry.get("copyright_note"),
            entry.get("copyright_verified_date"), entry.get("copyright_verified_by"),
        )
        if existing:
            cursor.execute(
                "UPDATE tblHymn SET Title=?,Tune=?,BibleText=?,Category=?,PrintedStanzaCount=?,"
                "IsActive=?,FirstLine=?,Meter=?,Author=?,Translator=?,Composer=?,SourceNote=?,"
                "TextCopyrightStatus=?,TuneCopyrightStatus=?,SettingCopyrightStatus=?,"
                "CopyrightOwner=?,CopyrightYear=?,LicenseSource=?,LicenseReference=?,CopyrightNote=?,"
                "CopyrightVerifiedDate=?,CopyrightVerifiedBy=?,PackageOwned=1 WHERE ID=? AND HymnalID=?",
                values + (entry["hymn_id"], hymnal_id),
            )
        else:
            cursor.execute(
                "INSERT INTO tblHymn (ID,HymnalID,Hymn,Title,EntrySlot,PrintedReference,"
                "Tune,BibleText,Category,PrintedStanzaCount,IsActive,FirstLine,Meter,Author,"
                "Translator,Composer,SourceNote,TextCopyrightStatus,TuneCopyrightStatus,"
                "SettingCopyrightStatus,CopyrightOwner,CopyrightYear,LicenseSource,LicenseReference,"
                "CopyrightNote,CopyrightVerifiedDate,CopyrightVerifiedBy,PackageOwned) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)",
                (entry["hymn_id"], hymnal_id, entry["printed_reference"], entry["title"],
                 entry["entry_slot"], entry["printed_reference"]) + values[1:],
            )
