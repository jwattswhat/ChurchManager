-- Introit text is intentionally not stored by ChurchManager. Congregations may
-- add the appropriate licensed material directly to their bulletin document.

DROP VIEW IF EXISTS rpt_service;
DROP VIEW IF EXISTS rpt_propers;

ALTER TABLE tblService
    DROP COLUMN IF EXISTS PsalmorIntroit;

ALTER TABLE tblPropers
    DROP COLUMN IF EXISTS Introit;

CREATE SQL SECURITY DEFINER VIEW rpt_service AS
SELECT ID,ChurchID,DateTime,Location,PropersID,LiturgicalDate,HolyCommunion,
       OrderofService,BulletinOrderTemplateID,OSNote,SermonID,Bulletin,
       Attendance,CommunionAttendance,CountforAttendance,Note
FROM tblService;

CREATE SQL SECURITY DEFINER VIEW rpt_propers AS
SELECT ID,LectionarySystemID,Cycle,Sort,Season,LiturgicalDate,Color,AltColor,
       Theme,HymnSug,Note
FROM tblPropers;
