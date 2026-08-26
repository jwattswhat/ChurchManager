CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_attendance_event AS
SELECT ae.ID,ae.ChurchID,ae.ServiceID,ae.DateTime,ae.Description,ae.AttendanceType,
       ae.CommunionOffered,ae.HandCount,
       COUNT(a.ID) AS KnownAttendance,
       GREATEST(COALESCE(ae.HandCount,0)-COUNT(a.ID),0) AS UnnamedAttendance,
       ae.HandCountCommunion,ae.Note
FROM tblAttendanceEvent ae
LEFT JOIN tblAttendance a ON a.AttendanceEventID=ae.ID
GROUP BY ae.ID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_attendance_weekly AS
SELECT MIN(e.ID) AS ID,e.ChurchID,
       DATE_SUB(DATE(e.DateTime),INTERVAL DAYOFWEEK(e.DateTime)-1 DAY) AS DateTime,
       e.AttendanceType,
       COUNT(*) AS EventCount,
       SUM(e.HandCount) AS Attendance,
       SUM(e.KnownAttendance) AS KnownAttendance,
       GREATEST(SUM(e.HandCount)-SUM(e.KnownAttendance),0) AS UnnamedAttendance,
       SUM(e.HandCountCommunion) AS Communion
FROM (
    SELECT ae.ID,ae.ChurchID,ae.DateTime,COALESCE(ae.AttendanceType,'') AS AttendanceType,
           COALESCE(ae.HandCount,0) AS HandCount,
           COALESCE(ae.HandCountCommunion,0) AS HandCountCommunion,
           COUNT(a.ID) AS KnownAttendance
    FROM tblAttendanceEvent ae
    LEFT JOIN tblAttendance a ON a.AttendanceEventID=ae.ID
    GROUP BY ae.ID
) e
GROUP BY e.ChurchID,
         DATE_SUB(DATE(e.DateTime),INTERVAL DAYOFWEEK(e.DateTime)-1 DAY),
         e.AttendanceType;

UPDATE tblReports
SET Title='Weekly Attendance Summary'
WHERE Report='CMAT02';
