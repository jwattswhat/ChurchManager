-- Retain an optional donor-provided estimate for internal reference only.
-- ChurchManager never verifies, accounts for, or prints this as its valuation.

ALTER TABLE tblContribution
    ADD COLUMN DonorEstimatedValue decimal(14,2) NULL AFTER NonCashDescription,
    ADD CONSTRAINT ck_contribution_donor_estimated_value
        CHECK (DonorEstimatedValue IS NULL OR DonorEstimatedValue > 0);
