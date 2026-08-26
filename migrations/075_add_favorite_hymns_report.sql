-- Add the metadata-only Favorite Hymns report with an exact #favorite tag match.

UPDATE tblHymn
SET Note=TRIM(CONCAT(COALESCE(NULLIF(TRIM(Note),''),''),
                     CASE WHEN NULLIF(TRIM(Note),'') IS NULL THEN '' ELSE ' ' END,
                     '#favorite'))
WHERE HymnalID=2 AND EntrySlot=363
  AND COALESCE(Note,'') NOT REGEXP '(^|[^[:alnum:]_])#favorite([^[:alnum:]_]|$)';

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_favorite_hymn AS
SELECT h.ID AS HymnID,h.HymnalID,y.Hymnal AS Hymnal,
       COALESCE(NULLIF(h.PrintedReference,''),h.Hymn) AS PrintedReference,
       h.Title,h.Tune,h.Category,h.BibleText
FROM tblHymn h
JOIN tblHymnal y ON y.ID=h.HymnalID
WHERE h.IsActive=1
  AND COALESCE(h.Note,'') REGEXP '(^|[^[:alnum:]_])#favorite([^[:alnum:]_]|$)';

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMHU05','Favorite Hymns','[ChurchID\r\nHymnalID]',NULL,
       'Favorite hymns in the selected hymnal, identified by the #favorite note tag.',1,p.ID
FROM tblPermission p WHERE p.Name='reports.worship.run'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);
