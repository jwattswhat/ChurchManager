-- Separate sensitive authorization for changing ChurchManager screen layouts.

INSERT INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('screens.design','Customize approved ChurchManager screen layouts.',1,1)
ON DUPLICATE KEY UPDATE Description=VALUES(Description),IsSensitive=1,Active=1;

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Master Administrator' AND p.Name='screens.design';
