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
                "SELECT RowNumber, TransactionDate, Description, Reference, "
                "Amount, MatchStatus FROM tblAccountingBankImportRow "
                "WHERE ImportBatchID=? ORDER BY RowNumber",
                (batch_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
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
