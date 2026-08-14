"""Structured bulletin-order templates and output rendering."""

from __future__ import annotations

import html


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
                "SELECT t.ID,t.Name,t.Description,t.Active,t.IsStarter,t.HymnalID,"
                "CASE WHEN h.ID IS NULL THEN 'No hymnal' "
                "ELSE CONCAT(h.Hymnal,' - ',h.Title) END "
                "FROM tblBulletinOrderTemplate t "
                "LEFT JOIN tblHymnal h ON h.ID=t.HymnalID "
                "ORDER BY t.IsStarter DESC,t.Name"
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def hymnals(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT ID,Hymnal,Title FROM tblHymnal ORDER BY Title,Hymnal")
            return cursor.fetchall()
        finally:
            cursor.close()

    def templates_for_service(self, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT c.PrimaryHymnalID,w.TemplateID FROM tblService s "
                "LEFT JOIN tblChurch c ON c.ID=s.ChurchID "
                "LEFT JOIN tblServiceBulletinOrder w ON w.ServiceID=s.ID "
                "WHERE s.ID=?", (service_id,),
            )
            row = cursor.fetchone()
            primary_hymnal_id = row[0] if row else None
            assigned_template_id = row[1] if row else None
        finally:
            cursor.close()
        return [
            template for template in self.templates()
            if template[5] is None
            or template[5] == primary_hymnal_id
            or template[0] == assigned_template_id
        ]

    def set_template_hymnal(self, template_id, hymnal_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE tblBulletinOrderTemplate SET HymnalID=?,Version=Version+1 "
                "WHERE ID=? AND IsStarter=0", (hymnal_id, template_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Starter bulletin orders cannot be changed.")
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
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
                "SELECT Description,HymnalID FROM tblBulletinOrderTemplate WHERE ID=?", (source_id,)
            )
            source = cursor.fetchone()
            if not source:
                raise ValueError("The selected bulletin order no longer exists.")
            cursor.execute(
                "INSERT INTO tblBulletinOrderTemplate "
                "(ChurchID,HymnalID,Name,Description,Active,IsStarter,Version) "
                "VALUES (?,?,?,?,1,0,1)",
                (church_id, source[1], name.strip(), source[0]),
            )
            new_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO tblBulletinOrderLine "
                "(TemplateID,Sequence,LineType,Label,ValueSource,ValueKey,ReferenceText,"
                "StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,TabAlignment,"
                "TabLeader,ConditionType,ConditionValue,Note,NeedsReview) "
                "SELECT ?,Sequence,LineType,Label,ValueSource,ValueKey,ReferenceText,"
                "StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,TabAlignment,"
                "TabLeader,ConditionType,ConditionValue,Note,NeedsReview "
                "FROM tblBulletinOrderLine WHERE TemplateID=?",
                (new_id, source_id),
            )
            cursor.execute(
                "INSERT INTO tblWorshipRoleRequirement "
                "(BulletinOrderTemplateID,WorshipRoleID,RequiredCount,Active) "
                "SELECT ?,WorshipRoleID,RequiredCount,Active "
                "FROM tblWorshipRoleRequirement WHERE BulletinOrderTemplateID=?",
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
                "SELECT COUNT(*) FROM tblServiceBulletinOrder WHERE TemplateID=?",
                (template_id,),
            )
            weekly_orders = cursor.fetchone()[0]
            cursor.execute(
                "UPDATE tblHymnUsage u "
                "JOIN tblServiceBulletinOrderLine l ON l.ID=u.ServiceBulletinOrderLineID "
                "JOIN tblServiceBulletinOrder o ON o.ServiceID=l.ServiceID "
                "SET u.ServiceBulletinOrderLineID=NULL WHERE o.TemplateID=?",
                (template_id,),
            )
            cursor.execute(
                "DELETE l FROM tblServiceBulletinOrderLine l "
                "JOIN tblServiceBulletinOrder o ON o.ServiceID=l.ServiceID "
                "WHERE o.TemplateID=?",
                (template_id,),
            )
            cursor.execute(
                "DELETE FROM tblServiceBulletinOrder WHERE TemplateID=?",
                (template_id,),
            )
            cursor.execute(
                "DELETE FROM tblBulletinOrderTemplate WHERE ID=? AND IsStarter=0",
                (template_id,),
            )
            if cursor.rowcount != 1:
                raise ValueError("Starter bulletin orders cannot be deleted.")
            self.connection.commit()
            return weekly_orders
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


class WeeklyBulletinOrderRepository:
    """Service-specific snapshot and overrides; template records are never changed."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)
        self.templates = BulletinOrderRepository(self.connection)

    def assignment(self, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ServiceID,TemplateID FROM tblServiceBulletinOrder WHERE ServiceID=?",
                (service_id,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    def lines(self, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ID,Sequence,Included,LineType,Label,ValueSource,ValueKey,WeeklyValue,"
                "ReferenceText,StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,"
                "TabAlignment,TabLeader,Note,TemplateLineID "
                "FROM tblServiceBulletinOrderLine WHERE ServiceID=? ORDER BY Sequence,ID",
                (service_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def apply_template(self, service_id, template_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT s.HolyCommunion,COALESCE(p.Season,''),s.ChurchID FROM tblService s "
                "LEFT JOIN tblPropers p ON p.ID=s.PropersID WHERE s.ID=?", (service_id,),
            )
            service = cursor.fetchone()
            if not service:
                raise ValueError("The selected service is unavailable.")
            cursor.execute(
                "SELECT u.HymnID,u.UsedAs,TRIM(CONCAT_WS(' ',h.Hymn,h.Title)) "
                "FROM tblHymnUsage u JOIN tblHymn h ON h.ID=u.HymnID "
                "LEFT JOIN tblServiceBulletinOrderLine l "
                "ON l.ID=u.ServiceBulletinOrderLineID "
                "WHERE u.ServiceID=? ORDER BY COALESCE(l.Sequence,2147483647),u.ID",
                (service_id,),
            )
            selected_hymns = cursor.fetchall()
            cursor.execute("DELETE FROM tblHymnUsage WHERE ServiceID=?", (service_id,))
            template_lines = self.templates.lines(template_id)
            cursor.execute("DELETE FROM tblServiceBulletinOrderLine WHERE ServiceID=?", (service_id,))
            cursor.execute(
                "INSERT INTO tblServiceBulletinOrder (ServiceID,TemplateID) VALUES (?,?) "
                "ON DUPLICATE KEY UPDATE TemplateID=VALUES(TemplateID),GeneratedPlainText=NULL,"
                "GeneratedHtml=NULL,GeneratedAt=NULL", (service_id, template_id),
            )
            cursor.execute(
                "UPDATE tblService SET BulletinOrderTemplateID=? WHERE ID=?",
                (template_id, service_id),
            )
            for line in template_lines:
                included = BulletinOrderGenerator.condition_included(
                    line[15], line[16], bool(service[0]), service[1],
                )
                cursor.execute(
                    "INSERT INTO tblServiceBulletinOrderLine "
                    "(ServiceID,TemplateLineID,Sequence,Included,LineType,Label,ValueSource,"
                    "ValueKey,ReferenceText,StyleName,LabelBold,ValueBold,Italic,IndentLevel,"
                    "TabPosition,TabAlignment,TabLeader,Note) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (service_id, line[0], line[1], included, line[2], line[3], line[4],
                     line[5], line[6], line[7], line[8], line[9], line[10], line[11],
                     line[12], line[13], line[14], line[17]),
                )
                weekly_line_id = cursor.lastrowid
                if line[4] == "SERVICE_HYMN":
                    match_index = next(
                        (index for index, hymn in enumerate(selected_hymns)
                         if hymn[1] == line[5]),
                        None,
                    )
                    if match_index is not None:
                        hymn_id, used_as, display = selected_hymns.pop(match_index)
                        cursor.execute(
                            "INSERT INTO tblHymnUsage "
                            "(ChurchID,ServiceID,ServiceBulletinOrderLineID,HymnID,UsedAs) "
                            "VALUES (?,?,?,?,?)",
                            (service[2], service_id, weekly_line_id, hymn_id, used_as),
                        )
                        cursor.execute(
                            "UPDATE tblServiceBulletinOrderLine SET WeeklyValue=? WHERE ID=?",
                            (display, weekly_line_id),
                        )
            self.connection.commit()
            return len(template_lines)
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def delete_order(self, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM tblServiceBulletinOrderLine WHERE ServiceID=?", (service_id,))
            deleted_lines = cursor.rowcount
            cursor.execute("DELETE FROM tblServiceBulletinOrder WHERE ServiceID=?", (service_id,))
            if cursor.rowcount != 1:
                raise ValueError("No weekly bulletin order exists for the selected service.")
            self.connection.commit()
            return deleted_lines
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def save_line(self, service_id, line_id, included, label, weekly_value, reference, note):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE tblServiceBulletinOrderLine SET Included=?,Label=?,WeeklyValue=?,"
                "ReferenceText=?,Note=? WHERE ID=? AND ServiceID=?",
                (included, label.strip(), weekly_value or None, reference or None, note or None,
                 line_id, service_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("The selected weekly bulletin line is unavailable.")
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def apply_resolved_values(self, service_id, resolved_values):
        """Copy current worship-planning selections into this service's weekly snapshot."""
        cursor = self.connection.cursor()
        try:
            updated = 0
            for resolved in resolved_values:
                line_id, value = resolved[:2]
                value_source = resolved[2] if len(resolved) > 2 else None
                if value in (None, ""):
                    continue
                if value_source == "SERVICE_READING":
                    cursor.execute(
                        "UPDATE tblServiceBulletinOrderLine SET WeeklyValue=? "
                        "WHERE ID=? AND ServiceID=? AND ValueSource='SERVICE_READING' "
                        "AND (WeeklyValue IS NULL OR WeeklyValue='')",
                        (str(value), line_id, service_id),
                    )
                else:
                    cursor.execute(
                        "UPDATE tblServiceBulletinOrderLine SET WeeklyValue=? "
                        "WHERE ID=? AND ServiceID=? AND ValueSource IS NOT NULL",
                        (str(value), line_id, service_id),
                    )
                updated += cursor.rowcount
            self.connection.commit()
            return updated
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def move_line(self, service_id, line_id, direction):
        rows = self.lines(service_id)
        index = next((i for i, row in enumerate(rows) if row[0] == line_id), None)
        target = None if index is None else index + direction
        if index is None or target < 0 or target >= len(rows):
            return
        cursor = self.connection.cursor()
        try:
            current_sequence, target_sequence = rows[index][1], rows[target][1]
            cursor.execute("UPDATE tblServiceBulletinOrderLine SET Sequence=-1 WHERE ID=?", (line_id,))
            cursor.execute("UPDATE tblServiceBulletinOrderLine SET Sequence=? WHERE ID=?",
                           (current_sequence, rows[target][0]))
            cursor.execute("UPDATE tblServiceBulletinOrderLine SET Sequence=? WHERE ID=?",
                           (target_sequence, line_id))
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
                "SELECT s.ID,s.DateTime,s.LiturgicalDate,COALESCE(t.Name,'Service') "
                "FROM tblService s LEFT JOIN tblBulletinOrderTemplate t "
                "ON t.ID=s.BulletinOrderTemplateID "
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
                "SELECT BulletinOrderTemplateID FROM tblService WHERE ID=?", (service_id,)
            )
            row = cursor.fetchone()
            if row and row[0]:
                return row[0]
            return None
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
            cursor.execute("SELECT Reading,Reference FROM tblReading WHERE PropersID=?", (service[4],))
            reading_rows = cursor.fetchall()
            readings = {str(row[0]).casefold(): row[1] for row in reading_rows}
            return service, hymns, readings
        finally:
            cursor.close()

    @staticmethod
    def condition_included(condition, value, communion, season):
        season = str(season or "").casefold()
        if condition == "COMMUNION":
            return communion
        if condition == "NO_COMMUNION":
            return not communion
        if condition == "INCLUDE_SEASON":
            return str(value or "").casefold() == season
        if condition == "EXCLUDE_SEASON":
            return str(value or "").casefold() != season
        return True

    @classmethod
    def _included(cls, line, service):
        return cls.condition_included(line[15], line[16], bool(service[3]), service[5])

    def render(self, template_id, service_id, prefer_weekly=True):
        service, hymns, readings = self._service_context(service_id)
        rendered = []
        weekly_lines = WeeklyBulletinOrderRepository(self.connection).lines(service_id)
        if weekly_lines:
            source_lines = [
                {
                    "id": line[0], "sequence": line[1], "included": bool(line[2]),
                    "type": line[3], "label": line[4], "source": line[5], "key": line[6],
                    "weekly_value": line[7], "reference": line[8], "style": line[9],
                    "label_bold": line[10], "value_bold": line[11], "italic": line[12],
                    "indent": line[13], "tab_position": line[14],
                    "tab_alignment": line[15], "tab_leader": line[16],
                } for line in weekly_lines if line[2]
            ]
        else:
            source_lines = [
                {
                    "id": line[0], "sequence": line[1], "included": True,
                    "type": line[2], "label": line[3], "source": line[4], "key": line[5],
                    "weekly_value": None, "reference": line[6], "style": line[7],
                    "label_bold": line[8], "value_bold": line[9], "italic": line[10],
                    "indent": line[11], "tab_position": line[12],
                    "tab_alignment": line[13], "tab_leader": line[14],
                } for line in self.repository.lines(template_id) if self._included(line, service)
            ]
        for source_line in source_lines:
            source, key = source_line["source"], source_line["key"]
            value = None
            if prefer_weekly and source_line["weekly_value"]:
                value = source_line["weekly_value"]
            elif source == "SERVICE_HYMN":
                value = hymns.get(str(key or "").casefold())
            elif source == "SERVICE_READING":
                value = readings.get(str(key or "").casefold())
                if value is None and str(key or "").casefold() == "first reading":
                    value = readings.get("old testament") or readings.get("first")
            item = {
                "id": source_line["id"], "sequence": source_line["sequence"],
                "type": source_line["type"], "label": source_line["label"],
                "value": value, "reference": source_line["reference"],
                "style": source_line["style"], "label_bold": bool(source_line["label_bold"]),
                "value_bold": bool(source_line["value_bold"]),
                "italic": bool(source_line["italic"]), "indent": source_line["indent"],
                "tab_position": source_line["tab_position"],
                "tab_alignment": source_line["tab_alignment"],
                "tab_leader": source_line["tab_leader"],
                "missing": bool(source and not value), "value_key": key,
                "value_source": source,
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
