CREATE VIEW `vwhymnusage` AS
select
    `u`.`ID` AS `ID`,
    `s`.`ID` AS `ServiceID`,
    `s`.`DateTime` AS `DateTime`,
    `h`.`ID` AS `HymnID`,
    h.Hymn as 'Hymn',
    `h`.`Title` AS `Title`,
    `u`.`UsedAs` AS `UsedAs`,
    `h`.`BibleText` AS `BibleText`,
    `h`.`Category` AS `Category`,
    `u`.`Note` AS `Note`
from
    (
        (
            `tblhymnusage` `u`
            join `tblservice` `s` on(`u`.`ServiceID` = `s`.`ID`)
        )
        join `tblhymn` `h` on(`u`.`HymnID` = `h`.`ID`)
    );