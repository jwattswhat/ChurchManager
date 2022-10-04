CREATE VIEW vwhymnusage AS
select
    `tblHymnUsage`.`ServiceID` AS `ServiceID`,
    `tblHymnUsage`.`HymnID` AS `HymnID`,
    tblHymn.Hymn AS Hymn,
    tblhymn.title as Title,
    tblhymn.bibletext as BibleText,
    tblHymn.category as Category,
    tblHymnUsage.UsedAs as UsedAs,
    `tblHymnUsage`.`Note` AS `Note`
from
    (
        `tblhymnusage`
        left join `tblhymn` on(`tblhymnusage`.`HymnID` = `tblHymn`.`ID`)
    );