-- Remove the non-distributable LSB lectionary catalog from the new system.
-- Historical service reading snapshots for removed LSB Propers are discarded.

CREATE TEMPORARY TABLE cm_remove_lectionary_system (
    ID int PRIMARY KEY
);

INSERT INTO cm_remove_lectionary_system (ID)
SELECT ID
FROM tblLectionarySystem
WHERE Name LIKE 'LSB %'
   OR Name LIKE 'Lutheran Service Book%';

CREATE TEMPORARY TABLE cm_remove_lectionary_edition (
    ID int PRIMARY KEY,
    PackageID int NULL
);

INSERT INTO cm_remove_lectionary_edition (ID,PackageID)
SELECT ID,PackageID
FROM tblLectionaryEdition
WHERE LectionarySystemID IN (SELECT ID FROM cm_remove_lectionary_system);

CREATE TEMPORARY TABLE cm_remove_proper (
    ID int PRIMARY KEY
);

INSERT INTO cm_remove_proper (ID)
SELECT ID
FROM tblPropers
WHERE LectionarySystemID IN (SELECT ID FROM cm_remove_lectionary_system)
   OR LectionaryEditionID IN (SELECT ID FROM cm_remove_lectionary_edition);

CREATE TEMPORARY TABLE cm_remove_appointment (
    ID int PRIMARY KEY
);

INSERT INTO cm_remove_appointment (ID)
SELECT ID
FROM tblReading
WHERE PropersID IN (SELECT ID FROM cm_remove_proper);

CREATE TEMPORARY TABLE cm_remove_service_snapshot (
    ID int PRIMARY KEY
);

INSERT INTO cm_remove_service_snapshot (ID)
SELECT ID
FROM tblService
WHERE PropersID IN (SELECT ID FROM cm_remove_proper);

UPDATE tblChurch
SET PrimaryLectionaryEditionID=NULL
WHERE PrimaryLectionaryEditionID IN (SELECT ID FROM cm_remove_lectionary_edition);

UPDATE tblService
SET PropersID=NULL
WHERE PropersID IN (SELECT ID FROM cm_remove_proper);

DELETE FROM tblServiceReadingSnapshot
WHERE ServiceID IN (SELECT ID FROM cm_remove_service_snapshot);

UPDATE tblReading
SET PairedAppointmentID=NULL
WHERE PairedAppointmentID IN (SELECT ID FROM cm_remove_appointment);

DELETE FROM tblProperHymnSuggestion
WHERE PropersID IN (SELECT ID FROM cm_remove_proper);

DELETE FROM tblReading
WHERE ID IN (SELECT ID FROM cm_remove_appointment);

DELETE FROM tblPropers
WHERE ID IN (SELECT ID FROM cm_remove_proper);

DELETE FROM tblLectionaryCycle
WHERE LectionaryEditionID IN (SELECT ID FROM cm_remove_lectionary_edition);

DELETE FROM tblLectionaryEdition
WHERE ID IN (SELECT ID FROM cm_remove_lectionary_edition);

DELETE FROM tblLectionarySystem
WHERE ID IN (SELECT ID FROM cm_remove_lectionary_system);

DELETE FROM tblLectionaryPackageImport
WHERE LectionaryPackageID IN (
    SELECT PackageID
    FROM cm_remove_lectionary_edition
    WHERE PackageID IS NOT NULL
)
AND NOT EXISTS (
    SELECT 1 FROM tblLectionaryEdition retained
    WHERE retained.PackageID=tblLectionaryPackageImport.LectionaryPackageID
)
AND NOT EXISTS (
    SELECT 1 FROM tblLectionarySystem retained_system
    WHERE retained_system.PackageID=tblLectionaryPackageImport.LectionaryPackageID
);

DELETE FROM tblLectionaryPackage
WHERE ID IN (
    SELECT PackageID
    FROM cm_remove_lectionary_edition
    WHERE PackageID IS NOT NULL
)
AND NOT EXISTS (
    SELECT 1 FROM tblLectionaryEdition retained
    WHERE retained.PackageID=tblLectionaryPackage.ID
)
AND NOT EXISTS (
    SELECT 1 FROM tblLectionarySystem retained_system
    WHERE retained_system.PackageID=tblLectionaryPackage.ID
);

DROP TEMPORARY TABLE cm_remove_appointment;
DROP TEMPORARY TABLE cm_remove_service_snapshot;
DROP TEMPORARY TABLE cm_remove_proper;
DROP TEMPORARY TABLE cm_remove_lectionary_edition;
DROP TEMPORARY TABLE cm_remove_lectionary_system;
