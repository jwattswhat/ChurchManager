CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_pastors_attendance_comparison AS
SELECT c.ID AS ChurchID,y.ReportYear,
       CASE WHEN y.ReportYear<YEAR(CURDATE())
            THEN COALESCE(SUM(CASE WHEN YEAR(ae.DateTime)=y.ReportYear
                                   THEN ae.HandCount ELSE 0 END),0)
            ELSE NULL END AS FullYearAttendance,
       COALESCE(SUM(CASE WHEN YEAR(ae.DateTime)=y.ReportYear
                         AND DATE_FORMAT(ae.DateTime,'%m%d')<=DATE_FORMAT(CURDATE(),'%m%d')
                         THEN ae.HandCount ELSE 0 END),0) AS ThroughDateAttendance,
       SUM(CASE WHEN YEAR(ae.DateTime)=y.ReportYear
                 AND DATE_FORMAT(ae.DateTime,'%m%d')<=DATE_FORMAT(CURDATE(),'%m%d')
                THEN 1 ELSE 0 END) AS EventsThroughDate,
       COALESCE(ROUND(
           SUM(CASE WHEN YEAR(ae.DateTime)=y.ReportYear
                     AND DATE_FORMAT(ae.DateTime,'%m%d')<=DATE_FORMAT(CURDATE(),'%m%d')
                    THEN ae.HandCount ELSE 0 END)
           / NULLIF(SUM(CASE WHEN YEAR(ae.DateTime)=y.ReportYear
                              AND DATE_FORMAT(ae.DateTime,'%m%d')<=DATE_FORMAT(CURDATE(),'%m%d')
                             THEN 1 ELSE 0 END),0),1),0) AS AverageThroughDate,
       COALESCE(SUM(CASE WHEN YEAR(ae.DateTime)=y.ReportYear
                         AND DATE_FORMAT(ae.DateTime,'%m%d')<=DATE_FORMAT(CURDATE(),'%m%d')
                         THEN ae.HandCountCommunion ELSE 0 END),0) AS CommunionThroughDate
FROM tblChurch c
CROSS JOIN (
    SELECT YEAR(CURDATE()) AS ReportYear
    UNION ALL SELECT YEAR(CURDATE())-1
    UNION ALL SELECT YEAR(CURDATE())-2
) y
LEFT JOIN tblAttendanceEvent ae ON ae.ChurchID=c.ID
GROUP BY c.ID,y.ReportYear;

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMAT04','Pastor''s Attendance Comparison','[ChurchID]',NULL,
       'Current year-to-date compared with the same period in the prior two years, including prior full-year totals.',
       1,p.ID
FROM tblPermission p WHERE p.Name='reports.attendance.run'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);
