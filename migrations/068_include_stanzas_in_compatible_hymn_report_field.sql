-- Keep older customized Worship Planning layouts useful. Their combined Hymn
-- field must include the same formatted reference (including stanzas) that the
-- current starter displays in its separate Reference column.
DROP VIEW IF EXISTS rpt_worship_planner_hymn;
CREATE SQL SECURITY DEFINER VIEW rpt_worship_planner_hymn AS
SELECT u.ID,u.ServiceID,l.Sequence,u.HymnID,u.UsedAs,
       COALESCE(h.Hymn,'') AS HymnNumber,
       COALESCE(h.Title,'') AS Title,
       u.Stanzas,
       COALESCE(l.ReferenceText,h.Hymn,'') AS ReferenceText,
       TRIM(CONCAT_WS(' ',
           NULLIF(COALESCE(l.ReferenceText,h.Hymn),''),
           NULLIF(h.Title,''))) AS Hymn
FROM tblHymnUsage u
JOIN tblHymn h ON h.ID=u.HymnID
LEFT JOIN tblServiceBulletinOrderLine l ON l.ID=u.ServiceBulletinOrderLineID;
