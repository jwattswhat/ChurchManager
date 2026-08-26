CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_individual_attendance AS
SELECT a.ID,p.ChurchID,p.ID AS PersonID,p.LastName,p.FirstName,
       ae.DateTime,ae.Description,ae.AttendanceType,a.Communion,a.Note
FROM tblAttendance a
JOIN tblPerson p ON p.ID=a.PersonID
JOIN tblAttendanceEvent ae ON ae.ID=a.AttendanceEventID;

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMAT03','Individual Attendance History',
       '[ChurchID\r\nPersonID\r\nStartDate\r\nEndDate]',NULL,
       'Named-person attendance and Communion history.',1,p.ID
FROM tblPermission p WHERE p.Name='reports.attendance.run'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);
