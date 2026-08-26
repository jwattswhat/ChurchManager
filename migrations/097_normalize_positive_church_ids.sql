-- Church identifiers are permanent positive keys. Normalize the historical
-- zero-valued test record and every ChurchID reference before enforcing that
-- invariant. Installations already using positive identifiers are unchanged.

DELIMITER $$
CREATE PROCEDURE cm_normalize_positive_church_ids()
BEGIN
    DECLARE finished int DEFAULT 0;
    DECLARE referenced_table varchar(64);
    DECLARE zero_default tinyint DEFAULT 0;
    DECLARE replacement_id int DEFAULT NULL;
    DECLARE prior_foreign_key_checks int DEFAULT @@FOREIGN_KEY_CHECKS;
    DECLARE church_columns CURSOR FOR
        SELECT c.TABLE_NAME, (c.COLUMN_DEFAULT = '0')
        FROM information_schema.COLUMNS c
        JOIN information_schema.TABLES t
          ON t.TABLE_SCHEMA=c.TABLE_SCHEMA AND t.TABLE_NAME=c.TABLE_NAME
        WHERE c.TABLE_SCHEMA=DATABASE()
          AND c.COLUMN_NAME='ChurchID'
          AND c.TABLE_NAME <> 'tblchurch'
          AND t.TABLE_TYPE='BASE TABLE';
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET finished=1;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET FOREIGN_KEY_CHECKS=prior_foreign_key_checks;
        RESIGNAL;
    END;

    IF EXISTS (SELECT 1 FROM tblChurch WHERE ID=0) THEN
        SELECT COALESCE(MAX(ID),0)+1 INTO replacement_id FROM tblChurch;
    END IF;
    SET FOREIGN_KEY_CHECKS=0;

    OPEN church_columns;
    church_loop: LOOP
        FETCH church_columns INTO referenced_table, zero_default;
        IF finished=1 THEN
            LEAVE church_loop;
        END IF;

        IF replacement_id IS NOT NULL THEN
            SET @church_update=CONCAT(
                'UPDATE `', REPLACE(referenced_table,'`','``'),
                '` SET ChurchID=? WHERE ChurchID=0'
            );
            PREPARE church_statement FROM @church_update;
            SET @replacement_church_id=replacement_id;
            EXECUTE church_statement USING @replacement_church_id;
            DEALLOCATE PREPARE church_statement;
        END IF;

        IF zero_default=1 THEN
            SET @church_default=CONCAT(
                'ALTER TABLE `', REPLACE(referenced_table,'`','``'),
                '` ALTER COLUMN ChurchID DROP DEFAULT'
            );
            PREPARE church_statement FROM @church_default;
            EXECUTE church_statement;
            DEALLOCATE PREPARE church_statement;
        END IF;
    END LOOP;
    CLOSE church_columns;

    IF replacement_id IS NOT NULL THEN
        UPDATE tblChurch SET ID=replacement_id WHERE ID=0;
    END IF;
    SET FOREIGN_KEY_CHECKS=prior_foreign_key_checks;
END$$
DELIMITER ;

CALL cm_normalize_positive_church_ids();
DROP PROCEDURE cm_normalize_positive_church_ids;
