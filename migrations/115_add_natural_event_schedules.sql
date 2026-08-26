-- Give Church Events the same controlled natural-language scheduling model used elsewhere.

ALTER TABLE tblChurchEvent
    ADD COLUMN IF NOT EXISTS ScheduleText varchar(255) NULL AFTER TimeZoneName,
    ADD COLUMN IF NOT EXISTS ScheduleRule varchar(255) NULL AFTER ScheduleText;

UPDATE tblChurchEvent
SET ScheduleText=CONCAT('Once on ',DATE_FORMAT(StartDateTime,'%M %e, %Y')),
    ScheduleRule=CONCAT('RDATE:',DATE_FORMAT(StartDateTime,'%Y%m%d'))
WHERE ScheduleText IS NULL OR ScheduleRule IS NULL;

ALTER TABLE tblChurchEvent
    MODIFY COLUMN ScheduleText varchar(255) NOT NULL,
    MODIFY COLUMN ScheduleRule varchar(255) NOT NULL;
