UPDATE tblWorshipRoleRequirement r
JOIN (
    SELECT BulletinOrderTemplateID,WorshipRoleID,MIN(ID) AS KeepID,
           MAX(RequiredCount) AS RequiredCount
    FROM tblWorshipRoleRequirement
    GROUP BY BulletinOrderTemplateID,WorshipRoleID
) grouped ON grouped.KeepID=r.ID
SET r.RequiredCount=grouped.RequiredCount;

DELETE duplicate
FROM tblWorshipRoleRequirement duplicate
JOIN tblWorshipRoleRequirement keeper
  ON keeper.BulletinOrderTemplateID=duplicate.BulletinOrderTemplateID
 AND keeper.WorshipRoleID=duplicate.WorshipRoleID
 AND keeper.ID<duplicate.ID;

ALTER TABLE tblWorshipRoleRequirement
    DROP FOREIGN KEY fk_worshiprequirement_church,
    DROP INDEX uq_worship_requirement,
    DROP COLUMN ChurchID,
    ADD UNIQUE KEY uq_worship_requirement
        (BulletinOrderTemplateID,WorshipRoleID);

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_required_position AS
SELECT s.ID AS ServiceID,r.WorshipRoleID,wr.Name AS Role,r.RequiredCount
FROM tblService s
JOIN tblWorshipRoleRequirement r
  ON r.BulletinOrderTemplateID=s.BulletinOrderTemplateID
 AND r.Active=1
JOIN tblWorshipRole wr ON wr.ID=r.WorshipRoleID
WHERE wr.Active=1;
