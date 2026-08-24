-- Printable, privacy-scoped attendance roster for Group secretaries.

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_group_attendance_sheet AS
SELECT g.ChurchID,
       g.ID AS GroupID,
       g.Name AS GroupName,
       g.PrivacyClass,
       p.ID AS PersonID,
       p.LastName,
       p.FirstName,
       m.StartDate AS MembershipStartDate,
       m.EndDate AS MembershipEndDate,
       GROUP_CONCAT(DISTINCT r.Label ORDER BY r.DisplayOrder,r.Label SEPARATOR ', ') AS Roles,
       CAST('' AS CHAR(8)) AS Present,
       CAST('' AS CHAR(8)) AS Absent,
       CAST('' AS CHAR(8)) AS Excused,
       CAST('' AS CHAR(160)) AS Notes
FROM tblGroup g
JOIN tblGroupMembership m ON m.GroupID=g.ID
JOIN tblPerson p ON p.ID=m.PersonID
LEFT JOIN tblGroupMembershipRole mr ON mr.GroupMembershipID=m.ID
LEFT JOIN tblGroupRole r ON r.ID=mr.GroupRoleID
GROUP BY g.ChurchID,g.ID,g.Name,g.PrivacyClass,p.ID,p.LastName,p.FirstName,
         m.StartDate,m.EndDate;

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMGR04','Groups - Attendance Sheet','[ChurchID\r\nGroupID\r\nStartDate]',NULL,
       'Printable effective-date Group roster with blank attendance, notes, and visitor lines.',1,p.ID
FROM tblPermission p WHERE p.Name='groups.reports.view'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),
Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);
