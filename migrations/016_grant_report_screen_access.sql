-- The broad permission opens the picker only; category permissions authorize reports.
INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name='reports.run'
WHERE r.Name IN ('Master Administrator','Pastor/Staff','Volunteer','Auditor');
