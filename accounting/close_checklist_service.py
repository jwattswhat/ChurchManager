"""Read-only safeguards evaluated before an accounting period is closed."""

from decimal import Decimal


def check(label, blocked, clear_detail, blocked_detail):
    return {
        "check": label,
        "status": "BLOCKED" if blocked else "CLEAR",
        "detail": blocked_detail if blocked else clear_detail,
    }


class CloseChecklistService:
    def __init__(self, connection):
        self.connection = connection
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def organizations(self):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT ID,LegalName FROM tblAccountingOrganization "
                                  "WHERE Active=1 ORDER BY LegalName")
            return cursor.fetchall()
        finally: cursor.close()

    def periods(self, organization_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT p.ID,CONCAT(y.Name,' - ',p.Name,' (',p.StartDate,' through ',p.EndDate,')') "
                "FROM tblAccountingFiscalPeriod p JOIN tblAccountingFiscalYear y "
                "ON y.ID=p.FiscalYearID WHERE y.OrganizationID=? "
                "ORDER BY p.StartDate DESC", (organization_id,))
            return cursor.fetchall()
        finally: cursor.close()

    def run(self, organization_id, period_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT p.StartDate,p.EndDate,p.Status,y.Name,p.Name "
                "FROM tblAccountingFiscalPeriod p JOIN tblAccountingFiscalYear y "
                "ON y.ID=p.FiscalYearID WHERE p.ID=? AND y.OrganizationID=?",
                (period_id, organization_id))
            period = cursor.fetchone()
            if period is None: raise ValueError("Select a fiscal period for this organization.")
            start, end = period[0], period[1]
            results = [check("Period status", period[2] != "OPEN",
                             "The period is open.", "The period is already {}.".format(period[2]))]

            self._execute(cursor,
                "SELECT COUNT(*) FROM tblAccountingTransaction WHERE OrganizationID=? "
                "AND TransactionDate BETWEEN ? AND ? AND Status IN ('DRAFT','READY','APPROVED')",
                (organization_id, start, end))
            count = cursor.fetchone()[0]
            results.append(check("Unposted transactions", count,
                                 "No unposted transactions remain in the period.",
                                 "{} draft, ready, or approved transaction(s) remain.".format(count)))

            self._execute(cursor,
                "SELECT COUNT(*) FROM (SELECT t.ID FROM tblAccountingTransaction t "
                "JOIN tblAccountingOrganization o ON o.ID=t.OrganizationID "
                "JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID "
                "WHERE t.OrganizationID=? AND t.TransactionDate BETWEEN ? AND ? "
                "AND t.Status IN ('READY','APPROVED') AND ("
                "t.TransactionType='RESTRICTION_RELEASE' OR "
                "t.TransactionType='CASH_DISBURSEMENT') "
                "GROUP BY t.ID,t.TransactionType,o.AttachmentThreshold "
                "HAVING (t.TransactionType='RESTRICTION_RELEASE' OR "
                "SUM(l.Debit)>=o.AttachmentThreshold) AND NOT EXISTS ("
                "SELECT 1 FROM tblAccountingAttachment a WHERE a.TransactionID=t.ID)) missing",
                (organization_id, start, end))
            count = cursor.fetchone()[0]
            results.append(check("Required source documents", count,
                                 "All transactions requiring documents have them.",
                                 "{} transaction(s) are missing required documents.".format(count)))

            self._execute(cursor,
                "SELECT COUNT(*) FROM tblAccountingBankImportRow r "
                "JOIN tblAccountingBankImportBatch b ON b.ID=r.ImportBatchID "
                "JOIN tblAccountingBankAccount ba ON ba.ID=b.BankAccountID "
                "WHERE ba.OrganizationID=? AND r.TransactionDate<=? "
                "AND r.MatchStatus='UNMATCHED'", (organization_id, end))
            count = cursor.fetchone()[0]
            results.append(check("Unmatched bank activity", count,
                                 "No unmatched imported bank rows remain through period end.",
                                 "{} unmatched bank row(s) remain through period end.".format(count)))

            self._execute(cursor,
                "SELECT COUNT(*) FROM tblAccountingReconciliation r "
                "JOIN tblAccountingBankAccount b ON b.ID=r.BankAccountID "
                "WHERE b.OrganizationID=? AND r.StatementDate<=? AND r.Status='DRAFT'",
                (organization_id, end))
            count = cursor.fetchone()[0]
            results.append(check("Draft reconciliations", count,
                                 "No draft reconciliations remain through period end.",
                                 "{} reconciliation draft(s) remain.".format(count)))

            self._execute(cursor,
                "SELECT COUNT(*) FROM tblAccountingBankAccount b WHERE b.OrganizationID=? "
                "AND b.Active=1 AND NOT EXISTS (SELECT 1 FROM tblAccountingReconciliation r "
                "WHERE r.BankAccountID=b.ID AND r.Status='COMPLETED' "
                "AND r.StatementDate>=?)", (organization_id, end))
            count = cursor.fetchone()[0]
            results.append(check("Completed bank statements", count,
                                 "Every active bank account has a completed reconciliation through period end.",
                                 "{} active bank account(s) lack a completed reconciliation through period end.".format(count)))

            self._execute(cursor,
                "SELECT COALESCE(SUM(l.Debit-l.Credit),0) "
                "FROM tblAccountingTransactionLine l JOIN tblAccountingTransaction t "
                "ON t.ID=l.TransactionID WHERE t.OrganizationID=? "
                "AND t.Status IN ('POSTED','REVERSED') AND t.TransactionDate<=?",
                (organization_id, end))
            difference = Decimal(cursor.fetchone()[0])
            results.append(check("Ledger balance", difference != 0,
                                 "Posted debits and credits balance through period end.",
                                 "Posted ledger difference is {}.".format(difference)))
            return {"period": "{} - {}".format(period[3], period[4]),
                    "start": start, "end": end, "status": period[2], "checks": results,
                    "ready": all(item["status"] == "CLEAR" for item in results)}
        finally: cursor.close()
