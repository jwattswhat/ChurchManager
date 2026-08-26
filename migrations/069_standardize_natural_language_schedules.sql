-- Replace ChurchManager's interim schedule codes with RFC 5545 recurrence text.
ALTER TABLE tblPrayer
    ADD COLUMN IF NOT EXISTS ScheduleText varchar(255) NULL AFTER RequestBy,
    MODIFY COLUMN ScheduleRule varchar(255) NOT NULL;

ALTER TABLE tblAnnouncement
    ADD COLUMN IF NOT EXISTS ScheduleText varchar(255) NULL AFTER RequestBy,
    MODIFY COLUMN ScheduleRule varchar(255) NOT NULL;

UPDATE tblPrayer
SET ScheduleText=CASE
        WHEN ScheduleRule='EVERY_SUNDAY' THEN 'Every Sunday'
        WHEN ScheduleRule='ANNUAL_FIRST_SUNDAY' THEN 'First Sunday of each year'
        WHEN ScheduleRule LIKE 'MONTHLY_SUNDAYS:%' THEN CONCAT(
            UCASE(LEFT(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                SUBSTRING_INDEX(ScheduleRule,':',-1),',',' and '),'1','first'),'2','second'),
                '3','third'),'4','fourth'),'5','fifth'),1)),
            SUBSTRING(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                SUBSTRING_INDEX(ScheduleRule,':',-1),',',' and '),'1','first'),'2','second'),
                '3','third'),'4','fourth'),'5','fifth'),2),
            IF(LOCATE(',',ScheduleRule)>0,' Sundays of each month',' Sunday of each month'))
        WHEN ScheduleRule LIKE 'ANNUAL_DATE:%' THEN CONCAT('Every year on ',
            DATE_FORMAT(STR_TO_DATE(CONCAT('2000-',SUBSTRING_INDEX(ScheduleRule,':',-1)),'%Y-%m-%d'),'%M %e'))
        WHEN ScheduleRule LIKE 'ONE_TIME:%' THEN CONCAT('Once on ',
            DATE_FORMAT(STR_TO_DATE(SUBSTRING_INDEX(ScheduleRule,':',-1),'%Y-%m-%d'),'%M %e, %Y'))
        ELSE COALESCE(NULLIF(ScheduleText,''),'Custom recurrence rule')
    END,
    ScheduleRule=CASE
        WHEN ScheduleRule='EVERY_SUNDAY' THEN 'RRULE:FREQ=WEEKLY;BYDAY=SU'
        WHEN ScheduleRule='ANNUAL_FIRST_SUNDAY' THEN 'RRULE:FREQ=YEARLY;BYMONTH=1;BYDAY=1SU'
        WHEN ScheduleRule LIKE 'MONTHLY_SUNDAYS:%' THEN CONCAT(
            'RRULE:FREQ=MONTHLY;BYDAY=',
            REPLACE(SUBSTRING_INDEX(ScheduleRule,':',-1),',','SU,'),'SU')
        WHEN ScheduleRule LIKE 'ANNUAL_DATE:%' THEN CONCAT(
            'RRULE:FREQ=YEARLY;BYMONTH=',
            CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(ScheduleRule,':',-1),'-',1) AS UNSIGNED),
            ';BYMONTHDAY=',
            CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(ScheduleRule,':',-1),'-',-1) AS UNSIGNED))
        WHEN ScheduleRule LIKE 'ONE_TIME:%' THEN CONCAT(
            'RDATE:',REPLACE(SUBSTRING_INDEX(ScheduleRule,':',-1),'-',''))
        ELSE ScheduleRule
    END;

UPDATE tblAnnouncement
SET ScheduleText=CASE
        WHEN ScheduleRule='EVERY_SUNDAY' THEN 'Every Sunday'
        WHEN ScheduleRule='ANNUAL_FIRST_SUNDAY' THEN 'First Sunday of each year'
        WHEN ScheduleRule LIKE 'MONTHLY_SUNDAYS:%' THEN CONCAT(
            UCASE(LEFT(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                SUBSTRING_INDEX(ScheduleRule,':',-1),',',' and '),'1','first'),'2','second'),
                '3','third'),'4','fourth'),'5','fifth'),1)),
            SUBSTRING(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                SUBSTRING_INDEX(ScheduleRule,':',-1),',',' and '),'1','first'),'2','second'),
                '3','third'),'4','fourth'),'5','fifth'),2),
            IF(LOCATE(',',ScheduleRule)>0,' Sundays of each month',' Sunday of each month'))
        WHEN ScheduleRule LIKE 'ANNUAL_DATE:%' THEN CONCAT('Every year on ',
            DATE_FORMAT(STR_TO_DATE(CONCAT('2000-',SUBSTRING_INDEX(ScheduleRule,':',-1)),'%Y-%m-%d'),'%M %e'))
        WHEN ScheduleRule LIKE 'ONE_TIME:%' THEN CONCAT('Once on ',
            DATE_FORMAT(STR_TO_DATE(SUBSTRING_INDEX(ScheduleRule,':',-1),'%Y-%m-%d'),'%M %e, %Y'))
        ELSE COALESCE(NULLIF(ScheduleText,''),'Custom recurrence rule')
    END,
    ScheduleRule=CASE
        WHEN ScheduleRule='EVERY_SUNDAY' THEN 'RRULE:FREQ=WEEKLY;BYDAY=SU'
        WHEN ScheduleRule='ANNUAL_FIRST_SUNDAY' THEN 'RRULE:FREQ=YEARLY;BYMONTH=1;BYDAY=1SU'
        WHEN ScheduleRule LIKE 'MONTHLY_SUNDAYS:%' THEN CONCAT(
            'RRULE:FREQ=MONTHLY;BYDAY=',
            REPLACE(SUBSTRING_INDEX(ScheduleRule,':',-1),',','SU,'),'SU')
        WHEN ScheduleRule LIKE 'ANNUAL_DATE:%' THEN CONCAT(
            'RRULE:FREQ=YEARLY;BYMONTH=',
            CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(ScheduleRule,':',-1),'-',1) AS UNSIGNED),
            ';BYMONTHDAY=',
            CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(ScheduleRule,':',-1),'-',-1) AS UNSIGNED))
        WHEN ScheduleRule LIKE 'ONE_TIME:%' THEN CONCAT(
            'RDATE:',REPLACE(SUBSTRING_INDEX(ScheduleRule,':',-1),'-',''))
        ELSE ScheduleRule
    END;

ALTER TABLE tblPrayer
    MODIFY COLUMN ScheduleText varchar(255) NOT NULL;

ALTER TABLE tblAnnouncement
    MODIFY COLUMN ScheduleText varchar(255) NOT NULL;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_sunday_prayer AS
SELECT ID,ChurchID,PrayerCategory,RequestFor,RequestBy,ScheduleText,ScheduleRule,
       StartDate,EndDate,Note
FROM tblPrayer;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_sunday_announcement AS
SELECT ID,ChurchID,AnnouncementCategory,Announcement,RequestBy,ScheduleText,ScheduleRule,
       StartDate,EndDate,Note
FROM tblAnnouncement;
