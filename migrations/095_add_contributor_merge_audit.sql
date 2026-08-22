-- Preserve duplicate-contributor merge provenance without deleting the
-- confidential contributor identity that originally owned historical records.

ALTER TABLE tblContributionContributor
    ADD COLUMN IF NOT EXISTS MergedIntoContributorID bigint NULL AFTER Note,
    ADD COLUMN IF NOT EXISTS MergedAt datetime(6) NULL AFTER MergedIntoContributorID,
    ADD COLUMN IF NOT EXISTS MergedByUserID int NULL AFTER MergedAt,
    ADD COLUMN IF NOT EXISTS MergeReason varchar(1000) NULL AFTER MergedByUserID;

ALTER TABLE tblContributionContributor
    ADD CONSTRAINT fk_contribution_contributor_merged_into
        FOREIGN KEY (MergedIntoContributorID) REFERENCES tblContributionContributor(ID),
    ADD CONSTRAINT fk_contribution_contributor_merged_by
        FOREIGN KEY (MergedByUserID) REFERENCES tblUser(ID);
