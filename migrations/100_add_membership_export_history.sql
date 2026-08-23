-- Record privacy-safe membership exports without retaining exported content.

CREATE TABLE tblMembershipExportHistory (
    ID BIGINT NOT NULL AUTO_INCREMENT,
    ChurchID INT NOT NULL,
    ExportedByUserID INT NOT NULL,
    EntityType VARCHAR(20) NOT NULL,
    DestinationFileName VARCHAR(255) NOT NULL,
    ExportSHA256 CHAR(64) NOT NULL,
    RowCount INT NOT NULL,
    IncludedUnlistedContacts TINYINT(1) NOT NULL DEFAULT 0,
    ExportedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    KEY ix_membership_export_church_time (ChurchID, ExportedAt),
    CONSTRAINT fk_membership_export_church
        FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_membership_export_user
        FOREIGN KEY (ExportedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT ck_membership_export_entity
        CHECK (EntityType IN ('People','Families')),
    CONSTRAINT ck_membership_export_count CHECK (RowCount >= 0)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;
