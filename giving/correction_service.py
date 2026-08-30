"""Create auditable replacements for immutable posted contribution batches."""

from __future__ import annotations

import json

from bulletin_orders import portable_connection
from giving.validation import (
    GivingValidationError,
    require_giving_bank_account,
    require_giving_organization,
)


class PostedBatchCorrectionService:
    """Create a linked accounting reversal and editable replacement batch."""

    def __init__(self, connection, user_id: int, authorization):
        self.connection = portable_connection(connection)
        self.user_id = int(user_id)
        self.authorization = authorization

    def posted_checks(self, original_batch_id: int):
        """Return checks eligible for the explicit returned-check workflow."""
        self.authorization.require("giving.batches.post", "record a returned contribution check")
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT g.ID,COALESCE(c.DisplayName,'Unidentified contributor'),g.ReferenceValue,g.Amount "
                "FROM tblContribution g LEFT JOIN tblContributionContributor c ON c.ID=g.ContributorID "
                "JOIN tblContributionBatch b ON b.ID=g.BatchID "
                "LEFT JOIN tblContributionReturn r ON r.OriginalContributionID=g.ID "
                "WHERE g.BatchID=? AND b.ChurchID=(SELECT ID FROM tblChurch ORDER BY ID LIMIT 1) "
                "AND b.Status='POSTED' AND g.ContributionMethod='CHECK' AND r.ID IS NULL "
                "ORDER BY c.DisplayName,g.ID", (original_batch_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def create(self, original_batch_id: int, reversal_date, reason: str,
               returned_contribution_id: int | None = None) -> tuple[int, int]:
        """Return ``(replacement_batch_id, reversal_transaction_id)`` atomically."""
        self.authorization.require("giving.batches.post", "correct a posted Giving batch")
        reason = str(reason or "").strip()
        if not reason:
            raise GivingValidationError("Enter the reason for correcting this posted batch.")
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT ChurchID,BatchDate,Description,ServiceID,AttendanceEventID,DepositDate,"
                "OrganizationID,BankAccountID,ControlTotal,CalculatedTotal,AccountingTransactionID,"
                "CorrectionBatchID,ReversalAccountingTransactionID FROM tblContributionBatch "
                "WHERE ID=? AND ChurchID=(SELECT ID FROM tblChurch ORDER BY ID LIMIT 1) "
                "AND Status='POSTED' FOR UPDATE", (original_batch_id,),
            )
            batch = cursor.fetchone()
            if not batch:
                raise GivingValidationError("Only a posted contribution batch can be corrected.")
            if batch[11] is not None or batch[12] is not None:
                raise GivingValidationError("A correction already exists for this contribution batch.")
            if batch[10] is None:
                raise GivingValidationError("The posted batch has no linked accounting transaction.")
            require_giving_organization(cursor, batch[0], batch[6])
            require_giving_bank_account(cursor, batch[6], batch[7])

            returned = None
            if returned_contribution_id is not None:
                cursor.execute(
                    "SELECT g.ID,g.ContributionMethod,g.Amount FROM tblContribution g "
                    "LEFT JOIN tblContributionReturn r ON r.OriginalContributionID=g.ID "
                    "WHERE g.ID=? AND g.BatchID=? AND r.ID IS NULL FOR UPDATE",
                    (returned_contribution_id, original_batch_id),
                )
                returned = cursor.fetchone()
                if not returned or returned[1] != "CHECK":
                    raise GivingValidationError("Select an unreturned check from this posted batch.")

            cursor.execute(
                "SELECT OrganizationID,TransactionNumber,Status,OriginalTransactionID,ReversalTransactionID "
                "FROM tblAccountingTransaction WHERE ID=? FOR UPDATE", (batch[10],),
            )
            original = cursor.fetchone()
            if not original or original[2] != "POSTED" or original[3] is not None or original[4] is not None:
                raise GivingValidationError("The linked accounting transaction cannot be reversed.")
            if original[0] != batch[6]:
                raise GivingValidationError(
                    "The linked accounting transaction belongs to another organization."
                )
            cursor.execute(
                "SELECT COUNT(*) FROM tblAccountingTransactionLine l "
                "LEFT JOIN tblAccountingAccount a ON a.ID=l.AccountID "
                "LEFT JOIN tblAccountingFund f ON f.ID=l.FundID "
                "LEFT JOIN tblAccountingFunction fn ON fn.ID=l.FunctionID "
                "LEFT JOIN tblAccountingPayee payee ON payee.ID=l.PayeeID "
                "WHERE l.TransactionID=? AND (a.ID IS NULL OR a.OrganizationID<>? "
                "OR f.ID IS NULL OR f.OrganizationID<>? "
                "OR (l.FunctionID IS NOT NULL AND (fn.ID IS NULL OR fn.OrganizationID<>?)) "
                "OR (l.PayeeID IS NOT NULL AND (payee.ID IS NULL OR payee.OrganizationID<>?)))",
                (batch[10], batch[6], batch[6], batch[6], batch[6]),
            )
            if cursor.fetchone()[0]:
                raise GivingValidationError(
                    "The linked accounting transaction contains an invalid accounting destination."
                )
            cursor.execute(
                "SELECT COUNT(*) FROM tblContributionAllocation ca "
                "JOIN tblContribution g ON g.ID=ca.ContributionID "
                "LEFT JOIN tblContributionPurpose p ON p.ID=ca.PurposeID "
                "LEFT JOIN tblAccountingFund f ON f.ID=ca.FundID "
                "LEFT JOIN tblAccountingAccount a ON a.ID=ca.RevenueAccountID "
                "LEFT JOIN tblAccountingFunction fn ON fn.ID=ca.FunctionID "
                "WHERE g.BatchID=? AND (ca.OrganizationID<>? OR p.ID IS NULL "
                "OR p.ChurchID<>? OR p.OrganizationID<>? "
                "OR f.ID IS NULL OR f.OrganizationID<>? "
                "OR a.ID IS NULL OR a.OrganizationID<>? "
                "OR (ca.FunctionID IS NOT NULL AND (fn.ID IS NULL OR fn.OrganizationID<>?)))",
                (original_batch_id, batch[6], batch[0], batch[6], batch[6], batch[6], batch[6]),
            )
            if cursor.fetchone()[0]:
                raise GivingValidationError(
                    "The posted batch contains an invalid Giving allocation."
                )
            cursor.execute(
                "SELECT COUNT(*) FROM tblContribution g "
                "LEFT JOIN tblContributionContributor c ON c.ID=g.ContributorID "
                "WHERE g.BatchID=? AND g.ContributorID IS NOT NULL "
                "AND (c.ID IS NULL OR c.ChurchID<>?)",
                (original_batch_id, batch[0]),
            )
            if cursor.fetchone()[0]:
                raise GivingValidationError(
                    "The posted batch contains a contributor from another church."
                )
            cursor.execute(
                "SELECT p.ID FROM tblAccountingFiscalPeriod p JOIN tblAccountingFiscalYear y "
                "ON y.ID=p.FiscalYearID WHERE y.OrganizationID=? AND ? BETWEEN p.StartDate AND p.EndDate "
                "AND y.Status='OPEN' AND p.Status='OPEN' FOR UPDATE", (batch[6], reversal_date),
            )
            periods = cursor.fetchall()
            if len(periods) != 1:
                raise GivingValidationError("The correction date must belong to exactly one open fiscal period.")
            cursor.execute(
                "SELECT LineNumber,AccountID,FundID,FunctionID,PayeeID,Description,Debit,Credit "
                "FROM tblAccountingTransactionLine WHERE TransactionID=? ORDER BY LineNumber FOR UPDATE",
                (batch[10],),
            )
            lines = cursor.fetchall()
            cursor.execute(
                "INSERT INTO tblAccountingTransaction "
                "(OrganizationID,TransactionDate,FiscalPeriodID,TransactionType,Status,Description,Reference,"
                "OriginalTransactionID,CreatedByUserID) VALUES (?,?,?,'REVERSAL','READY',?,?,?,?)",
                (batch[6], reversal_date, periods[0][0],
                 f"Correction of giving batch {original_batch_id}: {reason}"[:1000],
                 f"Giving batch {original_batch_id} correction", batch[10], self.user_id),
            )
            reversal_id = cursor.lastrowid
            for line in lines:
                cursor.execute(
                    "INSERT INTO tblAccountingTransactionLine "
                    "(TransactionID,LineNumber,AccountID,FundID,FunctionID,PayeeID,Description,Debit,Credit) "
                    "VALUES (?,?,?,?,?,?,?,?,?)", (reversal_id, *line[:6], line[7], line[6]),
                )
            cursor.execute(
                "INSERT INTO tblContributionBatch "
                "(ChurchID,BatchDate,Description,ServiceID,AttendanceEventID,DepositDate,OrganizationID,"
                "BankAccountID,Status,ControlTotal,CalculatedTotal,EnteredByUserID,CorrectsBatchID,CorrectionReason) "
                "VALUES (?,?,?,?,?,?,?,?, 'DRAFT',?,?, ?,?,?)",
                (batch[0], reversal_date, f"Correction - {batch[2]}"[:255], batch[3], batch[4],
                 reversal_date, batch[6], batch[7],
                 (batch[8] - returned[2]) if returned and batch[8] is not None else batch[8],
                 batch[9] - returned[2] if returned else batch[9], self.user_id,
                 original_batch_id, reason),
            )
            replacement_id = cursor.lastrowid
            cursor.execute(
                "SELECT ID,ContributorID,EnteredEnvelopeNumber,ContributionMethod,ReferenceValue,ReceivedDate,"
                "Amount,NonCashDescription,DonorEstimatedValue,StatementEligibility,GoodsOrServicesProvided,"
                "GoodsOrServicesDescription,GoodsOrServicesValue,IntangibleReligiousBenefitOnly,"
                "EligibilityOverrideReason,TributeType,HonoreeName,AcknowledgmentContact,"
                "DonorDisclosureAuthorized,AmountDisclosureAuthorized,DonorDirection,DirectionStatus,"
                "DirectionResolution,Note FROM tblContribution WHERE BatchID=? ORDER BY ID",
                (original_batch_id,),
            )
            for gift in cursor.fetchall():
                if returned and gift[0] == returned[0]:
                    continue
                cursor.execute(
                    "INSERT INTO tblContribution "
                    "(BatchID,CorrectionOfContributionID,ContributorID,EnteredEnvelopeNumber,ContributionMethod,"
                    "ReferenceValue,ReceivedDate,Amount,NonCashDescription,DonorEstimatedValue,StatementEligibility,"
                    "GoodsOrServicesProvided,GoodsOrServicesDescription,GoodsOrServicesValue,"
                    "IntangibleReligiousBenefitOnly,EligibilityOverrideReason,TributeType,HonoreeName,"
                    "AcknowledgmentContact,DonorDisclosureAuthorized,AmountDisclosureAuthorized,"
                    "DonorDirection,DirectionStatus,DirectionResolution,Note) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (replacement_id, gift[0], *gift[1:]),
                )
                new_gift_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO tblContributionAllocation "
                    "(ContributionID,PurposeID,OrganizationID,FundID,RevenueAccountID,FunctionID,Amount,DonorRestrictionNote) "
                    "SELECT ?,PurposeID,OrganizationID,FundID,RevenueAccountID,FunctionID,Amount,DonorRestrictionNote "
                    "FROM tblContributionAllocation WHERE ContributionID=? ORDER BY ID", (new_gift_id, gift[0]),
                )
            cursor.execute(
                "UPDATE tblContributionBatch SET CorrectionBatchID=?,ReversalAccountingTransactionID=?,"
                "CorrectionReason=?,Version=Version+1 WHERE ID=? AND CorrectionBatchID IS NULL",
                (replacement_id, reversal_id, reason, original_batch_id),
            )
            if cursor.rowcount != 1:
                raise GivingValidationError("The posted batch changed before its correction could be linked.")
            audit_json = json.dumps({"status": "READY", "original_transaction_id": batch[10],
                                     "giving_batch_id": original_batch_id}, separators=(",", ":"))
            cursor.execute(
                "INSERT INTO tblAccountingAuditEvent "
                "(OrganizationID,EntityType,EntityID,Action,AfterJSON,Reason,UserID) "
                "VALUES (?,'TRANSACTION',?,'GIVING_REVERSAL_CREATED',?,?,?)",
                (batch[6], str(reversal_id), audit_json, reason, self.user_id),
            )
            cursor.execute(
                "INSERT INTO tblContributionAuditEvent "
                "(ChurchID,UserID,Action,EntityType,EntityID,SafeReference) "
                "VALUES (?,?,'POSTED_BATCH_CORRECTION_CREATED','BATCH',?,?)",
                (batch[0], self.user_id, original_batch_id,
                 f"Replacement batch {replacement_id}; reversal transaction {reversal_id}"),
            )
            if returned:
                cursor.execute(
                    "INSERT INTO tblContributionReturn "
                    "(ChurchID,OriginalContributionID,OriginalBatchID,ReplacementBatchID,"
                    "ReversalAccountingTransactionID,ReturnDate,Reason,RecordedByUserID) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (batch[0], returned[0], original_batch_id, replacement_id, reversal_id,
                     reversal_date, reason, self.user_id),
                )
                cursor.execute(
                    "INSERT INTO tblContributionAuditEvent "
                    "(ChurchID,UserID,Action,EntityType,EntityID,SafeReference,Reason) "
                    "VALUES (?,?,'CONTRIBUTION_CHECK_RETURNED','CONTRIBUTION',?,?,?)",
                    (batch[0], self.user_id, returned[0],
                     f"Replacement batch {replacement_id}; reversal transaction {reversal_id}", reason),
                )
            self.connection.commit()
            return replacement_id, reversal_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def create_returned_check(self, original_batch_id: int, contribution_id: int,
                              return_date, reason: str) -> tuple[int, int]:
        """Correct a posted batch while omitting one returned check from its replacement."""
        return self.create(original_batch_id, return_date, reason, contribution_id)
