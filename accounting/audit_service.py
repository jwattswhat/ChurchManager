"""Read-only accounting audit history queries."""


class AccountingAuditService:
    def __init__(self, connection):
        self.connection = connection
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def organizations(self):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT ID, LegalName FROM tblAccountingOrganization "
                "ORDER BY LegalName",
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def events(
        self, organization_id=None, user_text="", action_text="",
        entity_text="", date_from=None, date_to=None,
    ):
        if date_from is not None and date_to is not None and date_to < date_from:
            raise ValueError("The Through date cannot be before the From date.")
        conditions, values = [], []
        if organization_id is not None:
            conditions.append("ae.OrganizationID=?")
            values.append(organization_id)
        if user_text.strip():
            conditions.append("(u.DisplayName LIKE ? OR u.Username LIKE ?)")
            pattern = "%{}%".format(user_text.strip())
            values.extend((pattern, pattern))
        if action_text.strip():
            conditions.append("ae.Action LIKE ?")
            values.append("%{}%".format(action_text.strip()))
        if entity_text.strip():
            conditions.append("(ae.EntityType LIKE ? OR ae.EntityID LIKE ?)")
            pattern = "%{}%".format(entity_text.strip())
            values.extend((pattern, pattern))
        if date_from is not None:
            conditions.append("ae.OccurredAt>=?")
            values.append(date_from)
        if date_to is not None:
            conditions.append("ae.OccurredAt<DATE_ADD(?, INTERVAL 1 DAY)")
            values.append(date_to)
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT ae.ID, ae.OccurredAt, o.LegalName, u.DisplayName, "
                "ae.Action, ae.EntityType, ae.EntityID, ae.Reason, "
                "ae.BeforeJSON, ae.AfterJSON "
                "FROM tblAccountingAuditEvent ae "
                "JOIN tblAccountingOrganization o ON o.ID=ae.OrganizationID "
                "JOIN tblUser u ON u.ID=ae.UserID" + where +
                " ORDER BY ae.OccurredAt DESC, ae.ID DESC LIMIT 1000",
                tuple(values),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
