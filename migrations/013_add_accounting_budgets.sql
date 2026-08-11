-- Versioned budgets with detailed line items tied to general-ledger accounts.
CREATE TABLE IF NOT EXISTS tblAccountingBudget (
    ID bigint NOT NULL AUTO_INCREMENT,
    OrganizationID int NOT NULL,
    FiscalYearID int NOT NULL,
    Name varchar(255) NOT NULL,
    DetailMode varchar(20) NOT NULL DEFAULT 'ACCOUNT_ONLY',
    VersionNumber int NOT NULL DEFAULT 1,
    Status varchar(20) NOT NULL DEFAULT 'DRAFT',
    BasedOnBudgetID bigint NULL,
    CreatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    ProposedByUserID int NULL,
    ProposedAt datetime(6) NULL,
    AdoptedByUserID int NULL,
    AdoptedAt datetime(6) NULL,
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_acct_budget_version (FiscalYearID, Name, VersionNumber),
    KEY ix_acct_budget_status (OrganizationID, FiscalYearID, Status),
    CONSTRAINT ck_acct_budget_version CHECK (VersionNumber > 0),
    CONSTRAINT ck_acct_budget_detail_mode CHECK (DetailMode IN ('ACCOUNT_ONLY','DETAILED')),
    CONSTRAINT ck_acct_budget_status CHECK (Status IN ('DRAFT','PROPOSED','ADOPTED','SUPERSEDED')),
    CONSTRAINT fk_acct_budget_org FOREIGN KEY (OrganizationID) REFERENCES tblAccountingOrganization(ID),
    CONSTRAINT fk_acct_budget_year FOREIGN KEY (FiscalYearID) REFERENCES tblAccountingFiscalYear(ID),
    CONSTRAINT fk_acct_budget_based_on FOREIGN KEY (BasedOnBudgetID) REFERENCES tblAccountingBudget(ID),
    CONSTRAINT fk_acct_budget_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_acct_budget_proposer FOREIGN KEY (ProposedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_acct_budget_adopter FOREIGN KEY (AdoptedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblAccountingBudgetLine (
    ID bigint NOT NULL AUTO_INCREMENT,
    BudgetID bigint NOT NULL,
    FiscalPeriodID int NOT NULL,
    AccountID int NOT NULL,
    FundID int NOT NULL,
    FunctionID int NULL,
    LineItemName varchar(255) NULL,
    Amount decimal(19,2) NOT NULL DEFAULT 0.00,
    Note varchar(1000) NULL,
    DisplayOrder int NOT NULL DEFAULT 0,
    PRIMARY KEY (ID),
    KEY ix_acct_budget_line_report (BudgetID, FiscalPeriodID, AccountID, FundID, FunctionID),
    KEY ix_acct_budget_line_order (BudgetID, DisplayOrder, ID),
    CONSTRAINT ck_acct_budget_line_amount CHECK (Amount >= 0),
    CONSTRAINT fk_acct_budget_line_budget FOREIGN KEY (BudgetID) REFERENCES tblAccountingBudget(ID),
    CONSTRAINT fk_acct_budget_line_period FOREIGN KEY (FiscalPeriodID) REFERENCES tblAccountingFiscalPeriod(ID),
    CONSTRAINT fk_acct_budget_line_account FOREIGN KEY (AccountID) REFERENCES tblAccountingAccount(ID),
    CONSTRAINT fk_acct_budget_line_fund FOREIGN KEY (FundID) REFERENCES tblAccountingFund(ID),
    CONSTRAINT fk_acct_budget_line_function FOREIGN KEY (FunctionID) REFERENCES tblAccountingFunction(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO tblPermission (Name, Description, Active) VALUES
('accounting.budgets.manage', 'Create and edit draft accounting budgets.', 1),
('accounting.budgets.adopt', 'Propose, adopt, supersede, and amend accounting budgets.', 1);

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p
  ON p.Name IN ('accounting.budgets.manage','accounting.budgets.adopt')
WHERE r.Name IN ('Treasurer','Accounting Administrator');

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p
  ON p.Name='accounting.reports.run'
WHERE r.Name IN ('Accounting Viewer','Auditor');
