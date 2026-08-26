ALTER TABLE tblContribution
    ADD COLUMN IF NOT EXISTS DirectionResolvedByUserID int NULL AFTER DirectionResolution,
    ADD COLUMN IF NOT EXISTS DirectionResolvedAt datetime(6) NULL AFTER DirectionResolvedByUserID;

-- A failed first attempt may have added the column as bigint before MariaDB
-- rejected its foreign key to tblUser.ID (int).  Normalize it safely.
ALTER TABLE tblContribution
    MODIFY COLUMN DirectionResolvedByUserID int NULL;

ALTER TABLE tblContribution
    ADD CONSTRAINT fk_contribution_direction_resolved_by
        FOREIGN KEY (DirectionResolvedByUserID) REFERENCES tblUser(ID);
