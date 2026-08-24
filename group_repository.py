"""Parameterized MariaDB persistence for congregational Groups."""

from __future__ import annotations


class GroupConflictError(RuntimeError):
    """Raised when a Group record changed after it was loaded."""


class MariaDBGroupRepository:
    """Persist Group identity and dated membership without exposing private data."""

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

    def list_groups(self, church_id, status=None, include_restricted=False):
        cursor = self.connection.cursor()
        try:
            sql = (
                "SELECT g.ID id,g.ChurchID church_id,g.GroupKey group_key,g.Name name,"
                "g.GroupTypeID group_type_id,t.Label group_type,g.Description description,"
                "g.Status status,g.StartDate start_date,g.EndDate end_date,"
                "g.ExpectedClosureDate expected_closure_date,g.UsualMeetingDescription usual_meeting_description,"
                "g.DefaultLocation default_location,g.CommunicationEnabled communication_enabled,"
                "g.PrivacyClass privacy_class,g.Notes notes,g.Version version,"
                "SUM(CASE WHEN m.StartDate<=CURRENT_DATE AND (m.EndDate IS NULL OR m.EndDate>=CURRENT_DATE) THEN 1 ELSE 0 END) current_members "
                "FROM tblGroup g JOIN tblGroupType t ON t.ID=g.GroupTypeID "
                "LEFT JOIN tblGroupMembership m ON m.GroupID=g.ID WHERE g.ChurchID=?"
            )
            values = [church_id]
            if not include_restricted:
                sql += " AND g.PrivacyClass='STANDARD'"
            if status:
                sql += " AND g.Status=?"
                values.append(str(status).upper())
            sql += " GROUP BY g.ID,t.Label ORDER BY g.Name,g.ID"
            self._execute(cursor, sql, tuple(values))
            return self._rows(cursor)
        finally:
            cursor.close()

    def group(self, group_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, (
                "SELECT g.ID id,g.ChurchID church_id,g.GroupKey group_key,g.Name name,"
                "g.GroupTypeID group_type_id,t.Label group_type,g.Description description,"
                "g.Status status,g.StartDate start_date,g.EndDate end_date,"
                "g.ExpectedClosureDate expected_closure_date,g.UsualMeetingDescription usual_meeting_description,"
                "g.DefaultLocation default_location,g.CommunicationEnabled communication_enabled,"
                "g.PrivacyClass privacy_class,g.Notes notes,g.Version version "
                "FROM tblGroup g JOIN tblGroupType t ON t.ID=g.GroupTypeID WHERE g.ID=?"
            ), (group_id,))
            rows = self._rows(cursor)
            return rows[0] if rows else None
        finally:
            cursor.close()

    def choices(self, church_id):
        return {
            "types": self._choice_rows("SELECT ID,Label FROM tblGroupType WHERE ChurchID=? AND Active=1 ORDER BY DisplayOrder,Label", (church_id,)),
            "people": self._choice_rows("SELECT ID,TRIM(CONCAT_WS(' ',FirstName,LastName)) FROM tblPerson WHERE ChurchID=? ORDER BY LastName,FirstName", (church_id,)),
            "roles": self._choice_rows("SELECT ID,Label FROM tblGroupRole WHERE ChurchID=? AND Active=1 ORDER BY DisplayOrder,Label", (church_id,)),
        }

    def churches(self):
        """Return congregations available to the Groups workspace."""
        return self._choice_rows("SELECT ID,Church FROM tblChurch ORDER BY Church")

    def _choice_rows(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def create_group(self, values):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, (
                "INSERT INTO tblGroup (ChurchID,GroupKey,Name,GroupTypeID,Description,Status,StartDate,EndDate,"
                "PrivacyClass,Notes,CreatedByUserID,UpdatedByUserID) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
            ), (values["church_id"], values["group_key"], values["name"], values["group_type_id"],
                values.get("description"), values["status"], values.get("start_date"), values.get("end_date"),
                values["privacy_class"], values.get("notes"), values["created_by_user_id"], values["created_by_user_id"]))
            group_id = cursor.lastrowid
            self._audit(cursor, values["created_by_user_id"], "GROUP_CREATED", group_id)
            self.connection.commit()
            return group_id
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def update_group(self, current, values, version):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, (
                "UPDATE tblGroup SET GroupKey=?,Name=?,GroupTypeID=?,Description=?,Status=?,StartDate=?,EndDate=?,"
                "PrivacyClass=?,Notes=?,UpdatedByUserID=?,Version=Version+1 WHERE ID=? AND Version=?"
            ), (values["group_key"], values["name"], values["group_type_id"], values.get("description"),
                values["status"], values.get("start_date"), values.get("end_date"), values["privacy_class"],
                values.get("notes"), values["updated_by_user_id"], current["id"], version))
            self._require_one(cursor)
            self._audit(cursor, values["updated_by_user_id"], "GROUP_UPDATED", current["id"])
            self.connection.commit()
            return True
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def person_church_id(self, person_id):
        rows = self._choice_rows("SELECT ChurchID,ID FROM tblPerson WHERE ID=?", (person_id,))
        return rows[0][0] if rows else None

    def membership_overlaps(self, group_id, person_id, start_date, end_date):
        rows = self._choice_rows(
            "SELECT ID,PersonID FROM tblGroupMembership WHERE GroupID=? AND PersonID=? "
            "AND StartDate<=COALESCE(?,'9999-12-31') AND COALESCE(EndDate,'9999-12-31')>=? LIMIT 1",
            (group_id, person_id, end_date, start_date),
        )
        return bool(rows)

    def create_membership(self, values):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, (
                "INSERT INTO tblGroupMembership (GroupID,PersonID,StartDate,EndDate,Notes,CreatedByUserID,UpdatedByUserID) "
                "VALUES (?,?,?,?,?,?,?)"
            ), (values["group_id"], values["person_id"], values["start_date"], values.get("end_date"),
                values.get("notes"), values["user_id"], values["user_id"]))
            membership_id = cursor.lastrowid
            self._audit(cursor, values["user_id"], "GROUP_MEMBERSHIP_CREATED", membership_id, "GroupMembership")
            self.connection.commit()
            return membership_id
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def memberships(self, group_id, current_only=True):
        cursor = self.connection.cursor()
        try:
            sql = (
                "SELECT m.ID id,m.PersonID person_id,TRIM(CONCAT_WS(' ',p.FirstName,p.LastName)) person,"
                "m.StartDate start_date,m.EndDate end_date,m.Notes notes,m.Version version "
                "FROM tblGroupMembership m JOIN tblPerson p ON p.ID=m.PersonID WHERE m.GroupID=?"
            )
            if current_only:
                sql += " AND m.StartDate<=CURRENT_DATE AND (m.EndDate IS NULL OR m.EndDate>=CURRENT_DATE)"
            sql += " ORDER BY p.LastName,p.FirstName,m.StartDate"
            self._execute(cursor, sql, (group_id,))
            return self._rows(cursor)
        finally:
            cursor.close()

    def membership(self, membership_id):
        """Return one membership with its Group privacy and Church scope."""
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, (
                "SELECT m.ID id,m.GroupID group_id,m.PersonID person_id,m.StartDate start_date,"
                "m.EndDate end_date,m.Notes notes,m.Version version,g.ChurchID church_id,"
                "g.PrivacyClass privacy_class FROM tblGroupMembership m "
                "JOIN tblGroup g ON g.ID=m.GroupID WHERE m.ID=?"
            ), (membership_id,))
            rows = self._rows(cursor); return rows[0] if rows else None
        finally:
            cursor.close()

    def end_membership(self, record, end_date, user_id):
        """Close one membership term without deleting its history."""
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, (
                "UPDATE tblGroupMembership SET EndDate=?,UpdatedByUserID=?,Version=Version+1 "
                "WHERE ID=? AND Version=?"
            ), (end_date, user_id, record["id"], record["version"]))
            self._require_one(cursor)
            self._audit(cursor, user_id, "GROUP_MEMBERSHIP_ENDED", record["id"], "GroupMembership")
            self.connection.commit(); return True
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def membership_roles(self, membership_id, current_only=True):
        """Return dated roles assigned to one membership term."""
        cursor = self.connection.cursor()
        try:
            sql = (
                "SELECT mr.ID id,mr.GroupRoleID group_role_id,r.Label role,mr.StartDate start_date,"
                "mr.EndDate end_date,mr.Version version FROM tblGroupMembershipRole mr "
                "JOIN tblGroupRole r ON r.ID=mr.GroupRoleID WHERE mr.GroupMembershipID=?"
            )
            if current_only:
                sql += " AND mr.StartDate<=CURRENT_DATE AND (mr.EndDate IS NULL OR mr.EndDate>=CURRENT_DATE)"
            sql += " ORDER BY r.DisplayOrder,r.Label,mr.StartDate"
            self._execute(cursor, sql, (membership_id,)); return self._rows(cursor)
        finally:
            cursor.close()

    def role_church_id(self, role_id):
        rows = self._choice_rows("SELECT ChurchID,ID FROM tblGroupRole WHERE ID=? AND Active=1", (role_id,))
        return rows[0][0] if rows else None

    def role_overlaps(self, membership_id, role_id, start_date, end_date):
        rows = self._choice_rows(
            "SELECT ID,GroupRoleID FROM tblGroupMembershipRole WHERE GroupMembershipID=? AND GroupRoleID=? "
            "AND StartDate<=COALESCE(?,'9999-12-31') AND COALESCE(EndDate,'9999-12-31')>=? LIMIT 1",
            (membership_id, role_id, end_date, start_date),
        )
        return bool(rows)

    def assign_role(self, values):
        """Create one dated role assignment transactionally."""
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, (
                "INSERT INTO tblGroupMembershipRole (GroupMembershipID,GroupRoleID,StartDate,EndDate,"
                "CreatedByUserID,UpdatedByUserID) VALUES (?,?,?,?,?,?)"
            ), (values["membership_id"], values["role_id"], values["start_date"], values.get("end_date"),
                values["user_id"], values["user_id"]))
            assignment_id = cursor.lastrowid
            self._audit(cursor, values["user_id"], "GROUP_ROLE_ASSIGNED", assignment_id, "GroupMembershipRole")
            self.connection.commit(); return assignment_id
        except Exception:
            self.connection.rollback(); raise
        finally:
            cursor.close()

    def _audit(self, cursor, user_id, action, entity_id, entity_type="Group"):
        self._execute(cursor, "INSERT INTO tblSecurityAuditEvent (UserID,Action,EntityType,EntityID) VALUES (?,?,?,?)",
                      (user_id, action, entity_type, str(entity_id)))

    @staticmethod
    def _require_one(cursor):
        if cursor.rowcount != 1:
            raise GroupConflictError("This Group changed. Reopen it and try again.")
