"""Atomic review and approval of READY accounting transactions."""

from __future__ import annotations

import json
from decimal import Decimal

from .draft_service import AccountingDraftError


class AccountingReviewService:
    def __init__(self, connection, acting_user_id):
        self.connection = connection
        self.acting_user_id = int(acting_user_id)
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def list_ready(self):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT t.ID, o.LegalName, t.TransactionDate, t.TransactionType, "
                "t.Description, t.Reference, t.Version, t.CreatedByUserID, "
                "COALESCE(SUM(l.Debit), 0) "
                "FROM tblAccountingTransaction t "
                "JOIN tblAccountingOrganization o ON o.ID=t.OrganizationID "
                "JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID "
                "WHERE t.Status='READY' "
                "GROUP BY t.ID, o.LegalName, t.TransactionDate, t.TransactionType, "
                "t.Description, t.Reference, t.Version, t.CreatedByUserID "
                "ORDER BY t.TransactionDate, t.ID",
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def lines(self, transaction_id):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT l.LineNumber, CONCAT(a.Code, ' - ', a.Name), "
                "CONCAT(f.Code, ' - ', f.Name), l.Description, l.Debit, l.Credit "
                "FROM tblAccountingTransactionLine l "
                "JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "JOIN tblAccountingFund f ON f.ID=l.FundID "
                "WHERE l.TransactionID=? ORDER BY l.LineNumber",
                (transaction_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def approve(self, transaction_id, expected_version, override_reason=None, can_override=False):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT t.OrganizationID, t.CreatedByUserID, t.Status, t.Version, "
                "o.ApprovalThreshold, t.TransactionType, o.ApprovalPolicy "
                "FROM tblAccountingTransaction t "
                "JOIN tblAccountingOrganization o ON o.ID=t.OrganizationID "
                "WHERE t.ID=? FOR UPDATE",
                (transaction_id,),
            )
            header = cursor.fetchone()
            if header is None or header[2] != "READY":
                raise AccountingDraftError("The transaction is no longer awaiting review.")
            if header[3] != expected_version:
                raise AccountingDraftError(
                    "This transaction changed after you opened it. Reload before approving."
                )
            self._execute(
                cursor,
                "SELECT Debit, Credit FROM tblAccountingTransactionLine "
                "WHERE TransactionID=? ORDER BY LineNumber FOR UPDATE",
                (transaction_id,),
            )
            lines = cursor.fetchall()
            debit = sum((Decimal(row[0]) for row in lines), Decimal("0"))
            credit = sum((Decimal(row[1]) for row in lines), Decimal("0"))
            if len(lines) < 2 or debit <= 0 or debit != credit:
                raise AccountingDraftError("The stored transaction is not balanced.")
            threshold = Decimal(header[4])
            independent = debit >= threshold or header[5] == "REVERSAL"
            override_used = independent and header[1] == self.acting_user_id
            reason = (override_reason or "").strip()
            if override_used:
                if header[6] != "INDEPENDENT_PREFERRED" or not can_override:
                    raise AccountingDraftError("You cannot approve a transaction you created under the current approval policy.")
                if not reason:
                    raise AccountingDraftError("Enter a reason for using the solo approval override.")
            self._execute(
                cursor,
                "UPDATE tblAccountingTransaction SET Status='APPROVED', "
                "ReviewedByUserID=?, ReviewedAt=CURRENT_TIMESTAMP(6), "
                "Version=Version+1 WHERE ID=? AND Version=? AND Status='READY'",
                (self.acting_user_id, transaction_id, expected_version),
            )
            if cursor.rowcount != 1:
                raise AccountingDraftError(
                    "This transaction changed after you opened it. Reload before approving."
                )
            after = json.dumps(
                {"status": "APPROVED", "total": str(debit)}, separators=(",", ":")
            )
            action = "TRANSACTION_APPROVED_OVERRIDE" if override_used else "TRANSACTION_APPROVED"
            self._execute(
                cursor,
                "INSERT INTO tblAccountingAuditEvent "
                "(OrganizationID, EntityType, EntityID, Action, AfterJSON, Reason, UserID) "
                "VALUES (?, 'TRANSACTION', ?, ?, ?, ?, ?)",
                (header[0], str(transaction_id), action, after, reason or None, self.acting_user_id),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
