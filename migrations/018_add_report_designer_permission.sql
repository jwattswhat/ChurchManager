-- Separate authorization for changing visual report layouts.

INSERT INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('reports.design','Customize approved ChurchManager report layouts.',1,1)
ON DUPLICATE KEY UPDATE Description=VALUES(Description),IsSensitive=1,Active=1;

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Master Administrator' AND p.Name='reports.design';
