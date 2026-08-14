-- Remove obsolete JSForm-era storage only after run_churchdb_migrations.py has
-- verified that its normalized replacements contain the converted data.

DROP VIEW IF EXISTS rpt_service;
DROP VIEW IF EXISTS rpt_participant;
DROP VIEW IF EXISTS rpt_service_role;
DROP VIEW IF EXISTS rpt_worship_service_assignment;
DROP VIEW IF EXISTS rpt_worship_planner_participant;
DROP VIEW IF EXISTS rpt_alt_reading;

ALTER TABLE tblService
    DROP FOREIGN KEY IF EXISTS fk_service_checklist;

ALTER TABLE tblService
    DROP COLUMN IF EXISTS OrderofService,
    DROP COLUMN IF EXISTS CheckListID,
    DROP COLUMN IF EXISTS CheckList;

ALTER TABLE tblParticipant
    DROP COLUMN IF EXISTS Roles,
    DROP COLUMN IF EXISTS Schedule;

ALTER TABLE tblWorshipRole
    DROP INDEX IF EXISTS uq_worship_role_legacy,
    DROP COLUMN IF EXISTS LegacyRoleID;

ALTER TABLE tblWorshipSchedulePattern
    DROP INDEX IF EXISTS uq_worship_schedule_legacy,
    DROP COLUMN IF EXISTS SourceLegacyScheduleID;

ALTER TABLE tblServiceRole
    DROP INDEX IF EXISTS uq_servicerole_assignment,
    MODIFY COLUMN WorshipRoleID int NOT NULL,
    DROP COLUMN IF EXISTS Role,
    ADD UNIQUE KEY IF NOT EXISTS uq_servicerole_assignment
        (ServiceID,ParticipantID,WorshipRoleID);

ALTER TABLE tblBulletinOrderTemplate
    DROP INDEX IF EXISTS uq_bulletin_order_source,
    DROP COLUMN IF EXISTS SourceLegacyName;

ALTER TABLE tblBulletinOrderLine
    DROP COLUMN IF EXISTS LegacyContent;

DROP TABLE IF EXISTS tblOrderofService;
DROP TABLE IF EXISTS tblSchedule;
DROP TABLE IF EXISTS tblCheckList;
DROP TABLE IF EXISTS tblAltReading;

CREATE SQL SECURITY DEFINER VIEW rpt_service AS
SELECT s.ID,s.ChurchID,s.DateTime,s.Location,s.PropersID,s.LiturgicalDate,
       s.HolyCommunion,
       COALESCE(weekly_template.Name,service_template.Name,'') AS OrderofService,
       s.BulletinOrderTemplateID,s.OSNote,s.SermonID,s.Bulletin,
       s.Attendance,s.CommunionAttendance,s.CountforAttendance,s.Note
FROM tblService s
LEFT JOIN tblServiceBulletinOrder weekly ON weekly.ServiceID=s.ID
LEFT JOIN tblBulletinOrderTemplate weekly_template ON weekly_template.ID=weekly.TemplateID
LEFT JOIN tblBulletinOrderTemplate service_template
       ON service_template.ID=s.BulletinOrderTemplateID;

CREATE SQL SECURITY DEFINER VIEW rpt_participant AS
SELECT ID,PersonID,COALESCE(NULLIF(DisplayName,''),Name) AS Name,
       Phone,eMail,Active,ExternalParticipant,Note
FROM tblParticipant;

CREATE SQL SECURITY DEFINER VIEW rpt_service_role AS
SELECT sr.ID,sr.ServiceID,sr.ParticipantID,sr.WorshipRoleID,
       wr.Name AS Role,sr.AssignmentStatus,sr.Note
FROM tblServiceRole sr
JOIN tblWorshipRole wr ON wr.ID=sr.WorshipRoleID;

CREATE SQL SECURITY DEFINER VIEW rpt_worship_service_assignment AS
SELECT sr.ID,sr.ServiceID,sr.ParticipantID,sr.WorshipRoleID,
       wr.Name AS Role,COALESCE(NULLIF(p.DisplayName,''),p.Name) AS Participant,
       sr.AssignmentStatus,sr.Note
FROM tblServiceRole sr
JOIN tblParticipant p ON p.ID=sr.ParticipantID
JOIN tblWorshipRole wr ON wr.ID=sr.WorshipRoleID;

CREATE SQL SECURITY DEFINER VIEW rpt_worship_planner_participant AS
SELECT sr.ID,sr.ServiceID,sr.WorshipRoleID,wr.Name AS Role,
       COALESCE(NULLIF(p.DisplayName,''),p.Name) AS Name,
       sr.AssignmentStatus AS Status
FROM tblServiceRole sr
JOIN tblParticipant p ON p.ID=sr.ParticipantID
JOIN tblWorshipRole wr ON wr.ID=sr.WorshipRoleID;
