-- Add dated Group meetings and attendance distinct from worship attendance.

CREATE TABLE tblGroupMeeting (
    ID bigint NOT NULL AUTO_INCREMENT,
    GroupID int NOT NULL,
    StartsAt datetime NOT NULL,
    EndsAt datetime NULL,
    Title varchar(150) NOT NULL,
    Location varchar(150) NULL,
    Status varchar(12) NOT NULL DEFAULT 'SCHEDULED',
    AttendanceMode varchar(12) NOT NULL DEFAULT 'ROSTER',
    TotalHeadCount int NULL,
    RescheduledToMeetingID bigint NULL,
    Notes varchar(1000) NULL,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_group_meeting_start (GroupID,StartsAt),
    KEY ix_group_meeting_date (GroupID,StartsAt,Status),
    CONSTRAINT ck_group_meeting_times CHECK (EndsAt IS NULL OR EndsAt >= StartsAt),
    CONSTRAINT ck_group_meeting_status CHECK (Status IN ('SCHEDULED','HELD','CANCELLED','RESCHEDULED')),
    CONSTRAINT ck_group_meeting_mode CHECK (AttendanceMode IN ('ROSTER','HEADCOUNT','BOTH')),
    CONSTRAINT ck_group_meeting_head_count CHECK (TotalHeadCount IS NULL OR TotalHeadCount >= 0),
    CONSTRAINT ck_group_meeting_reschedule CHECK (
        (Status='RESCHEDULED' AND RescheduledToMeetingID IS NOT NULL)
        OR (Status<>'RESCHEDULED' AND RescheduledToMeetingID IS NULL)
    ),
    CONSTRAINT ck_group_meeting_version CHECK (Version > 0),
    CONSTRAINT fk_group_meeting_group FOREIGN KEY (GroupID) REFERENCES tblGroup(ID),
    CONSTRAINT fk_group_meeting_replacement FOREIGN KEY (RescheduledToMeetingID) REFERENCES tblGroupMeeting(ID),
    CONSTRAINT fk_group_meeting_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_group_meeting_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tblGroupMeetingAttendance (
    ID bigint NOT NULL AUTO_INCREMENT,
    GroupMeetingID bigint NOT NULL,
    PersonID int NOT NULL,
    AttendanceStatus varchar(10) NOT NULL DEFAULT 'UNKNOWN',
    ArrivedAt datetime NULL,
    DepartedAt datetime NULL,
    Notes varchar(500) NULL,
    RecordedByUserID int NOT NULL,
    RecordedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedByUserID int NOT NULL,
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_group_meeting_person (GroupMeetingID,PersonID),
    KEY ix_group_attendance_person (PersonID,AttendanceStatus,GroupMeetingID),
    CONSTRAINT ck_group_attendance_status CHECK (AttendanceStatus IN ('PRESENT','ABSENT','EXCUSED','UNKNOWN')),
    CONSTRAINT ck_group_attendance_times CHECK (DepartedAt IS NULL OR ArrivedAt IS NULL OR DepartedAt >= ArrivedAt),
    CONSTRAINT ck_group_attendance_version CHECK (Version > 0),
    CONSTRAINT fk_group_attendance_meeting FOREIGN KEY (GroupMeetingID) REFERENCES tblGroupMeeting(ID),
    CONSTRAINT fk_group_attendance_person FOREIGN KEY (PersonID) REFERENCES tblPerson(ID),
    CONSTRAINT fk_group_attendance_recorder FOREIGN KEY (RecordedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_group_attendance_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('groups.meetings.view','View authorized Group meetings.',0,1),
('groups.meetings.edit','Create, reschedule, cancel, and update Group meetings.',0,1),
('groups.attendance.view','View authorized Group meeting attendance.',0,1),
('groups.attendance.record','Record and update Group meeting attendance.',0,1);

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r JOIN tblPermission p ON p.Name IN (
    'groups.meetings.view','groups.meetings.edit','groups.attendance.view','groups.attendance.record'
) WHERE r.Name='Master Administrator';
