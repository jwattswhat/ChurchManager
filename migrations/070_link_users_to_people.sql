-- Optionally associate one ChurchManager login with one congregation person.
ALTER TABLE tblUser
    ADD COLUMN IF NOT EXISTS PersonID int NULL AFTER ID;

DELIMITER $$
CREATE PROCEDURE migrate_user_person_link()
BEGIN
    IF EXISTS (
        SELECT PersonID FROM tblUser
        WHERE PersonID IS NOT NULL
        GROUP BY PersonID HAVING COUNT(*) > 1
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT='Duplicate tblUser.PersonID values must be resolved before migration';
    END IF;

    IF EXISTS (
        SELECT 1 FROM tblUser u
        LEFT JOIN tblPerson p ON p.ID=u.PersonID
        WHERE u.PersonID IS NOT NULL AND p.ID IS NULL
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT='Invalid tblUser.PersonID values must be resolved before migration';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tblUser'
          AND COLUMN_NAME='PersonID' AND NON_UNIQUE=0
    ) THEN
        ALTER TABLE tblUser
            ADD CONSTRAINT uq_user_person UNIQUE (PersonID);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='tblUser'
          AND COLUMN_NAME='PersonID' AND REFERENCED_TABLE_NAME='tblPerson'
          AND REFERENCED_COLUMN_NAME='ID'
    ) THEN
        ALTER TABLE tblUser
            ADD CONSTRAINT fk_user_person FOREIGN KEY (PersonID)
            REFERENCES tblPerson(ID) ON DELETE SET NULL;
    END IF;
END$$
CALL migrate_user_person_link()$$
DROP PROCEDURE migrate_user_person_link$$
DELIMITER ;
