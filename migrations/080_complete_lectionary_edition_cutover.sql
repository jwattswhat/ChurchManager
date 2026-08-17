-- Make the installed/local lectionary edition the sole congregation default.

ALTER TABLE tblChurch
    DROP FOREIGN KEY IF EXISTS fk_church_primary_lectionary;

ALTER TABLE tblChurch
    DROP INDEX IF EXISTS ix_church_primary_lectionary,
    DROP COLUMN IF EXISTS PrimaryLectionarySystemID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW vwLectionaryEditionLookup AS
SELECT e.ID,
       CONCAT(s.Name, ' — ', e.Name) AS DisplayName
FROM tblLectionaryEdition e
JOIN tblLectionarySystem s ON s.ID=e.LectionarySystemID
LEFT JOIN tblLectionaryPackage p ON p.ID=e.PackageID
WHERE e.IsActive=1
  AND s.Active=1
  AND (e.PackageID IS NULL OR p.IsActive=1);
