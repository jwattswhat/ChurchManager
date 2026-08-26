-- Complete the approved visual report inventory without reactivating retired reports.

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMAT02','Weekly Attendance Listing','[ChurchID\r\nAttendanceType\r\nStartDate\r\nEndDate]',NULL,
       'Standard editable visual report starter.',1,p.ID
FROM tblPermission p WHERE p.Name='reports.attendance.run'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);

UPDATE tblReports SET Available=0 WHERE Report='CMSM01';
