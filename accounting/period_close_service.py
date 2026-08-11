"""Atomic, audited fiscal-period close and reopen operations."""

import json

from .close_checklist_service import CloseChecklistService


class PeriodCloseService:
    def __init__(self, connection, acting_user_id, checklist=None):
        self.connection = connection
        self.acting_user_id = int(acting_user_id)
        self.checklist = checklist or CloseChecklistService(connection)
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def close(self, organization_id, period_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT p.Status,p.Name,p.StartDate,p.EndDate FROM tblAccountingFiscalPeriod p "
                "JOIN tblAccountingFiscalYear y ON y.ID=p.FiscalYearID "
                "WHERE p.ID=? AND y.OrganizationID=? FOR UPDATE",
                (period_id, organization_id))
            period = cursor.fetchone()
            if period is None or period[0] != "OPEN":
                raise ValueError("Select an open fiscal period.")
            result = self.checklist.run(organization_id, period_id)
            blockers = [item["check"] for item in result["checks"]
                        if item["status"] != "CLEAR"]
            if blockers:
                raise ValueError("The period cannot be closed until these checks are clear: {}.".format(
                    ", ".join(blockers)))
            self._execute(cursor,
                "UPDATE tblAccountingFiscalPeriod SET Status='CLOSED' "
                "WHERE ID=? AND Status='OPEN'", (period_id,))
            if cursor.rowcount != 1:
                raise ValueError("The fiscal period changed. Run the checklist again.")
            after = json.dumps({"status":"CLOSED", "period":period[1],
                                "start":str(period[2]), "end":str(period[3])},
                               separators=(",", ":"))
            self._execute(cursor,
                "INSERT INTO tblAccountingAuditEvent "
                "(OrganizationID,EntityType,EntityID,Action,AfterJSON,UserID) "
                "VALUES (?,'FISCAL_PERIOD',?,'PERIOD_CLOSED',?,?)",
                (organization_id, str(period_id), after, self.acting_user_id))
            self.connection.commit()
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()

    def reopen(self, organization_id, period_id, reason):
        reason = (reason or "").strip()
        if not reason:
            raise ValueError("Enter a reason for reopening the fiscal period.")
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT p.Status,p.Name,o.ApprovalPolicy FROM tblAccountingFiscalPeriod p "
                "JOIN tblAccountingFiscalYear y ON y.ID=p.FiscalYearID "
                "JOIN tblAccountingOrganization o ON o.ID=y.OrganizationID "
                "WHERE p.ID=? AND y.OrganizationID=? FOR UPDATE",
                (period_id, organization_id))
            period = cursor.fetchone()
            if period is None or period[0] != "CLOSED":
                raise ValueError("Select a closed fiscal period.")
            self._execute(cursor,
                "SELECT UserID FROM tblAccountingAuditEvent WHERE OrganizationID=? "
                "AND EntityType='FISCAL_PERIOD' AND CAST(EntityID AS UNSIGNED)=? "
                "AND Action='PERIOD_CLOSED' ORDER BY OccurredAt DESC,ID DESC LIMIT 1",
                (organization_id, period_id))
            closed = cursor.fetchone()
            same_user = closed is not None and closed[0] == self.acting_user_id
            if same_user and period[2] == "INDEPENDENT_REQUIRED":
                raise ValueError(
                    "A different authorized user must reopen this period under the current policy."
                )
            action = "PERIOD_REOPENED_OVERRIDE" if same_user else "PERIOD_REOPENED"
            self._execute(cursor,
                "UPDATE tblAccountingFiscalPeriod SET Status='OPEN' "
                "WHERE ID=? AND Status='CLOSED'", (period_id,))
            if cursor.rowcount != 1:
                raise ValueError("The fiscal period changed. Reload before reopening.")
            after = json.dumps({"status":"OPEN", "period":period[1],
                                "solo_override":same_user}, separators=(",", ":"))
            self._execute(cursor,
                "INSERT INTO tblAccountingAuditEvent "
                "(OrganizationID,EntityType,EntityID,Action,AfterJSON,Reason,UserID) "
                "VALUES (?,'FISCAL_PERIOD',?,?,?,?,?)",
                (organization_id, str(period_id), action, after, reason,
                 self.acting_user_id))
            self.connection.commit()
        except Exception:
            self.connection.rollback(); raise
        finally: cursor.close()
