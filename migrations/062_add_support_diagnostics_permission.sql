-- Permit every active ChurchManager role to create a privacy-safe support package.
INSERT INTO tblPermission (Name, Description, IsSensitive)
SELECT 'application.support.create',
       'Create a local privacy-safe ChurchManager support package.', 0
WHERE NOT EXISTS (
    SELECT 1 FROM tblPermission WHERE Name='application.support.create'
);

INSERT INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID, p.ID
FROM tblRole r
JOIN tblPermission p ON p.Name='application.support.create'
LEFT JOIN tblRolePermission rp ON rp.RoleID=r.ID AND rp.PermissionID=p.ID
WHERE r.Active=1 AND rp.RoleID IS NULL;
