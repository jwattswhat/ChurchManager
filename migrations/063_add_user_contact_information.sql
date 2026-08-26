-- Optional administrative contact information for ChurchManager application users.
ALTER TABLE tblUser
    ADD COLUMN IF NOT EXISTS Email varchar(254) NULL AFTER DisplayName,
    ADD COLUMN IF NOT EXISTS Phone varchar(50) NULL AFTER Email;
