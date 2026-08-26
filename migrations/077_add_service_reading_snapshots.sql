-- Preserve the readings actually selected for each saved Worship Service.

CREATE TABLE IF NOT EXISTS tblServiceReadingSnapshot (
    ID bigint NOT NULL AUTO_INCREMENT,
    ServiceID int NOT NULL,
    SourceProperID int NULL,
    SourceAppointmentID int NULL,
    SourceSystemCode varchar(150) NULL,
    SourceEditionCode varchar(150) NULL,
    SourceProperKey varchar(200) NULL,
    SourceAppointmentKey varchar(220) NULL,
    SystemName varchar(255) NULL,
    EditionName varchar(255) NULL,
    CycleName varchar(100) NULL,
    ProperName varchar(255) NULL,
    Role varchar(40) NULL,
    Reading varchar(100) NOT NULL,
    Reference varchar(500) NOT NULL,
    NormalizedCitation varchar(500) NULL,
    TrackCode varchar(100) NULL,
    OptionGroupCode varchar(100) NULL,
    OptionType varchar(30) NULL,
    Sequence int NOT NULL,
    CreatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_service_reading_snapshot_sequence (ServiceID,Sequence),
    KEY ix_service_reading_snapshot_proper (SourceProperID),
    KEY ix_service_reading_snapshot_appointment (SourceAppointmentID),
    CONSTRAINT fk_service_reading_snapshot_service
        FOREIGN KEY (ServiceID) REFERENCES tblService(ID) ON DELETE CASCADE,
    CONSTRAINT fk_service_reading_snapshot_proper
        FOREIGN KEY (SourceProperID) REFERENCES tblPropers(ID) ON DELETE SET NULL,
    CONSTRAINT fk_service_reading_snapshot_appointment
        FOREIGN KEY (SourceAppointmentID) REFERENCES tblReading(ID) ON DELETE SET NULL,
    CONSTRAINT chk_service_reading_snapshot_sequence CHECK (Sequence>0)
) ENGINE=InnoDB;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_reading AS
SELECT ID,ServiceID,Sequence AS SortOrder,Reading,Reference
FROM tblServiceReadingSnapshot;
