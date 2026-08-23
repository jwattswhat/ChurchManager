"""Parameterized MariaDB persistence and safe audit for pastoral-care work."""

from __future__ import annotations

import json

class PastoralCareConflictError(RuntimeError):
    """Raised when a record changed since the user loaded it."""


class MariaDBPastoralCareRepository:
    """Persist operational pastoral care and its non-narrative audit events."""

    def __init__(self, connection):
        self.connection = connection
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    @staticmethod
    def _rows(cursor):
        names = [column[0] for column in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]

    def work_list(self, assigned_user_id=None):
        """Return safe dashboard fields; restricted-note tables are never joined."""

        cursor = self.connection.cursor()
        try:
            sql = (
                "SELECT n.ID AS id,n.ChurchID AS church_id,n.PersonID AS person_id,"
                "n.FamilyID AS family_id,"
                "COALESCE(NULLIF(TRIM(CONCAT_WS(' ',p.FirstName,p.LastName)),''),"
                "f.FamilyName,n.DisplaySubject) "
                "AS display_subject,n.Category AS category,n.AssignedUserID AS assigned_user_id,"
                "u.DisplayName AS assignee,n.Priority AS priority,n.Status AS status,"
                "n.DueDate AS due_date,n.NextFollowUpDate AS next_follow_up_date,"
                "n.ScheduleText AS schedule_text,n.ScheduleStatus AS schedule_status,"
                "n.Version AS version FROM tblPastoralCareNeed n "
                "LEFT JOIN tblPerson p ON p.ID=n.PersonID "
                "LEFT JOIN tblFamily f ON f.ID=n.FamilyID "
                "LEFT JOIN tblUser u ON u.ID=n.AssignedUserID "
                "WHERE n.Status IN ('OPEN','WAITING')"
            )
            values = ()
            if assigned_user_id is not None:
                sql += " AND n.AssignedUserID=?"
                values = (assigned_user_id,)
            sql += " ORDER BY COALESCE(n.NextFollowUpDate,n.DueDate,'9999-12-31'),n.Priority DESC,n.ID"
            self._execute(cursor, sql, values)
            return self._rows(cursor)
        finally:
            cursor.close()

    def need(self, care_need_id):
        """Return one safe operational record without ciphertext or narrative."""

        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT n.ID AS id,n.ChurchID AS church_id,n.PersonID AS person_id,"
                "n.FamilyID AS family_id,n.DisplaySubject AS display_subject,n.Category AS category,"
                "n.Source AS source,n.AssignedUserID AS assigned_user_id,u.DisplayName AS assignee,"
                "n.Priority AS priority,"
                "n.Status AS status,n.OpenedDate AS opened_date,n.DueDate AS due_date,"
                "n.NextFollowUpDate AS next_follow_up_date,n.ScheduleText AS schedule_text,"
                "n.ScheduleRule AS schedule_rule,n.ScheduleStatus AS schedule_status,"
                "n.CompletedDate AS completed_date,n.ClosedDate AS closed_date,"
                "n.SafeSummary AS safe_summary,n.Version AS version "
                "FROM tblPastoralCareNeed n LEFT JOIN tblUser u ON u.ID=n.AssignedUserID "
                "WHERE n.ID=?",
                (care_need_id,),
            )
            rows = self._rows(cursor)
            return rows[0] if rows else None
        finally:
            cursor.close()

    def history(self, care_need_id):
        """Return non-restricted action history for one care need."""

        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT a.ID AS id,a.ActionDateTime AS action_datetime,"
                "u.DisplayName AS caregiver,a.ActionType AS action_type,"
                "a.Result AS result,a.SafeOutcome AS safe_outcome,"
                "a.NextFollowUpDate AS next_follow_up_date "
                "FROM tblPastoralCareAction a JOIN tblUser u ON u.ID=a.CaregiverUserID "
                "WHERE a.CareNeedID=? ORDER BY a.ActionDateTime DESC,a.ID DESC",
                (care_need_id,),
            )
            return self._rows(cursor)
        finally:
            cursor.close()

    def choices(self):
        """Return safe maintained choices needed by the care editors."""

        return {
            "churches": self._choice_rows("SELECT ID,Church FROM tblChurch ORDER BY Church"),
            "people": self._choice_rows(
                "SELECT ID,TRIM(CONCAT_WS(' ',FirstName,LastName)) FROM tblPerson "
                "ORDER BY LastName,FirstName"
            ),
            "families": self._choice_rows(
                "SELECT ID,FamilyName FROM tblFamily ORDER BY FamilyName"
            ),
            "users": self._choice_rows(
                "SELECT ID,DisplayName FROM tblUser WHERE Active=1 ORDER BY DisplayName"
            ),
            "categories": _choice_values(self._choice_rows(
                "SELECT ID,Choices FROM tblChoices WHERE Field='PastoralCareCategory' "
                "ORDER BY Choices"
            )),
        }

    def default_church_id(self):
        """Return the sole congregation ID, or ``None`` when it is ambiguous."""

        rows = self._choice_rows("SELECT ID,Church FROM tblChurch ORDER BY Church")
        return rows[0][0] if len(rows) == 1 else None

    def church_id_for_name(self, church_name):
        """Resolve one exact displayed congregation name to its identifier."""

        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT ID FROM tblChurch WHERE Church=? ORDER BY ID",
                (str(church_name or "").strip(),),
            )
            rows = cursor.fetchall()
            return rows[0][0] if len(rows) == 1 else None
        finally:
            cursor.close()

    def _choice_rows(self, sql):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()

    def create_need(self, values):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "INSERT INTO tblPastoralCareNeed "
                "(ChurchID,PersonID,FamilyID,DisplaySubject,Category,Source,AssignedUserID,"
                "Priority,Status,OpenedDate,DueDate,NextFollowUpDate,ScheduleText,ScheduleRule,"
                "ScheduleStatus,SafeSummary,CreatedByUserID,UpdatedByUserID) "
                "VALUES (?,?,?,?,?,?,?,?, 'OPEN',?,?,?,?,?,?,?,?,?)",
                (
                    values["church_id"], values.get("person_id"), values.get("family_id"),
                    values.get("display_subject"), values["category"], values["source"],
                    values.get("assigned_user_id"), values["priority"], values["opened_date"],
                    values.get("due_date"), values.get("next_follow_up_date"),
                    values.get("schedule_text"), values.get("schedule_rule"),
                    values.get("schedule_status"), values.get("safe_summary"),
                    values["created_by_user_id"], values["created_by_user_id"],
                ),
            )
            care_need_id = cursor.lastrowid
            self._audit(cursor, values["created_by_user_id"], "PASTORAL_CARE_CREATED", care_need_id)
            self.connection.commit()
            return care_need_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def assign(self, record, assignee, version, user_id):
        cursor = self.connection.cursor()
        try:
            if assignee is not None:
                self._execute(cursor, "SELECT Active FROM tblUser WHERE ID=?", (assignee,))
                row = cursor.fetchone()
                if not row or not row[0]:
                    raise ValueError("The selected caregiver is unavailable.")
            self._execute(
                cursor,
                "UPDATE tblPastoralCareNeed SET AssignedUserID=?,UpdatedByUserID=?,"
                "Version=Version+1 WHERE ID=? AND Version=?",
                (assignee, user_id, record["id"], version),
            )
            self._require_one(cursor)
            self._audit(cursor, user_id, "PASTORAL_CARE_ASSIGNED", record["id"])
            self.connection.commit()
            return True
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def record_action(self, record, values):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "INSERT INTO tblPastoralCareAction "
                "(CareNeedID,ActionDateTime,CaregiverUserID,ActionType,Result,SafeOutcome,"
                "NextFollowUpDate,CreatedByUserID,UpdatedByUserID) VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    record["id"], values["action_datetime"], values["caregiver_user_id"],
                    values["action_type"], values["result"], values.get("safe_outcome"),
                    values.get("next_follow_up_date"), values["created_by_user_id"],
                    values["created_by_user_id"],
                ),
            )
            action_id = cursor.lastrowid
            if values.get("next_follow_up_date") is not None:
                self._execute(
                    cursor,
                    "UPDATE tblPastoralCareNeed SET NextFollowUpDate=?,UpdatedByUserID=?,"
                    "Version=Version+1 WHERE ID=? AND Version=?",
                    (values["next_follow_up_date"], values["created_by_user_id"],
                     record["id"], record["version"]),
                )
                self._require_one(cursor)
            self._audit(cursor, values["created_by_user_id"], "PASTORAL_ACTION_RECORDED", action_id,
                        entity_type="PastoralCareAction")
            self.connection.commit()
            return action_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def change_status(self, record, status, version, user_id):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "UPDATE tblPastoralCareNeed SET Status=?,"
                "CompletedDate=CASE WHEN ?='COMPLETED' THEN CURRENT_DATE ELSE NULL END,"
                "ClosedDate=CASE WHEN ?='CLOSED_NOT_NEEDED' THEN CURRENT_DATE ELSE NULL END,"
                "UpdatedByUserID=?,Version=Version+1 WHERE ID=? AND Version=?",
                (status, status, status, user_id, record["id"], version),
            )
            self._require_one(cursor)
            self._audit(cursor, user_id, "PASTORAL_STATUS_CHANGED", record["id"])
            self.connection.commit()
            return True
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def _audit(self, cursor, user_id, action, entity_id, entity_type="PastoralCareNeed"):
        self._execute(
            cursor,
            "INSERT INTO tblSecurityAuditEvent (UserID,Action,EntityType,EntityID) "
            "VALUES (?,?,?,?)",
            (user_id, action, entity_type, str(entity_id)),
        )

    @staticmethod
    def _require_one(cursor):
        if cursor.rowcount != 1:
            raise PastoralCareConflictError(
                "This pastoral care record changed. Reopen it and try again."
            )


def _choice_values(rows):
    """Parse the maintained JSON or historical bracketed-line choice format."""

    if not rows:
        return []
    text = str(rows[0][1] or "").strip()
    try:
        values = json.loads(text)
    except (TypeError, ValueError):
        values = None
    if not isinstance(values, list):
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1]
        values = text.splitlines()
    return [str(value).strip() for value in values if str(value).strip()]
