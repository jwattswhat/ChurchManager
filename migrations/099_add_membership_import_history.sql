-- Record reviewed membership imports without retaining confidential source rows.

CREATE TABLE tblMembershipImportHistory (
    ID BIGINT NOT NULL AUTO_INCREMENT,
    ChurchID INT NOT NULL,
    ImportedByUserID INT NOT NULL,
    EntityType VARCHAR(20) NOT NULL,
    SourceFileName VARCHAR(255) NOT NULL,
    SourceSHA256 CHAR(64) NOT NULL,
    RowCount INT NOT NULL,
    ImportedCount INT NOT NULL,
    RejectedCount INT NOT NULL DEFAULT 0,
    ImportedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    KEY ix_membership_import_church_time (ChurchID, ImportedAt),
    CONSTRAINT fk_membership_import_church
        FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_membership_import_user
        FOREIGN KEY (ImportedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT ck_membership_import_entity
        CHECK (EntityType IN ('People','Families')),
    CONSTRAINT ck_membership_import_counts
        CHECK (RowCount >= 0 AND ImportedCount >= 0 AND RejectedCount >= 0
               AND RowCount = ImportedCount + RejectedCount)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;
