-- Preserve the approved distribution boundary in every installed lectionary package.

ALTER TABLE tblLectionaryPackage
    ADD COLUMN IF NOT EXISTS DistributionScope varchar(20) NOT NULL
        DEFAULT 'LOCAL_ONLY' AFTER PackageNotice;

ALTER TABLE tblLectionaryPackage
    ADD CONSTRAINT IF NOT EXISTS chk_lectionary_package_distribution_scope
        CHECK (DistributionScope IN ('REDISTRIBUTABLE','LOCAL_ONLY'));
