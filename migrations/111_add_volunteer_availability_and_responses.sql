CREATE TABLE IF NOT EXISTS tblParticipantAvailabilityException (
    ID int NOT NULL AUTO_INCREMENT,
    ParticipantID int NOT NULL,
    WorshipRoleID int NULL,
    StartDate date NOT NULL,
    EndDate date NOT NULL,
    Reason varchar(255) NULL,
    Active tinyint(1) NOT NULL DEFAULT 1,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    KEY ix_participant_exception_dates (ParticipantID,Active,StartDate,EndDate),
    KEY ix_participant_exception_role (WorshipRoleID),
    CONSTRAINT fk_participantexception_participant FOREIGN KEY (ParticipantID)
        REFERENCES tblParticipant(ID) ON DELETE CASCADE,
    CONSTRAINT fk_participantexception_role FOREIGN KEY (WorshipRoleID)
        REFERENCES tblWorshipRole(ID) ON DELETE CASCADE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

ALTER TABLE tblServiceRole
    ADD COLUMN IF NOT EXISTS RespondedAt datetime NULL AFTER AssignmentStatus,
    ADD COLUMN IF NOT EXISTS ResponseSource varchar(30) NULL AFTER RespondedAt;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_volunteer_availability AS
SELECT e.ID,e.ParticipantID,
       COALESCE(NULLIF(p.DisplayName,''),p.Name) AS Participant,
       e.WorshipRoleID,COALESCE(wr.Name,'All roles') AS Role,
       e.StartDate,e.EndDate,e.Reason,e.Active,e.CreatedAt,e.UpdatedAt
FROM tblParticipantAvailabilityException e
JOIN tblParticipant p ON p.ID=e.ParticipantID
LEFT JOIN tblWorshipRole wr ON wr.ID=e.WorshipRoleID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_service_assignment AS
SELECT sr.ID,sr.ServiceID,sr.ParticipantID,sr.WorshipRoleID,
       wr.Name AS Role,COALESCE(NULLIF(p.DisplayName,''),p.Name) AS Participant,
       sr.AssignmentStatus,sr.RespondedAt,sr.ResponseSource,sr.Note
FROM tblServiceRole sr
JOIN tblParticipant p ON p.ID=sr.ParticipantID
JOIN tblWorshipRole wr ON wr.ID=sr.WorshipRoleID;
