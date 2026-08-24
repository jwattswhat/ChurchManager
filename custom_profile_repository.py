"""Parameterized MariaDB persistence for custom profile fields and tags."""

from __future__ import annotations

import json


class MariaDBCustomProfileRepository:
    """Persist normalized custom-profile metadata and typed values atomically."""

    VALUE_COLUMNS = {
        "SHORT_TEXT": "TextValue", "LONG_TEXT": "TextValue", "INTEGER": "IntegerValue",
        "DECIMAL": "DecimalValue", "DATE": "DateValue", "BOOLEAN": "BooleanValue",
        "SINGLE_CHOICE": "OptionID",
    }

    def __init__(self, connection):
        self.connection = connection
        self.marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    @staticmethod
    def _rows(cursor):
        names = [item[0] for item in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]

    def definitions(self, church_id, entity_type, include_drafts=False, include_restricted=False):
        clauses = ["ChurchID=?", "EntityType=?"]
        values = [church_id, entity_type]
        if not include_drafts: clauses.append("LifecycleStatus<>'DRAFT'")
        if not include_restricted: clauses.append("PrivacyClass='STANDARD'")
        return self._query_definitions(" AND ".join(clauses), tuple(values))

    def profile_definitions(self, church_id, entity_type, profile_id, include_restricted=False):
        parent = "tblPersonCustomFieldValue" if entity_type == "PERSON" else "tblFamilyCustomFieldValue"
        parent_id = "PersonID" if entity_type == "PERSON" else "FamilyID"
        privacy = "" if include_restricted else " AND d.PrivacyClass='STANDARD'"
        where = (
            "d.ChurchID=? AND d.EntityType=? AND (d.LifecycleStatus='ACTIVE' OR "
            f"(d.LifecycleStatus='RETIRED' AND EXISTS (SELECT 1 FROM {parent} v "
            f"WHERE v.DefinitionID=d.ID AND v.{parent_id}=?)))" + privacy
        )
        return self._query_definitions(where, (church_id, entity_type, profile_id), alias="d")

    def _query_definitions(self, where, values, alias=""):
        prefix = f"{alias}." if alias else ""
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, (
                f"SELECT {prefix}ID id,{prefix}ChurchID church_id,{prefix}EntityType entity_type,"
                f"{prefix}FieldKey field_key,{prefix}Label label,{prefix}HelpText help_text,"
                f"{prefix}SectionLabel section_label,{prefix}DataType data_type,"
                f"{prefix}LifecycleStatus lifecycle_status,{prefix}PrivacyClass privacy_class,"
                f"{prefix}DisplayOrder display_order,{prefix}Required required,{prefix}Searchable searchable,"
                f"{prefix}ReportAllowed report_allowed,{prefix}ExportAllowed export_allowed,"
                f"{prefix}MaxLength max_length,{prefix}MinimumValue minimum_value,"
                f"{prefix}MaximumValue maximum_value,{prefix}DecimalPlaces decimal_places,{prefix}Version version "
                f"FROM tblCustomFieldDefinition {alias} WHERE {where} "
                f"ORDER BY {prefix}SectionLabel,{prefix}DisplayOrder,{prefix}Label"
            ), values)
            return self._rows(cursor)
        finally: cursor.close()

    def definition(self, definition_id):
        rows = self._query_definitions("ID=?", (definition_id,))
        return rows[0] if rows else None

    def definition_key_exists(self, church_id, entity_type, field_key):
        return bool(self._scalar(
            "SELECT COUNT(*) FROM tblCustomFieldDefinition WHERE ChurchID=? AND EntityType=? AND FieldKey=?",
            (church_id, entity_type, field_key),
        ))

    def active_definition_count(self, church_id, entity_type):
        return int(self._scalar(
            "SELECT COUNT(*) FROM tblCustomFieldDefinition WHERE ChurchID=? AND EntityType=? AND LifecycleStatus='ACTIVE'",
            (church_id, entity_type),
        ))

    def create_definition(self, item):
        cursor = self.connection.cursor()
        try:
            columns = (
                "ChurchID,EntityType,FieldKey,Label,HelpText,SectionLabel,DataType,PrivacyClass,DisplayOrder,"
                "Required,Searchable,ReportAllowed,ExportAllowed,MaxLength,MinimumValue,MaximumValue,"
                "DecimalPlaces,CreatedByUserID,UpdatedByUserID"
            )
            self._execute(cursor, f"INSERT INTO tblCustomFieldDefinition ({columns}) VALUES ({','.join(['?'] * 19)})", (
                item["church_id"], item["entity_type"], item["field_key"], item["label"], item["help_text"],
                item["section_label"], item["data_type"], item["privacy_class"], item["display_order"],
                item["required"], item["searchable"], item["report_allowed"], item["export_allowed"],
                item["max_length"], item["minimum_value"], item["maximum_value"], item["decimal_places"],
                item["user_id"], item["user_id"],
            ))
            definition_id = cursor.lastrowid
            self._audit(cursor, item["church_id"], item["user_id"], "CUSTOM_FIELD_CREATED", "DEFINITION", definition_id, definition_id)
            self.connection.commit(); return definition_id
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def set_definition_status(self, current, status, user_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "UPDATE tblCustomFieldDefinition SET LifecycleStatus=?,UpdatedByUserID=?,Version=Version+1 WHERE ID=? AND Version=?",
                          (status, user_id, current["id"], current["version"]))
            if cursor.rowcount != 1: raise RuntimeError("The custom field changed after it was loaded.")
            self._audit(cursor, current["church_id"], user_id, f"CUSTOM_FIELD_{status}", "DEFINITION", current["id"], current["id"])
            self.connection.commit(); return True
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def options(self, definition_id, active_only=False):
        cursor = self.connection.cursor()
        try:
            sql = "SELECT ID id,OptionKey option_key,Label label,DisplayOrder display_order,Active active FROM tblCustomFieldOption WHERE DefinitionID=?"
            if active_only: sql += " AND Active=1"
            sql += " ORDER BY DisplayOrder,Label"
            self._execute(cursor, sql, (definition_id,)); return self._rows(cursor)
        finally: cursor.close()

    def create_option(self, definition, key, label, user_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "INSERT INTO tblCustomFieldOption (DefinitionID,OptionKey,Label,CreatedByUserID,UpdatedByUserID) VALUES (?,?,?,?,?)",
                          (definition["id"], key, label, user_id, user_id))
            option_id = cursor.lastrowid
            self._audit(cursor, definition["church_id"], user_id, "CUSTOM_FIELD_OPTION_CREATED", "OPTION", option_id, definition["id"])
            self.connection.commit(); return option_id
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def profile_church_id(self, entity_type, profile_id):
        table = "tblPerson" if entity_type == "PERSON" else "tblFamily"
        return self._scalar(f"SELECT ChurchID FROM {table} WHERE ID=?", (profile_id,))

    def profile_values(self, entity_type, profile_id, definitions):
        scalar_table, id_column = self._profile_table(entity_type)
        multi_table = "tblPersonCustomFieldOptionValue" if entity_type == "PERSON" else "tblFamilyCustomFieldOptionValue"
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, f"SELECT v.DefinitionID,v.TextValue,v.IntegerValue,v.DecimalValue,v.DateValue,v.BooleanValue,v.OptionID,o.OptionKey FROM {scalar_table} v LEFT JOIN tblCustomFieldOption o ON o.ID=v.OptionID WHERE v.{id_column}=?", (profile_id,))
            scalar = {row[0]: row[1:] for row in cursor.fetchall()}
            self._execute(cursor, f"SELECT m.DefinitionID,o.OptionKey FROM {multi_table} m JOIN tblCustomFieldOption o ON o.ID=m.OptionID WHERE m.{id_column}=? ORDER BY o.DisplayOrder,o.ID", (profile_id,))
            multiple = {}
            for definition_id, option_key in cursor.fetchall(): multiple.setdefault(definition_id, []).append(option_key)
            result = {}
            for definition in definitions:
                definition_id = definition["id"]
                if definition["data_type"] == "MULTIPLE_CHOICE": result[definition["field_key"]] = tuple(multiple.get(definition_id, ()))
                elif definition_id in scalar:
                    values = scalar[definition_id]
                    index = {"SHORT_TEXT": 0, "LONG_TEXT": 0, "INTEGER": 1, "DECIMAL": 2,
                             "DATE": 3, "BOOLEAN": 4, "SINGLE_CHOICE": 5}[definition["data_type"]]
                    value = values[index]
                    if definition["data_type"] == "SINGLE_CHOICE" and value is not None:
                        value = values[6]
                    result[definition["field_key"]] = value
            return result
        finally: cursor.close()

    def save_profile_values(self, entity_type, profile_id, changes, user_id):
        table, id_column = self._profile_table(entity_type)
        multi = "tblPersonCustomFieldOptionValue" if entity_type == "PERSON" else "tblFamilyCustomFieldOptionValue"
        cursor = self.connection.cursor()
        try:
            for definition_id, (definition, value) in changes.items():
                if definition["data_type"] == "MULTIPLE_CHOICE":
                    self._execute(cursor, f"DELETE FROM {multi} WHERE {id_column}=? AND DefinitionID=?", (profile_id, definition_id))
                    for option_key in value or ():
                        option_id = self._option_id(cursor, definition_id, option_key)
                        self._execute(cursor, f"INSERT INTO {multi} ({id_column},DefinitionID,OptionID,AssignedByUserID) VALUES (?,?,?,?)",
                                      (profile_id, definition_id, option_id, user_id))
                else:
                    self._execute(cursor, f"DELETE FROM {table} WHERE {id_column}=? AND DefinitionID=?", (profile_id, definition_id))
                    if value is not None:
                        column = self.VALUE_COLUMNS[definition["data_type"]]
                        stored = self._option_id(cursor, definition_id, value) if column == "OptionID" else value
                        self._execute(cursor, f"INSERT INTO {table} ({id_column},DefinitionID,{column},CreatedByUserID,UpdatedByUserID) VALUES (?,?,?,?,?)",
                                      (profile_id, definition_id, stored, user_id, user_id))
                self._audit(cursor, definition["church_id"], user_id, "CUSTOM_FIELD_VALUE_CHANGED", entity_type, profile_id, definition_id)
            self.connection.commit(); return True
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def tags(self, church_id, entity_type, include_restricted=False, active_only=True):
        cursor = self.connection.cursor()
        try:
            sql = "SELECT ID id,ChurchID church_id,EntityType entity_type,TagKey tag_key,Label label,Description description,PrivacyClass privacy_class,DisplayColor display_color,DisplayOrder display_order,Active active FROM tblProfileTagDefinition WHERE ChurchID=? AND EntityType=?"
            if active_only: sql += " AND Active=1"
            if not include_restricted: sql += " AND PrivacyClass='STANDARD'"
            sql += " ORDER BY DisplayOrder,Label"
            self._execute(cursor, sql, (church_id, entity_type)); return self._rows(cursor)
        finally: cursor.close()

    def tag(self, tag_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT ID id,ChurchID church_id,EntityType entity_type,PrivacyClass privacy_class,Active active FROM tblProfileTagDefinition WHERE ID=?", (tag_id,))
            rows = self._rows(cursor); return rows[0] if rows else None
        finally: cursor.close()

    def tag_key_exists(self, church_id, entity_type, tag_key):
        return bool(self._scalar(
            "SELECT COUNT(*) FROM tblProfileTagDefinition WHERE ChurchID=? AND EntityType=? AND TagKey=?",
            (church_id, entity_type, tag_key),
        ))

    def create_tag(self, item):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "INSERT INTO tblProfileTagDefinition (ChurchID,EntityType,TagKey,Label,Description,PrivacyClass,DisplayColor,DisplayOrder,CreatedByUserID,UpdatedByUserID) VALUES (?,?,?,?,?,?,?,?,?,?)", (
                item["church_id"], item["entity_type"], item["tag_key"], item["label"],
                item["description"], item["privacy_class"], item["display_color"],
                item["display_order"], item["user_id"], item["user_id"],
            ))
            tag_id = cursor.lastrowid
            self._audit(cursor, item["church_id"], item["user_id"], "PROFILE_TAG_CREATED", "TAG", tag_id, None)
            self.connection.commit()
            return tag_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def set_tag_active(self, tag, active, user_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "UPDATE tblProfileTagDefinition SET Active=?,UpdatedByUserID=? WHERE ID=?", (
                int(active), user_id, tag["id"],
            ))
            if cursor.rowcount != 1:
                raise RuntimeError("The profile tag changed after it was loaded.")
            self._audit(cursor, tag["church_id"], user_id, "PROFILE_TAG_ACTIVATED" if active else "PROFILE_TAG_RETIRED", "TAG", tag["id"], None)
            self.connection.commit()
            return True
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def profile_tag_count(self, entity_type, profile_id):
        table = "tblPersonTag" if entity_type == "PERSON" else "tblFamilyTag"
        column = "PersonID" if entity_type == "PERSON" else "FamilyID"
        return int(self._scalar(f"SELECT COUNT(*) FROM {table} WHERE {column}=?", (profile_id,)))

    def set_tag(self, entity_type, profile_id, tag, assigned, user_id):
        table = "tblPersonTag" if entity_type == "PERSON" else "tblFamilyTag"
        column = "PersonID" if entity_type == "PERSON" else "FamilyID"
        cursor = self.connection.cursor()
        try:
            if assigned:
                self._execute(cursor, f"INSERT IGNORE INTO {table} ({column},TagDefinitionID,AssignedByUserID) VALUES (?,?,?)", (profile_id, tag["id"], user_id))
            else:
                self._execute(cursor, f"DELETE FROM {table} WHERE {column}=? AND TagDefinitionID=?", (profile_id, tag["id"]))
            self._audit(cursor, tag["church_id"], user_id, "PROFILE_TAG_ASSIGNED" if assigned else "PROFILE_TAG_REMOVED", entity_type, profile_id, None)
            self.connection.commit(); return True
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def _option_id(self, cursor, definition_id, option_key):
        self._execute(cursor, "SELECT ID FROM tblCustomFieldOption WHERE DefinitionID=? AND OptionKey=? AND Active=1", (definition_id, option_key))
        row = cursor.fetchone()
        if not row: raise ValueError("The selected custom-field choice is unavailable.")
        return row[0]

    @staticmethod
    def _profile_table(entity_type):
        return ("tblPersonCustomFieldValue", "PersonID") if entity_type == "PERSON" else ("tblFamilyCustomFieldValue", "FamilyID")

    def _scalar(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, sql, values); row = cursor.fetchone(); return row[0] if row else None
        finally: cursor.close()

    def _audit(self, cursor, church_id, user_id, action, entity_type, entity_id, definition_id):
        self._execute(cursor, "INSERT INTO tblProfileCustomAuditEvent (ChurchID,UserID,Action,EntityType,EntityID,DefinitionID,SafeSummary) VALUES (?,?,?,?,?,?,?)",
                      (church_id, user_id, action, entity_type, entity_id, definition_id,
                       json.dumps({"changed": True}, separators=(",", ":"))))
