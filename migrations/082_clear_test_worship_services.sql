-- Clear disposable worship-service test data without affecting any real database.

DROP PROCEDURE IF EXISTS cm_clear_test_worship_services;

DELIMITER $$
CREATE PROCEDURE cm_clear_test_worship_services()
BEGIN
    IF LOWER(DATABASE()) = 'churchdbtest' THEN
        DELETE FROM tblAttendanceEvent
        WHERE ServiceID IS NOT NULL;

        DELETE FROM tblService;
    END IF;
END$$
DELIMITER ;

CALL cm_clear_test_worship_services();
DROP PROCEDURE cm_clear_test_worship_services;
