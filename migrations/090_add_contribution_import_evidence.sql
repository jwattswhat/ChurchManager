-- Record privacy-safe metadata for controlled contribution CSV evidence files.

CREATE TABLE IF NOT EXISTS tblContributionImportEvidence (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    BatchID bigint NOT NULL,
    StoredPath varchar(255) NOT NULL,
    OriginalName varchar(255) NOT NULL,
    FileHash char(64) NOT NULL,
    FileSize bigint NOT NULL,
    MappingJSON longtext NOT NULL,
    RowCount int NOT NULL,
    ImportedTotal decimal(19,2) NOT NULL,
    ImportedByUserID int NOT NULL,
    ImportedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_contribution_import_file (ChurchID,FileHash),
    UNIQUE KEY uq_contribution_import_batch (BatchID),
    CONSTRAINT fk_contribution_import_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_contribution_import_batch FOREIGN KEY (BatchID) REFERENCES tblContributionBatch(ID),
    CONSTRAINT fk_contribution_import_user FOREIGN KEY (ImportedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT ck_contribution_import_rows CHECK (RowCount > 0),
    CONSTRAINT ck_contribution_import_total CHECK (ImportedTotal > 0)
) ENGINE=InnoDB;
