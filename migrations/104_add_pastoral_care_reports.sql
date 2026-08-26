-- Minimum-necessary pastoral-care reports. Restricted notes are never joined.

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_pastoral_care_work_list AS
SELECT n.ID AS CareNeedID,
       n.ChurchID,
       COALESCE(
           NULLIF(TRIM(CONCAT_WS(' ',p.FirstName,p.LastName)),''),
           f.FamilyName,
           n.DisplaySubject
       ) AS Subject,
       n.Category,
       COALESCE(u.DisplayName,'Unassigned') AS Assignee,
       n.Priority,
       n.Status,
       n.DueDate,
       n.NextFollowUpDate,
       n.ScheduleText
FROM tblPastoralCareNeed n
LEFT JOIN tblPerson p ON p.ID=n.PersonID
LEFT JOIN tblFamily f ON f.ID=n.FamilyID
LEFT JOIN tblUser u ON u.ID=n.AssignedUserID
WHERE n.Status IN ('OPEN','WAITING');

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_pastoral_care_activity_summary AS
SELECT n.ChurchID,
       DATE(a.ActionDateTime) AS ActionDate,
       n.Category,
       a.ActionType,
       a.Result,
       COUNT(*) AS ActionCount
FROM tblPastoralCareAction a
JOIN tblPastoralCareNeed n ON n.ID=a.CareNeedID
GROUP BY n.ChurchID,DATE(a.ActionDateTime),n.Category,a.ActionType,a.Result;

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMPC01','Pastoral Care - Work List','[ChurchID\r\nStartDate\r\nEndDate]',NULL,
       'Protected operational work list; restricted notes and narrative are excluded.',1,p.ID
FROM tblPermission p WHERE p.Name='pastoral.care.report'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMPC02','Pastoral Care - Activity Summary','[ChurchID\r\nStartDate\r\nEndDate]',NULL,
       'Protected aggregate action counts without subject identity or narrative.',1,p.ID
FROM tblPermission p WHERE p.Name='pastoral.care.report'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);
