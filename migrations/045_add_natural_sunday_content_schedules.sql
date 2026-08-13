ALTER TABLE tblPrayer
    ADD COLUMN IF NOT EXISTS ScheduleRule varchar(100) NULL AFTER Continuous;

ALTER TABLE tblAnnouncement
    ADD COLUMN IF NOT EXISTS ScheduleRule varchar(100) NULL AFTER Continuous;

UPDATE tblPrayer
SET ScheduleRule=CASE
    WHEN First=1 AND Second=1 AND Third=1 AND Fourth=1 AND Fifth=1
        THEN 'EVERY_SUNDAY'
    WHEN First=0 AND Second=0 AND Third=0 AND Fourth=0 AND Fifth=0
        THEN 'EVERY_SUNDAY'
    ELSE CONCAT('MONTHLY_SUNDAYS:',CONCAT_WS(',',
        IF(First=1,'1',NULL),IF(Second=1,'2',NULL),IF(Third=1,'3',NULL),
        IF(Fourth=1,'4',NULL),IF(Fifth=1,'5',NULL)))
END
WHERE ScheduleRule IS NULL OR ScheduleRule='';

UPDATE tblAnnouncement
SET ScheduleRule=CASE
    WHEN First=1 AND Second=1 AND Third=1 AND Fourth=1 AND Fifth=1
        THEN 'EVERY_SUNDAY'
    WHEN First=0 AND Second=0 AND Third=0 AND Fourth=0 AND Fifth=0
        THEN 'EVERY_SUNDAY'
    ELSE CONCAT('MONTHLY_SUNDAYS:',CONCAT_WS(',',
        IF(First=1,'1',NULL),IF(Second=1,'2',NULL),IF(Third=1,'3',NULL),
        IF(Fourth=1,'4',NULL),IF(Fifth=1,'5',NULL)))
END
WHERE ScheduleRule IS NULL OR ScheduleRule='';

ALTER TABLE tblPrayer
    MODIFY COLUMN ScheduleRule varchar(100) NOT NULL DEFAULT 'EVERY_SUNDAY';

ALTER TABLE tblAnnouncement
    MODIFY COLUMN ScheduleRule varchar(100) NOT NULL DEFAULT 'EVERY_SUNDAY';

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_sunday_prayer AS
SELECT ID,ChurchID,PrayerCategory,RequestFor,RequestBy,Continuous,ScheduleRule,
       StartDate,EndDate,Note
FROM tblPrayer;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_sunday_announcement AS
SELECT ID,ChurchID,Label,Announcement,RequestBy,Continuous,ScheduleRule,
       StartDate,EndDate,eDisplayOnly,Note
FROM tblAnnouncement;
