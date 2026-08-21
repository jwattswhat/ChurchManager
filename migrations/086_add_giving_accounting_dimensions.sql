-- Complete the accounting destination required to hand giving batches to the ledger.

ALTER TABLE tblContributionPurpose
    ADD COLUMN IF NOT EXISTS FunctionID int NULL AFTER RevenueAccountID;

ALTER TABLE tblContributionPurpose
    ADD CONSTRAINT fk_contribution_purpose_function
        FOREIGN KEY (FunctionID) REFERENCES tblAccountingFunction(ID);

ALTER TABLE tblContributionAllocation
    ADD COLUMN IF NOT EXISTS FunctionID int NULL AFTER RevenueAccountID;

ALTER TABLE tblContributionAllocation
    ADD CONSTRAINT fk_contribution_allocation_function
        FOREIGN KEY (FunctionID) REFERENCES tblAccountingFunction(ID);

UPDATE tblContributionAllocation allocation
JOIN tblContributionPurpose purpose ON purpose.ID=allocation.PurposeID
SET allocation.FunctionID=purpose.FunctionID
WHERE allocation.FunctionID IS NULL;
