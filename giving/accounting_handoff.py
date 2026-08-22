"""Privacy-safe handoff from the giving subledger to fund accounting."""

from __future__ import annotations

import json
from collections import defaultdict
from decimal import Decimal

from bulletin_orders import portable_connection
from giving.validation import GivingValidationError


class GivingAccountingHandoff:
    """Create one summarized accounting receipt for a reviewed giving batch."""

    def __init__(self, connection, user_id: int, authorization):
        self.connection = portable_connection(connection)
        self.user_id = int(user_id)
        self.authorization = authorization

    def send(self, batch_id: int) -> int:
        """Link a Ready batch to a new Ready transaction, without donor detail."""
        self.authorization.require("giving.batches.post", "send a Giving batch to accounting")
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT b.ChurchID,b.OrganizationID,b.DepositDate,b.Status,b.CalculatedTotal,"
                "b.AccountingTransactionID,b.Description,ba.AccountID,a.FunctionRequirement,b.CorrectsBatchID "
                "FROM tblContributionBatch b LEFT JOIN tblAccountingBankAccount ba ON ba.ID=b.BankAccountID "
                "LEFT JOIN tblAccountingAccount a ON a.ID=ba.AccountID "
                "WHERE b.ID=? FOR UPDATE", (batch_id,),
            )
            batch = cursor.fetchone()
            if not batch:
                raise GivingValidationError("The selected contribution batch is unavailable.")
            if batch[3] != "READY" or batch[5] is not None:
                raise GivingValidationError("Only an unlinked Ready batch can be sent to accounting.")
            if batch[2] is None or batch[7] is None:
                raise GivingValidationError("The deposit date and receiving bank account are required.")
            if batch[8] == "REQUIRED":
                raise GivingValidationError("The receiving bank account cannot require a functional classification.")
            if batch[9] is not None:
                cursor.execute("SELECT Status FROM tblContributionBatch WHERE ID=? FOR UPDATE", (batch[9],))
                corrected = cursor.fetchone()
                if not corrected or corrected[0] != "VOID":
                    raise GivingValidationError(
                        "Post the linked accounting reversal before sending the replacement batch."
                    )

            cursor.execute(
                "SELECT p.ID FROM tblAccountingFiscalPeriod p JOIN tblAccountingFiscalYear y ON y.ID=p.FiscalYearID "
                "WHERE y.OrganizationID=? AND ? BETWEEN p.StartDate AND p.EndDate "
                "AND y.Status='OPEN' AND p.Status='OPEN'", (batch[1], batch[2]),
            )
            periods = cursor.fetchall()
            if len(periods) != 1:
                raise GivingValidationError("The deposit date must belong to exactly one open fiscal period.")

            cursor.execute(
                "SELECT a.FundID,a.RevenueAccountID,a.FunctionID,SUM(a.Amount) "
                "FROM tblContributionAllocation a JOIN tblContribution g ON g.ID=a.ContributionID "
                "WHERE g.BatchID=? GROUP BY a.FundID,a.RevenueAccountID,a.FunctionID "
                "HAVING SUM(a.Amount)>0 "
                "ORDER BY a.FundID,a.RevenueAccountID,a.FunctionID", (batch_id,),
            )
            credits = cursor.fetchall()
            if not credits:
                raise GivingValidationError("The contribution batch has no accounting allocations.")
            total = sum((Decimal(row[3]) for row in credits), Decimal("0.00"))
            if total != Decimal(batch[4]):
                raise GivingValidationError("The accounting allocations do not equal the batch total.")
            debits = defaultdict(lambda: Decimal("0.00"))
            for fund_id, _account_id, _function_id, amount in credits:
                debits[fund_id] += Decimal(amount)

            description = f"Contribution deposit - {batch[6]}"[:1000]
            reference = f"Giving batch {batch_id}"
            cursor.execute(
                "INSERT INTO tblAccountingTransaction "
                "(OrganizationID,TransactionDate,FiscalPeriodID,TransactionType,Status,Description,Reference,CreatedByUserID) "
                "VALUES (?,?,?,'CASH_RECEIPT','READY',?,?,?)",
                (batch[1], batch[2], periods[0][0], description, reference, self.user_id),
            )
            transaction_id = cursor.lastrowid
            line_number = 1
            for fund_id, amount in sorted(debits.items()):
                cursor.execute(
                    "INSERT INTO tblAccountingTransactionLine "
                    "(TransactionID,LineNumber,AccountID,FundID,FunctionID,Description,Debit,Credit) "
                    "VALUES (?,?,?,?,NULL,'Contribution deposit',?,0.00)",
                    (transaction_id, line_number, batch[7], fund_id, amount),
                )
                line_number += 1
            for fund_id, account_id, function_id, amount in credits:
                cursor.execute(
                    "INSERT INTO tblAccountingTransactionLine "
                    "(TransactionID,LineNumber,AccountID,FundID,FunctionID,Description,Debit,Credit) "
                    "VALUES (?,?,?,?,?,'Contribution revenue',0.00,?)",
                    (transaction_id, line_number, account_id, fund_id, function_id, amount),
                )
                line_number += 1

            safe = json.dumps({"status": "READY", "total": str(total),
                               "giving_batch_id": batch_id}, separators=(",", ":"))
            cursor.execute(
                "INSERT INTO tblAccountingAuditEvent "
                "(OrganizationID,EntityType,EntityID,Action,AfterJSON,UserID) "
                "VALUES (?,'TRANSACTION',?,'GIVING_BATCH_SENT',?,?)",
                (batch[1], str(transaction_id), safe, self.user_id),
            )
            cursor.execute(
                "UPDATE tblContributionBatch SET AccountingTransactionID=?,Version=Version+1 "
                "WHERE ID=? AND Status='READY' AND AccountingTransactionID IS NULL",
                (transaction_id, batch_id),
            )
            if cursor.rowcount != 1:
                raise GivingValidationError("The contribution batch changed before it could be linked.")
            cursor.execute(
                "INSERT INTO tblContributionAuditEvent "
                "(ChurchID,UserID,Action,EntityType,EntityID,SafeReference) "
                "VALUES (?,?,'BATCH_SENT_TO_ACCOUNTING','BATCH',?,?)",
                (batch[0], self.user_id, batch_id, reference),
            )
            self.connection.commit()
            return transaction_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
