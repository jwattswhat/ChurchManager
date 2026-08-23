-- Retain deliberate human decisions about advisory duplicate matches.

CREATE TABLE tblDuplicateReviewResolution (
    ID BIGINT NOT NULL AUTO_INCREMENT,
    ChurchID INT NOT NULL,
    EntityType VARCHAR(20) NOT NULL,
    FirstRecordID INT NOT NULL,
    SecondRecordID INT NOT NULL,
    MatchReason VARCHAR(100) NOT NULL,
    Resolution VARCHAR(20) NOT NULL,
    ResolutionNote VARCHAR(500) NULL,
    ResolvedByUserID INT NOT NULL,
    ResolvedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_duplicate_resolution_pair
        (ChurchID, EntityType, FirstRecordID, SecondRecordID, MatchReason),
    KEY ix_duplicate_resolution_church (ChurchID, EntityType, Resolution),
    CONSTRAINT fk_duplicate_resolution_church
        FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_duplicate_resolution_user
        FOREIGN KEY (ResolvedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT ck_duplicate_resolution_entity
        CHECK (EntityType IN ('Person','Family')),
    CONSTRAINT ck_duplicate_resolution_value
        CHECK (Resolution IN ('NOT_DUPLICATE','DEFERRED')),
    CONSTRAINT ck_duplicate_resolution_order
        CHECK (FirstRecordID > 0 AND SecondRecordID > FirstRecordID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;
