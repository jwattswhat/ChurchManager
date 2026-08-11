-- Bank reconciliation foundation and non-posting import staging.
CREATE TABLE IF NOT EXISTS tblAccountingBankAccount (
 ID int NOT NULL AUTO_INCREMENT, OrganizationID int NOT NULL, AccountID int NOT NULL,
 Name varchar(255) NOT NULL, InstitutionName varchar(255) NULL, AccountLastFour char(4) NULL,
 Active tinyint(1) NOT NULL DEFAULT 1, PRIMARY KEY(ID),
 UNIQUE KEY uq_acct_bank_ledger_account(OrganizationID,AccountID),
 CONSTRAINT fk_acct_bank_org FOREIGN KEY(OrganizationID) REFERENCES tblAccountingOrganization(ID),
 CONSTRAINT fk_acct_bank_account FOREIGN KEY(AccountID) REFERENCES tblAccountingAccount(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingBankImportBatch (
 ID bigint NOT NULL AUTO_INCREMENT, BankAccountID int NOT NULL, OriginalName varchar(255) NOT NULL,
 FileHash char(64) NOT NULL, FileFormat varchar(20) NOT NULL, MappingJSON longtext NULL,
 RowCount int NOT NULL DEFAULT 0, ImportedByUserID int NOT NULL,
 ImportedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6), PRIMARY KEY(ID),
 UNIQUE KEY uq_acct_bank_import_hash(BankAccountID,FileHash),
 CONSTRAINT fk_acct_import_bank FOREIGN KEY(BankAccountID) REFERENCES tblAccountingBankAccount(ID),
 CONSTRAINT fk_acct_import_user FOREIGN KEY(ImportedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingBankImportRow (
 ID bigint NOT NULL AUTO_INCREMENT, ImportBatchID bigint NOT NULL, RowNumber int NOT NULL,
 ExternalID varchar(255) NULL, TransactionDate date NOT NULL, Description varchar(1000) NOT NULL,
 Reference varchar(255) NULL, Amount decimal(19,4) NOT NULL, Fingerprint char(64) NOT NULL,
 MatchStatus varchar(20) NOT NULL DEFAULT 'UNMATCHED', MatchedTransactionLineID bigint NULL,
 PRIMARY KEY(ID), UNIQUE KEY uq_acct_import_row(ImportBatchID,RowNumber),
 KEY ix_acct_import_fingerprint(Fingerprint),
 CONSTRAINT ck_acct_import_match CHECK(MatchStatus IN ('UNMATCHED','MATCHED','IGNORED')),
 CONSTRAINT fk_acct_import_row_batch FOREIGN KEY(ImportBatchID) REFERENCES tblAccountingBankImportBatch(ID),
 CONSTRAINT fk_acct_import_row_line FOREIGN KEY(MatchedTransactionLineID) REFERENCES tblAccountingTransactionLine(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingReconciliation (
 ID bigint NOT NULL AUTO_INCREMENT, BankAccountID int NOT NULL, StatementDate date NOT NULL,
 BeginningBalance decimal(19,4) NOT NULL, EndingBalance decimal(19,4) NOT NULL,
 Status varchar(20) NOT NULL DEFAULT 'DRAFT', PreparedByUserID int NOT NULL,
 PreparedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6), CompletedAt datetime(6) NULL,
 PRIMARY KEY(ID), UNIQUE KEY uq_acct_reconciliation_statement(BankAccountID,StatementDate),
 CONSTRAINT ck_acct_reconciliation_status CHECK(Status IN ('DRAFT','COMPLETED')),
 CONSTRAINT fk_acct_reconciliation_bank FOREIGN KEY(BankAccountID) REFERENCES tblAccountingBankAccount(ID),
 CONSTRAINT fk_acct_reconciliation_user FOREIGN KEY(PreparedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingReconciliationItem (
 ID bigint NOT NULL AUTO_INCREMENT, ReconciliationID bigint NOT NULL,
 TransactionLineID bigint NOT NULL, ImportRowID bigint NULL, ClearedDate date NOT NULL,
 ClearedAmount decimal(19,4) NOT NULL, PRIMARY KEY(ID),
 UNIQUE KEY uq_acct_reconciliation_line(ReconciliationID,TransactionLineID),
 CONSTRAINT fk_acct_recon_item_header FOREIGN KEY(ReconciliationID) REFERENCES tblAccountingReconciliation(ID),
 CONSTRAINT fk_acct_recon_item_line FOREIGN KEY(TransactionLineID) REFERENCES tblAccountingTransactionLine(ID),
 CONSTRAINT fk_acct_recon_item_import FOREIGN KEY(ImportRowID) REFERENCES tblAccountingBankImportRow(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
