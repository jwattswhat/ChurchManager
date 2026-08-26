-- Remove a pre-normalization identifier that prevents package-owned systems
-- from being inserted on databases upgraded from the original application.

ALTER TABLE tblLectionarySystem
    DROP COLUMN IF EXISTS OldID;
