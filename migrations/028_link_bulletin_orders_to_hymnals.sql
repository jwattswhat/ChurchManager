ALTER TABLE tblBulletinOrderTemplate
    ADD COLUMN IF NOT EXISTS HymnalID int NULL AFTER ChurchID;

ALTER TABLE tblBulletinOrderTemplate
    ADD KEY IF NOT EXISTS ix_bulletin_order_hymnal (HymnalID);

ALTER TABLE tblBulletinOrderTemplate
    ADD CONSTRAINT fk_bulletin_order_hymnal
    FOREIGN KEY (HymnalID) REFERENCES tblHymnal(ID)
    ON DELETE SET NULL;

UPDATE tblBulletinOrderTemplate t
JOIN tblHymnal h ON UPPER(TRIM(h.Hymnal)) = 'LSB'
SET t.HymnalID = h.ID
WHERE t.Name = 'LCMS Divine Service One';
