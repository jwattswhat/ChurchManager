-- Register the Projects and Scheduling starter reports in the report catalog.
INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMPS01','Projects - Active Summary','[ChurchID]',NULL,'Current planned, active, and on-hold congregational projects.',1,p.ID
FROM tblPermission p WHERE p.Name='projects.reports'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMPS02','Projects - Due and Overdue Work','[ChurchID]',NULL,'Incomplete project steps with approaching or overdue dates.',1,p.ID
FROM tblPermission p WHERE p.Name='projects.reports'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMPS03','Projects - Project Plan','[ChurchID\r\nProjectID]',NULL,'Ordered plan for one selected congregational project.',1,p.ID
FROM tblPermission p WHERE p.Name='projects.reports'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMPS04','Projects - Completed History','[ChurchID]',NULL,'Completed congregational project history.',1,p.ID
FROM tblPermission p WHERE p.Name='projects.reports'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);
