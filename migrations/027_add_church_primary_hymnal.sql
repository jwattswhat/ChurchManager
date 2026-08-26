ALTER TABLE tblChurch
    ADD COLUMN IF NOT EXISTS PrimaryHymnalID int NULL AFTER Logo;

ALTER TABLE tblChurch
    ADD KEY IF NOT EXISTS ix_church_primary_hymnal (PrimaryHymnalID);

ALTER TABLE tblChurch
    ADD CONSTRAINT fk_church_primary_hymnal
    FOREIGN KEY (PrimaryHymnalID) REFERENCES tblHymnal(ID)
    ON DELETE SET NULL;
