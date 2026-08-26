CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_service AS
SELECT s.ID,s.ChurchID,s.DateTime,COALESCE(s.Location,'') AS Location,
       COALESCE(s.LiturgicalDate,p.LiturgicalDate,'') AS LiturgicalDate,
       s.HolyCommunion,
       COALESCE(ls.Name,'Not selected') AS Lectionary,
       COALESCE(p.Season,'') AS Season,COALESCE(p.Color,'') AS Color,
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

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_order AS
SELECT ID,ServiceID,Sequence,LineType,Label,COALESCE(WeeklyValue,'') AS WeeklyValue,
       COALESCE(ReferenceText,'') AS ReferenceText,COALESCE(Note,'') AS Note
FROM tblServiceBulletinOrderLine
WHERE Included=1;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_reading AS
SELECT r.ID,s.ID AS ServiceID,
       CASE LOWER(TRIM(r.Reading))
         WHEN 'old testament' THEN 1 WHEN 'epistle' THEN 2 WHEN 'gospel' THEN 3
         ELSE 9 END AS SortOrder,
       r.Reading,r.Reference
FROM tblService s
JOIN tblReading r ON r.PropersID=s.PropersID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_hymn AS
SELECT u.ID,u.ServiceID,l.Sequence,u.UsedAs,
       TRIM(CONCAT_WS(' ',NULLIF(h.Hymn,''),NULLIF(h.Title,''))) AS Hymn
FROM tblHymnUsage u
JOIN tblHymn h ON h.ID=u.HymnID
LEFT JOIN tblServiceBulletinOrderLine l ON l.ID=u.ServiceBulletinOrderLineID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_participant AS
SELECT sr.ID,sr.ServiceID,sr.Role,p.Name
FROM tblServiceRole sr
JOIN tblParticipant p ON p.ID=sr.ParticipantID;
