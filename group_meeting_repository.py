"""Parameterized persistence for Group meetings and their attendance."""

from __future__ import annotations


class GroupMeetingConflictError(RuntimeError):
    """Raised when a meeting changed after it was displayed."""


class MariaDBGroupMeetingRepository:
    """Store dated meetings and Person attendance without touching worship attendance."""

    def __init__(self, connection):
        self.connection = connection
        self.marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    @staticmethod
    def _rows(cursor):
        names = [column[0] for column in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]

    def _all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, sql, values)
            return self._rows(cursor)
        finally:
            cursor.close()

    def meetings(self, group_id):
        """Return meeting history in reverse chronological order."""
        return self._all(
            "SELECT ID id,GroupID group_id,StartsAt starts_at,EndsAt ends_at,Title title,"
            "Location location,Status status,AttendanceMode attendance_mode,TotalHeadCount total_head_count,"
            "RescheduledToMeetingID rescheduled_to_meeting_id,Notes notes,Version version "
            "FROM tblGroupMeeting WHERE GroupID=? ORDER BY StartsAt DESC,ID DESC", (group_id,)
        )

    def meeting(self, meeting_id):
        rows = self._all(
            "SELECT m.ID id,m.GroupID group_id,m.StartsAt starts_at,m.EndsAt ends_at,m.Title title,"
            "m.Location location,m.Status status,m.AttendanceMode attendance_mode,m.TotalHeadCount total_head_count,"
            "m.RescheduledToMeetingID rescheduled_to_meeting_id,m.Notes notes,m.Version version,"
            "g.ChurchID church_id,g.PrivacyClass privacy_class,g.Status group_status "
            "FROM tblGroupMeeting m JOIN tblGroup g ON g.ID=m.GroupID WHERE m.ID=?", (meeting_id,)
        )
        return rows[0] if rows else None

    def create_meeting(self, values):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "INSERT INTO tblGroupMeeting (GroupID,StartsAt,EndsAt,Title,Location,Status,"
                          "AttendanceMode,TotalHeadCount,Notes,CreatedByUserID,UpdatedByUserID) "
                          "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                          (values["group_id"], values["starts_at"], values.get("ends_at"), values["title"],
                           values.get("location"), values["status"], values["attendance_mode"],
                           values.get("total_head_count"), values.get("notes"), values["user_id"], values["user_id"]))
            meeting_id = cursor.lastrowid
            self._audit(cursor, values["user_id"], "GROUP_MEETING_CREATED", "GroupMeeting", meeting_id)
            self.connection.commit(); return meeting_id
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def roster_for_date(self, group_id, meeting_id, meeting_date):
        """Return the effective roster plus any existing guest attendance rows."""
        return self._all(
            "SELECT p.ID person_id,TRIM(CONCAT_WS(' ',p.FirstName,p.LastName)) person,"
            "CASE WHEN m.ID IS NULL THEN 0 ELSE 1 END is_member "
            "FROM tblPerson p LEFT JOIN tblGroupMembership m ON m.PersonID=p.ID AND m.GroupID=? "
            "AND m.StartDate<=? AND (m.EndDate IS NULL OR m.EndDate>=?) "
            "WHERE p.ChurchID=(SELECT ChurchID FROM tblGroup WHERE ID=?) "
            "AND (m.ID IS NOT NULL OR p.ID IN (SELECT PersonID FROM tblGroupMeetingAttendance WHERE GroupMeetingID=?)) "
            "ORDER BY is_member DESC,p.LastName,p.FirstName,p.ID",
            (group_id, meeting_date, meeting_date, group_id, meeting_id),
        )

    def attendance(self, meeting_id):
        return self._all(
            "SELECT a.ID id,a.PersonID person_id,TRIM(CONCAT_WS(' ',p.FirstName,p.LastName)) person,"
            "a.AttendanceStatus attendance_status,a.ArrivedAt arrived_at,a.DepartedAt departed_at,"
            "a.Notes notes,a.Version version FROM tblGroupMeetingAttendance a "
            "JOIN tblPerson p ON p.ID=a.PersonID WHERE a.GroupMeetingID=? ORDER BY p.LastName,p.FirstName",
            (meeting_id,),
        )

    def available_people(self, church_id):
        return self._all("SELECT ID id,TRIM(CONCAT_WS(' ',FirstName,LastName)) person FROM tblPerson "
                         "WHERE ChurchID=? ORDER BY LastName,FirstName,ID", (church_id,))

    def replace_attendance(self, meeting, entries, total_head_count, user_id):
        """Replace the displayed Person statuses in one audited transaction."""
        cursor = self.connection.cursor()
        try:
            for person_id, status in entries:
                self._execute(cursor, "INSERT INTO tblGroupMeetingAttendance "
                              "(GroupMeetingID,PersonID,AttendanceStatus,RecordedByUserID,UpdatedByUserID) "
                              "VALUES (?,?,?,?,?) ON DUPLICATE KEY UPDATE AttendanceStatus=VALUES(AttendanceStatus),"
                              "UpdatedByUserID=VALUES(UpdatedByUserID),Version=Version+1",
                              (meeting["id"], person_id, status, user_id, user_id))
            self._execute(cursor, "UPDATE tblGroupMeeting SET TotalHeadCount=?,Status=CASE WHEN Status='SCHEDULED' "
                          "THEN 'HELD' ELSE Status END,UpdatedByUserID=?,Version=Version+1 "
                          "WHERE ID=? AND Version=?", (total_head_count, user_id, meeting["id"], meeting["version"]))
            if cursor.rowcount != 1: raise GroupMeetingConflictError("This meeting changed. Reopen it and try again.")
            self._audit(cursor, user_id, "GROUP_ATTENDANCE_RECORDED", "GroupMeeting", meeting["id"])
            self.connection.commit(); return True
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def add_guest(self, meeting_id, person_id, user_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "INSERT INTO tblGroupMeetingAttendance "
                          "(GroupMeetingID,PersonID,AttendanceStatus,RecordedByUserID,UpdatedByUserID) "
                          "VALUES (?,?, 'UNKNOWN',?,?)", (meeting_id, person_id, user_id, user_id))
            self._audit(cursor, user_id, "GROUP_ATTENDANCE_GUEST_ADDED", "GroupMeeting", meeting_id)
            self.connection.commit(); return True
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def _audit(self, cursor, user_id, action, entity_type, entity_id):
        self._execute(cursor, "INSERT INTO tblSecurityAuditEvent (UserID,Action,EntityType,EntityID) VALUES (?,?,?,?)",
                      (user_id, action, entity_type, str(entity_id)))
