ALTER TABLE tblService
    ADD COLUMN IF NOT EXISTS LiturgicalColorOverride VARCHAR(32) NULL AFTER PropersID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_service AS
SELECT s.ID,s.ChurchID,s.DateTime,COALESCE(s.Location,'') AS Location,
       COALESCE(s.LiturgicalDate,p.LiturgicalDate,'') AS LiturgicalDate,
       s.HolyCommunion,
       COALESCE(ls.Name,'Not selected') AS Lectionary,
       COALESCE(p.Season,'') AS Season,
       COALESCE(NULLIF(TRIM(s.LiturgicalColorOverride),''),p.Color,'') AS Color,
       COALESCE(p.Theme,'') AS Theme,
       COALESCE(t.Name,'Not selected') AS OrderOfService,
       TRIM(CONCAT_WS(' - ',NULLIF(se.Reference,''),NULLIF(se.Title,''))) AS Sermon,
       COALESCE(s.Bulletin,'') AS Bulletin,COALESCE(s.OSNote,'') AS OSNote,
       COALESCE(s.Note,'') AS Note
FROM tblService s
LEFT JOIN tblPropers p ON p.ID=s.PropersID
LEFT JOIN tblLectionarySystem ls ON ls.ID=p.LectionarySystemID
LEFT JOIN tblBulletinOrderTemplate t ON t.ID=s.BulletinOrderTemplateID
LEFT JOIN tblSermon se ON se.ID=s.SermonID;
