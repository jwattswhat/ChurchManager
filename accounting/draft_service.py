"""Atomic creation of balanced accounting drafts."""

from __future__ import annotations

import json
from dataclasses import asdict
from decimal import Decimal

from .models import JournalLine, JournalTransaction
from .validation import validate_transaction


class AccountingDraftError(ValueError):
    """A transaction cannot be saved as an accounting draft."""


class AccountingDraftService:
    def __init__(self, connection, acting_user_id):
        self.connection = connection
        self.acting_user_id = int(acting_user_id)
        module = connection.__class__.__module__
        self.marker = "%s" if module.startswith("mysql.connector") else "?"

    def _execute(self, cursor, sql, values=()):
        return cursor.execute(sql.replace("?", self.marker), values)

    def choices(self, organization_id):
        """Return active posting choices for the draft-entry screen."""
        cursor = self.connection.cursor()
        try:
            result = {}
            queries = {
                "accounts": (
                    "SELECT ID, CONCAT(Code, ' - ', Name), FunctionRequirement "
                    "FROM tblAccountingAccount WHERE OrganizationID=? "
                    "AND Active=1 AND PostingAllowed=1 ORDER BY DisplayOrder, Code"
                ),
                "funds": (
                    "SELECT ID, CONCAT(Code, ' - ', Name) FROM tblAccountingFund "
                    "WHERE OrganizationID=? AND Active=1 ORDER BY Code"
                ),
                "restricted_funds": (
                    "SELECT ID, CONCAT(Code, ' - ', Name) FROM tblAccountingFund "
                    "WHERE OrganizationID=? AND Active=1 "
                    "AND NetAssetClass='WITH_DONOR_RESTRICTIONS' ORDER BY Code"
                ),
                "unrestricted_funds": (
                    "SELECT ID, CONCAT(Code, ' - ', Name) FROM tblAccountingFund "
                    "WHERE OrganizationID=? AND Active=1 "
                    "AND NetAssetClass='WITHOUT_DONOR_RESTRICTIONS' ORDER BY Code"
                ),
                "functions": (
                    "SELECT ID, CONCAT(Code, ' - ', Name) FROM tblAccountingFunction "
                    "WHERE OrganizationID=? AND Active=1 ORDER BY DisplayOrder, Code"
                ),
                "payees": (
                    "SELECT ID, Name FROM tblAccountingPayee "
                    "WHERE OrganizationID=? AND Active=1 ORDER BY Name"
                ),
                "cash_accounts": (
                    "SELECT a.ID, CONCAT(a.Code, ' - ', a.Name), a.FunctionRequirement "
                    "FROM tblAccountingBankAccount b JOIN tblAccountingAccount a ON a.ID=b.AccountID "
                    "WHERE b.OrganizationID=? AND b.Active=1 AND a.Active=1 "
                    "AND a.PostingAllowed=1 ORDER BY a.Code"
                ),
                "revenue_accounts": (
                    "SELECT ID, CONCAT(Code, ' - ', Name), FunctionRequirement "
                    "FROM tblAccountingAccount WHERE OrganizationID=? AND Active=1 "
                    "AND PostingAllowed=1 AND AccountType='REVENUE' ORDER BY Code"
                ),
                "expense_accounts": (
                    "SELECT ID, CONCAT(Code, ' - ', Name), FunctionRequirement "
                    "FROM tblAccountingAccount WHERE OrganizationID=? AND Active=1 "
                    "AND PostingAllowed=1 AND AccountType='EXPENSE' ORDER BY Code"
                ),
                "opening_accounts": (
                    "SELECT ID, CONCAT(Code, ' - ', Name), FunctionRequirement "
                    "FROM tblAccountingAccount WHERE OrganizationID=? AND Active=1 "
                    "AND PostingAllowed=1 AND AccountType IN ('ASSET','LIABILITY','NET_ASSET') "
                    "ORDER BY DisplayOrder,Code"
                ),
                "transfer_out_accounts": (
                    "SELECT ID, CONCAT(Code, ' - ', Name), FunctionRequirement "
                    "FROM tblAccountingAccount WHERE OrganizationID=? AND Active=1 "
                    "AND PostingAllowed=1 AND AccountType='TRANSFER' "
                    "AND NormalBalance='DEBIT' ORDER BY Code"
                ),
                "transfer_in_accounts": (
                    "SELECT ID, CONCAT(Code, ' - ', Name), FunctionRequirement "
                    "FROM tblAccountingAccount WHERE OrganizationID=? AND Active=1 "
                    "AND PostingAllowed=1 AND AccountType='TRANSFER' "
                    "AND NormalBalance='CREDIT' ORDER BY Code"
                ),
            }
            for name, sql in queries.items():
                self._execute(cursor, sql, (organization_id,))
                result[name] = cursor.fetchall()
            return result
        finally:
            cursor.close()

    def list_organizations(self):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT ID, LegalName FROM tblAccountingOrganization "
                "WHERE Active=1 ORDER BY LegalName",
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def list_drafts(self, can_edit_any=False):
        cursor = self.connection.cursor()
        try:
            sql = (
                "SELECT t.ID, o.LegalName, t.TransactionDate, t.TransactionType, "
                "t.Description, t.Reference, t.Version, t.CreatedByUserID "
                "FROM tblAccountingTransaction t "
                "JOIN tblAccountingOrganization o ON o.ID=t.OrganizationID "
                "WHERE t.Status='DRAFT'"
            )
            values = ()
            if not can_edit_any:
                sql += " AND t.CreatedByUserID=?"
                values = (self.acting_user_id,)
            sql += " ORDER BY t.TransactionDate DESC, t.ID DESC"
            self._execute(cursor, sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def load(self, transaction_id, can_edit_any=False):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT ID, OrganizationID, TransactionDate, TransactionType, "
                "Description, Reference, Version, CreatedByUserID, Status "
                "FROM tblAccountingTransaction WHERE ID=?",
                (transaction_id,),
            )
            row = cursor.fetchone()
            if row is None or row[8] != "DRAFT":
                raise AccountingDraftError("The selected draft is no longer available.")
            if row[7] != self.acting_user_id and not can_edit_any:
                raise AccountingDraftError("You may edit only drafts that you created.")
            self._execute(
                cursor,
                "SELECT LineNumber, AccountID, FundID, Debit, Credit, FunctionID, "
                "PayeeID, Description FROM tblAccountingTransactionLine "
                "WHERE TransactionID=? ORDER BY LineNumber",
                (transaction_id,),
            )
            lines = tuple(
                JournalLine(
                    item[0], item[1], item[2], Decimal(item[3]), Decimal(item[4]),
                    item[5], item[6], item[7] or "",
                )
                for item in cursor.fetchall()
            )
            transaction = JournalTransaction(
                row[1], row[2], row[4], lines, row[5] or "", row[3]
            )
            return transaction, row[6], row[7]
        finally:
            cursor.close()

    def _fiscal_period_id(self, cursor, transaction):
        self._execute(
            cursor,
            "SELECT p.ID FROM tblAccountingFiscalPeriod p "
            "JOIN tblAccountingFiscalYear y ON y.ID=p.FiscalYearID "
            "WHERE y.OrganizationID=? AND ? BETWEEN p.StartDate AND p.EndDate "
            "AND y.Status='OPEN' AND p.Status='OPEN'",
            (transaction.organization_id, transaction.transaction_date),
        )
        rows = cursor.fetchall()
        if len(rows) != 1:
            raise AccountingDraftError(
                "The transaction date must belong to exactly one open fiscal period."
            )
        return rows[0][0]

    def create(self, transaction: JournalTransaction):
        self._validate_for_draft(transaction)
        cursor = self.connection.cursor()
        try:
            self._validate_opening_accounts(cursor, transaction)
            period_id = self._fiscal_period_id(cursor, transaction)
            self._insert_header(cursor, transaction, period_id)
            transaction_id = cursor.lastrowid
            self._insert_lines(cursor, transaction_id, transaction)
            self._audit(cursor, transaction_id, "DRAFT_CREATED", transaction)
            self.connection.commit()
            return transaction_id
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def update(self, transaction_id, expected_version, transaction, can_edit_any=False):
        self._validate_for_draft(transaction)
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT Version, CreatedByUserID, Status FROM tblAccountingTransaction "
                "WHERE ID=? FOR UPDATE",
                (transaction_id,),
            )
            row = cursor.fetchone()
            if row is None or row[2] != "DRAFT":
                raise AccountingDraftError("The selected draft is no longer editable.")
            if row[1] != self.acting_user_id and not can_edit_any:
                raise AccountingDraftError("You may edit only drafts that you created.")
            if row[0] != expected_version:
                raise AccountingDraftError(
                    "This draft changed after you opened it. Reload before saving."
                )
            self._validate_opening_accounts(cursor, transaction)
            period_id = self._fiscal_period_id(cursor, transaction)
            self._execute(
                cursor,
                "UPDATE tblAccountingTransaction SET OrganizationID=?, "
                "TransactionDate=?, FiscalPeriodID=?, TransactionType=?, "
                "Description=?, Reference=?, Version=Version+1 WHERE ID=? "
                "AND Version=? AND Status='DRAFT'",
                (
                    transaction.organization_id, transaction.transaction_date,
                    period_id, transaction.transaction_type,
                    transaction.description.strip(), transaction.reference.strip() or None,
                    transaction_id, expected_version,
                ),
            )
            if cursor.rowcount != 1:
                raise AccountingDraftError(
                    "This draft changed after you opened it. Reload before saving."
                )
            self._execute(
                cursor,
                "DELETE FROM tblAccountingTransactionLine WHERE TransactionID=?",
                (transaction_id,),
            )
            self._insert_lines(cursor, transaction_id, transaction)
            self._audit(cursor, transaction_id, "DRAFT_UPDATED", transaction)
            self.connection.commit()
            return expected_version + 1
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def submit(self, transaction_id, expected_version, can_edit_any=False):
        """Lock and move a stored balanced draft to READY for review."""
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT OrganizationID, TransactionDate, TransactionType, Description, "
                "Reference, Version, CreatedByUserID, Status "
                "FROM tblAccountingTransaction WHERE ID=? FOR UPDATE",
                (transaction_id,),
            )
            row = cursor.fetchone()
            if row is None or row[7] != "DRAFT":
                raise AccountingDraftError("The selected draft is no longer editable.")
            if row[6] != self.acting_user_id and not can_edit_any:
                raise AccountingDraftError("You may submit only drafts that you created.")
            if row[5] != expected_version:
                raise AccountingDraftError(
                    "This draft changed after you opened it. Reload before submitting."
                )
            self._execute(
                cursor,
                "SELECT LineNumber, AccountID, FundID, Debit, Credit, FunctionID, "
                "PayeeID, Description FROM tblAccountingTransactionLine "
                "WHERE TransactionID=? ORDER BY LineNumber FOR UPDATE",
                (transaction_id,),
            )
            lines = tuple(
                JournalLine(
                    item[0], item[1], item[2], Decimal(item[3]), Decimal(item[4]),
                    item[5], item[6], item[7] or "",
                )
                for item in cursor.fetchall()
            )
            transaction = JournalTransaction(
                row[0], row[1], row[3], lines, row[4] or "", row[2]
            )
            self._validate_for_draft(transaction)
            self._validate_opening_accounts(cursor, transaction)
            self._fiscal_period_id(cursor, transaction)
            if transaction.transaction_type in {"CASH_DISBURSEMENT", "RESTRICTION_RELEASE", "OPENING_BALANCE"}:
                total = sum((line.debit for line in transaction.lines), Decimal("0"))
                self._execute(
                    cursor,
                    "SELECT AttachmentThreshold FROM tblAccountingOrganization WHERE ID=?",
                    (transaction.organization_id,),
                )
                threshold_row = cursor.fetchone()
                if threshold_row is None:
                    raise AccountingDraftError("The accounting organization is unavailable.")
                attachment_required = (
                    transaction.transaction_type in {"RESTRICTION_RELEASE", "OPENING_BALANCE"}
                    or total >= Decimal(threshold_row[0])
                )
                if attachment_required:
                    self._execute(
                        cursor,
                        "SELECT COUNT(*) FROM tblAccountingAttachment WHERE TransactionID=?",
                        (transaction_id,),
                    )
                    if cursor.fetchone()[0] < 1:
                        raise AccountingDraftError(
                            "Add a receipt, invoice, or voucher, or the required "
                            "supporting authority, before submitting this transaction."
                        )
            self._execute(
                cursor,
                "UPDATE tblAccountingTransaction SET Status='READY', "
                "Version=Version+1 WHERE ID=? AND Version=? AND Status='DRAFT'",
                (transaction_id, expected_version),
            )
            if cursor.rowcount != 1:
                raise AccountingDraftError(
                    "This draft changed after you opened it. Reload before submitting."
                )
            self._audit(cursor, transaction_id, "DRAFT_MARKED_READY", transaction)
            self.connection.commit()
            return expected_version + 1
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def delete(self, transaction_id, expected_version):
        """Delete only the acting user's unchanged, unposted draft with audit."""
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT OrganizationID,TransactionDate,TransactionType,Description,"
                "Reference,Version,CreatedByUserID,Status "
                "FROM tblAccountingTransaction WHERE ID=? FOR UPDATE",
                (transaction_id,),
            )
            row = cursor.fetchone()
            if row is None or row[7] != "DRAFT":
                raise AccountingDraftError("Only an unposted draft can be deleted.")
            if row[6] != self.acting_user_id:
                raise AccountingDraftError("You may delete only drafts that you created.")
            if row[5] != expected_version:
                raise AccountingDraftError(
                    "This draft changed after you opened it. Reload before deleting."
                )
            self._execute(
                cursor,
                "SELECT COUNT(*) FROM tblAccountingAttachment WHERE TransactionID=?",
                (transaction_id,),
            )
            if cursor.fetchone()[0]:
                raise AccountingDraftError(
                    "Remove the draft's attachments before deleting the draft."
                )
            before = json.dumps(
                {
                    "organization_id": row[0],
                    "transaction_date": str(row[1]),
                    "transaction_type": row[2],
                    "description": row[3],
                    "reference": row[4],
                    "version": row[5],
                    "created_by_user_id": row[6],
                    "status": row[7],
                },
                separators=(",", ":"), sort_keys=True,
            )
            self._execute(
                cursor,
                "DELETE FROM tblAccountingTransactionLine WHERE TransactionID=?",
                (transaction_id,),
            )
            self._execute(
                cursor,
                "DELETE FROM tblAccountingTransaction WHERE ID=? AND Version=? "
                "AND Status='DRAFT' AND CreatedByUserID=?",
                (transaction_id, expected_version, self.acting_user_id),
            )
            if cursor.rowcount != 1:
                raise AccountingDraftError(
                    "This draft changed after you opened it. Reload before deleting."
                )
            self._execute(
                cursor,
                "INSERT INTO tblAccountingAuditEvent "
                "(OrganizationID,EntityType,EntityID,Action,BeforeJSON,UserID) "
                "VALUES (?,'TRANSACTION',?,'DRAFT_DELETED',?,?)",
                (row[0], str(transaction_id), before, self.acting_user_id),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    @staticmethod
    def _validate_for_draft(transaction):
        validate_transaction(transaction)
        if transaction.transaction_type not in {
            "JOURNAL", "CASH_RECEIPT", "CASH_DISBURSEMENT", "RESTRICTION_RELEASE",
            "OPENING_BALANCE"
        }:
            raise AccountingDraftError("This transaction type is not available yet.")
        if (
            transaction.transaction_type == "CASH_DISBURSEMENT"
            and not transaction.reference.strip()
        ):
            raise AccountingDraftError(
                "A source-document reference is required for a cash disbursement."
            )
        if transaction.transaction_type == "OPENING_BALANCE" and not transaction.reference.strip():
            raise AccountingDraftError("A source-document reference is required for opening balances.")

    def _validate_opening_accounts(self, cursor, transaction):
        if transaction.transaction_type != "OPENING_BALANCE":
            return
        account_ids = sorted({line.account_id for line in transaction.lines})
        placeholders = ",".join("?" for _ in account_ids)
        self._execute(cursor,
            "SELECT COUNT(*) FROM tblAccountingAccount WHERE OrganizationID=? "
            "AND ID IN ({}) AND Active=1 AND PostingAllowed=1 "
            "AND AccountType IN ('ASSET','LIABILITY','NET_ASSET')".format(placeholders),
            (transaction.organization_id, *account_ids))
        if cursor.fetchone()[0] != len(account_ids):
            raise AccountingDraftError("Opening balances may use only active asset, liability, and net-asset accounts.")

    def _insert_header(self, cursor, transaction, period_id):
        self._execute(
            cursor,
                "INSERT INTO tblAccountingTransaction "
                "(OrganizationID, TransactionDate, FiscalPeriodID, TransactionType, "
                "Status, Description, Reference, CreatedByUserID) "
                "VALUES (?, ?, ?, ?, 'DRAFT', ?, ?, ?)",
                (
                    transaction.organization_id,
                    transaction.transaction_date,
                    period_id,
                    transaction.transaction_type,
                    transaction.description.strip(),
                    transaction.reference.strip() or None,
                    self.acting_user_id,
                ),
        )

    def _insert_lines(self, cursor, transaction_id, transaction):
        for line in transaction.lines:
            self._execute(
                cursor,
                    "INSERT INTO tblAccountingTransactionLine "
                    "(TransactionID, LineNumber, AccountID, FundID, FunctionID, "
                    "PayeeID, Description, Debit, Credit) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        transaction_id, line.line_number, line.account_id,
                        line.fund_id, line.function_id, line.payee_id,
                        line.description.strip() or None, line.debit, line.credit,
                    ),
            )

    def _audit(self, cursor, transaction_id, action, transaction):
        after = json.dumps(
            asdict(transaction), default=str, separators=(",", ":"), sort_keys=True
        )
        self._execute(
            cursor,
            "INSERT INTO tblAccountingAuditEvent "
            "(OrganizationID, EntityType, EntityID, Action, AfterJSON, UserID) "
            "VALUES (?, 'TRANSACTION', ?, ?, ?, ?)",
            (transaction.organization_id, str(transaction_id), action, after, self.acting_user_id),
        )
