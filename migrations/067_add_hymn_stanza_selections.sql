-- Store optional service-specific hymn stanza selections and expose them to reports.
ALTER TABLE tblHymnUsage
    ADD COLUMN IF NOT EXISTS Stanzas varchar(100) NULL AFTER UsedAs;

DROP VIEW IF EXISTS rpt_worship_planner_hymn;
CREATE SQL SECURITY DEFINER VIEW rpt_worship_planner_hymn AS
SELECT u.ID,u.ServiceID,l.Sequence,u.HymnID,u.UsedAs,
       COALESCE(h.Hymn,'') AS HymnNumber,
       COALESCE(h.Title,'') AS Title,
       u.Stanzas,
       COALESCE(l.ReferenceText,h.Hymn,'') AS ReferenceText,
       TRIM(CONCAT_WS(' ',NULLIF(h.Hymn,''),NULLIF(h.Title,''))) AS Hymn
FROM tblHymnUsage u
JOIN tblHymn h ON h.ID=u.HymnID
LEFT JOIN tblServiceBulletinOrderLine l ON l.ID=u.ServiceBulletinOrderLineID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_hymn_usage AS
SELECT ID,ChurchID,ServiceID,HymnID,UsedAs,Stanzas,Note
FROM tblHymnUsage;
