-- Add the versioned lectionary package structure without cutting over current screens.

CREATE TABLE IF NOT EXISTS tblLectionaryPackage (
    ID int NOT NULL AUTO_INCREMENT,
    PackageCode varchar(100) NOT NULL,
    PackageVersion varchar(50) NOT NULL,
    Title varchar(255) NOT NULL,
    SourceName varchar(255) NOT NULL,
    SourceReference varchar(500) NOT NULL,
    PackageNotice varchar(500) NOT NULL,
    Checksum char(64) NOT NULL,
    InstalledAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    IsActive tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_lectionary_package_code (PackageCode),
    CONSTRAINT chk_lectionary_package_active CHECK (IsActive IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tblLectionaryPackageImport (
    ID bigint NOT NULL AUTO_INCREMENT,
    LectionaryPackageID int NOT NULL,
    PackageVersion varchar(50) NOT NULL,
    Checksum char(64) NOT NULL,
    Action varchar(20) NOT NULL,
    SystemCount int NOT NULL,
    EditionCount int NOT NULL,
    CycleCount int NOT NULL,
    ProperCount int NOT NULL,
    AppointmentCount int NOT NULL,
    ImportedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    KEY ix_lectionary_package_import (LectionaryPackageID,ImportedAt),
    CONSTRAINT fk_lectionary_package_import_package
        FOREIGN KEY (LectionaryPackageID) REFERENCES tblLectionaryPackage(ID)
        ON DELETE RESTRICT,
    CONSTRAINT chk_lectionary_package_import_action
        CHECK (Action IN ('INSTALL','UPGRADE'))
) ENGINE=InnoDB;

ALTER TABLE tblLectionarySystem
    ADD COLUMN IF NOT EXISTS SystemCode varchar(150) NULL AFTER ID,
    ADD COLUMN IF NOT EXISTS PackageID int NULL AFTER SystemCode,
    ADD COLUMN IF NOT EXISTS IsStarter tinyint(1) NOT NULL DEFAULT 0 AFTER Active,
    ADD UNIQUE KEY IF NOT EXISTS uq_lectionary_system_code (SystemCode),
    ADD KEY IF NOT EXISTS ix_lectionary_system_package (PackageID),
    ADD CONSTRAINT fk_lectionary_system_package
        FOREIGN KEY (PackageID) REFERENCES tblLectionaryPackage(ID)
        ON DELETE RESTRICT;

CREATE TABLE IF NOT EXISTS tblLectionaryEdition (
    ID int NOT NULL AUTO_INCREMENT,
    LectionarySystemID int NOT NULL,
    EditionCode varchar(150) NOT NULL,
    Name varchar(255) NOT NULL,
    EditionYear smallint NULL,
    Status varchar(20) NOT NULL DEFAULT 'STABLE',
    ValidFrom date NULL,
    ValidThrough date NULL,
    PackageID int NULL,
    IsStarter tinyint(1) NOT NULL DEFAULT 0,
    IsActive tinyint(1) NOT NULL DEFAULT 1,
    SourceNote text NULL,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_lectionary_edition_code (EditionCode),
    KEY ix_lectionary_edition_system (LectionarySystemID,IsActive),
    KEY ix_lectionary_edition_package (PackageID),
    CONSTRAINT fk_lectionary_edition_system
        FOREIGN KEY (LectionarySystemID) REFERENCES tblLectionarySystem(ID)
        ON DELETE RESTRICT,
    CONSTRAINT fk_lectionary_edition_package
        FOREIGN KEY (PackageID) REFERENCES tblLectionaryPackage(ID)
        ON DELETE RESTRICT,
    CONSTRAINT chk_lectionary_edition_status
        CHECK (Status IN ('STABLE','TRIAL','RETIRED','LOCAL')),
    CONSTRAINT chk_lectionary_edition_dates
        CHECK (ValidThrough IS NULL OR ValidFrom IS NULL OR ValidThrough>=ValidFrom),
    CONSTRAINT chk_lectionary_edition_flags
        CHECK (IsStarter IN (0,1) AND IsActive IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tblLectionaryCycle (
    ID int NOT NULL AUTO_INCREMENT,
    LectionaryEditionID int NOT NULL,
    CycleCode varchar(100) NOT NULL,
    DisplayName varchar(100) NOT NULL,
    Sequence int NOT NULL,
    IsActive tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_lectionary_cycle_code (LectionaryEditionID,CycleCode),
    UNIQUE KEY uq_lectionary_cycle_sequence (LectionaryEditionID,Sequence),
    CONSTRAINT fk_lectionary_cycle_edition
        FOREIGN KEY (LectionaryEditionID) REFERENCES tblLectionaryEdition(ID)
        ON DELETE RESTRICT,
    CONSTRAINT chk_lectionary_cycle_sequence CHECK (Sequence>0),
    CONSTRAINT chk_lectionary_cycle_active CHECK (IsActive IN (0,1))
) ENGINE=InnoDB;

ALTER TABLE tblPropers
    ADD COLUMN IF NOT EXISTS LectionaryEditionID int NULL AFTER LectionarySystemID,
    ADD COLUMN IF NOT EXISTS LectionaryCycleID int NULL AFTER LectionaryEditionID,
    ADD COLUMN IF NOT EXISTS ProperKey varchar(200) NULL AFTER LectionaryCycleID,
    ADD COLUMN IF NOT EXISTS CalendarRule varchar(255) NULL AFTER AltColor,
    ADD COLUMN IF NOT EXISTS PackageID int NULL AFTER CalendarRule,
    ADD COLUMN IF NOT EXISTS IsStarter tinyint(1) NOT NULL DEFAULT 0 AFTER PackageID,
    ADD COLUMN IF NOT EXISTS IsActive tinyint(1) NOT NULL DEFAULT 1 AFTER IsStarter,
    ADD COLUMN IF NOT EXISTS SourceNote text NULL AFTER Note,
    ADD UNIQUE KEY IF NOT EXISTS uq_propers_stable_key (ProperKey),
    ADD KEY IF NOT EXISTS ix_propers_edition_cycle_sort
        (LectionaryEditionID,LectionaryCycleID,Sort),
    ADD KEY IF NOT EXISTS ix_propers_package (PackageID),
    ADD CONSTRAINT fk_propers_lectionary_edition
        FOREIGN KEY (LectionaryEditionID) REFERENCES tblLectionaryEdition(ID)
        ON DELETE RESTRICT,
    ADD CONSTRAINT fk_propers_lectionary_cycle
        FOREIGN KEY (LectionaryCycleID) REFERENCES tblLectionaryCycle(ID)
        ON DELETE RESTRICT,
    ADD CONSTRAINT fk_propers_package
        FOREIGN KEY (PackageID) REFERENCES tblLectionaryPackage(ID)
        ON DELETE RESTRICT;

ALTER TABLE tblReading
    ADD COLUMN IF NOT EXISTS AppointmentKey varchar(220) NULL AFTER PropersID,
    ADD COLUMN IF NOT EXISTS Role varchar(40) NULL AFTER AppointmentKey,
    ADD COLUMN IF NOT EXISTS DisplayRole varchar(100) NULL AFTER Role,
    ADD COLUMN IF NOT EXISTS DisplayCitation varchar(500) NULL AFTER Reference,
    ADD COLUMN IF NOT EXISTS NormalizedCitation varchar(500) NULL AFTER DisplayCitation,
    ADD COLUMN IF NOT EXISTS TrackCode varchar(100) NULL AFTER NormalizedCitation,
    ADD COLUMN IF NOT EXISTS OptionGroupCode varchar(100) NULL AFTER TrackCode,
    ADD COLUMN IF NOT EXISTS OptionType varchar(30) NULL AFTER OptionGroupCode,
    ADD COLUMN IF NOT EXISTS PairedAppointmentID int NULL AFTER OptionType,
    ADD COLUMN IF NOT EXISTS Sequence int NULL AFTER PairedAppointmentID,
    ADD COLUMN IF NOT EXISTS IsDefault tinyint(1) NOT NULL DEFAULT 1 AFTER Sequence,
    ADD COLUMN IF NOT EXISTS PackageID int NULL AFTER IsDefault,
    ADD COLUMN IF NOT EXISTS IsStarter tinyint(1) NOT NULL DEFAULT 0 AFTER PackageID,
    ADD COLUMN IF NOT EXISTS IsActive tinyint(1) NOT NULL DEFAULT 1 AFTER IsStarter,
    ADD UNIQUE KEY IF NOT EXISTS uq_reading_appointment_key (AppointmentKey),
    ADD KEY IF NOT EXISTS ix_reading_proper_sequence (PropersID,Sequence),
    ADD KEY IF NOT EXISTS ix_reading_pair (PairedAppointmentID),
    ADD KEY IF NOT EXISTS ix_reading_package (PackageID),
    ADD CONSTRAINT fk_reading_pair
        FOREIGN KEY (PairedAppointmentID) REFERENCES tblReading(ID)
        ON DELETE RESTRICT,
    ADD CONSTRAINT fk_reading_package
        FOREIGN KEY (PackageID) REFERENCES tblLectionaryPackage(ID)
        ON DELETE RESTRICT;

ALTER TABLE tblChurch
    ADD COLUMN IF NOT EXISTS PrimaryLectionaryEditionID int NULL AFTER PrimaryLectionarySystemID,
    ADD KEY IF NOT EXISTS ix_church_primary_lectionary_edition (PrimaryLectionaryEditionID),
    ADD CONSTRAINT fk_church_primary_lectionary_edition
        FOREIGN KEY (PrimaryLectionaryEditionID) REFERENCES tblLectionaryEdition(ID)
        ON DELETE SET NULL;
