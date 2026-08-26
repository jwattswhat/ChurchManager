-- Add explicit, versioned calendar and cycle-resolution metadata.

ALTER TABLE tblLectionaryEdition
    ADD COLUMN IF NOT EXISTS ResolverVersion varchar(20) NOT NULL DEFAULT '1' AFTER SourceNote,
    ADD COLUMN IF NOT EXISTS CycleRule varchar(100) NOT NULL DEFAULT 'none' AFTER ResolverVersion;
