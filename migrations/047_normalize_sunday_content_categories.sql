ALTER TABLE tblAnnouncement
    ADD COLUMN IF NOT EXISTS AnnouncementCategory VARCHAR(255) NOT NULL DEFAULT 'General' AFTER ChurchID;

ALTER TABLE tblAnnouncement
    DROP COLUMN IF EXISTS Label,
    DROP COLUMN IF EXISTS eDisplayOnly;

INSERT INTO tblChoices (Field,Choices,Note)
SELECT 'PrayerCategory',
       COALESCE(CONCAT('[',GROUP_CONCAT(DISTINCT PrayerCategory ORDER BY PrayerCategory SEPARATOR '\n'),']'),'[General]'),
       'Categories used to group weekly prayers.'
FROM tblPrayer
WHERE PrayerCategory IS NOT NULL AND TRIM(PrayerCategory) <> ''
HAVING NOT EXISTS (SELECT 1 FROM tblChoices WHERE Field='PrayerCategory');

INSERT INTO tblChoices (Field,Choices,Note)
SELECT 'AnnouncementCategory','[General]','Categories used to group weekly announcements.'
WHERE NOT EXISTS (SELECT 1 FROM tblChoices WHERE Field='AnnouncementCategory');

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_sunday_announcement AS
SELECT ID,ChurchID,AnnouncementCategory,Announcement,RequestBy,ScheduleRule,
       StartDate,EndDate,Note
FROM tblAnnouncement;
