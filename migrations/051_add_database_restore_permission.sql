INSERT IGNORE INTO tblPermission (Name,Description,IsSensitive,Active)
VALUES ('application.database.restore',
        'Restore the active ChurchManager database from a verified backup.',1,1);

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r JOIN tblPermission p
WHERE r.Name='Master Administrator' AND p.Name='application.database.restore';
