-- Retain safe provenance after a deliberately reviewed person or family merge.

CREATE TABLE tblMembershipMergeHistory (
    ID BIGINT NOT NULL AUTO_INCREMENT,
    ChurchID INT NOT NULL,
    EntityType VARCHAR(20) NOT NULL,
    SurvivorRecordID INT NOT NULL,
    RemovedRecordID INT NOT NULL,
    SurvivorName VARCHAR(255) NOT NULL,
    RemovedName VARCHAR(255) NOT NULL,
    MatchReason VARCHAR(100) NOT NULL,
    MergeReason VARCHAR(500) NOT NULL,
    RelationshipsMoved INT NOT NULL DEFAULT 0,
    MergedByUserID INT NOT NULL,
    MergedAt DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_membership_merge_removed (EntityType, RemovedRecordID),
    KEY ix_membership_merge_church (ChurchID, EntityType, MergedAt),
    CONSTRAINT fk_membership_merge_church
        FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_membership_merge_user
        FOREIGN KEY (MergedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT ck_membership_merge_entity
        CHECK (EntityType IN ('Person','Family')),
    CONSTRAINT ck_membership_merge_distinct
        CHECK (SurvivorRecordID > 0 AND RemovedRecordID > 0
               AND SurvivorRecordID <> RemovedRecordID),
    CONSTRAINT ck_membership_merge_relationships
        CHECK (RelationshipsMoved >= 0)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
