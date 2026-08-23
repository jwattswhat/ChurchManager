-- Retire the generic Projects and Tasks subsystem. Focused ministry workflows
-- such as worship preparation checklists and pastoral follow-ups remain.

DROP VIEW IF EXISTS rpt_task_worker;
DROP VIEW IF EXISTS rpt_task;
DROP VIEW IF EXISTS rpt_project;

DELETE FROM tblReports
WHERE Report IN ('CMPJ01','CMPJ02','CMPJ03','CMPJ04');

DELETE rp
FROM tblRolePermission rp
JOIN tblPermission p ON p.ID=rp.PermissionID
WHERE p.Name='reports.ministry.run';

DELETE FROM tblPermission
WHERE Name='reports.ministry.run';

UPDATE tblPermission
SET Description='Manage documents, announcements, and journal entries.'
WHERE Name='ministry.manage';

DROP TABLE IF EXISTS tblTaskWorker;
DROP TABLE IF EXISTS tblTask;
DROP TABLE IF EXISTS tblProject;
