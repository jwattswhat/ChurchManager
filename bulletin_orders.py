"""Structured bulletin-order templates, legacy conversion, and output rendering."""

from __future__ import annotations

from dataclasses import dataclass
import html
import re


PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")
TAG_RE = re.compile(r"<[^>]+>")
BREAK_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)

HYMN_KEYS = {
    "entrance", "processional", "office hymn", "of the day", "communion",
    "hymn", "closing", "gloria in excelsis", "sanctus", "agnus dei",
    "creed", "post communion", "kyrie",
}
READING_KEYS = {
    "psalm", "first", "second", "third", "first reading", "old testament",
    "epistle", "gospel",
}


@dataclass(frozen=True)
class ParsedLegacyLine:
    line_type: str
    label: str
    value_source: str | None
    value_key: str | None
    reference: str | None
    style_name: str
    label_bold: bool
    value_bold: bool
    italic: bool
    indent_level: int
    has_tab: bool
    condition_type: str
    condition_value: str | None
    needs_review: bool


def _plain_content(content: str) -> str:
    text = BREAK_RE.sub("\n", content or "")
    text = html.unescape(text)
    # Some old records used invalid numeric tab entities that unescape to a NUL.
    text = text.replace("\x00", "\t")
    text = TAG_RE.sub("", text)
    return text.strip(" \r\n")


def parse_legacy_line(content: str) -> ParsedLegacyLine:
    raw = content or ""
    plain = _plain_content(raw)
    match = PLACEHOLDER_RE.search(plain)
    key = match.group(1).strip() if match else None
    lowered_key = key.casefold() if key else None
    value_source = None
    line_type = "TEXT"
    if lowered_key in HYMN_KEYS:
        value_source, line_type = "SERVICE_HYMN", "HYMN"
    elif lowered_key in READING_KEYS:
        value_source, line_type = "SERVICE_READING", "READING"

    label_text = PLACEHOLDER_RE.sub("", plain).strip()
    parts = [part.strip() for part in label_text.split("\t")]
    label = parts[0] if parts else ""
    reference = " ".join(part for part in parts[1:] if part) or None
    has_tab = "\t" in plain
    if not key and raw.lstrip().lower().startswith("<b>"):
        line_type = "HEADING"

    condition_type = "ALWAYS"
    condition_value = None
    condition_text = plain.casefold()
    if "omitted during advent" in condition_text:
        condition_type, condition_value = "EXCLUDE_SEASON", "Advent"
    elif "omitted during lent" in condition_text:
        condition_type, condition_value = "EXCLUDE_SEASON", "Lent"

    return ParsedLegacyLine(
        line_type=line_type,
        label=label,
        value_source=value_source,
        value_key=key,
        reference=reference,
        style_name="Section Heading" if line_type == "HEADING" else "Normal",
        label_bold="<b>" in raw.lower() and not key,
        value_bold=bool(key and "<b>" in raw.lower()),
        italic="<i>" in raw.lower(),
        indent_level=1 if plain.startswith("\t") else 0,
        has_tab=has_tab,
        condition_type=condition_type,
        condition_value=condition_value,
        needs_review=bool("{" in plain and not key) or (bool(key) and value_source is None),
    )


def _columns(cursor, table):
    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=?", (table,),
    )
    return {row[0].casefold(): row[0] for row in cursor.fetchall()}


def migrate_legacy_orders(connection):
    """Idempotently convert every legacy template while retaining its source content."""
    cursor = connection.cursor()
    try:
        columns = _columns(cursor, "tblOrderofService")
        required = {"id", "orderofservice", "line", "content"}
        if not required.issubset(columns):
            raise RuntimeError("The legacy Order of Service table is missing required fields.")
        optional = [name for name in ("title", "page", "file", "note") if name in columns]
        select_fields = [columns[name] for name in ("id", "orderofservice", "line", "content")]
        select_fields.extend(columns[name] for name in optional)
        cursor.execute(
            "SELECT " + ",".join(select_fields) + " FROM tblOrderofService "
            "ORDER BY OrderofService, Line, ID"
        )
        records = cursor.fetchall()

        templates = {}
        converted = 0
        reviewed = 0
        for record in records:
            legacy_id, legacy_name, _legacy_sequence, content = record[:4]
            extras = dict(zip(optional, record[4:]))
            if legacy_name not in templates:
                cursor.execute(
                    "INSERT INTO tblBulletinOrderTemplate "
                    "(Name,Description,Active,IsStarter,SourceLegacyName) VALUES (?,?,1,1,?) "
                    "ON DUPLICATE KEY UPDATE ID=LAST_INSERT_ID(ID)",
                    (legacy_name, "Converted from the original Order of Service records.", legacy_name),
                )
                template_id = cursor.lastrowid
                if not template_id:
                    cursor.execute(
                        "SELECT ID FROM tblBulletinOrderTemplate WHERE SourceLegacyName=?",
                        (legacy_name,),
                    )
                    template_id = cursor.fetchone()[0]
                templates[legacy_name] = [template_id, 0]
            template_id, count = templates[legacy_name]
            sequence = (count + 1) * 10
            templates[legacy_name][1] += 1
            parsed = parse_legacy_line(content)
            note_parts = [str(extras.get("note") or "").strip()]
            if extras.get("file"):
                note_parts.append(f"Legacy file: {extras['file']}")
            note = "\n".join(part for part in note_parts if part) or None
            reference = parsed.reference or (
                str(extras.get("page")) if extras.get("page") is not None else None
            )
            label = str(extras.get("title") or parsed.label or "").strip()
            cursor.execute(
                "INSERT INTO tblBulletinOrderLine "
                "(TemplateID,Sequence,LineType,Label,ValueSource,ValueKey,ReferenceText,"
                "StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,TabAlignment,"
                "TabLeader,ConditionType,ConditionValue,Note,LegacyContent,NeedsReview) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
                "ON DUPLICATE KEY UPDATE ID=ID",
                (
                    template_id, sequence, parsed.line_type, label, parsed.value_source,
                    parsed.value_key, reference, parsed.style_name, parsed.label_bold,
                    parsed.value_bold, parsed.italic, parsed.indent_level,
                    4.75 if parsed.has_tab else None, "RIGHT" if parsed.has_tab else "LEFT",
                    "NONE", parsed.condition_type, parsed.condition_value, note, content,
                    parsed.needs_review,
                ),
            )
            converted += cursor.rowcount == 1
            reviewed += parsed.needs_review
        connection.commit()
        return {"templates": len(templates), "lines_added": converted, "needs_review": reviewed}
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def render_plain_line(label, value=None, reference=None, indent_level=0, has_tab=False):
    left = ("\t" * int(indent_level or 0)) + (label or "")
    right = value or reference or ""
    if right:
        return left + ("\t" if has_tab else " ") + str(right)
    return left
