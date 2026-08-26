ALTER TABLE tblService
    ADD COLUMN IF NOT EXISTS BulletinOrderTemplateID int NULL AFTER OrderofService;

UPDATE tblService s
JOIN tblBulletinOrderTemplate t ON t.SourceLegacyName=s.OrderofService
SET s.BulletinOrderTemplateID=t.ID
WHERE s.BulletinOrderTemplateID IS NULL;

ALTER TABLE tblService
    ADD KEY IF NOT EXISTS ix_service_bulletin_order_template (BulletinOrderTemplateID);

ALTER TABLE tblService
    ADD CONSTRAINT fk_service_bulletin_order_template_choice
    FOREIGN KEY (BulletinOrderTemplateID) REFERENCES tblBulletinOrderTemplate(ID)
    ON DELETE SET NULL;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_service AS
SELECT ID,ChurchID,DateTime,Location,PropersID,LiturgicalDate,HolyCommunion,
       OrderofService,BulletinOrderTemplateID,OSNote,PsalmorIntroit,SermonID,
       Bulletin,Attendance,CommunionAttendance,CountforAttendance,Note
FROM tblService;
