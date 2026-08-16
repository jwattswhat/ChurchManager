"""Preflight validation for metadata-only Order of Service packages."""

from __future__ import annotations

import re
from dataclasses import dataclass

from bulletin_orders import portable_connection


_KEY = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_CHECKSUM = re.compile(r"^[0-9a-f]{64}$")
_MARKUP = re.compile(
    r"(?:<\s*/?\s*[a-z][^>]*>|\bdata:|\bfile:|\\rtf|!\[[^]]*\]\(|"
    r"\.(?:png|jpe?g|gif|svg|mp3|wav|pdf)\b)", re.IGNORECASE,
)


class OrderOfServicePackageError(ValueError):
    """Raised when package preflight finds unsafe or inconsistent metadata."""


@dataclass(frozen=True)
class ValidatedOrderOfServicePackage:
    package_code: str
    package_version: str
    template_count: int
    line_count: int
    role_count: int


class OrderOfServicePackageValidator:
    """Validate package structure without touching a database or filesystem."""

    MANIFEST_FIELDS = frozenset({
        "package_code", "package_version", "title", "template_prefix", "source_name",
        "source_reference", "package_notice", "hymnal_package_code",
        "minimum_hymnal_version", "schema_version", "checksum", "templates",
    })
    TEMPLATE_FIELDS = frozenset({
        "template_key", "name", "description", "hymnal_package_code", "lines",
        "required_positions",
    })
    LINE_FIELDS = frozenset({
        "line_key", "sequence", "line_type", "label", "value_source",
        "value_key", "reference", "style", "label_bold", "value_bold",
        "italic", "indent", "tab_position", "tab_alignment", "tab_leader",
        "condition", "condition_value", "note",
    })
    ROLE_FIELDS = frozenset({"role_key", "required_count"})
    LINE_TYPES = frozenset({
        "HEADING", "LITURGY", "HYMN", "READING", "SERMON", "OFFERING",
        "COMMUNION", "TEXT",
    })
    CONDITIONS = frozenset({
        "ALWAYS", "COMMUNION", "NO_COMMUNION", "INCLUDE_SEASON",
        "EXCLUDE_SEASON", "USER_CHOICE",
    })
    FORBIDDEN_FIELD_PARTS = (
        "html", "rtf", "markdown", "body", "content", "lyrics", "stanza_text",
        "prayer_text", "collect_text", "responsive_text", "psalm_text",
        "music", "notation", "score", "audio", "recording", "image", "artwork",
        "attachment", "binary", "blob", "media", "file_path", "content_url",
    )

    def __init__(self, installed_hymnals=(), supported_schema=1):
        self.installed_hymnals = {str(value).casefold() for value in installed_hymnals}
        self.supported_schema = int(supported_schema)

    def validate(self, package, actual_checksum=None):
        """Return a summary only when the complete in-memory package is safe."""
        if not isinstance(package, dict):
            raise OrderOfServicePackageError("The package manifest must be an object.")
        self._known_fields(package, self.MANIFEST_FIELDS, "manifest")
        code = self._key(package.get("package_code"), "package code")
        if code.startswith("local-"):
            raise OrderOfServicePackageError("A distributed package cannot use the local namespace.")
        version = self._short(package.get("package_version"), 50, "package version")
        self._short(package.get("title"), 255, "package title")
        prefix = str(package.get("template_prefix") or "")
        if len(prefix) > 20 or _MARKUP.search(prefix):
            raise OrderOfServicePackageError("The template prefix is invalid.")
        if not re.fullmatch(r"[A-Z][A-Z0-9]{1,11} ", prefix):
            raise OrderOfServicePackageError(
                "The template prefix must be an uppercase catalog abbreviation followed by one space."
            )
        self._short(package.get("source_name", ""), 255, "source name", required=False)
        self._short(package.get("source_reference", ""), 500, "source reference", required=False)
        self._short(package.get("package_notice", ""), 500, "package notice", required=False)
        schema = package.get("schema_version")
        if not isinstance(schema, int) or schema != self.supported_schema:
            raise OrderOfServicePackageError("The package schema version is not supported.")
        checksum = str(package.get("checksum") or "").casefold()
        if not _CHECKSUM.fullmatch(checksum):
            raise OrderOfServicePackageError("The package checksum is invalid.")
        if actual_checksum is not None and checksum != str(actual_checksum).casefold():
            raise OrderOfServicePackageError("The package checksum does not match its contents.")
        dependency = package.get("hymnal_package_code")
        if dependency:
            dependency = self._key(dependency, "hymnal package code")
            if dependency.casefold() not in self.installed_hymnals:
                raise OrderOfServicePackageError("The required hymnal package is not installed.")
        templates = package.get("templates")
        if not isinstance(templates, list) or not templates:
            raise OrderOfServicePackageError("The package must contain at least one template.")
        template_keys = set(); total_lines = 0; total_roles = 0
        for index, template in enumerate(templates, start=1):
            lines, roles = self._template(template, index, dependency, prefix, template_keys)
            total_lines += lines; total_roles += roles
        return ValidatedOrderOfServicePackage(code, version, len(templates), total_lines, total_roles)

    def _template(self, template, index, package_hymnal, prefix, keys):
        if not isinstance(template, dict):
            raise OrderOfServicePackageError(f"Template {index} must be an object.")
        self._known_fields(template, self.TEMPLATE_FIELDS, f"template {index}")
        key = self._key(template.get("template_key"), f"template {index} key")
        if key.startswith("local-") or key in keys:
            raise OrderOfServicePackageError("Template keys must be unique package keys.")
        keys.add(key)
        name = self._short(template.get("name"), 255, f"template {index} name")
        if not name.startswith(prefix):
            raise OrderOfServicePackageError(
                f"Packaged template names must begin with {prefix!r}."
            )
        self._short(template.get("description", ""), 250, "template description", required=False)
        template_hymnal = template.get("hymnal_package_code")
        if template_hymnal and self._key(template_hymnal, "template hymnal dependency") != package_hymnal:
            raise OrderOfServicePackageError("A template hymnal dependency must match its package manifest.")
        lines = template.get("lines")
        if not isinstance(lines, list) or not lines:
            raise OrderOfServicePackageError("Every template must contain at least one outline line.")
        line_keys = set(); sequences = set()
        for line_index, line in enumerate(lines, start=1):
            self._line(line, line_index, line_keys, sequences)
        roles = template.get("required_positions", [])
        if not isinstance(roles, list):
            raise OrderOfServicePackageError("Required positions must be a list.")
        role_keys = set()
        for role_index, role in enumerate(roles, start=1):
            self._role(role, role_index, role_keys)
        return len(lines), len(roles)

    def _line(self, line, index, keys, sequences):
        if not isinstance(line, dict):
            raise OrderOfServicePackageError(f"Line {index} must be an object.")
        self._known_fields(line, self.LINE_FIELDS, f"line {index}")
        key = self._key(line.get("line_key"), f"line {index} key")
        sequence = line.get("sequence")
        if key.startswith("local-") or key in keys or not isinstance(sequence, int) or sequence < 1 or sequence in sequences:
            raise OrderOfServicePackageError("Line keys and positive sequences must be unique within a template.")
        keys.add(key); sequences.add(sequence)
        line_type = str(line.get("line_type") or "").upper()
        condition = str(line.get("condition") or "ALWAYS").upper()
        if line_type not in self.LINE_TYPES:
            raise OrderOfServicePackageError(f"Unsupported Order of Service line type: {line_type or '[blank]'}.")
        if condition not in self.CONDITIONS:
            raise OrderOfServicePackageError(f"Unsupported Order of Service condition: {condition or '[blank]'}.")
        self._short(line.get("label"), 120, "outline label")
        self._short(line.get("reference", ""), 80, "outline reference", required=False)
        self._short(line.get("note", ""), 250, "planning note", required=False)

    def _role(self, role, index, keys):
        if not isinstance(role, dict):
            raise OrderOfServicePackageError(f"Role {index} must be an object.")
        self._known_fields(role, self.ROLE_FIELDS, f"role {index}")
        key = self._key(role.get("role_key"), f"role {index} key")
        count = role.get("required_count")
        if key in keys or not isinstance(count, int) or count < 0 or count > 99:
            raise OrderOfServicePackageError("Role keys must be unique and counts must be from 0 through 99.")
        keys.add(key)

    def _known_fields(self, value, allowed, location):
        unknown = set(value) - allowed
        if unknown:
            field = sorted(unknown)[0]
            if any(part in field.casefold() for part in self.FORBIDDEN_FIELD_PARTS):
                raise OrderOfServicePackageError(f"Prohibited content field in {location}: {field}.")
            raise OrderOfServicePackageError(f"Unknown field in {location}: {field}.")

    @staticmethod
    def _key(value, label):
        value = str(value or "").strip().casefold()
        if not _KEY.fullmatch(value):
            raise OrderOfServicePackageError(f"The {label} is not a valid stable key.")
        return value

    @staticmethod
    def _short(value, maximum, label, required=True):
        value = str(value or "").strip()
        if required and not value:
            raise OrderOfServicePackageError(f"The {label} is required.")
        if len(value) > maximum:
            raise OrderOfServicePackageError(f"The {label} cannot exceed {maximum} characters.")
        if _MARKUP.search(value):
            raise OrderOfServicePackageError(f"The {label} contains prohibited markup or media.")
        return value


class OrderOfServicePackageImporter:
    """Install one validated package atomically without touching local templates."""

    def __init__(self, connection, installed_hymnals=(), hymnal_ids=None):
        self.connection = portable_connection(connection)
        self.installed_hymnals = tuple(installed_hymnals)
        self.hymnal_ids = {str(key).casefold(): value for key, value in (hymnal_ids or {}).items()}

    def install(self, package, actual_checksum=None):
        """Validate, install or upgrade, log, and commit the complete package."""
        summary = OrderOfServicePackageValidator(self.installed_hymnals).validate(
            package, actual_checksum=actual_checksum,
        )
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ID,PackageVersion FROM tblOrderOfServicePackage WHERE PackageCode=? FOR UPDATE",
                (summary.package_code,),
            )
            existing = cursor.fetchone()
            action = "UPGRADE" if existing else "INSTALL"
            if existing:
                package_id = existing[0]
                cursor.execute(
                    "UPDATE tblOrderOfServicePackage SET PackageVersion=?,Title=?,TemplatePrefix=?,"
                    "SourceName=?,SourceReference=?,PackageNotice=?,HymnalPackageCode=?,"
                    "MinimumHymnalVersion=?,SchemaVersion=?,Checksum=?,IsActive=1 WHERE ID=?",
                    self._package_values(package) + (package_id,),
                )
            else:
                cursor.execute(
                    "INSERT INTO tblOrderOfServicePackage "
                    "(PackageCode,PackageVersion,Title,TemplatePrefix,SourceName,SourceReference,"
                    "PackageNotice,HymnalPackageCode,MinimumHymnalVersion,SchemaVersion,Checksum) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (summary.package_code,) + self._package_values(package),
                )
                package_id = cursor.lastrowid
            cursor.execute(
                "UPDATE tblBulletinOrderTemplate SET Active=0 WHERE PackageID=?",
                (package_id,),
            )
            for template in package["templates"]:
                self._install_template(cursor, package_id, package, template)
            cursor.execute(
                "INSERT INTO tblOrderOfServicePackageImport "
                "(PackageID,PackageVersion,Checksum,Action,TemplateCount,LineCount,RoleCount) "
                "VALUES (?,?,?,?,?,?,?)",
                (package_id, summary.package_version, package["checksum"], action,
                 summary.template_count, summary.line_count, summary.role_count),
            )
            self.connection.commit()
            return summary
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    @staticmethod
    def _package_values(package):
        return (
            package["package_version"], package["title"], package["template_prefix"],
            package.get("source_name", ""), package.get("source_reference", ""),
            package.get("package_notice", ""), package.get("hymnal_package_code"),
            package.get("minimum_hymnal_version"), package["schema_version"],
            package["checksum"].casefold(),
        )

    def _install_template(self, cursor, package_id, package, template):
        key = template["template_key"].casefold()
        cursor.execute(
            "SELECT ID,PackageID,IsStarter FROM tblBulletinOrderTemplate WHERE TemplateKey=? FOR UPDATE",
            (key,),
        )
        existing = cursor.fetchone()
        if existing and (existing[1] != package_id or not existing[2]):
            raise OrderOfServicePackageError(
                "A package cannot overwrite a local template or another package's template."
            )
        dependency = template.get("hymnal_package_code") or package.get("hymnal_package_code")
        hymnal_id = self.hymnal_ids.get(str(dependency).casefold()) if dependency else None
        if dependency and hymnal_id is None:
            raise OrderOfServicePackageError("The installed hymnal dependency has no database mapping.")
        if existing:
            template_id = existing[0]
            cursor.execute(
                "UPDATE tblBulletinOrderTemplate SET Name=?,Description=?,HymnalID=?,Active=1,"
                "IsStarter=1,Version=Version+1 WHERE ID=? AND PackageID=?",
                (template["name"], template.get("description", ""), hymnal_id,
                 template_id, package_id),
            )
        else:
            cursor.execute(
                "INSERT INTO tblBulletinOrderTemplate "
                "(TemplateKey,PackageID,ChurchID,HymnalID,Name,Description,Active,IsStarter,Version) "
                "VALUES (?,?,NULL,?,?,?,1,1,1)",
                (key, package_id, hymnal_id, template["name"], template.get("description", "")),
            )
            template_id = cursor.lastrowid
        cursor.execute("DELETE FROM tblBulletinOrderLine WHERE TemplateID=?", (template_id,))
        for line in sorted(template["lines"], key=lambda item: item["sequence"]):
            cursor.execute(
                "INSERT INTO tblBulletinOrderLine "
                "(LineKey,TemplateID,Sequence,LineType,Label,ValueSource,ValueKey,ReferenceText,"
                "StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,TabAlignment,"
                "TabLeader,ConditionType,ConditionValue,Note,NeedsReview) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)",
                (line["line_key"].casefold(), template_id, line["sequence"],
                 line["line_type"].upper(), line["label"], line.get("value_source"),
                 line.get("value_key"), line.get("reference"), line.get("style", "Normal"),
                 int(bool(line.get("label_bold"))), int(bool(line.get("value_bold"))),
                 int(bool(line.get("italic"))), int(line.get("indent", 0)),
                 line.get("tab_position"), line.get("tab_alignment", "LEFT"),
                 line.get("tab_leader", "NONE"), line.get("condition", "ALWAYS").upper(),
                 line.get("condition_value"), line.get("note")),
            )
        cursor.execute(
            "DELETE FROM tblOrderOfServicePackageRoleRequirement WHERE TemplateID=?",
            (template_id,),
        )
        for role in template.get("required_positions", []):
            cursor.execute(
                "INSERT INTO tblOrderOfServicePackageRoleRequirement "
                "(PackageID,TemplateID,RoleKey,RequiredCount) VALUES (?,?,?,?)",
                (package_id, template_id, role["role_key"].casefold(), role["required_count"]),
            )
