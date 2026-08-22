-- Register generic, customizable mailing-label layouts backed by the secure directory dataset.

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMML03','Mailing Labels - Families','[ChurchID]',NULL,
       'Three-column family mailing labels using listed family addresses.',1,p.ID
FROM tblPermission p WHERE p.Name='reports.membership.contact'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMML04','Mailing Labels - Members','[ChurchID]',NULL,
       'Three-column individual mailing labels using listed family addresses.',1,p.ID
FROM tblPermission p WHERE p.Name='reports.membership.contact'
ON DUPLICATE KEY UPDATE
Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,
RequiredPermissionID=VALUES(RequiredPermissionID);
