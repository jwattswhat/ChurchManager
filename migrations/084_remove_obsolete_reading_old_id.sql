-- Remove the pre-normalization reading identifier that prevents package-owned
-- citation records from being inserted on upgraded databases.

ALTER TABLE tblReading
    DROP COLUMN IF EXISTS OldID;
