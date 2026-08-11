"""Atomic bank-statement reconciliation without ledger writes."""

from __future__ import annotations

import json
from decimal import Decimal


class BankReconciliationService:
    def __init__(self, connection, acting_user_id):
        self.connection = connection
        self.acting_user_id = int(acting_user_id)
        self.marker = (
            "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"
        )

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def bank_accounts(self):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT b.ID,CONCAT(b.Name,' - ',a.Code,' ',a.Name) "
                "FROM tblAccountingBankAccount b "
                "JOIN tblAccountingAccount a ON a.ID=b.AccountID "
                "WHERE b.Active=1 ORDER BY b.Name",
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def create_draft(self, bank_account_id, statement_date,
                     beginning_balance, ending_balance):
        beginning = Decimal(str(beginning_balance)).quantize(Decimal("0.01"))
        ending = Decimal(str(ending_balance)).quantize(Decimal("0.01"))
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT OrganizationID FROM tblAccountingBankAccount "
                "WHERE ID=? AND Active=1 FOR UPDATE",
                (bank_account_id,),
            )
            account = cursor.fetchone()
            if account is None:
                raise ValueError("Select an active bank account.")
            self._execute(
                cursor,
                "SELECT ID FROM tblAccountingReconciliation "
                "WHERE BankAccountID=? AND StatementDate=?",
                (bank_account_id, statement_date),
            )
            if cursor.fetchone() is not None:
                raise ValueError("A reconciliation already exists for this statement date.")
            self._execute(
                cursor,
                "SELECT MAX(StatementDate) FROM tblAccountingReconciliation "
                "WHERE BankAccountID=? AND Status='COMPLETED'",
                (bank_account_id,),
            )
            previous_date = cursor.fetchone()[0]
            self._execute(
                cursor,
                "INSERT INTO tblAccountingReconciliation "
                "(BankAccountID,StatementDate,BeginningBalance,EndingBalance,PreparedByUserID) "
                "VALUES (?,?,?,?,?)",
                (
                    bank_account_id, statement_date, beginning, ending,
                    self.acting_user_id,
                ),
            )
            reconciliation_id = cursor.lastrowid
            self._execute(
                cursor,
                "INSERT INTO tblAccountingReconciliationItem "
                "(ReconciliationID,TransactionLineID,ImportRowID,ClearedDate,ClearedAmount) "
                "SELECT ?,r.MatchedTransactionLineID,r.ID,r.TransactionDate,r.Amount "
                "FROM tblAccountingBankImportRow r "
                "JOIN tblAccountingBankImportBatch i ON i.ID=r.ImportBatchID "
                "WHERE i.BankAccountID=? AND r.MatchStatus='MATCHED' "
                "AND r.TransactionDate<=? AND (? IS NULL OR r.TransactionDate>?) "
                "AND NOT EXISTS (SELECT 1 FROM tblAccountingReconciliationItem used "
                " WHERE used.ImportRowID=r.ID OR "
                " used.TransactionLineID=r.MatchedTransactionLineID)",
                (
                    reconciliation_id, bank_account_id, statement_date,
                    previous_date, previous_date,
                ),
            )
            self._audit(
                cursor, account[0], reconciliation_id, "BANK_RECONCILIATION_CREATED",
                {
                    "statement_date": statement_date.isoformat(),
                    "beginning_balance": str(beginning),
                    "ending_balance": str(ending),
                },
            )
            self.connection.commit()
            return reconciliation_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def reconciliations(self):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT r.ID,b.Name,r.StatementDate,r.BeginningBalance,r.EndingBalance,"
                "COALESCE(SUM(x.ClearedAmount),0),"
                "r.BeginningBalance+COALESCE(SUM(x.ClearedAmount),0),"
                "r.EndingBalance-(r.BeginningBalance+COALESCE(SUM(x.ClearedAmount),0)),"
                "r.Status,COUNT(x.ID) "
                "FROM tblAccountingReconciliation r "
                "JOIN tblAccountingBankAccount b ON b.ID=r.BankAccountID "
                "LEFT JOIN tblAccountingReconciliationItem x ON x.ReconciliationID=r.ID "
                "GROUP BY r.ID,b.Name,r.StatementDate,r.BeginningBalance,r.EndingBalance,r.Status "
                "ORDER BY r.StatementDate DESC,r.ID DESC",
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def complete(self, reconciliation_id):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT r.BankAccountID,r.StatementDate,r.BeginningBalance,r.EndingBalance,"
                "r.Status,b.OrganizationID "
                "FROM tblAccountingReconciliation r "
                "JOIN tblAccountingBankAccount b ON b.ID=r.BankAccountID "
                "WHERE r.ID=? FOR UPDATE",
                (reconciliation_id,),
            )
            header = cursor.fetchone()
            if header is None or header[4] != "DRAFT":
                raise ValueError("Select a draft reconciliation.")
            self._execute(
                cursor,
                "SELECT MAX(StatementDate) FROM tblAccountingReconciliation "
                "WHERE BankAccountID=? AND Status='COMPLETED' AND StatementDate<?",
                (header[0], header[1]),
            )
            previous_date = cursor.fetchone()[0]
            self._execute(
                cursor,
                "SELECT COUNT(*) FROM tblAccountingBankImportRow r "
                "JOIN tblAccountingBankImportBatch i ON i.ID=r.ImportBatchID "
                "WHERE i.BankAccountID=? AND r.MatchStatus='UNMATCHED' "
                "AND r.TransactionDate<=? AND (? IS NULL OR r.TransactionDate>?)",
                (header[0], header[1], previous_date, previous_date),
            )
            unmatched = cursor.fetchone()[0]
            if unmatched:
                raise ValueError(
                    "Resolve or ignore all bank rows in the statement period before completion."
                )
            self._execute(
                cursor,
                "SELECT COALESCE(SUM(ClearedAmount),0) "
                "FROM tblAccountingReconciliationItem WHERE ReconciliationID=?",
                (reconciliation_id,),
            )
            activity = Decimal(str(cursor.fetchone()[0]))
            difference = Decimal(str(header[3])) - (
                Decimal(str(header[2])) + activity
            )
            if difference != 0:
                raise ValueError(
                    "The reconciliation difference must be zero before completion."
                )
            self._execute(
                cursor,
                "UPDATE tblAccountingReconciliation "
                "SET Status='COMPLETED',CompletedAt=CURRENT_TIMESTAMP(6) WHERE ID=?",
                (reconciliation_id,),
            )
            self._audit(
                cursor, header[5], reconciliation_id,
                "BANK_RECONCILIATION_COMPLETED",
                {"cleared_activity": str(activity), "difference": str(difference)},
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def _audit(self, cursor, organization_id, reconciliation_id, action, after):
        self._execute(
            cursor,
            "INSERT INTO tblAccountingAuditEvent "
            "(OrganizationID,EntityType,EntityID,Action,AfterJSON,UserID) "
            "VALUES (?,'BANK_RECONCILIATION',?,?,?,?)",
            (
                organization_id, str(reconciliation_id), action,
                json.dumps(after, separators=(",", ":")), self.acting_user_id,
            ),
        )
