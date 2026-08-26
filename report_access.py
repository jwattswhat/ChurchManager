"""Fail-closed report catalog authorization."""

from authorization import AuthorizationDenied


class ReportAccessService:
    def __init__(self, connection, authorization):
        self.connection = connection
        self.authorization = authorization
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def _catalog_rows(self):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT r.ID,r.Report,r.Title,p.Name "
                "FROM tblReports r "
                "JOIN tblPermission p ON p.ID=r.RequiredPermissionID AND p.Active=1 "
                "WHERE r.Available=1 "
                "AND r.Report NOT IN ('CFCA01','CFCR01','CFGR01','CMDN01','CMDN02') "
                "ORDER BY r.Title"
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def allowed_reports(self):
        return tuple(
            row for row in self._catalog_rows()
            if self.authorization.has_permission(row[3])
        )

    def require_report(self, report_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT r.Report,p.Name FROM tblReports r "
                "JOIN tblPermission p ON p.ID=r.RequiredPermissionID AND p.Active=1 "
                "WHERE r.ID=? AND r.Available=1", (report_id,)
            )
            row = cursor.fetchone()
        finally:
            cursor.close()
        if row is None:
            raise AuthorizationDenied("This report is unavailable or has no valid permission.")
        self.authorization.require(row[1], "run report {}".format(row[0]))
        return row

    def configure_picker(self, control, customized_codes=()):
        rows = self.allowed_reports()
        if hasattr(control, "SetCatalogRows"):
            customized_codes = set(customized_codes)
            control.SetCatalogRows([
                {
                    "id": row[0],
                    "values": [
                        row[1], row[2],
                        "Customized" if row[1] in customized_codes else "Starter",
                    ],
                    "foreground": "#0066CC" if row[1] in customized_codes else None,
                }
                for row in rows
            ])
            return len(rows)
        control.choices.id = [row[0] for row in rows]
        control.choices.display = ["{} ({})".format(row[2], row[1]) for row in rows]
        control.choices.fielddata = [[row[2], "({})".format(row[1])] for row in rows]
        control.Set(control.choices.display)
        control.ChangeValue("")
        return len(rows)
