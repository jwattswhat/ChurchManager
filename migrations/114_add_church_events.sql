-- Add the bounded Church event list used by external calendar integration.

CREATE TABLE IF NOT EXISTS tblChurchEvent (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    EventKey varchar(64) NOT NULL,
    Title varchar(150) NOT NULL,
    Description varchar(1000) NULL,
    StartDateTime datetime NOT NULL,
    EndDateTime datetime NULL,
    AllDay tinyint(1) NOT NULL DEFAULT 0,
    TimeZoneName varchar(64) NOT NULL DEFAULT 'America/Chicago',
    Location varchar(150) NULL,
    OwnerType varchar(12) NULL,
    OwnerID int NULL,
    Status varchar(12) NOT NULL DEFAULT 'PLANNED',
    CalendarEligible tinyint(1) NOT NULL DEFAULT 0,
    Version int NOT NULL DEFAULT 1,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_church_event_key (ChurchID,EventKey),
    KEY ix_church_event_agenda (ChurchID,StartDateTime,Status),
    CONSTRAINT ck_church_event_status CHECK (Status IN ('PLANNED','CONFIRMED','CANCELLED','COMPLETED')),
    CONSTRAINT ck_church_event_owner CHECK (OwnerType IS NULL OR OwnerType IN ('PERSON','GROUP','USER')),
    CONSTRAINT ck_church_event_end CHECK (EndDateTime IS NULL OR EndDateTime >= StartDateTime),
    CONSTRAINT ck_church_event_version CHECK (Version > 0),
    CONSTRAINT fk_church_event_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_church_event_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_church_event_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('calendar.view','View safe ChurchManager calendar events.',0,1),
('calendar.events.manage','Create and maintain simple Church events.',1,1),
('calendar.export','Preview and export approved events to iCalendar files.',1,1),
('calendar.configure','Configure protected external calendar integration.',1,1),
('calendar.publish','Publish approved events to an external calendar.',1,1);

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r JOIN tblPermission p ON p.Name LIKE 'calendar.%'
WHERE r.Name='Master Administrator';

