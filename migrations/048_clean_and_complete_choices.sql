DELETE FROM tblChoices
WHERE Field IN ('AccountType','OrderofService','PsalmorIntroit','Roles','EnteredBy','GroupType');

UPDATE tblHymnUsage SET UsedAs='Hymn of Invocation' WHERE UsedAs='Entrance';
UPDATE tblHymnUsage SET UsedAs='Hymn of the Day' WHERE UsedAs='Of the Day';
UPDATE tblHymnUsage SET UsedAs='Distribution Hymn' WHERE UsedAs='Communion';
UPDATE tblHymnUsage SET UsedAs='Closing Hymn' WHERE UsedAs='Closing';

UPDATE tblProperHymnSuggestion SET SuggestedAs='Closing Hymn' WHERE SuggestedAs='Closing';

UPDATE tblBulletinOrderLine
SET ValueKey=CASE ValueKey
    WHEN 'Entrance' THEN 'Hymn of Invocation'
    WHEN 'Of the Day' THEN 'Hymn of the Day'
    WHEN 'Communion' THEN 'Distribution Hymn'
    WHEN 'Closing' THEN 'Closing Hymn'
    ELSE ValueKey END
WHERE ValueSource='SERVICE_HYMN';

UPDATE tblServiceBulletinOrderLine
SET ValueKey=CASE ValueKey
    WHEN 'Entrance' THEN 'Hymn of Invocation'
    WHEN 'Of the Day' THEN 'Hymn of the Day'
    WHEN 'Communion' THEN 'Distribution Hymn'
    WHEN 'Closing' THEN 'Closing Hymn'
    ELSE ValueKey END
WHERE ValueSource='SERVICE_HYMN';

DELETE FROM tblChoices
WHERE Field IN ('UsedAs','AnnouncementCategory','AddressLabel','Reading','Season','Category');

INSERT INTO tblChoices (Field,Choices,Note) VALUES
('UsedAs',
 '[Hymn of Invocation\nKyrie\nGloria in Excelsis\nHymn of the Day\nCreed\nDistribution Hymn\nSanctus\nAgnus Dei\nNunc Dimittis\nMagnificat\nPost Communion\nClosing Hymn\nHymn\nOffice\nSermon]',
 'Controlled descriptions for hymn usage and worship planning.'),
('AnnouncementCategory',
 '[General\nBuilding\nCommunion\nDonations\nLCMS\nMeetings\nRadio\nWebsite]',
 'Categories used to group weekly announcements.'),
('AddressLabel',
 '[Main\nHome\nMailing\nBusiness\nOther]',
 'Labels used for person and family addresses.'),
('Reading',
 '[Old Testament\nEpistle\nGospel]',
 'Reading roles used by the lectionary and weekly order of service.');

INSERT INTO tblChoices (Field,Choices,Note)
SELECT 'Season',
       COALESCE(CONCAT('[',GROUP_CONCAT(DISTINCT Season ORDER BY Season SEPARATOR '\n'),']'),'[Advent\nChristmas\nEpiphany\nLent\nEaster\nPentecost]'),
       'Liturgical seasons currently present in the Propers table.'
FROM tblPropers
WHERE Season IS NOT NULL AND TRIM(Season) <> '';

INSERT INTO tblChoices (Field,Choices,Note)
SELECT 'Category',
       COALESCE(CONCAT('[',GROUP_CONCAT(DISTINCT Category ORDER BY Category SEPARATOR '\n'),']'),'[General]'),
       'Hymn categories currently present in the Hymn table.'
FROM tblHymn
WHERE Category IS NOT NULL AND TRIM(Category) <> '';
