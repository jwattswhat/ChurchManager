DELETE FROM tblWorshipRoleRequirement WHERE BulletinOrderTemplateID IS NULL;

ALTER TABLE tblWorshipRoleRequirement
    MODIFY COLUMN BulletinOrderTemplateID int NOT NULL;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_required_position AS
SELECT s.ID AS ServiceID,r.WorshipRoleID,wr.Name AS Role,r.RequiredCount
FROM tblService s
JOIN tblWorshipRoleRequirement r
  ON r.ChurchID=s.ChurchID
 AND r.BulletinOrderTemplateID=s.BulletinOrderTemplateID
 AND r.Active=1
JOIN tblWorshipRole wr ON wr.ID=r.WorshipRoleID
WHERE wr.Active=1;
