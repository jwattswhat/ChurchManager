"""Atomic accounting posting and permanent transaction numbering."""

from __future__ import annotations

import json
from decimal import Decimal

from .draft_service import AccountingDraftError


class AccountingPostingService:
    def __init__(self, connection, acting_user_id):
        self.connection = connection
        self.acting_user_id = int(acting_user_id)
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def list_postable(self):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT t.ID, o.LegalName, t.TransactionDate, t.Status, t.Description, "
                "t.Reference, t.Version, COALESCE(SUM(l.Debit),0) "
                "FROM tblAccountingTransaction t "
                "JOIN tblAccountingOrganization o ON o.ID=t.OrganizationID "
                "JOIN tblAccountingTransactionLine l ON l.TransactionID=t.ID "
                "WHERE t.Status IN ('READY','APPROVED') "
                "GROUP BY t.ID, o.LegalName, t.TransactionDate, t.Status, t.Description, "
                "t.Reference, t.Version ORDER BY t.TransactionDate, t.ID")
            return cursor.fetchall()
        finally:
            cursor.close()

    def lines(self, transaction_id):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT l.LineNumber, CONCAT(a.Code, ' - ', a.Name), "
                "CONCAT(f.Code, ' - ', f.Name), l.Description, l.Debit, l.Credit "
                "FROM tblAccountingTransactionLine l "
                "JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "JOIN tblAccountingFund f ON f.ID=l.FundID "
                "WHERE l.TransactionID=? ORDER BY l.LineNumber", (transaction_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    def post(self, transaction_id, expected_version):
        cursor = self.connection.cursor()
        try:
            self._execute(cursor,
                "SELECT t.OrganizationID, t.FiscalPeriodID, t.Status, t.Version, "
                "t.CreatedByUserID, t.ReviewedByUserID, o.ApprovalThreshold, "
                "o.NextTransactionNumber, t.OriginalTransactionID, "
                "EXISTS(SELECT 1 FROM tblAccountingAuditEvent ae WHERE "
                "ae.EntityType='TRANSACTION' AND CAST(ae.EntityID AS UNSIGNED)=t.ID "
                "AND ae.Action='TRANSACTION_APPROVED_OVERRIDE' "
                "AND ae.UserID=t.ReviewedByUserID) AS HasApprovalOverride "
                ", t.TransactionType, o.AttachmentThreshold "
                "FROM tblAccountingTransaction t "
                "JOIN tblAccountingOrganization o ON o.ID=t.OrganizationID "
                "WHERE t.ID=? FOR UPDATE", (transaction_id,))
            header = cursor.fetchone()
            if header is None or header[2] not in ("READY", "APPROVED"):
                raise AccountingDraftError("The transaction is no longer available for posting.")
            if header[3] != expected_version:
                raise AccountingDraftError(
                    "This transaction changed after you opened it. Reload before posting."
                )
            self._execute(cursor,
                "SELECT p.Status, y.Status FROM tblAccountingFiscalPeriod p "
                "JOIN tblAccountingFiscalYear y ON y.ID=p.FiscalYearID "
                "WHERE p.ID=? FOR UPDATE", (header[1],))
            period = cursor.fetchone()
            if period is None or period[0] != "OPEN" or period[1] != "OPEN":
                raise AccountingDraftError("The transaction's fiscal period is not open.")
            self._execute(cursor,
                "SELECT l.Debit, l.Credit, a.Active, a.PostingAllowed, f.Active, "
                "fn.Active, a.FunctionRequirement, l.FunctionID "
                "FROM tblAccountingTransactionLine l "
                "JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "JOIN tblAccountingFund f ON f.ID=l.FundID "
                "LEFT JOIN tblAccountingFunction fn ON fn.ID=l.FunctionID "
                "WHERE l.TransactionID=? ORDER BY l.LineNumber FOR UPDATE",
                (transaction_id,))
            lines = cursor.fetchall()
            debit = sum((Decimal(row[0]) for row in lines), Decimal("0"))
            credit = sum((Decimal(row[1]) for row in lines), Decimal("0"))
            if len(lines) < 2 or debit <= 0 or debit != credit:
                raise AccountingDraftError("The stored transaction is not balanced.")
            for row in lines:
                if not row[2] or not row[3] or not row[4]:
                    raise AccountingDraftError("A transaction account or fund is inactive.")
                if row[7] is not None and not row[5]:
                    raise AccountingDraftError("A transaction function is inactive.")
                if row[6] == "REQUIRED" and row[7] is None:
                    raise AccountingDraftError("A required functional classification is missing.")
                if row[6] == "PROHIBITED" and row[7] is not None:
                    raise AccountingDraftError("A prohibited functional classification is present.")
            attachment_required = (
                header[10] == "RESTRICTION_RELEASE"
                or (header[10] == "CASH_DISBURSEMENT" and debit >= Decimal(header[11]))
            )
            if attachment_required:
                self._execute(
                    cursor,
                    "SELECT COUNT(*) FROM tblAccountingAttachment WHERE TransactionID=?",
                    (transaction_id,),
                )
                if cursor.fetchone()[0] < 1:
                    raise AccountingDraftError(
                        "This transaction requires a receipt, invoice, or voucher, "
                        "or its supporting authority, before it can be posted."
                    )
            threshold = Decimal(header[6])
            independent_required = (
                debit >= threshold or header[8] is not None
                or header[10] == "RESTRICTION_RELEASE"
            )
            valid_independent_approval = (
                header[2] == "APPROVED" and header[5] is not None
                and (header[5] != header[4] or bool(header[9]))
            )
            if independent_required and not valid_independent_approval:
                raise AccountingDraftError(
                    "This transaction requires approval by a different user before posting."
                )
            number = header[7]
            self._execute(cursor,
                "UPDATE tblAccountingOrganization SET NextTransactionNumber=? "
                "WHERE ID=? AND NextTransactionNumber=?",
                (number + 1, header[0], number))
            if cursor.rowcount != 1:
                raise AccountingDraftError("The next transaction number changed. Try again.")
            self._execute(cursor,
                "UPDATE tblAccountingTransaction SET Status='POSTED', TransactionNumber=?, "
                "PostedByUserID=?, PostedAt=CURRENT_TIMESTAMP(6), Version=Version+1 "
                "WHERE ID=? AND Version=? AND Status IN ('READY','APPROVED')",
                (number, self.acting_user_id, transaction_id, expected_version))
            if cursor.rowcount != 1:
                raise AccountingDraftError(
                    "This transaction changed after you opened it. Reload before posting."
                )
            if header[8] is not None:
                self._execute(cursor, "UPDATE tblAccountingTransaction SET Status='REVERSED', ReversalTransactionID=?, Version=Version+1 WHERE ID=? AND Status='POSTED' AND ReversalTransactionID IS NULL", (transaction_id, header[8]))
                if cursor.rowcount != 1: raise AccountingDraftError("The original transaction can no longer be reversed.")
            after = json.dumps({"status":"POSTED", "transaction_number":number,
                                "total":str(debit)}, separators=(",", ":"))
            self._execute(cursor,
                "INSERT INTO tblAccountingAuditEvent "
                "(OrganizationID, EntityType, EntityID, Action, AfterJSON, UserID) "
                "VALUES (?, 'TRANSACTION', ?, 'TRANSACTION_POSTED', ?, ?)",
                (header[0], str(transaction_id), after, self.acting_user_id))
            self.connection.commit()
            return number
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
