-- Configurable approval policy for congregations with only one accounting operator.
ALTER TABLE tblAccountingOrganization
    ADD COLUMN ApprovalPolicy varchar(30) NOT NULL DEFAULT 'INDEPENDENT_PREFERRED'
    AFTER ApprovalThreshold,
    ADD CONSTRAINT ck_acct_org_approval_policy
    CHECK (ApprovalPolicy IN ('INDEPENDENT_REQUIRED','INDEPENDENT_PREFERRED'));

INSERT IGNORE INTO tblPermission (Name, Description, Active) VALUES
('accounting.approval.override', 'Use a reason-required audited solo approval override.', 1);

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID FROM tblRole r JOIN tblPermission p
  ON p.Name='accounting.approval.override'
WHERE r.Name='Treasurer';
