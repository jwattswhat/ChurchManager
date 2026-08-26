"""Atomic, non-posting persistence for parsed bank files."""
from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
from .bank_import import CsvMapping,file_hash,parse_csv

class BankImportService:
    def __init__(self,connection,acting_user_id):
        self.connection,self.acting_user_id=connection,int(acting_user_id)
        self.marker="%s" if connection.__class__.__module__.startswith("mysql.connector") else "?"
    def _execute(self,cursor,sql,values=()):return cursor.execute(sql.replace("?",self.marker),values)
    def bank_accounts(self):
        cursor=self.connection.cursor()
        try:
            self._execute(cursor,"SELECT b.ID,CONCAT(b.Name,' - ',a.Code,' ',a.Name) FROM tblAccountingBankAccount b JOIN tblAccountingAccount a ON a.ID=b.AccountID WHERE b.Active=1 ORDER BY b.Name")
            return cursor.fetchall()
        finally:cursor.close()

    def staged_batches(self):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT i.ID, b.Name, i.OriginalName, i.ImportedAt, i.RowCount "
                "FROM tblAccountingBankImportBatch i "
                "JOIN tblAccountingBankAccount b ON b.ID=i.BankAccountID "
                "ORDER BY i.ImportedAt DESC, i.ID DESC",
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def staged_rows(self, batch_id):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT ID, RowNumber, TransactionDate, Description, Reference, "
                "Amount, MatchStatus FROM tblAccountingBankImportRow "
                "WHERE ImportBatchID=? ORDER BY RowNumber",
                (batch_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def set_row_ignored(self, import_row_id, ignored):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT r.MatchStatus, b.OrganizationID "
                "FROM tblAccountingBankImportRow r "
                "JOIN tblAccountingBankImportBatch i ON i.ID=r.ImportBatchID "
                "JOIN tblAccountingBankAccount b ON b.ID=i.BankAccountID "
                "WHERE r.ID=? FOR UPDATE",
                (import_row_id,),
            )
            current = cursor.fetchone()
            if current is None:
                raise ValueError("The staged bank row no longer exists.")
            if current[0] == "MATCHED":
                raise ValueError("A matched bank row cannot be ignored or restored.")
            desired = "IGNORED" if ignored else "UNMATCHED"
            if current[0] == desired:
                self.connection.rollback()
                return False
            self._execute(
                cursor,
                "UPDATE tblAccountingBankImportRow SET MatchStatus=? WHERE ID=?",
                (desired, import_row_id),
            )
            action = "BANK_ROW_IGNORED" if ignored else "BANK_ROW_RESTORED"
            self._execute(
                cursor,
                "INSERT INTO tblAccountingAuditEvent "
                "(OrganizationID,EntityType,EntityID,Action,BeforeJSON,AfterJSON,UserID) "
                "VALUES (?,'BANK_IMPORT_ROW',?,?,?,?,?)",
                (
                    current[1], str(import_row_id), action,
                    json.dumps({"match_status": current[0]}, separators=(",", ":")),
                    json.dumps({"match_status": desired}, separators=(",", ":")),
                    self.acting_user_id,
                ),
            )
            self.connection.commit()
            return True
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def match_candidates(self, import_row_id):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT l.ID, t.TransactionNumber, t.TransactionDate, "
                "t.Description, t.Reference, l.Debit-l.Credit "
                "FROM tblAccountingBankImportRow r "
                "JOIN tblAccountingBankImportBatch i ON i.ID=r.ImportBatchID "
                "JOIN tblAccountingBankAccount b ON b.ID=i.BankAccountID "
                "JOIN tblAccountingTransactionLine l ON l.AccountID=b.AccountID "
                "JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
                "LEFT JOIN tblAccountingBankImportRow used "
                " ON used.MatchedTransactionLineID=l.ID "
                "WHERE r.ID=? AND r.MatchStatus='UNMATCHED' "
                "AND t.Status='POSTED' AND l.Debit-l.Credit=r.Amount "
                "AND t.TransactionDate BETWEEN DATE_SUB(r.TransactionDate, INTERVAL 7 DAY) "
                "AND DATE_ADD(r.TransactionDate, INTERVAL 7 DAY) "
                "AND used.ID IS NULL "
                "ORDER BY ABS(DATEDIFF(t.TransactionDate,r.TransactionDate)), "
                "t.TransactionDate,t.TransactionNumber,l.LineNumber",
                (import_row_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def match_row(self, import_row_id, transaction_line_id):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT r.MatchStatus, r.Amount, b.AccountID, b.OrganizationID "
                "FROM tblAccountingBankImportRow r "
                "JOIN tblAccountingBankImportBatch i ON i.ID=r.ImportBatchID "
                "JOIN tblAccountingBankAccount b ON b.ID=i.BankAccountID "
                "WHERE r.ID=? FOR UPDATE",
                (import_row_id,),
            )
            imported = cursor.fetchone()
            if imported is None:
                raise ValueError("The staged bank row no longer exists.")
            if imported[0] != "UNMATCHED":
                raise ValueError("Only an unmatched bank row can be matched.")
            self._execute(
                cursor,
                "SELECT l.ID FROM tblAccountingTransactionLine l "
                "JOIN tblAccountingTransaction t ON t.ID=l.TransactionID "
                "LEFT JOIN tblAccountingBankImportRow used "
                " ON used.MatchedTransactionLineID=l.ID "
                "WHERE l.ID=? AND l.AccountID=? AND t.Status='POSTED' "
                "AND l.Debit-l.Credit=? AND used.ID IS NULL FOR UPDATE",
                (transaction_line_id, imported[2], imported[1]),
            )
            if cursor.fetchone() is None:
                raise ValueError(
                    "The selected posted line is unavailable or its amount does not match."
                )
            self._execute(
                cursor,
                "UPDATE tblAccountingBankImportRow "
                "SET MatchStatus='MATCHED',MatchedTransactionLineID=? WHERE ID=?",
                (transaction_line_id, import_row_id),
            )
            self._audit_match(
                cursor, imported[3], import_row_id, "BANK_ROW_MATCHED",
                "UNMATCHED", "MATCHED", transaction_line_id,
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def unmatch_row(self, import_row_id):
        cursor = self.connection.cursor()
        try:
            self._execute(
                cursor,
                "SELECT r.MatchStatus,r.MatchedTransactionLineID,b.OrganizationID "
                "FROM tblAccountingBankImportRow r "
                "JOIN tblAccountingBankImportBatch i ON i.ID=r.ImportBatchID "
                "JOIN tblAccountingBankAccount b ON b.ID=i.BankAccountID "
                "LEFT JOIN tblAccountingReconciliationItem x ON x.ImportRowID=r.ID "
                "WHERE r.ID=? AND x.ID IS NULL FOR UPDATE",
                (import_row_id,),
            )
            imported = cursor.fetchone()
            if imported is None or imported[0] != "MATCHED":
                raise ValueError(
                    "Only an unreconciled matched bank row can be unmatched."
                )
            self._execute(
                cursor,
                "UPDATE tblAccountingBankImportRow "
                "SET MatchStatus='UNMATCHED',MatchedTransactionLineID=NULL WHERE ID=?",
                (import_row_id,),
            )
            self._audit_match(
                cursor, imported[2], import_row_id, "BANK_ROW_UNMATCHED",
                "MATCHED", "UNMATCHED", imported[1],
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def _audit_match(self, cursor, organization_id, row_id, action,
                     before_status, after_status, transaction_line_id):
        self._execute(
            cursor,
            "INSERT INTO tblAccountingAuditEvent "
            "(OrganizationID,EntityType,EntityID,Action,BeforeJSON,AfterJSON,UserID) "
            "VALUES (?,'BANK_IMPORT_ROW',?,?,?,?,?)",
            (
                organization_id, str(row_id), action,
                json.dumps(
                    {"match_status": before_status}, separators=(",", ":")
                ),
                json.dumps(
                    {
                        "match_status": after_status,
                        "transaction_line_id": transaction_line_id,
                    },
                    separators=(",", ":"),
                ),
                self.acting_user_id,
            ),
        )
    def stage_csv(self,bank_account_id,source,mapping:CsvMapping):
        path=Path(source);content=path.read_bytes();rows=parse_csv(content,mapping);digest=file_hash(content)
        cursor=self.connection.cursor()
        try:
            self._execute(cursor,"SELECT OrganizationID FROM tblAccountingBankAccount WHERE ID=? AND Active=1 FOR UPDATE",(bank_account_id,));account=cursor.fetchone()
            if account is None:raise ValueError("Select an active accounting bank account.")
            self._execute(cursor,"SELECT ID FROM tblAccountingBankImportBatch WHERE BankAccountID=? AND FileHash=?",(bank_account_id,digest))
            if cursor.fetchone() is not None:raise ValueError("This bank file has already been imported for the selected account.")
            self._execute(cursor,"INSERT INTO tblAccountingBankImportBatch (BankAccountID,OriginalName,FileHash,FileFormat,MappingJSON,RowCount,ImportedByUserID) VALUES (?,?,?,'CSV',?,?,?)",(bank_account_id,path.name,digest,json.dumps(asdict(mapping),separators=(",",":")),len(rows),self.acting_user_id));batch_id=cursor.lastrowid
            for row in rows:
                self._execute(cursor,"INSERT INTO tblAccountingBankImportRow (ImportBatchID,RowNumber,ExternalID,TransactionDate,Description,Reference,Amount,Fingerprint) VALUES (?,?,?,?,?,?,?,?)",(batch_id,row.row_number,row.external_id or None,row.transaction_date,row.description,row.reference or None,row.amount,row.fingerprint))
            self._execute(cursor,"INSERT INTO tblAccountingAuditEvent (OrganizationID,EntityType,EntityID,Action,AfterJSON,UserID) VALUES (?,'BANK_IMPORT',?,'BANK_FILE_STAGED',?,?)",(account[0],str(batch_id),json.dumps({"file_hash":digest,"file_name":path.name,"row_count":len(rows)},separators=(",",":")),self.acting_user_id))
            self.connection.commit();return batch_id,len(rows)
        except Exception:self.connection.rollback();raise
        finally:cursor.close()
