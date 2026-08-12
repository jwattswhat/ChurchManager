-- Keep accounting report layouts behind a separate sensitive permission.

INSERT INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('accounting.reports.design','Customize approved accounting report layouts.',1,1)
ON DUPLICATE KEY UPDATE Description=VALUES(Description),IsSensitive=1,Active=1;

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Master Administrator' AND p.Name='accounting.reports.design';
