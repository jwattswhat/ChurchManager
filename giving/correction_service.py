"""Create auditable replacements for immutable posted contribution batches."""

from __future__ import annotations

import json

from bulletin_orders import portable_connection
from giving.validation import GivingValidationError


class PostedBatchCorrectionService:
    """Create a linked accounting reversal and editable replacement batch."""

    def __init__(self, connection, user_id: int, authorization):
        self.connection = portable_connection(connection)
        self.user_id = int(user_id)
        self.authorization = authorization

    def create(self, original_batch_id: int, reversal_date, reason: str) -> tuple[int, int]:
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
                "WHERE ID=? AND Status='POSTED' FOR UPDATE", (original_batch_id,),
            )
            batch = cursor.fetchone()
            if not batch:
                raise GivingValidationError("Only a posted contribution batch can be corrected.")
            if batch[11] is not None or batch[12] is not None:
                raise GivingValidationError("A correction already exists for this contribution batch.")
            if batch[10] is None:
                raise GivingValidationError("The posted batch has no linked accounting transaction.")

            cursor.execute(
                "SELECT OrganizationID,TransactionNumber,Status,OriginalTransactionID,ReversalTransactionID "
                "FROM tblAccountingTransaction WHERE ID=? FOR UPDATE", (batch[10],),
            )
            original = cursor.fetchone()
            if not original or original[2] != "POSTED" or original[3] is not None or original[4] is not None:
                raise GivingValidationError("The linked accounting transaction cannot be reversed.")
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
                 reversal_date, batch[6], batch[7], batch[8], batch[9], self.user_id,
                 original_batch_id, reason),
            )
            replacement_id = cursor.lastrowid
            cursor.execute(
                "SELECT ID,ContributorID,EnteredEnvelopeNumber,ContributionMethod,ReferenceValue,ReceivedDate,"
                "Amount,StatementEligibility,Note,DirectionStatus FROM tblContribution WHERE BatchID=? ORDER BY ID",
                (original_batch_id,),
            )
            for gift in cursor.fetchall():
                cursor.execute(
                    "INSERT INTO tblContribution "
                    "(BatchID,CorrectionOfContributionID,ContributorID,EnteredEnvelopeNumber,ContributionMethod,"
                    "ReferenceValue,ReceivedDate,Amount,StatementEligibility,Note,DirectionStatus) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)", (replacement_id, gift[0], *gift[1:]),
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
            self.connection.commit()
            return replacement_id, reversal_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
