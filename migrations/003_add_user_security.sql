-- Reusable ChurchManager identities, roles, permissions, and security audit.
CREATE TABLE IF NOT EXISTS tblUser (
    ID int NOT NULL AUTO_INCREMENT,
    Username varchar(100) NOT NULL,
    DisplayName varchar(255) NOT NULL,
    PasswordHash varchar(255) NOT NULL,
    Active tinyint(1) NOT NULL DEFAULT 1,
    MasterAdministrator tinyint(1) NOT NULL DEFAULT 0,
    MustChangePassword tinyint(1) NOT NULL DEFAULT 1,
    FailedLoginCount int NOT NULL DEFAULT 0,
    LockedUntil datetime(6) NULL,
    LastLoginAt datetime(6) NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_user_username (Username)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblRole (
    ID int NOT NULL AUTO_INCREMENT,
    Name varchar(100) NOT NULL,
    Description varchar(500) NULL,
    SystemRole tinyint(1) NOT NULL DEFAULT 0,
    Active tinyint(1) NOT NULL DEFAULT 1,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_role_name (Name)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblPermission (
    ID int NOT NULL AUTO_INCREMENT,
    Name varchar(150) NOT NULL,
    Description varchar(500) NULL,
    IsSensitive tinyint(1) NOT NULL DEFAULT 0,
    Active tinyint(1) NOT NULL DEFAULT 1,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_permission_name (Name)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblUserRole (
    ID int NOT NULL AUTO_INCREMENT,
    UserID int NOT NULL,
    RoleID int NOT NULL,
    EffectiveFrom datetime(6) NULL,
    EffectiveUntil datetime(6) NULL,
    AssignedByUserID int NULL,
    AssignedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_userrole_assignment (UserID, RoleID),
    CONSTRAINT fk_userrole_user FOREIGN KEY (UserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_userrole_role FOREIGN KEY (RoleID) REFERENCES tblRole(ID),
    CONSTRAINT fk_userrole_assigner FOREIGN KEY (AssignedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblRolePermission (
    ID int NOT NULL AUTO_INCREMENT,
    RoleID int NOT NULL,
    PermissionID int NOT NULL,
    AssignedByUserID int NULL,
    AssignedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_rolepermission_assignment (RoleID, PermissionID),
    CONSTRAINT fk_rolepermission_role FOREIGN KEY (RoleID) REFERENCES tblRole(ID),
    CONSTRAINT fk_rolepermission_permission FOREIGN KEY (PermissionID) REFERENCES tblPermission(ID),
    CONSTRAINT fk_rolepermission_assigner FOREIGN KEY (AssignedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblSecurityAuditEvent (
    ID bigint NOT NULL AUTO_INCREMENT,
    UserID int NULL,
    SessionID char(36) NULL,
    Action varchar(100) NOT NULL,
    EntityType varchar(100) NULL,
    EntityID varchar(100) NULL,
    FormName varchar(150) NULL,
    BeforeJSON longtext NULL,
    AfterJSON longtext NULL,
    Reason varchar(1000) NULL,
    Workstation varchar(255) NULL,
    OccurredAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    KEY ix_securityaudit_user_time (UserID, OccurredAt),
    KEY ix_securityaudit_action_time (Action, OccurredAt),
    CONSTRAINT fk_securityaudit_user FOREIGN KEY (UserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO tblRole (Name, Description, SystemRole) VALUES
('Master Administrator', 'Complete ChurchManager administration and emergency authority.', 1),
('Pastor/Staff', 'Congregational and ministry work as explicitly permitted.', 1),
('Volunteer', 'Limited assigned operational work.', 1),
('Accounting Viewer', 'View permitted posted accounting records and reports.', 1),
('Accounting Entry Clerk', 'Create and edit permitted accounting drafts.', 1),
('Treasurer', 'Create, review, post, reconcile, and report.', 1),
('Accounting Approver', 'Approve accounting transactions under policy.', 1),
('Accounting Administrator', 'Maintain accounting configuration and periods.', 1),
('Auditor', 'Read-only accounting and audit access.', 1);

INSERT INTO tblPermission (Name, Description, IsSensitive) VALUES
('security.users.view', 'View ChurchManager users.', 1),
('security.users.manage', 'Create, disable, unlock, and reset ChurchManager users.', 1),
('security.roles.view', 'View roles and permission assignments.', 1),
('security.roles.manage', 'Manage roles and permission assignments.', 1),
('security.audit.view', 'View the security audit history.', 1),
('application.config.manage', 'Manage ChurchManager configuration.', 1),
('application.backup.run', 'Create a ChurchManager database backup.', 1),
('accounting.transactions.view', 'View permitted accounting transactions.', 1),
('accounting.transactions.create', 'Create accounting drafts.', 1),
('accounting.transactions.edit_own_draft', 'Edit accounting drafts created by the user.', 1),
('accounting.transactions.edit_any_draft', 'Edit any permitted accounting draft.', 1),
('accounting.transactions.delete_draft', 'Delete a permitted accounting draft with audit.', 1),
('accounting.transactions.mark_ready', 'Submit an accounting draft for review.', 1),
('accounting.transactions.approve', 'Approve an accounting transaction under policy.', 1),
('accounting.transactions.post', 'Post a validated accounting transaction.', 1),
('accounting.transactions.reverse', 'Reverse a posted accounting transaction.', 1),
('accounting.reports.run', 'Run permitted accounting reports.', 1),
('accounting.reconciliation.manage', 'Manage bank reconciliations.', 1),
('accounting.master_data.manage', 'Manage accounts, funds, functions, and related setup.', 1),
('accounting.periods.override', 'Perform controlled accounting period overrides.', 1),
('accounting.audit.view', 'View detailed accounting audit history.', 1);
