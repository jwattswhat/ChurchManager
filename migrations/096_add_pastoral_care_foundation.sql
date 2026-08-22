-- Protected pastoral-care scheduling and ciphertext-only restricted notes.

CREATE TABLE IF NOT EXISTS tblPastoralCareNeed (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    PersonID int NULL,
    FamilyID int NULL,
    DisplaySubject varchar(255) NULL,
    Category varchar(100) NOT NULL,
    Source varchar(40) NOT NULL DEFAULT 'MANUAL',
    AssignedUserID int NULL,
    Priority varchar(10) NOT NULL DEFAULT 'NORMAL',
    Status varchar(24) NOT NULL DEFAULT 'OPEN',
    OpenedDate date NOT NULL,
    DueDate date NULL,
    NextFollowUpDate date NULL,
    ScheduleText varchar(255) NULL,
    ScheduleRule varchar(255) NULL,
    ScheduleStatus varchar(10) NULL,
    CompletedDate date NULL,
    ClosedDate date NULL,
    SafeSummary varchar(500) NULL,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    KEY ix_pastoral_need_queue (ChurchID, Status, AssignedUserID, NextFollowUpDate, DueDate),
    KEY ix_pastoral_need_person (ChurchID, PersonID, Status),
    KEY ix_pastoral_need_family (ChurchID, FamilyID, Status),
    CONSTRAINT ck_pastoral_need_source CHECK (Source IN ('MANUAL','ATTENDANCE_FOLLOWUP','PRAYER_REQUEST','HOSPITAL_NOTICE','LIFE_EVENT','OTHER')),
    CONSTRAINT ck_pastoral_need_priority CHECK (Priority IN ('NORMAL','URGENT')),
    CONSTRAINT ck_pastoral_need_status CHECK (Status IN ('OPEN','WAITING','COMPLETED','CLOSED_NOT_NEEDED')),
    CONSTRAINT ck_pastoral_need_schedule_status CHECK (ScheduleStatus IS NULL OR ScheduleStatus IN ('ACTIVE','PAUSED','ENDED')),
    CONSTRAINT ck_pastoral_need_version CHECK (Version > 0),
    CONSTRAINT fk_pastoral_need_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_pastoral_need_person FOREIGN KEY (PersonID) REFERENCES tblPerson(ID) ON DELETE SET NULL,
    CONSTRAINT fk_pastoral_need_family FOREIGN KEY (FamilyID) REFERENCES tblFamily(ID) ON DELETE SET NULL,
    CONSTRAINT fk_pastoral_need_assignee FOREIGN KEY (AssignedUserID) REFERENCES tblUser(ID) ON DELETE SET NULL,
    CONSTRAINT fk_pastoral_need_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_pastoral_need_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblPastoralCareAction (
    ID bigint NOT NULL AUTO_INCREMENT,
    CareNeedID bigint NOT NULL,
    ActionDateTime datetime(6) NOT NULL,
    CaregiverUserID int NOT NULL,
    ActionType varchar(20) NOT NULL,
    Result varchar(20) NOT NULL,
    SafeOutcome varchar(500) NULL,
    NextFollowUpDate date NULL,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    KEY ix_pastoral_action_need_time (CareNeedID, ActionDateTime),
    KEY ix_pastoral_action_caregiver (CaregiverUserID, ActionDateTime),
    CONSTRAINT ck_pastoral_action_type CHECK (ActionType IN ('CALL','VISIT','CARD','MEAL','EMAIL','PRAYER','REFERRAL','OTHER')),
    CONSTRAINT ck_pastoral_action_result CHECK (Result IN ('COMPLETED','ATTEMPTED','DEFERRED','NOT_NEEDED')),
    CONSTRAINT ck_pastoral_action_version CHECK (Version > 0),
    CONSTRAINT fk_pastoral_action_need FOREIGN KEY (CareNeedID) REFERENCES tblPastoralCareNeed(ID),
    CONSTRAINT fk_pastoral_action_caregiver FOREIGN KEY (CaregiverUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_pastoral_action_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_pastoral_action_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblPastoralRestrictedNote (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    CareNeedID bigint NOT NULL,
    CareActionID bigint NULL,
    Ciphertext longblob NOT NULL,
    Nonce varbinary(32) NOT NULL,
    AuthenticationTag varbinary(32) NOT NULL,
    Algorithm varchar(40) NOT NULL,
    KeyVersion int NOT NULL,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    KEY ix_pastoral_note_need (CareNeedID, CreatedAt),
    CONSTRAINT ck_pastoral_note_algorithm CHECK (Algorithm='AES-256-GCM'),
    CONSTRAINT ck_pastoral_note_key_version CHECK (KeyVersion > 0),
    CONSTRAINT ck_pastoral_note_version CHECK (Version > 0),
    CONSTRAINT fk_pastoral_note_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_pastoral_note_need FOREIGN KEY (CareNeedID) REFERENCES tblPastoralCareNeed(ID),
    CONSTRAINT fk_pastoral_note_action FOREIGN KEY (CareActionID) REFERENCES tblPastoralCareAction(ID),
    CONSTRAINT fk_pastoral_note_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_pastoral_note_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO tblPermission (Name, Description, IsSensitive, Active) VALUES
('pastoral.care.view.assigned','View pastoral care assigned to the current user.',1,1),
('pastoral.care.view.all','View all pastoral care operational records.',1,1),
('pastoral.care.create','Create pastoral care needs.',1,1),
('pastoral.care.assign','Assign and reassign pastoral care.',1,1),
('pastoral.care.update','Update pastoral care needs and actions.',1,1),
('pastoral.care.close','Complete or close pastoral care needs.',1,1),
('pastoral.notes.view','Decrypt and view restricted pastoral notes.',1,1),
('pastoral.notes.edit','Create and update encrypted restricted pastoral notes.',1,1),
('pastoral.care.report','Run protected pastoral care reports.',1,1),
('pastoral.care.admin','Administer pastoral care policy and encryption recovery.',1,1);

INSERT IGNORE INTO tblRolePermission (RoleID, PermissionID)
SELECT r.ID,p.ID FROM tblRole r JOIN tblPermission p ON p.Name LIKE 'pastoral.%'
WHERE r.Name='Master Administrator';

DELETE FROM tblChoices WHERE Field IN ('PastoralCareCategory','PastoralCareActionType');
INSERT INTO tblChoices (Field,Choices,Note) VALUES
('PastoralCareCategory','[Hospital\nHomebound\nBereavement\nNew Visitor\nAttendance Concern\nPrayer Follow-up\nFamily Need\nMilestone\nOther]','Broad minimum-necessary pastoral care categories.'),
('PastoralCareActionType','[Call\nVisit\nCard\nMeal\nEmail\nPrayer\nReferral\nOther]','Pastoral care action types.');
