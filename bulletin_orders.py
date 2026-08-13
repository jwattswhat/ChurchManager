"""Structured bulletin-order templates, legacy conversion, and output rendering."""

from __future__ import annotations

from dataclasses import dataclass
import html
import re


PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")
TAG_RE = re.compile(r"<[^>]+>")
BREAK_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


class _PortableCursor:
    def __init__(self, cursor):
        self._cursor = cursor
        self._marker = "%s" if cursor.__class__.__module__.startswith("mysql.connector") else "?"

    def execute(self, sql, values=()):
        return self._cursor.execute(sql.replace("?", self._marker), values)

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class _PortableConnection:
    def __init__(self, connection):
        self._connection = connection

    def cursor(self, *args, **kwargs):
        return _PortableCursor(self._connection.cursor(*args, **kwargs))

    def __getattr__(self, name):
        return getattr(self._connection, name)


def portable_connection(connection):
    return connection if isinstance(connection, _PortableConnection) else _PortableConnection(connection)

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


class BulletinOrderRepository:
    """Small persistence boundary used by the bulletin-order editor."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def templates(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ID,Name,Description,Active,IsStarter FROM tblBulletinOrderTemplate "
                "ORDER BY IsStarter DESC,Name"
            )
            return cursor.fetchall()
        finally:
            cursor.close()


    def lines(self, template_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ID,Sequence,LineType,Label,ValueSource,ValueKey,ReferenceText,"
                "StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,TabAlignment,"
                "TabLeader,ConditionType,ConditionValue,Note,NeedsReview "
                "FROM tblBulletinOrderLine WHERE TemplateID=? ORDER BY Sequence,ID",
                (template_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def duplicate_template(self, source_id, name, church_id=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT Description FROM tblBulletinOrderTemplate WHERE ID=?", (source_id,)
            )
            source = cursor.fetchone()
            if not source:
                raise ValueError("The selected bulletin order no longer exists.")
            cursor.execute(
                "INSERT INTO tblBulletinOrderTemplate "
                "(ChurchID,Name,Description,Active,IsStarter,Version) VALUES (?,?,?,1,0,1)",
                (church_id, name.strip(), source[0]),
            )
            new_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO tblBulletinOrderLine "
                "(TemplateID,Sequence,LineType,Label,ValueSource,ValueKey,ReferenceText,"
                "StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,TabAlignment,"
                "TabLeader,ConditionType,ConditionValue,Note,LegacyContent,NeedsReview) "
                "SELECT ?,Sequence,LineType,Label,ValueSource,ValueKey,ReferenceText,"
                "StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,TabAlignment,"
                "TabLeader,ConditionType,ConditionValue,Note,LegacyContent,NeedsReview "
                "FROM tblBulletinOrderLine WHERE TemplateID=?",
                (new_id, source_id),
            )
            self.connection.commit()
            return new_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def delete_custom_template(self, template_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "DELETE FROM tblBulletinOrderTemplate WHERE ID=? AND IsStarter=0",
                (template_id,),
            )
            if cursor.rowcount != 1:
                raise ValueError("Starter bulletin orders cannot be deleted.")
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def save_line(self, template_id, values, line_id=None):
        fields = (
            "Sequence", "LineType", "Label", "ValueSource", "ValueKey", "ReferenceText",
            "StyleName", "LabelBold", "ValueBold", "Italic", "IndentLevel", "TabPosition",
            "TabAlignment", "TabLeader", "ConditionType", "ConditionValue", "Note",
        )
        data = tuple(values.get(field) for field in fields)
        cursor = self.connection.cursor()
        try:
            if line_id is None:
                cursor.execute(
                    "INSERT INTO tblBulletinOrderLine (TemplateID," + ",".join(fields) + ") "
                    "VALUES (" + ",".join("?" for _ in range(len(fields) + 1)) + ")",
                    (template_id,) + data,
                )
                line_id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE tblBulletinOrderLine SET "
                    + ",".join(field + "=?" for field in fields)
                    + " WHERE ID=? AND TemplateID=?",
                    data + (line_id, template_id),
                )
            self.connection.commit()
            return line_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def delete_line(self, template_id, line_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "DELETE l FROM tblBulletinOrderLine l "
                "JOIN tblBulletinOrderTemplate t ON t.ID=l.TemplateID "
                "WHERE l.ID=? AND l.TemplateID=? AND t.IsStarter=0", (line_id, template_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Starter bulletin orders cannot be changed.")
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def move_line(self, template_id, line_id, direction):
        rows = self.lines(template_id)
        index = next((i for i, row in enumerate(rows) if row[0] == line_id), None)
        target = None if index is None else index + direction
        if index is None or target < 0 or target >= len(rows):
            return
        cursor = self.connection.cursor()
        try:
            current_sequence, target_sequence = rows[index][1], rows[target][1]
            cursor.execute("UPDATE tblBulletinOrderLine SET Sequence=-1 WHERE ID=?", (line_id,))
            cursor.execute(
                "UPDATE tblBulletinOrderLine SET Sequence=? WHERE ID=?",
                (current_sequence, rows[target][0]),
            )
            cursor.execute(
                "UPDATE tblBulletinOrderLine SET Sequence=? WHERE ID=?",
                (target_sequence, line_id),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()


class BulletinOrderGenerator:
    def __init__(self, connection):
        self.connection = portable_connection(connection)
        self.repository = BulletinOrderRepository(self.connection)

    def services(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ID,DateTime,LiturgicalDate,OrderofService FROM tblService "
                "ORDER BY DateTime DESC,ID DESC"
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def suggested_template_id(self, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT TemplateID FROM tblServiceBulletinOrder WHERE ServiceID=?", (service_id,)
            )
            row = cursor.fetchone()
            if row:
                return row[0]
            cursor.execute(
                "SELECT t.ID FROM tblService s JOIN tblBulletinOrderTemplate t "
                "ON t.SourceLegacyName=s.OrderofService WHERE s.ID=?", (service_id,),
            )
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            cursor.close()

    def _service_context(self, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT s.ID,s.DateTime,s.LiturgicalDate,s.HolyCommunion,s.PropersID,"
                "COALESCE(p.Season,'') FROM tblService s "
                "LEFT JOIN tblPropers p ON p.ID=s.PropersID WHERE s.ID=?", (service_id,),
            )
            service = cursor.fetchone()
            if not service:
                raise ValueError("The selected service is unavailable.")
            cursor.execute(
                "SELECT hu.UsedAs,h.Hymn,h.Title FROM tblHymnUsage hu "
                "JOIN tblHymn h ON h.ID=hu.HymnID WHERE hu.ServiceID=?", (service_id,),
            )
            hymns = {str(row[0]).casefold(): (row[1] or row[2] or "") for row in cursor.fetchall()}
            cursor.execute("SELECT Reading,Reference FROM tblAltReading WHERE ServiceID=?", (service_id,))
            reading_rows = cursor.fetchall()
            if not reading_rows:
                cursor.execute("SELECT Reading,Reference FROM tblReading WHERE PropersID=?", (service[4],))
                reading_rows = cursor.fetchall()
            readings = {str(row[0]).casefold(): row[1] for row in reading_rows}
            return service, hymns, readings
        finally:
            cursor.close()

    @staticmethod
    def _included(line, service):
        condition, value = line[15], line[16]
        communion, season = bool(service[3]), str(service[5] or "").casefold()
        if condition == "COMMUNION":
            return communion
        if condition == "NO_COMMUNION":
            return not communion
        if condition == "INCLUDE_SEASON":
            return str(value or "").casefold() == season
        if condition == "EXCLUDE_SEASON":
            return str(value or "").casefold() != season
        return True

    def render(self, template_id, service_id):
        service, hymns, readings = self._service_context(service_id)
        rendered = []
        for line in self.repository.lines(template_id):
            if not self._included(line, service):
                continue
            source, key = line[4], line[5]
            value = None
            if source == "SERVICE_HYMN":
                value = hymns.get(str(key or "").casefold())
            elif source == "SERVICE_READING":
                value = readings.get(str(key or "").casefold())
                if value is None and str(key or "").casefold() == "first reading":
                    value = readings.get("old testament") or readings.get("first")
            item = {
                "id": line[0], "sequence": line[1], "type": line[2], "label": line[3],
                "value": value, "reference": line[6], "style": line[7],
                "label_bold": bool(line[8]), "value_bold": bool(line[9]),
                "italic": bool(line[10]), "indent": line[11], "tab_position": line[12],
                "tab_alignment": line[13], "tab_leader": line[14],
                "missing": bool(source and not value), "value_key": key,
            }
            rendered.append(item)
        plain = "\r\n".join(
            render_plain_line(item["label"], item["value"], item["reference"], item["indent"],
                              item["tab_position"] is not None)
            for item in rendered
        )
        html_lines = []
        for item in rendered:
            label = html.escape(item["label"] or "")
            right = html.escape(str(item["value"] or item["reference"] or ""))
            if item["label_bold"]:
                label = f"<strong>{label}</strong>"
            if item["value_bold"]:
                right = f"<strong>{right}</strong>"
            content = label + (("\t" if item["tab_position"] is not None else " ") + right if right else "")
            if item["italic"]:
                content = f"<em>{content}</em>"
            html_lines.append(f"<p>{content}</p>")
        return {"service": service, "lines": rendered, "plain_text": plain,
                "html": "\n".join(html_lines)}
