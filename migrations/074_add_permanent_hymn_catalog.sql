ALTER TABLE tblHymnal
    ADD COLUMN IF NOT EXISTS PackageCode varchar(100) NULL,
    ADD COLUMN IF NOT EXISTS PackageVersion varchar(50) NULL,
    ADD COLUMN IF NOT EXISTS Edition varchar(255) NULL,
    ADD COLUMN IF NOT EXISTS PublicationYear smallint unsigned NULL,
    ADD COLUMN IF NOT EXISTS ISBN varchar(40) NULL,
    ADD COLUMN IF NOT EXISTS HymnIDStart int NULL,
    ADD COLUMN IF NOT EXISTS HymnIDEnd int NULL,
    ADD COLUMN IF NOT EXISTS IsActive tinyint(1) NOT NULL DEFAULT 1;

ALTER TABLE tblHymnal
    ADD UNIQUE KEY IF NOT EXISTS uq_hymnal_package_code (PackageCode),
    ADD UNIQUE KEY IF NOT EXISTS uq_hymnal_id_range_start (HymnIDStart),
    ADD UNIQUE KEY IF NOT EXISTS uq_hymnal_id_range_end (HymnIDEnd);

ALTER TABLE tblHymn
    ADD COLUMN IF NOT EXISTS EntrySlot smallint unsigned NULL,
    ADD COLUMN IF NOT EXISTS PrintedReference varchar(50) NULL,
    ADD COLUMN IF NOT EXISTS PrintedStanzaCount smallint unsigned NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS IsActive tinyint(1) NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS PackageOwned tinyint(1) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS FirstLine varchar(500) NULL,
    ADD COLUMN IF NOT EXISTS Meter varchar(50) NULL,
    ADD COLUMN IF NOT EXISTS Author varchar(255) NULL,
    ADD COLUMN IF NOT EXISTS Translator varchar(255) NULL,
    ADD COLUMN IF NOT EXISTS Composer varchar(255) NULL,
    ADD COLUMN IF NOT EXISTS SourceNote text NULL,
    ADD COLUMN IF NOT EXISTS TextCopyrightStatus varchar(20) NOT NULL DEFAULT 'UNKNOWN',
    ADD COLUMN IF NOT EXISTS TuneCopyrightStatus varchar(20) NOT NULL DEFAULT 'UNKNOWN',
    ADD COLUMN IF NOT EXISTS SettingCopyrightStatus varchar(20) NOT NULL DEFAULT 'UNKNOWN',
    ADD COLUMN IF NOT EXISTS CopyrightOwner varchar(255) NULL,
    ADD COLUMN IF NOT EXISTS CopyrightYear smallint unsigned NULL,
    ADD COLUMN IF NOT EXISTS LicenseSource varchar(100) NULL,
    ADD COLUMN IF NOT EXISTS LicenseReference varchar(255) NULL,
    ADD COLUMN IF NOT EXISTS CopyrightNote text NULL,
    ADD COLUMN IF NOT EXISTS CopyrightVerifiedDate date NULL,
    ADD COLUMN IF NOT EXISTS CopyrightVerifiedBy varchar(255) NULL;

ALTER TABLE tblHymn
    ADD UNIQUE KEY IF NOT EXISTS uq_hymn_hymnal_entry_slot (HymnalID,EntrySlot),
    ADD KEY IF NOT EXISTS ix_hymn_active_reference (HymnalID,IsActive,PrintedReference);

CREATE TABLE IF NOT EXISTS tblHymnalPackageImport (
    ID bigint NOT NULL AUTO_INCREMENT,
    HymnalID int NOT NULL,
    PackageCode varchar(100) NOT NULL,
    PackageVersion varchar(50) NOT NULL,
    Checksum char(64) NOT NULL,
    Action varchar(20) NOT NULL,
    EntryCount int NOT NULL,
    WarningCount int NOT NULL DEFAULT 0,
    ImportedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    KEY ix_hymnal_package_import (HymnalID,ImportedAt),
    CONSTRAINT fk_hymnal_package_import_hymnal FOREIGN KEY (HymnalID)
        REFERENCES tblHymnal(ID) ON DELETE RESTRICT
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

CREATE TABLE IF NOT EXISTS tblLocalHymnIDAllocation (
    HymnID int NOT NULL,
    EntrySlot smallint unsigned NOT NULL,
    AllocatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    RetiredAt datetime NULL,
    PRIMARY KEY (HymnID),
    UNIQUE KEY uq_local_hymn_entry_slot (EntrySlot)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

CREATE TABLE IF NOT EXISTS tblHymnIDConversionLog (
    ID bigint NOT NULL AUTO_INCREMENT,
    MigrationCode varchar(100) NOT NULL,
    HymnalID int NOT NULL,
    OldHymnID int NOT NULL,
    PermanentHymnID int NOT NULL,
    EntrySlot smallint unsigned NOT NULL,
    PrintedReference varchar(50) NOT NULL,
    ConvertedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_hymn_id_conversion (MigrationCode,OldHymnID),
    UNIQUE KEY uq_hymn_permanent_conversion (MigrationCode,PermanentHymnID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

DROP PROCEDURE IF EXISTS cm_migrate_permanent_lsb_hymn_ids;
DELIMITER $$
CREATE PROCEDURE cm_migrate_permanent_lsb_hymn_ids()
BEGIN
    DECLARE lsb_count int DEFAULT 0;
    DECLARE lsb_old_id int DEFAULT NULL;
    DECLARE invalid_count int DEFAULT 0;

    -- ChurchDBTest worship records are disposable at this conversion boundary.
    -- Remove them before pruning synthetic or out-of-scope hymn records so no
    -- historical service can retain an invalid hymn reference.
    DELETE attendance_record FROM tblAttendance attendance_record
    JOIN tblAttendanceEvent attendance_event
      ON attendance_event.ID=attendance_record.AttendanceEventID
    WHERE attendance_event.ServiceID IS NOT NULL;
    DELETE FROM tblAttendanceEvent WHERE ServiceID IS NOT NULL;
    DELETE FROM tblSecurityAuditEvent
    WHERE EntityType='WORSHIP_SERVICE' OR Action='WORSHIP_SERVICE_DELETED';
    DELETE FROM tblService;

    -- Remove the old synthetic test catalog and anything tied specifically to
    -- it. A prior interrupted run may already have moved its T001-T008 entries
    -- into the Local block, so recognize those fixtures by their stable codes.
    DELETE suggestion FROM tblProperHymnSuggestion suggestion
    JOIN tblHymn hymn ON hymn.ID=suggestion.HymnID
    LEFT JOIN tblHymnal hymnal ON hymnal.ID=hymn.HymnalID
    WHERE (
        UPPER(TRIM(hymnal.Hymnal))='TEST'
        AND hymnal.Title='Synthetic Test Hymnal'
        AND hymnal.Publisher='ChurchManager Test Data'
    ) OR (hymn.Hymn REGEXP '^T00[1-8]$' AND hymn.Title LIKE 'Test % Hymn');
    DELETE allocation FROM tblLocalHymnIDAllocation allocation
    JOIN tblHymn hymn ON hymn.ID=allocation.HymnID
    WHERE hymn.Hymn REGEXP '^T00[1-8]$' AND hymn.Title LIKE 'Test % Hymn';
    DELETE FROM tblHymn
    WHERE (Hymn REGEXP '^T00[1-8]$' AND Title LIKE 'Test % Hymn')
       OR HymnalID IN (
           SELECT ID FROM tblHymnal
           WHERE UPPER(TRIM(Hymnal))='TEST'
             AND Title='Synthetic Test Hymnal'
             AND Publisher='ChurchManager Test Data'
       );
    UPDATE tblChurch SET PrimaryHymnalID=NULL
    WHERE PrimaryHymnalID IN (
        SELECT ID FROM tblHymnal
        WHERE UPPER(TRIM(Hymnal))='TEST'
          AND Title='Synthetic Test Hymnal'
          AND Publisher='ChurchManager Test Data'
    );
    DELETE FROM tblBulletinOrderTemplate
    WHERE HymnalID IN (
        SELECT ID FROM tblHymnal
        WHERE UPPER(TRIM(Hymnal))='TEST'
          AND Title='Synthetic Test Hymnal'
          AND Publisher='ChurchManager Test Data'
    );
    DELETE FROM tblHymnal
    WHERE UPPER(TRIM(Hymnal))='TEST'
      AND Title='Synthetic Test Hymnal'
      AND Publisher='ChurchManager Test Data';
    DELETE FROM tblHymnIDConversionLog
    WHERE MigrationCode='074_permanent_local_ids'
      AND PrintedReference REGEXP '^T00[1-8]$';

    SELECT COUNT(*),MIN(ID) INTO lsb_count,lsb_old_id
    FROM tblHymnal WHERE UPPER(TRIM(Hymnal))='LSB';
    IF lsb_count > 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Permanent hymn migration requires exactly zero or one LSB hymnal record';
    END IF;

    SELECT COUNT(*) INTO invalid_count FROM tblHymnal
    WHERE UPPER(TRIM(Hymnal)) NOT IN ('LSB','LOCAL')
      AND NOT (
          UPPER(TRIM(Hymnal))='TEST'
          AND Title='Synthetic Test Hymnal'
          AND Publisher='ChurchManager Test Data'
      );
    IF invalid_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Unregistered hymnals must receive an approved permanent block before migration';
    END IF;

    SELECT COUNT(*) INTO invalid_count FROM tblHymnal
    WHERE ID=2 AND UPPER(TRIM(Hymnal))<>'LSB';
    IF invalid_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Permanent HymnalID 2 is already occupied by a non-LSB record';
    END IF;
    SELECT COUNT(*) INTO invalid_count FROM tblHymnal
    WHERE ID=1 AND UPPER(TRIM(Hymnal)) NOT IN ('LOCAL','LSB');
    IF invalid_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Permanent HymnalID 1 is already occupied by a non-local record';
    END IF;

    IF lsb_count=0 THEN
        INSERT INTO tblHymnal
            (ID,Hymnal,Title,Publisher,Note,PackageCode,PackageVersion,Edition,
             PublicationYear,ISBN,HymnIDStart,HymnIDEnd,IsActive)
        VALUES
            (2,'LSB','Lutheran Service Book','Concordia Publishing House',
             'Installed metadata catalog; no lyrics or music are stored.',
             'lsb','1.0.0','Pew Edition',2006,'978-0-7586-0217-5',10001,14999,1);
        SET lsb_old_id=2;
    ELSEIF lsb_old_id<>2 THEN
        INSERT INTO tblHymnal
            (ID,Hymnal,Title,Publisher,Note,PackageCode,PackageVersion,Edition,
             PublicationYear,ISBN,HymnIDStart,HymnIDEnd,IsActive)
        SELECT 2,Hymnal,Title,Publisher,Note,'lsb','1.0.0','Pew Edition',2006,
               '978-0-7586-0217-5',10001,14999,1
        FROM tblHymnal WHERE ID=lsb_old_id;
        UPDATE tblHymn SET HymnalID=2 WHERE HymnalID=lsb_old_id;
        UPDATE tblChurch SET PrimaryHymnalID=2 WHERE PrimaryHymnalID=lsb_old_id;
        UPDATE tblBulletinOrderTemplate SET HymnalID=2 WHERE HymnalID=lsb_old_id;
        DELETE FROM tblHymnal WHERE ID=lsb_old_id;
        SET lsb_old_id=2;
    END IF;

    UPDATE tblHymnal SET
        Hymnal='LSB',Title='Lutheran Service Book',
        Publisher='Concordia Publishing House',PackageCode='lsb',
        PackageVersion='1.0.0',Edition='Pew Edition',PublicationYear=2006,
        ISBN='978-0-7586-0217-5',HymnIDStart=10001,HymnIDEnd=14999,IsActive=1
    WHERE ID=2;

    INSERT INTO tblHymnal
        (ID,Hymnal,Title,Publisher,Note,PackageCode,PackageVersion,Edition,
         HymnIDStart,HymnIDEnd,IsActive)
    SELECT 1,'LOCAL','Local Congregation Hymns','Local Congregation',
           'Congregation-owned hymn metadata. IDs are never reused.',
           'local','1.0.0','Local',5001,9999,1
    WHERE NOT EXISTS (SELECT 1 FROM tblHymnal WHERE ID=1);
    UPDATE tblHymnal SET
        Hymnal='LOCAL',Title='Local Congregation Hymns',
        Publisher='Local Congregation',PackageCode='local',
        PackageVersion='1.0.0',Edition='Local',HymnIDStart=5001,HymnIDEnd=9999,
        IsActive=1
    WHERE ID=1;

    DROP TEMPORARY TABLE IF EXISTS tmp_local_hymn_id_map;
    CREATE TEMPORARY TABLE tmp_local_hymn_id_map (
        OldHymnID int NOT NULL PRIMARY KEY,
        PermanentHymnID int NOT NULL UNIQUE,
        EntrySlot smallint unsigned NOT NULL UNIQUE,
        PrintedReference varchar(50) NOT NULL
    ) ENGINE=InnoDB;
    INSERT INTO tmp_local_hymn_id_map
        (OldHymnID,PermanentHymnID,EntrySlot,PrintedReference)
    SELECT ID,5000+ID,ID,COALESCE(NULLIF(PrintedReference,''),Hymn)
    FROM tblHymn WHERE HymnalID=1 AND ID BETWEEN 1 AND 4999;

    SELECT COUNT(*) INTO invalid_count
    FROM tmp_local_hymn_id_map map
    JOIN tblHymn existing ON existing.ID=map.PermanentHymnID;
    IF invalid_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='A permanent local HymnID is already occupied';
    END IF;

    INSERT INTO tblHymn
        (ID,HymnalID,Hymn,Title,Tune,BibleText,Category,File,Image,Note,
         EntrySlot,PrintedReference,PrintedStanzaCount,IsActive,PackageOwned,
         FirstLine,Meter,Author,Translator,Composer,SourceNote,
         TextCopyrightStatus,TuneCopyrightStatus,SettingCopyrightStatus,
         CopyrightOwner,CopyrightYear,LicenseSource,LicenseReference,
         CopyrightNote,CopyrightVerifiedDate,CopyrightVerifiedBy)
    SELECT map.PermanentHymnID,1,old.Hymn,old.Title,old.Tune,old.BibleText,
           old.Category,old.File,old.Image,old.Note,map.EntrySlot,map.PrintedReference,
           old.PrintedStanzaCount,old.IsActive,0,old.FirstLine,old.Meter,
           old.Author,old.Translator,old.Composer,old.SourceNote,old.TextCopyrightStatus,
           old.TuneCopyrightStatus,old.SettingCopyrightStatus,old.CopyrightOwner,
           old.CopyrightYear,old.LicenseSource,old.LicenseReference,
           old.CopyrightNote,old.CopyrightVerifiedDate,old.CopyrightVerifiedBy
    FROM tmp_local_hymn_id_map map JOIN tblHymn old ON old.ID=map.OldHymnID;

    INSERT INTO tblHymnIDConversionLog
        (MigrationCode,HymnalID,OldHymnID,PermanentHymnID,EntrySlot,PrintedReference)
    SELECT '074_permanent_local_ids',1,OldHymnID,PermanentHymnID,EntrySlot,PrintedReference
    FROM tmp_local_hymn_id_map;
    UPDATE tblHymnUsage usage_record
    JOIN tmp_local_hymn_id_map map ON map.OldHymnID=usage_record.HymnID
    SET usage_record.HymnID=map.PermanentHymnID;
    UPDATE tblProperHymnSuggestion suggestion
    JOIN tmp_local_hymn_id_map map ON map.OldHymnID=suggestion.HymnID
    SET suggestion.HymnID=map.PermanentHymnID;
    DELETE old FROM tblHymn old
    JOIN tmp_local_hymn_id_map map ON map.OldHymnID=old.ID;

    SELECT COUNT(*) INTO invalid_count FROM tblHymn
    WHERE HymnalID=1 AND (ID<5001 OR ID>9999);
    IF invalid_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Existing local hymns require an explicit permanent-ID review';
    END IF;
    INSERT IGNORE INTO tblLocalHymnIDAllocation (HymnID,EntrySlot)
    SELECT ID,ID-5000 FROM tblHymn WHERE HymnalID=1;
    UPDATE tblHymn SET EntrySlot=ID-5000,
        PrintedReference=COALESCE(NULLIF(PrintedReference,''),Hymn),PackageOwned=0
    WHERE HymnalID=1;
    DROP TEMPORARY TABLE tmp_local_hymn_id_map;

    DELETE suggestion FROM tblProperHymnSuggestion suggestion
    JOIN tblHymn hymn ON hymn.ID=suggestion.HymnID
    WHERE hymn.HymnalID=2 AND NOT (
        TRIM(Hymn) REGEXP '^(LSB[[:space:]]+)?[0-9]+$'
        AND CAST(SUBSTRING_INDEX(TRIM(Hymn),' ',-1) AS UNSIGNED) BETWEEN 1 AND 966
    );
    DELETE FROM tblHymn
    WHERE HymnalID=2 AND NOT (
        TRIM(Hymn) REGEXP '^(LSB[[:space:]]+)?[0-9]+$'
        AND CAST(SUBSTRING_INDEX(TRIM(Hymn),' ',-1) AS UNSIGNED) BETWEEN 1 AND 966
    );

    SELECT COUNT(*) INTO invalid_count FROM (
        SELECT CAST(SUBSTRING_INDEX(TRIM(Hymn),' ',-1) AS UNSIGNED) AS slot_number
        FROM tblHymn WHERE HymnalID=2
        GROUP BY slot_number HAVING COUNT(*)>1
    ) duplicate_slots;
    IF invalid_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='LSB conversion contains duplicate printed hymn numbers';
    END IF;

    DROP TEMPORARY TABLE IF EXISTS tmp_lsb_hymn_id_map;
    CREATE TEMPORARY TABLE tmp_lsb_hymn_id_map (
        OldHymnID int NOT NULL PRIMARY KEY,
        PermanentHymnID int NOT NULL UNIQUE,
        EntrySlot smallint unsigned NOT NULL UNIQUE,
        PrintedReference varchar(50) NOT NULL
    ) ENGINE=InnoDB;
    INSERT INTO tmp_lsb_hymn_id_map (OldHymnID,PermanentHymnID,EntrySlot,PrintedReference)
    SELECT ID,10000+CAST(SUBSTRING_INDEX(TRIM(Hymn),' ',-1) AS UNSIGNED),
           CAST(SUBSTRING_INDEX(TRIM(Hymn),' ',-1) AS UNSIGNED),
           CONCAT('LSB ',CAST(SUBSTRING_INDEX(TRIM(Hymn),' ',-1) AS UNSIGNED))
    FROM tblHymn WHERE HymnalID=2 AND NOT (ID BETWEEN 10001 AND 14999);

    SELECT COUNT(*) INTO invalid_count
    FROM tmp_lsb_hymn_id_map map
    JOIN tblHymn existing ON existing.ID=map.PermanentHymnID
    LEFT JOIN tmp_lsb_hymn_id_map source_map ON source_map.OldHymnID=existing.ID
    WHERE source_map.OldHymnID IS NULL;
    IF invalid_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='A permanent LSB HymnID is already occupied';
    END IF;

    INSERT INTO tblHymn
        (ID,HymnalID,Hymn,Title,Tune,BibleText,Category,File,Image,Note,
         EntrySlot,PrintedReference,PrintedStanzaCount,IsActive,PackageOwned,
         FirstLine,Meter,Author,Translator,Composer,SourceNote,
         TextCopyrightStatus,TuneCopyrightStatus,SettingCopyrightStatus,
         CopyrightOwner,CopyrightYear,LicenseSource,LicenseReference,
         CopyrightNote,CopyrightVerifiedDate,CopyrightVerifiedBy)
    SELECT map.PermanentHymnID,2,old.Hymn,old.Title,old.Tune,old.BibleText,
           old.Category,old.File,old.Image,old.Note,map.EntrySlot,map.PrintedReference,
           old.PrintedStanzaCount,old.IsActive,1,old.FirstLine,old.Meter,
           old.Author,old.Translator,old.Composer,old.SourceNote,old.TextCopyrightStatus,
           old.TuneCopyrightStatus,old.SettingCopyrightStatus,old.CopyrightOwner,
           old.CopyrightYear,old.LicenseSource,old.LicenseReference,
           old.CopyrightNote,old.CopyrightVerifiedDate,old.CopyrightVerifiedBy
    FROM tmp_lsb_hymn_id_map map JOIN tblHymn old ON old.ID=map.OldHymnID;

    INSERT INTO tblHymnIDConversionLog
        (MigrationCode,HymnalID,OldHymnID,PermanentHymnID,EntrySlot,PrintedReference)
    SELECT '074_permanent_lsb_ids',2,OldHymnID,PermanentHymnID,EntrySlot,PrintedReference
    FROM tmp_lsb_hymn_id_map;

    UPDATE tblHymnUsage usage_record
    JOIN tmp_lsb_hymn_id_map map ON map.OldHymnID=usage_record.HymnID
    SET usage_record.HymnID=map.PermanentHymnID;
    UPDATE tblProperHymnSuggestion suggestion
    JOIN tmp_lsb_hymn_id_map map ON map.OldHymnID=suggestion.HymnID
    SET suggestion.HymnID=map.PermanentHymnID;
    DELETE old FROM tblHymn old
    JOIN tmp_lsb_hymn_id_map map ON map.OldHymnID=old.ID;

    UPDATE tblHymn SET
        EntrySlot=CAST(SUBSTRING_INDEX(TRIM(Hymn),' ',-1) AS UNSIGNED),
        PrintedReference=CONCAT('LSB ',CAST(SUBSTRING_INDEX(TRIM(Hymn),' ',-1) AS UNSIGNED)),
        PackageOwned=1,IsActive=1
    WHERE HymnalID=2;

    SELECT COUNT(*) INTO invalid_count FROM tblHymn h
    LEFT JOIN tblHymnal y ON y.ID=h.HymnalID
    WHERE y.ID IS NULL OR h.ID<y.HymnIDStart OR h.ID>y.HymnIDEnd
       OR h.EntrySlot<1 OR h.EntrySlot>4999;
    IF invalid_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Permanent hymn range verification failed';
    END IF;

    DROP TEMPORARY TABLE tmp_lsb_hymn_id_map;
END$$
DELIMITER ;

CALL cm_migrate_permanent_lsb_hymn_ids();
DROP PROCEDURE cm_migrate_permanent_lsb_hymn_ids;

ALTER TABLE tblHymnUsage DROP FOREIGN KEY fk_hymnusage_hymn;
ALTER TABLE tblHymnUsage
    ADD CONSTRAINT fk_hymnusage_hymn FOREIGN KEY (HymnID)
        REFERENCES tblHymn(ID) ON DELETE RESTRICT;

ALTER TABLE tblProperHymnSuggestion DROP FOREIGN KEY fk_proper_hymn_suggestion_hymn;
ALTER TABLE tblProperHymnSuggestion
    ADD CONSTRAINT fk_proper_hymn_suggestion_hymn FOREIGN KEY (HymnID)
        REFERENCES tblHymn(ID) ON DELETE RESTRICT;

ALTER TABLE tblHymn MODIFY COLUMN ID int NOT NULL;
ALTER TABLE tblHymnal MODIFY COLUMN ID int NOT NULL;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_hymn AS
SELECT ID,HymnalID,EntrySlot,PrintedReference,Hymn,Title,Tune,BibleText,Category,
       PrintedStanzaCount,IsActive,FirstLine,Meter,Author,Translator,Composer,
       SourceNote,TextCopyrightStatus,TuneCopyrightStatus,
       SettingCopyrightStatus,CopyrightOwner,CopyrightYear,LicenseSource,
       LicenseReference,CopyrightNote,CopyrightVerifiedDate,CopyrightVerifiedBy,Note
FROM tblHymn;
