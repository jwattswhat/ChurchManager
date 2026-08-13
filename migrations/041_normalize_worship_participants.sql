ALTER TABLE tblParticipant
    ADD COLUMN IF NOT EXISTS DisplayName varchar(255) NULL AFTER PersonID,
    ADD COLUMN IF NOT EXISTS Active tinyint(1) NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS ExternalParticipant tinyint(1) NOT NULL DEFAULT 0;

UPDATE tblParticipant
SET DisplayName=COALESCE(NULLIF(DisplayName,''),Name),
    ExternalParticipant=CASE WHEN PersonID IS NULL THEN 1 ELSE ExternalParticipant END;

CREATE TABLE IF NOT EXISTS tblWorshipRole (
    ID int NOT NULL AUTO_INCREMENT,
    LegacyRoleID int NULL,
    Name varchar(100) NOT NULL,
    Description varchar(500) NULL,
    DisplayOrder int NOT NULL DEFAULT 100,
    Active tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_worship_role_name (Name),
    UNIQUE KEY uq_worship_role_legacy (LegacyRoleID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

INSERT INTO tblWorshipRole (LegacyRoleID,Name,Description,DisplayOrder) VALUES
(1,'Liturgist',NULL,10),(2,'Crucifer','Carries the cross',20),
(3,'Preacher',NULL,30),(4,'Thurifer','Carries the thurible',40),
(5,'Candle-Bearer',NULL,50),(6,'Acolyte','Lights candles',60),
(7,'Reader',NULL,70),(8,'Cantor',NULL,80),(9,'Lector','Reads the lessons',90),
(10,'Organist',NULL,100),(11,'Accompanist',NULL,110),(12,'Elder',NULL,120)
ON DUPLICATE KEY UPDATE LegacyRoleID=VALUES(LegacyRoleID),DisplayOrder=VALUES(DisplayOrder);

INSERT INTO tblWorshipRole (Name,DisplayOrder)
SELECT DISTINCT TRIM(sr.Role),500
FROM tblServiceRole sr
WHERE TRIM(COALESCE(sr.Role,''))<>'' AND TRIM(sr.Role) NOT REGEXP '^[0-9]+$'
ON DUPLICATE KEY UPDATE Name=VALUES(Name);

CREATE TABLE IF NOT EXISTS tblParticipantRole (
    ID int NOT NULL AUTO_INCREMENT,
    ParticipantID int NOT NULL,
    WorshipRoleID int NOT NULL,
    Active tinyint(1) NOT NULL DEFAULT 1,
    Note varchar(500) NULL,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_participant_worship_role (ParticipantID,WorshipRoleID),
    CONSTRAINT fk_participantrole_participant FOREIGN KEY (ParticipantID)
        REFERENCES tblParticipant(ID) ON DELETE CASCADE,
    CONSTRAINT fk_participantrole_role FOREIGN KEY (WorshipRoleID)
        REFERENCES tblWorshipRole(ID) ON DELETE CASCADE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

INSERT IGNORE INTO tblParticipantRole (ParticipantID,WorshipRoleID)
SELECT p.ID,r.ID
FROM tblParticipant p
JOIN tblWorshipRole r ON r.LegacyRoleID IS NOT NULL
WHERE FIND_IN_SET(
    CAST(r.LegacyRoleID AS CHAR),
    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(p.Roles,''),'[',''),']',''),';',','),CHAR(13),','),CHAR(10),',')
)>0;

INSERT IGNORE INTO tblParticipantRole (ParticipantID,WorshipRoleID)
SELECT p.ID,r.ID
FROM tblParticipant p
JOIN tblWorshipRole r ON FIND_IN_SET(
    r.Name,
    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(p.Roles,''),'[',''),']',''),';',','),CHAR(13),','),CHAR(10),',')
)>0;

CREATE TABLE IF NOT EXISTS tblWorshipSchedulePattern (
    ID int NOT NULL AUTO_INCREMENT,
    SourceLegacyScheduleID int NULL,
    Description varchar(255) NOT NULL,
    ServiceTime time NULL,
    DaysOfWeek varchar(255) NULL,
    Months varchar(255) NULL,
    Seasons varchar(500) NULL,
    RotationIncrement int NULL,
    Active tinyint(1) NOT NULL DEFAULT 1,
    Note text NULL,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_worship_schedule_description (Description),
    UNIQUE KEY uq_worship_schedule_legacy (SourceLegacyScheduleID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

INSERT INTO tblWorshipSchedulePattern
    (SourceLegacyScheduleID,Description,ServiceTime,DaysOfWeek,Months,Seasons,
     RotationIncrement,Note)
SELECT ID,COALESCE(NULLIF(Description,''),CONCAT('Schedule ',ID)),Time,
       DaysofWeek,Months,Seasons,Increment,Note
FROM tblSchedule
ON DUPLICATE KEY UPDATE Description=VALUES(Description),ServiceTime=VALUES(ServiceTime),
    DaysOfWeek=VALUES(DaysOfWeek),Months=VALUES(Months),Seasons=VALUES(Seasons),
    RotationIncrement=VALUES(RotationIncrement),Note=VALUES(Note);

CREATE TABLE IF NOT EXISTS tblParticipantAvailability (
    ID int NOT NULL AUTO_INCREMENT,
    ParticipantID int NOT NULL,
    WorshipRoleID int NOT NULL,
    SchedulePatternID int NOT NULL,
    Active tinyint(1) NOT NULL DEFAULT 1,
    Note varchar(500) NULL,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_participant_role_schedule (ParticipantID,WorshipRoleID,SchedulePatternID),
    CONSTRAINT fk_participantavailability_participant FOREIGN KEY (ParticipantID)
        REFERENCES tblParticipant(ID) ON DELETE CASCADE,
    CONSTRAINT fk_participantavailability_role FOREIGN KEY (WorshipRoleID)
        REFERENCES tblWorshipRole(ID) ON DELETE CASCADE,
    CONSTRAINT fk_participantavailability_schedule FOREIGN KEY (SchedulePatternID)
        REFERENCES tblWorshipSchedulePattern(ID) ON DELETE CASCADE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

INSERT IGNORE INTO tblParticipantAvailability
    (ParticipantID,WorshipRoleID,SchedulePatternID)
SELECT pr.ParticipantID,pr.WorshipRoleID,sp.ID
FROM tblParticipantRole pr
JOIN tblParticipant p ON p.ID=pr.ParticipantID
JOIN tblWorshipSchedulePattern sp ON sp.SourceLegacyScheduleID IS NOT NULL
WHERE FIND_IN_SET(
    CAST(sp.SourceLegacyScheduleID AS CHAR),
    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(p.Schedule,''),'[',''),']',''),';',','),CHAR(13),','),CHAR(10),',')
)>0;

CREATE TABLE IF NOT EXISTS tblWorshipRoleRequirement (
    ID int NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    BulletinOrderTemplateID int NULL,
    WorshipRoleID int NOT NULL,
    RequiredCount smallint unsigned NOT NULL DEFAULT 1,
    Active tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_worship_requirement (ChurchID,BulletinOrderTemplateID,WorshipRoleID),
    CONSTRAINT fk_worshiprequirement_church FOREIGN KEY (ChurchID)
        REFERENCES tblChurch(ID) ON DELETE CASCADE,
    CONSTRAINT fk_worshiprequirement_template FOREIGN KEY (BulletinOrderTemplateID)
        REFERENCES tblBulletinOrderTemplate(ID) ON DELETE CASCADE,
    CONSTRAINT fk_worshiprequirement_role FOREIGN KEY (WorshipRoleID)
        REFERENCES tblWorshipRole(ID) ON DELETE CASCADE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

ALTER TABLE tblServiceRole
    ADD COLUMN IF NOT EXISTS WorshipRoleID int NULL AFTER ParticipantID,
    ADD COLUMN IF NOT EXISTS AssignmentStatus varchar(30) NOT NULL DEFAULT 'ASSIGNED',
    ADD COLUMN IF NOT EXISTS Note varchar(500) NULL,
    ADD KEY IF NOT EXISTS ix_servicerole_worship_role (WorshipRoleID);

UPDATE tblServiceRole sr
JOIN tblWorshipRole r ON r.Name=sr.Role OR (
    TRIM(sr.Role) REGEXP '^[0-9]+$' AND r.LegacyRoleID=CAST(TRIM(sr.Role) AS UNSIGNED)
)
SET sr.WorshipRoleID=r.ID,sr.Role=r.Name
WHERE sr.WorshipRoleID IS NULL;

ALTER TABLE tblServiceRole
    ADD CONSTRAINT fk_servicerole_worship_role FOREIGN KEY (WorshipRoleID)
        REFERENCES tblWorshipRole(ID) ON DELETE RESTRICT;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_role AS
SELECT ID,Name,Description,DisplayOrder,Active FROM tblWorshipRole;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_participant AS
SELECT p.ID,p.PersonID,
       COALESCE(NULLIF(p.DisplayName,''),NULLIF(p.Name,''),
                TRIM(CONCAT_WS(' ',pe.FirstName,pe.LastName))) AS DisplayName,
       p.Phone,p.eMail,p.Active,p.ExternalParticipant,p.Note
FROM tblParticipant p
LEFT JOIN tblPerson pe ON pe.ID=p.PersonID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_service_assignment AS
SELECT sr.ID,sr.ServiceID,sr.ParticipantID,sr.WorshipRoleID,
       COALESCE(wr.Name,sr.Role) AS Role,
       COALESCE(NULLIF(p.DisplayName,''),p.Name) AS Participant,
       sr.AssignmentStatus,sr.Note
FROM tblServiceRole sr
JOIN tblParticipant p ON p.ID=sr.ParticipantID
LEFT JOIN tblWorshipRole wr ON wr.ID=sr.WorshipRoleID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_participant AS
SELECT sr.ID,sr.ServiceID,COALESCE(wr.Name,sr.Role) AS Role,
       COALESCE(NULLIF(p.DisplayName,''),p.Name) AS Name
FROM tblServiceRole sr
JOIN tblParticipant p ON p.ID=sr.ParticipantID
LEFT JOIN tblWorshipRole wr ON wr.ID=sr.WorshipRoleID
WHERE sr.AssignmentStatus<>'DECLINED';
