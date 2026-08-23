-- Record privacy-safe membership portable archives without storing their contents.

CREATE TABLE tblMembershipArchiveHistory (
    ID BIGINT NOT NULL AUTO_INCREMENT,
    ChurchID INT NOT NULL,
    CreatedByUserID INT NOT NULL,
    ArchiveFileName VARCHAR(255) NOT NULL,
    ArchiveSHA256 CHAR(64) NOT NULL,
    PersonRowCount INT NOT NULL,
    FamilyRowCount INT NOT NULL,
    IncludedUnlistedContacts TINYINT(1) NOT NULL DEFAULT 0,
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    KEY ix_membership_archive_church_time (ChurchID, CreatedAt),
    CONSTRAINT fk_membership_archive_church
        FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_membership_archive_user
        FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT ck_membership_archive_counts
        CHECK (PersonRowCount >= 0 AND FamilyRowCount >= 0),
    CONSTRAINT ck_membership_archive_unlisted
        CHECK (IncludedUnlistedContacts = 0)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;
