-- Confidential member-giving foundation for ChurchManager 0.3.
-- Donor identity remains outside the general ledger; accounting receives only
-- summarized batch postings in later implementation phases.

CREATE TABLE IF NOT EXISTS tblContributionContributor (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    ContributorType varchar(12) NOT NULL,
    PersonID int NULL,
    FamilyID int NULL,
    DisplayName varchar(255) NOT NULL,
    StatementName varchar(255) NULL,
    Address varchar(255) NULL,
    Address2 varchar(255) NULL,
    City varchar(255) NULL,
    State varchar(100) NULL,
    PostalCode varchar(30) NULL,
    Email varchar(255) NULL,
    IsActive tinyint(1) NOT NULL DEFAULT 1,
    StatementEnabled tinyint(1) NOT NULL DEFAULT 1,
    Note varchar(2000) NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_contribution_contributor_person (ChurchID, PersonID),
    UNIQUE KEY uq_contribution_contributor_family (ChurchID, FamilyID),
    KEY ix_contribution_contributor_name (ChurchID, IsActive, DisplayName),
    CONSTRAINT ck_contribution_contributor_type CHECK (ContributorType IN ('PERSON','FAMILY','EXTERNAL')),
    -- Link shape is enforced by giving.validation. MariaDB cannot use these
    -- SET-NULL foreign-key columns in a CHECK constraint. SET NULL is required
    -- so removing a directory record never erases historical giving identity.
    CONSTRAINT fk_contribution_contributor_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_contribution_contributor_person FOREIGN KEY (PersonID) REFERENCES tblPerson(ID) ON DELETE SET NULL,
    CONSTRAINT fk_contribution_contributor_family FOREIGN KEY (FamilyID) REFERENCES tblFamily(ID) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblContributionEnvelopeAssignment (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    ContributorID bigint NOT NULL,
    EnvelopeNumber varchar(30) NOT NULL,
    EffectiveFrom date NOT NULL,
    EffectiveThrough date NULL,
    Note varchar(1000) NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_contribution_envelope_start (ChurchID, EnvelopeNumber, EffectiveFrom),
    KEY ix_contribution_envelope_lookup (ChurchID, EnvelopeNumber, EffectiveFrom, EffectiveThrough),
    KEY ix_contribution_envelope_contributor (ContributorID, EffectiveFrom),
    CONSTRAINT ck_contribution_envelope_number CHECK (CHAR_LENGTH(TRIM(EnvelopeNumber)) > 0),
    CONSTRAINT ck_contribution_envelope_dates CHECK (EffectiveThrough IS NULL OR EffectiveFrom <= EffectiveThrough),
    CONSTRAINT fk_contribution_envelope_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_contribution_envelope_contributor FOREIGN KEY (ContributorID) REFERENCES tblContributionContributor(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblContributionPurpose (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    Name varchar(255) NOT NULL,
    Description varchar(1000) NULL,
    ApprovalDate date NOT NULL,
    ApprovingAuthority varchar(255) NOT NULL,
    EffectiveFrom date NOT NULL,
    EffectiveThrough date NULL,
    IsActive tinyint(1) NOT NULL DEFAULT 1,
    OrganizationID int NOT NULL,
    FundID int NOT NULL,
    RevenueAccountID int NOT NULL,
    ControlAndDiscretionConfirmed tinyint(1) NOT NULL DEFAULT 0,
    StatementTreatment varchar(20) NOT NULL DEFAULT 'ELIGIBLE',
    Note varchar(2000) NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_contribution_purpose_name (ChurchID, Name),
    KEY ix_contribution_purpose_active (ChurchID, IsActive, EffectiveFrom, EffectiveThrough),
    CONSTRAINT ck_contribution_purpose_dates CHECK (EffectiveFrom <= EffectiveThrough OR EffectiveThrough IS NULL),
    CONSTRAINT ck_contribution_purpose_statement CHECK (StatementTreatment IN ('ELIGIBLE','INELIGIBLE','REVIEW')),
    CONSTRAINT fk_contribution_purpose_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_contribution_purpose_org FOREIGN KEY (OrganizationID) REFERENCES tblAccountingOrganization(ID),
    CONSTRAINT fk_contribution_purpose_fund FOREIGN KEY (FundID) REFERENCES tblAccountingFund(ID),
    CONSTRAINT fk_contribution_purpose_revenue FOREIGN KEY (RevenueAccountID) REFERENCES tblAccountingAccount(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblContributionBatch (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    BatchDate date NOT NULL,
    Description varchar(500) NOT NULL,
    ServiceID int NULL,
    AttendanceEventID int NULL,
    DepositDate date NULL,
    OrganizationID int NOT NULL,
    BankAccountID int NULL,
    Status varchar(12) NOT NULL DEFAULT 'DRAFT',
    ControlTotal decimal(19,2) NULL,
    CalculatedTotal decimal(19,2) NOT NULL DEFAULT 0.00,
    AccountingTransactionID bigint NULL,
    CorrectsBatchID bigint NULL,
    CorrectionBatchID bigint NULL,
    Version int NOT NULL DEFAULT 1,
    EnteredByUserID int NOT NULL,
    EnteredAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    ReviewedByUserID int NULL,
    ReviewedAt datetime(6) NULL,
    PostedByUserID int NULL,
    PostedAt datetime(6) NULL,
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_contribution_batch_transaction (AccountingTransactionID),
    KEY ix_contribution_batch_status (ChurchID, Status, BatchDate),
    KEY ix_contribution_batch_service (ServiceID),
    CONSTRAINT ck_contribution_batch_status CHECK (Status IN ('DRAFT','READY','POSTED','VOID')),
    CONSTRAINT ck_contribution_batch_totals CHECK (
        CalculatedTotal >= 0 AND (ControlTotal IS NULL OR ControlTotal >= 0)
    ),
    CONSTRAINT ck_contribution_batch_version CHECK (Version > 0),
    CONSTRAINT fk_contribution_batch_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_contribution_batch_service FOREIGN KEY (ServiceID) REFERENCES tblService(ID) ON DELETE SET NULL,
    CONSTRAINT fk_contribution_batch_attendance FOREIGN KEY (AttendanceEventID) REFERENCES tblAttendanceEvent(ID) ON DELETE SET NULL,
    CONSTRAINT fk_contribution_batch_org FOREIGN KEY (OrganizationID) REFERENCES tblAccountingOrganization(ID),
    CONSTRAINT fk_contribution_batch_bank FOREIGN KEY (BankAccountID) REFERENCES tblAccountingBankAccount(ID),
    CONSTRAINT fk_contribution_batch_transaction FOREIGN KEY (AccountingTransactionID) REFERENCES tblAccountingTransaction(ID),
    CONSTRAINT fk_contribution_batch_corrects FOREIGN KEY (CorrectsBatchID) REFERENCES tblContributionBatch(ID),
    CONSTRAINT fk_contribution_batch_correction FOREIGN KEY (CorrectionBatchID) REFERENCES tblContributionBatch(ID),
    CONSTRAINT fk_contribution_batch_entered_by FOREIGN KEY (EnteredByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_contribution_batch_reviewed_by FOREIGN KEY (ReviewedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_contribution_batch_posted_by FOREIGN KEY (PostedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblContribution (
    ID bigint NOT NULL AUTO_INCREMENT,
    BatchID bigint NOT NULL,
    ContributorID bigint NULL,
    EnteredEnvelopeNumber varchar(30) NULL,
    ContributionMethod varchar(20) NOT NULL DEFAULT 'CASH',
    ReferenceValue varchar(255) NULL,
    ReceivedDate date NOT NULL,
    Amount decimal(19,2) NOT NULL DEFAULT 0.00,
    NonCashDescription varchar(1000) NULL,
    StatementEligibility varchar(20) NOT NULL DEFAULT 'ELIGIBLE',
    GoodsOrServicesProvided tinyint(1) NOT NULL DEFAULT 0,
    GoodsOrServicesDescription varchar(1000) NULL,
    GoodsOrServicesValue decimal(19,2) NULL,
    IntangibleReligiousBenefitOnly tinyint(1) NOT NULL DEFAULT 0,
    EligibilityOverrideReason varchar(1000) NULL,
    TributeType varchar(20) NULL,
    HonoreeName varchar(255) NULL,
    AcknowledgmentContact varchar(1000) NULL,
    DonorDisclosureAuthorized tinyint(1) NOT NULL DEFAULT 0,
    AmountDisclosureAuthorized tinyint(1) NOT NULL DEFAULT 0,
    DonorDirection varchar(1000) NULL,
    DirectionStatus varchar(20) NOT NULL DEFAULT 'NONE',
    DirectionResolution varchar(1000) NULL,
    Note varchar(2000) NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    KEY ix_contribution_batch (BatchID, ID),
    KEY ix_contribution_contributor_date (ContributorID, ReceivedDate),
    CONSTRAINT ck_contribution_method CHECK (ContributionMethod IN ('CASH','CHECK','ELECTRONIC','NON_CASH','OTHER')),
    CONSTRAINT ck_contribution_amount CHECK (Amount >= 0),
    CONSTRAINT ck_contribution_statement CHECK (StatementEligibility IN ('ELIGIBLE','INELIGIBLE','REVIEW')),
    CONSTRAINT ck_contribution_goods_value CHECK (GoodsOrServicesValue IS NULL OR GoodsOrServicesValue >= 0),
    CONSTRAINT ck_contribution_benefit CHECK (NOT (GoodsOrServicesProvided=1 AND IntangibleReligiousBenefitOnly=1)),
    CONSTRAINT ck_contribution_tribute CHECK (
        (TributeType IS NULL AND HonoreeName IS NULL) OR
        (TributeType IN ('IN_MEMORY_OF','IN_HONOR_OF') AND HonoreeName IS NOT NULL)
    ),
    CONSTRAINT ck_contribution_direction CHECK (DirectionStatus IN ('NONE','REVIEW','CLARIFIED','RETURNED','ACCEPTED')),
    CONSTRAINT fk_contribution_batch FOREIGN KEY (BatchID) REFERENCES tblContributionBatch(ID),
    CONSTRAINT fk_contribution_contributor FOREIGN KEY (ContributorID) REFERENCES tblContributionContributor(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblContributionAllocation (
    ID bigint NOT NULL AUTO_INCREMENT,
    ContributionID bigint NOT NULL,
    PurposeID bigint NULL,
    OrganizationID int NOT NULL,
    FundID int NOT NULL,
    RevenueAccountID int NOT NULL,
    Amount decimal(19,2) NOT NULL,
    DonorRestrictionNote varchar(1000) NULL,
    PRIMARY KEY (ID),
    KEY ix_contribution_allocation_contribution (ContributionID, ID),
    KEY ix_contribution_allocation_fund (OrganizationID, FundID),
    CONSTRAINT ck_contribution_allocation_amount CHECK (Amount > 0),
    CONSTRAINT fk_contribution_allocation_contribution FOREIGN KEY (ContributionID) REFERENCES tblContribution(ID),
    CONSTRAINT fk_contribution_allocation_purpose FOREIGN KEY (PurposeID) REFERENCES tblContributionPurpose(ID),
    CONSTRAINT fk_contribution_allocation_org FOREIGN KEY (OrganizationID) REFERENCES tblAccountingOrganization(ID),
    CONSTRAINT fk_contribution_allocation_fund FOREIGN KEY (FundID) REFERENCES tblAccountingFund(ID),
    CONSTRAINT fk_contribution_allocation_revenue FOREIGN KEY (RevenueAccountID) REFERENCES tblAccountingAccount(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblContributionAuditEvent (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    UserID int NULL,
    Action varchar(100) NOT NULL,
    EntityType varchar(100) NOT NULL,
    EntityID bigint NULL,
    SafeReference varchar(255) NULL,
    Reason varchar(1000) NULL,
    OccurredAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    KEY ix_contribution_audit_church_time (ChurchID, OccurredAt),
    KEY ix_contribution_audit_entity (EntityType, EntityID, OccurredAt),
    CONSTRAINT fk_contribution_audit_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_contribution_audit_user FOREIGN KEY (UserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO tblRole (Name, Description, SystemRole, Active) VALUES
('Giving Entry Clerk', 'Enter confidential contribution batches and maintain contributor records.', 1, 1),
('Giving Administrator', 'Administer confidential giving, posting, statements, and reports.', 1, 1);

INSERT IGNORE INTO tblPermission (Name, Description, IsSensitive, Active) VALUES
('giving.contributors.manage', 'Maintain confidential contributors and envelope assignments.', 1, 1),
('giving.batches.enter', 'Create and edit confidential draft contribution batches.', 1, 1),
('giving.batches.review', 'Review and mark contribution batches ready.', 1, 1),
('giving.batches.post', 'Post and correct contribution batches.', 1, 1),
('giving.history.view', 'View contributor-level giving history.', 1, 1),
('giving.statements.generate', 'Generate confidential contribution statements.', 1, 1),
('giving.reports.summary', 'Run giving summary reports without contributor identity.', 1, 1),
('giving.reports.confidential', 'Run donor-identifying giving reports.', 1, 1),
('giving.purposes.manage', 'Maintain approved congregational contribution purposes.', 1, 1);

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name IN (
    'giving.contributors.manage','giving.batches.enter','giving.batches.review',
    'giving.batches.post','giving.history.view','giving.statements.generate',
    'giving.reports.summary','giving.reports.confidential','giving.purposes.manage'
)
WHERE r.Name IN ('Master Administrator','Treasurer','Giving Administrator');

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name IN (
    'giving.contributors.manage','giving.batches.enter','giving.batches.review',
    'giving.history.view','giving.reports.summary'
)
WHERE r.Name='Giving Entry Clerk';
