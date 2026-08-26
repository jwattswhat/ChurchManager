"""Create linked reversal transactions from posted entries."""
import json
from .draft_service import AccountingDraftError

class AccountingReversalService:
    def __init__(self, connection, acting_user_id):
        self.connection, self.acting_user_id = connection, int(acting_user_id)
        self.marker = "%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"
    def _execute(self, cursor, sql, values=()): return cursor.execute(sql.replace("?", self.marker), values)
    def create(self, original_id, reversal_date, reason):
        reason = reason.strip()
        if not reason: raise AccountingDraftError("Enter a reason for the reversal.")
        cursor = self.connection.cursor()
        try:
            self._execute(cursor, "SELECT OrganizationID, TransactionNumber, Status, OriginalTransactionID, ReversalTransactionID FROM tblAccountingTransaction WHERE ID=? FOR UPDATE", (original_id,))
            original = cursor.fetchone()
            if original is None or original[2] != "POSTED": raise AccountingDraftError("Only a currently posted transaction can be reversed.")
            if original[3] is not None: raise AccountingDraftError("A reversal transaction cannot itself be reversed.")
            if original[4] is not None: raise AccountingDraftError("A reversal already exists for this transaction.")
            self._execute(cursor, "SELECT p.ID FROM tblAccountingFiscalPeriod p JOIN tblAccountingFiscalYear y ON y.ID=p.FiscalYearID WHERE y.OrganizationID=? AND ? BETWEEN p.StartDate AND p.EndDate AND y.Status='OPEN' AND p.Status='OPEN' FOR UPDATE", (original[0], reversal_date))
            periods = cursor.fetchall()
            if len(periods) != 1: raise AccountingDraftError("The reversal date must belong to one open fiscal period.")
            self._execute(cursor, "SELECT LineNumber, AccountID, FundID, FunctionID, PayeeID, Description, Debit, Credit FROM tblAccountingTransactionLine WHERE TransactionID=? ORDER BY LineNumber FOR UPDATE", (original_id,))
            lines = cursor.fetchall()
            self._execute(cursor, "INSERT INTO tblAccountingTransaction (OrganizationID, TransactionDate, FiscalPeriodID, TransactionType, Status, Description, Reference, OriginalTransactionID, CreatedByUserID) VALUES (?, ?, ?, 'REVERSAL', 'READY', ?, ?, ?, ?)", (original[0], reversal_date, periods[0][0], "Reversal of transaction {}: {}".format(original[1], reason), "Reversal of transaction {}".format(original[1]), original_id, self.acting_user_id))
            reversal_id = cursor.lastrowid
            for line in lines:
                self._execute(cursor, "INSERT INTO tblAccountingTransactionLine (TransactionID, LineNumber, AccountID, FundID, FunctionID, PayeeID, Description, Debit, Credit) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (reversal_id, *line[:6], line[7], line[6]))
            after = json.dumps({"status":"READY","original_transaction_id":original_id,"reason":reason}, separators=(",", ":"))
            self._execute(cursor, "INSERT INTO tblAccountingAuditEvent (OrganizationID, EntityType, EntityID, Action, AfterJSON, Reason, UserID) VALUES (?, 'TRANSACTION', ?, 'REVERSAL_CREATED', ?, ?, ?)", (original[0], str(reversal_id), after, reason, self.acting_user_id))
            self.connection.commit(); return reversal_id
        except Exception: self.connection.rollback(); raise
        finally: cursor.close()
