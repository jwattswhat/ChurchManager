CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_member_attendance_followup AS
SELECT p.ID AS PersonID,p.ChurchID,p.LastName,p.FirstName,p.Status,
       last_seen.LastAttended,
       COUNT(DISTINCT CASE
           WHEN last_seen.LastWeek IS NULL OR service_weeks.ServiceWeek>last_seen.LastWeek
           THEN service_weeks.ServiceWeek END) AS MissedWeeks
FROM tblPerson p
LEFT JOIN (
    SELECT a.PersonID,MAX(ae.DateTime) AS LastAttended,
           MAX(DATE_SUB(DATE(ae.DateTime),INTERVAL DAYOFWEEK(ae.DateTime)-1 DAY)) AS LastWeek
    FROM tblAttendance a
    JOIN tblAttendanceEvent ae ON ae.ID=a.AttendanceEventID
    WHERE ae.AttendanceType='Worship Service' AND ae.DateTime<CURDATE()+INTERVAL 1 DAY
    GROUP BY a.PersonID
) last_seen ON last_seen.PersonID=p.ID
LEFT JOIN (
    SELECT DISTINCT ChurchID,
           DATE_SUB(DATE(DateTime),INTERVAL DAYOFWEEK(DateTime)-1 DAY) AS ServiceWeek
    FROM tblAttendanceEvent
    WHERE AttendanceType='Worship Service' AND DateTime<CURDATE()+INTERVAL 1 DAY
) service_weeks ON service_weeks.ChurchID=p.ChurchID
WHERE p.Member=1
GROUP BY p.ID,p.ChurchID,p.LastName,p.FirstName,p.Status,
         last_seen.LastAttended,last_seen.LastWeek;

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMAT05','Member Attendance Follow-up','[ChurchID\r\nMissedWeeks]',NULL,
       'Current members with consecutive missed recorded worship weeks; threshold-reaching rows are red.',
       1,p.ID
FROM tblPermission p WHERE p.Name='reports.attendance.run'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);
