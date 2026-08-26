-- Retire the obsolete database-backed enhancement/bug tracker. Development
-- work is maintained in repository documentation and the project issue tracker.

DROP VIEW IF EXISTS rpt_enhancement;

DELETE FROM tblReports
WHERE Report='CMEN01';

DELETE rp
FROM tblRolePermission rp
JOIN tblPermission p ON p.ID=rp.PermissionID
WHERE p.Name='application.enhancements.manage';

DELETE FROM tblPermission
WHERE Name='application.enhancements.manage';

DROP TABLE IF EXISTS tblEnhancement;
