-- Permit zero-dollar purpose classification for donated property.
-- ChurchManager records descriptions only and never assigns property value.

ALTER TABLE tblContributionAllocation
    DROP CONSTRAINT ck_contribution_allocation_amount;

ALTER TABLE tblContributionAllocation
    ADD CONSTRAINT ck_contribution_allocation_amount CHECK (Amount >= 0);
