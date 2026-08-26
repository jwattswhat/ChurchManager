-- Phase 1 accounting ledger foundation. Test database only until acceptance.

CREATE TABLE IF NOT EXISTS tblAccountingOrganization (
    ID int NOT NULL AUTO_INCREMENT,
    ChurchID int NULL,
    LegalName varchar(255) NOT NULL,
    FiscalYearStartMonth tinyint NOT NULL DEFAULT 1,
    BaseCurrency char(3) NOT NULL DEFAULT 'USD',
    ReportingBasis varchar(20) NOT NULL DEFAULT 'MODIFIED_CASH',
    NextTransactionNumber bigint NOT NULL DEFAULT 1,
    ApprovalThreshold decimal(19,2) NOT NULL DEFAULT 500.00,
    AttachmentThreshold decimal(19,2) NOT NULL DEFAULT 250.00,
    Active tinyint(1) NOT NULL DEFAULT 1,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    CONSTRAINT ck_acct_org_start_month CHECK (FiscalYearStartMonth BETWEEN 1 AND 12),
    CONSTRAINT ck_acct_org_thresholds CHECK (ApprovalThreshold >= 0 AND AttachmentThreshold >= 0),
    CONSTRAINT fk_acct_org_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingAccount (
    ID int NOT NULL AUTO_INCREMENT,
    OrganizationID int NOT NULL,
    Code varchar(30) NOT NULL,
    Name varchar(255) NOT NULL,
    AccountType varchar(20) NOT NULL,
    NormalBalance varchar(10) NOT NULL,
    PostingAllowed tinyint(1) NOT NULL DEFAULT 1,
    FunctionRequirement varchar(15) NOT NULL DEFAULT 'OPTIONAL',
    StatementGroup varchar(100) NULL,
    DisplayOrder int NOT NULL DEFAULT 0,
    EffectiveFrom date NULL,
    EffectiveUntil date NULL,
    Active tinyint(1) NOT NULL DEFAULT 1,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_acct_account_code (OrganizationID, Code),
    KEY ix_acct_account_type (OrganizationID, AccountType, Active),
    CONSTRAINT ck_acct_account_type CHECK (AccountType IN ('ASSET','LIABILITY','NET_ASSET','REVENUE','EXPENSE','TRANSFER','OTHER')),
    CONSTRAINT ck_acct_normal_balance CHECK (NormalBalance IN ('DEBIT','CREDIT')),
    CONSTRAINT ck_acct_function_rule CHECK (FunctionRequirement IN ('REQUIRED','OPTIONAL','PROHIBITED')),
    CONSTRAINT fk_acct_account_org FOREIGN KEY (OrganizationID) REFERENCES tblAccountingOrganization(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingFund (
    ID int NOT NULL AUTO_INCREMENT,
    OrganizationID int NOT NULL,
    Code varchar(30) NOT NULL,
    Name varchar(255) NOT NULL,
    NetAssetClass varchar(30) NOT NULL,
    RestrictionType varchar(30) NOT NULL DEFAULT 'NONE',
    BoardDesignated tinyint(1) NOT NULL DEFAULT 0,
    RestrictionText varchar(1000) NULL,
    EffectiveFrom date NULL,
    EffectiveUntil date NULL,
    NetAssetAccountID int NULL,
    Active tinyint(1) NOT NULL DEFAULT 1,
    ClosedDate date NULL,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_acct_fund_code (OrganizationID, Code),
    KEY ix_acct_fund_class (OrganizationID, NetAssetClass, Active),
    CONSTRAINT ck_acct_fund_class CHECK (NetAssetClass IN ('WITHOUT_DONOR_RESTRICTIONS','WITH_DONOR_RESTRICTIONS')),
    CONSTRAINT ck_acct_restriction_type CHECK (RestrictionType IN ('NONE','PURPOSE','TIME','PURPOSE_AND_TIME')),
    CONSTRAINT ck_acct_fund_designation CHECK (NOT (NetAssetClass='WITH_DONOR_RESTRICTIONS' AND BoardDesignated=1)),
    CONSTRAINT fk_acct_fund_org FOREIGN KEY (OrganizationID) REFERENCES tblAccountingOrganization(ID),
    CONSTRAINT fk_acct_fund_netasset FOREIGN KEY (NetAssetAccountID) REFERENCES tblAccountingAccount(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingFunction (
    ID int NOT NULL AUTO_INCREMENT,
    OrganizationID int NOT NULL,
    Code varchar(30) NOT NULL,
    Name varchar(255) NOT NULL,
    FunctionClass varchar(20) NOT NULL DEFAULT 'PROGRAM',
    DisplayOrder int NOT NULL DEFAULT 0,
    Active tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_acct_function_code (OrganizationID, Code),
    CONSTRAINT ck_acct_function_class CHECK (FunctionClass IN ('PROGRAM','MANAGEMENT_GENERAL','FUNDRAISING')),
    CONSTRAINT fk_acct_function_org FOREIGN KEY (OrganizationID) REFERENCES tblAccountingOrganization(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingFiscalYear (
    ID int NOT NULL AUTO_INCREMENT,
    OrganizationID int NOT NULL,
    Name varchar(100) NOT NULL,
    StartDate date NOT NULL,
    EndDate date NOT NULL,
    Status varchar(15) NOT NULL DEFAULT 'OPEN',
    ClosingTransactionID bigint NULL,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_acct_year_name (OrganizationID, Name),
    CONSTRAINT ck_acct_year_dates CHECK (StartDate <= EndDate),
    CONSTRAINT ck_acct_year_status CHECK (Status IN ('OPEN','CLOSING','CLOSED')),
    CONSTRAINT fk_acct_year_org FOREIGN KEY (OrganizationID) REFERENCES tblAccountingOrganization(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingFiscalPeriod (
    ID int NOT NULL AUTO_INCREMENT,
    FiscalYearID int NOT NULL,
    PeriodNumber smallint NOT NULL,
    Name varchar(100) NOT NULL,
    StartDate date NOT NULL,
    EndDate date NOT NULL,
    Status varchar(15) NOT NULL DEFAULT 'OPEN',
    PRIMARY KEY (ID),
    UNIQUE KEY uq_acct_period_number (FiscalYearID, PeriodNumber),
    KEY ix_acct_period_dates (StartDate, EndDate, Status),
    CONSTRAINT ck_acct_period_dates CHECK (StartDate <= EndDate),
    CONSTRAINT ck_acct_period_status CHECK (Status IN ('OPEN','CLOSED')),
    CONSTRAINT fk_acct_period_year FOREIGN KEY (FiscalYearID) REFERENCES tblAccountingFiscalYear(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingPayee (
    ID int NOT NULL AUTO_INCREMENT,
    OrganizationID int NOT NULL,
    Name varchar(255) NOT NULL,
    Reference varchar(255) NULL,
    ContactData longtext NULL,
    Active tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    KEY ix_acct_payee_name (OrganizationID, Name, Active),
    CONSTRAINT fk_acct_payee_org FOREIGN KEY (OrganizationID) REFERENCES tblAccountingOrganization(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingTransaction (
    ID bigint NOT NULL AUTO_INCREMENT,
    OrganizationID int NOT NULL,
    TransactionNumber bigint NULL,
    TransactionDate date NOT NULL,
    FiscalPeriodID int NOT NULL,
    TransactionType varchar(30) NOT NULL DEFAULT 'JOURNAL',
    Status varchar(20) NOT NULL DEFAULT 'DRAFT',
    Description varchar(1000) NOT NULL,
    Reference varchar(255) NULL,
    OriginalTransactionID bigint NULL,
    ReversalTransactionID bigint NULL,
    Version int NOT NULL DEFAULT 1,
    CreatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    ReviewedByUserID int NULL,
    ReviewedAt datetime(6) NULL,
    PostedByUserID int NULL,
    PostedAt datetime(6) NULL,
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_acct_transaction_number (OrganizationID, TransactionNumber),
    KEY ix_acct_transaction_date (OrganizationID, TransactionDate),
    KEY ix_acct_transaction_status (OrganizationID, Status, TransactionDate),
    KEY ix_acct_transaction_period (FiscalPeriodID, Status),
    KEY ix_acct_transaction_reference (OrganizationID, Reference),
    CONSTRAINT ck_acct_transaction_status CHECK (Status IN ('DRAFT','READY','APPROVED','POSTED','REVERSED')),
    CONSTRAINT fk_acct_transaction_org FOREIGN KEY (OrganizationID) REFERENCES tblAccountingOrganization(ID),
    CONSTRAINT fk_acct_transaction_period FOREIGN KEY (FiscalPeriodID) REFERENCES tblAccountingFiscalPeriod(ID),
    CONSTRAINT fk_acct_transaction_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_acct_transaction_reviewer FOREIGN KEY (ReviewedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_acct_transaction_poster FOREIGN KEY (PostedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_acct_transaction_original FOREIGN KEY (OriginalTransactionID) REFERENCES tblAccountingTransaction(ID),
    CONSTRAINT fk_acct_transaction_reversal FOREIGN KEY (ReversalTransactionID) REFERENCES tblAccountingTransaction(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingTransactionLine (
    ID bigint NOT NULL AUTO_INCREMENT,
    TransactionID bigint NOT NULL,
    LineNumber smallint NOT NULL,
    AccountID int NOT NULL,
    FundID int NOT NULL,
    FunctionID int NULL,
    PayeeID int NULL,
    Description varchar(1000) NULL,
    Debit decimal(19,2) NOT NULL DEFAULT 0.00,
    Credit decimal(19,2) NOT NULL DEFAULT 0.00,
    ClearedState varchar(15) NOT NULL DEFAULT 'UNCLEARED',
    PRIMARY KEY (ID),
    UNIQUE KEY uq_acct_transaction_line (TransactionID, LineNumber),
    KEY ix_acct_line_account (AccountID, TransactionID),
    KEY ix_acct_line_fund (FundID, TransactionID),
    KEY ix_acct_line_function (FunctionID, TransactionID),
    KEY ix_acct_line_payee (PayeeID, TransactionID),
    CONSTRAINT ck_acct_line_amounts CHECK (Debit >= 0 AND Credit >= 0 AND ((Debit > 0 AND Credit = 0) OR (Credit > 0 AND Debit = 0))),
    CONSTRAINT ck_acct_line_cleared CHECK (ClearedState IN ('UNCLEARED','CLEARED','RECONCILED')),
    CONSTRAINT fk_acct_line_transaction FOREIGN KEY (TransactionID) REFERENCES tblAccountingTransaction(ID),
    CONSTRAINT fk_acct_line_account FOREIGN KEY (AccountID) REFERENCES tblAccountingAccount(ID),
    CONSTRAINT fk_acct_line_fund FOREIGN KEY (FundID) REFERENCES tblAccountingFund(ID),
    CONSTRAINT fk_acct_line_function FOREIGN KEY (FunctionID) REFERENCES tblAccountingFunction(ID),
    CONSTRAINT fk_acct_line_payee FOREIGN KEY (PayeeID) REFERENCES tblAccountingPayee(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingAttachment (
    ID bigint NOT NULL AUTO_INCREMENT,
    TransactionID bigint NOT NULL,
    StoredPath varchar(1000) NOT NULL,
    OriginalName varchar(255) NOT NULL,
    DocumentType varchar(100) NULL,
    FileHash char(64) NOT NULL,
    AddedByUserID int NOT NULL,
    AddedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    KEY ix_acct_attachment_transaction (TransactionID),
    CONSTRAINT fk_acct_attachment_transaction FOREIGN KEY (TransactionID) REFERENCES tblAccountingTransaction(ID),
    CONSTRAINT fk_acct_attachment_user FOREIGN KEY (AddedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingAuditEvent (
    ID bigint NOT NULL AUTO_INCREMENT,
    OrganizationID int NOT NULL,
    EntityType varchar(100) NOT NULL,
    EntityID varchar(100) NOT NULL,
    Action varchar(100) NOT NULL,
    BeforeJSON longtext NULL,
    AfterJSON longtext NULL,
    Reason varchar(1000) NULL,
    UserID int NOT NULL,
    OccurredAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    KEY ix_acct_audit_entity (OrganizationID, EntityType, EntityID, OccurredAt),
    KEY ix_acct_audit_user (UserID, OccurredAt),
    CONSTRAINT fk_acct_audit_org FOREIGN KEY (OrganizationID) REFERENCES tblAccountingOrganization(ID),
    CONSTRAINT fk_acct_audit_user FOREIGN KEY (UserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE tblAccountingFiscalYear
    ADD CONSTRAINT fk_acct_year_closing_transaction
    FOREIGN KEY (ClosingTransactionID) REFERENCES tblAccountingTransaction(ID);

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.reports.run')
WHERE r.Name='Accounting Viewer';

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.transactions.create','accounting.transactions.edit_own_draft','accounting.transactions.delete_draft','accounting.transactions.mark_ready')
WHERE r.Name='Accounting Entry Clerk';

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.transactions.create','accounting.transactions.edit_any_draft','accounting.transactions.delete_draft','accounting.transactions.mark_ready','accounting.transactions.post','accounting.transactions.reverse','accounting.reports.run','accounting.reconciliation.manage')
WHERE r.Name='Treasurer';

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.transactions.approve')
WHERE r.Name='Accounting Approver';

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.reports.run','accounting.reconciliation.manage','accounting.master_data.manage','accounting.periods.override','accounting.audit.view')
WHERE r.Name='Accounting Administrator';

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN
('accounting.transactions.view','accounting.reports.run','accounting.audit.view')
WHERE r.Name='Auditor';
