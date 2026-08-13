CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_required_position AS
SELECT s.ID AS ServiceID,r.WorshipRoleID,wr.Name AS Role,r.RequiredCount
FROM tblService s
JOIN tblWorshipRoleRequirement r
  ON r.ChurchID=s.ChurchID
 AND r.Active=1
 AND (
      r.BulletinOrderTemplateID=s.BulletinOrderTemplateID
      OR (
          r.BulletinOrderTemplateID IS NULL
          AND NOT EXISTS (
              SELECT 1
              FROM tblWorshipRoleRequirement r_specific
              WHERE r_specific.ChurchID=s.ChurchID
                AND r_specific.BulletinOrderTemplateID=s.BulletinOrderTemplateID
                AND r_specific.Active=1
          )
      )
 )
JOIN tblWorshipRole wr ON wr.ID=r.WorshipRoleID
WHERE wr.Active=1;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_participant AS
SELECT sr.ID,sr.ServiceID,sr.WorshipRoleID,COALESCE(wr.Name,sr.Role) AS Role,
       COALESCE(NULLIF(p.DisplayName,''),p.Name) AS Name,
       sr.AssignmentStatus AS Status
FROM tblServiceRole sr
JOIN tblParticipant p ON p.ID=sr.ParticipantID
LEFT JOIN tblWorshipRole wr ON wr.ID=sr.WorshipRoleID;
