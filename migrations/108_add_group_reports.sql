-- Approved Group roster, participation, and meeting-attendance report views.

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_group_current_roster AS
SELECT g.ChurchID,
       g.ID AS GroupID,
       g.Name AS GroupName,
       g.PrivacyClass,
       p.ID AS PersonID,
       p.LastName,
       p.FirstName,
       m.StartDate,
       GROUP_CONCAT(DISTINCT r.Label ORDER BY r.DisplayOrder,r.Label SEPARATOR ', ') AS Roles
FROM tblGroup g
JOIN tblGroupMembership m ON m.GroupID=g.ID
JOIN tblPerson p ON p.ID=m.PersonID
LEFT JOIN tblGroupMembershipRole mr
  ON mr.GroupMembershipID=m.ID
 AND mr.StartDate<=CURRENT_DATE
 AND (mr.EndDate IS NULL OR mr.EndDate>=CURRENT_DATE)
LEFT JOIN tblGroupRole r ON r.ID=mr.GroupRoleID
WHERE m.StartDate<=CURRENT_DATE
  AND (m.EndDate IS NULL OR m.EndDate>=CURRENT_DATE)
GROUP BY g.ChurchID,g.ID,g.Name,g.PrivacyClass,p.ID,p.LastName,p.FirstName,m.StartDate;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_person_group_participation AS
SELECT g.ChurchID,
       g.ID AS GroupID,
       g.Name AS GroupName,
       g.PrivacyClass,
       p.ID AS PersonID,
       p.LastName,
       p.FirstName,
       m.StartDate,
       m.EndDate,
       CASE
         WHEN m.StartDate<=CURRENT_DATE AND (m.EndDate IS NULL OR m.EndDate>=CURRENT_DATE)
         THEN 'Current' ELSE 'Ended'
       END AS MembershipStatus
FROM tblGroupMembership m
JOIN tblGroup g ON g.ID=m.GroupID
JOIN tblPerson p ON p.ID=m.PersonID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_group_meeting_attendance AS
SELECT g.ChurchID,
       g.ID AS GroupID,
       g.Name AS GroupName,
       g.PrivacyClass,
       gm.ID AS GroupMeetingID,
       gm.StartsAt,
       gm.Title AS MeetingTitle,
       gm.Status AS MeetingStatus,
       p.ID AS PersonID,
       p.LastName,
       p.FirstName,
       a.AttendanceStatus
FROM tblGroupMeeting gm
JOIN tblGroup g ON g.ID=gm.GroupID
JOIN tblGroupMeetingAttendance a ON a.GroupMeetingID=gm.ID
JOIN tblPerson p ON p.ID=a.PersonID;

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMGR01','Groups - Current Roster','[ChurchID\r\nGroupID]',NULL,
       'Current authorized roster for one selected Group.',1,p.ID
FROM tblPermission p WHERE p.Name='groups.reports.view'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),
Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMGR02','Groups - Person Participation History','[ChurchID\r\nPersonID]',NULL,
       'Current and ended authorized Group membership for one Person or all People.',1,p.ID
FROM tblPermission p WHERE p.Name='groups.reports.view'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),
Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMGR03','Groups - Meeting Attendance','[ChurchID\r\nGroupID\r\nStartDate\r\nEndDate]',NULL,
       'Recorded attendance for authorized Group meetings in a selected period.',1,p.ID
FROM tblPermission p WHERE p.Name='groups.reports.view'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),
Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);
