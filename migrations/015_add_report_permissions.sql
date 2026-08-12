-- Per-report authorization foundation for non-accounting reports.

ALTER TABLE tblReports
    ADD COLUMN RequiredPermissionID int(11) NULL AFTER Available,
    ADD KEY ix_reports_required_permission (RequiredPermissionID),
    ADD CONSTRAINT fk_reports_required_permission
        FOREIGN KEY (RequiredPermissionID) REFERENCES tblPermission(ID);

INSERT INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('reports.general.run','Run low-sensitivity administration reports.',0,1),
('reports.attendance.run','Run attendance summaries and event reports.',0,1),
('reports.membership.run','Run membership lists and aggregate reports.',1,1),
('reports.membership.contact','Run reports containing member contact or address information.',1,1),
('reports.worship.run','Run worship, hymn, reading, and service reports.',0,1),
('reports.ministry.run','Run project, task, and ministry-operation reports.',0,1),
('reports.pastoral.confidential','Run confidential pastoral, prayer, visit, and personal-history reports.',1,1)
ON DUPLICATE KEY UPDATE
Description=VALUES(Description),IsSensitive=VALUES(IsSensitive),Active=1;

UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.general.run'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMAS01','CMDO01','CMEN01','CMRP01');

UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.attendance.run'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMAT01');

UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.membership.run'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMML01','CMML02','CMPE01');

UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.membership.contact'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMMD01','CMMI01','CMMI02','CMMI03','CMPH02');

UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.worship.run'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMHU01','CMHU02','CMHU03','CMHU04','CMSM01','CMWP01','CMWS01');

UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.ministry.run'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMPJ01','CMPJ02','CMPJ03','CMPJ04');

UPDATE tblReports r JOIN tblPermission p ON p.Name='reports.pastoral.confidential'
SET r.RequiredPermissionID=p.ID
WHERE r.Report IN ('CMBATCH00','CMJR01','CMPA01','CMPR01');

ALTER TABLE tblReports MODIFY RequiredPermissionID int(11) NOT NULL;

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Master Administrator'
AND p.Name IN ('reports.general.run','reports.attendance.run','reports.membership.run',
               'reports.membership.contact','reports.worship.run','reports.ministry.run',
               'reports.pastoral.confidential');

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Pastor/Staff'
AND p.Name IN ('reports.general.run','reports.attendance.run','reports.membership.run',
               'reports.membership.contact','reports.worship.run','reports.ministry.run',
               'reports.pastoral.confidential');

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r JOIN tblPermission p ON p.Name='reports.worship.run'
WHERE r.Name='Volunteer';

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r JOIN tblPermission p
ON p.Name IN ('reports.general.run','reports.attendance.run')
WHERE r.Name='Auditor';
