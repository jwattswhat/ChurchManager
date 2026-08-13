ALTER TABLE tblChurch
    ADD COLUMN IF NOT EXISTS PrimaryLectionarySystemID int NULL AFTER PrimaryHymnalID;

ALTER TABLE tblChurch
    ADD KEY IF NOT EXISTS ix_church_primary_lectionary (PrimaryLectionarySystemID);

ALTER TABLE tblChurch
    ADD CONSTRAINT fk_church_primary_lectionary
    FOREIGN KEY (PrimaryLectionarySystemID) REFERENCES tblLectionarySystem(ID)
    ON DELETE SET NULL;
