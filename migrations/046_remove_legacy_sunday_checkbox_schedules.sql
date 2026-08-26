ALTER TABLE tblPrayer
    DROP COLUMN Continuous,
    DROP COLUMN First,
    DROP COLUMN Second,
    DROP COLUMN Third,
    DROP COLUMN Fourth,
    DROP COLUMN Fifth;

ALTER TABLE tblAnnouncement
    DROP COLUMN Continuous,
    DROP COLUMN First,
    DROP COLUMN Second,
    DROP COLUMN Third,
    DROP COLUMN Fourth,
    DROP COLUMN Fifth;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_sunday_prayer AS
SELECT ID,ChurchID,PrayerCategory,RequestFor,RequestBy,ScheduleRule,
       StartDate,EndDate,Note
FROM tblPrayer;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_sunday_announcement AS
SELECT ID,ChurchID,Label,Announcement,RequestBy,ScheduleRule,
       StartDate,EndDate,eDisplayOnly,Note
FROM tblAnnouncement;
