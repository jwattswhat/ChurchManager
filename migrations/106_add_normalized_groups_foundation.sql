-- Normalize congregational Groups, membership terms, and dated role assignments.

SET @group_migration_user = (SELECT MIN(ID) FROM tblUser);

RENAME TABLE tblGroup TO tblGroupPre106, tblGroupMember TO tblGroupMemberPre106;

CREATE TABLE tblGroupType (
    ID int NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    GroupTypeKey varchar(80) NOT NULL,
    Label varchar(100) NOT NULL,
    Description varchar(255) NULL,
    DisplayOrder int NOT NULL DEFAULT 0,
    DefaultPrivacyClass varchar(12) NOT NULL DEFAULT 'STANDARD',
    Active tinyint(1) NOT NULL DEFAULT 1,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_group_type_key (ChurchID, GroupTypeKey),
    UNIQUE KEY uq_group_type_label (ChurchID, Label),
    CONSTRAINT ck_group_type_privacy CHECK (DefaultPrivacyClass IN ('STANDARD','RESTRICTED')),
    CONSTRAINT fk_group_type_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_group_type_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_group_type_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tblGroupRole (
    ID int NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    GroupRoleKey varchar(80) NOT NULL,
    Label varchar(100) NOT NULL,
    Description varchar(255) NULL,
    LeadershipRole tinyint(1) NOT NULL DEFAULT 0,
    WarningLimit int NULL,
    DisplayOrder int NOT NULL DEFAULT 0,
    Active tinyint(1) NOT NULL DEFAULT 1,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_group_role_key (ChurchID, GroupRoleKey),
    UNIQUE KEY uq_group_role_label (ChurchID, Label),
    CONSTRAINT ck_group_role_warning_limit CHECK (WarningLimit IS NULL OR WarningLimit > 0),
    CONSTRAINT fk_group_role_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_group_role_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_group_role_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tblGroup (
    ID int NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    GroupKey varchar(100) NOT NULL,
    Name varchar(150) NOT NULL,
    GroupTypeID int NOT NULL,
    Description varchar(500) NULL,
    Status varchar(12) NOT NULL DEFAULT 'DRAFT',
    StartDate date NULL,
    EndDate date NULL,
    ExpectedClosureDate date NULL,
    UsualMeetingDescription varchar(255) NULL,
    DefaultLocation varchar(150) NULL,
    CommunicationEnabled tinyint(1) NOT NULL DEFAULT 0,
    PrivacyClass varchar(12) NOT NULL DEFAULT 'STANDARD',
    Notes varchar(1000) NULL,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_group_key (ChurchID, GroupKey),
    UNIQUE KEY uq_group_current_name (ChurchID, Name, Status),
    KEY ix_group_scope (ChurchID, Status, GroupTypeID, Name),
    CONSTRAINT ck_group_status CHECK (Status IN ('DRAFT','ACTIVE','INACTIVE','CLOSED')),
    CONSTRAINT ck_group_privacy CHECK (PrivacyClass IN ('STANDARD','RESTRICTED')),
    CONSTRAINT ck_group_dates CHECK (EndDate IS NULL OR StartDate IS NULL OR EndDate >= StartDate),
    CONSTRAINT ck_group_closed_date CHECK (Status <> 'CLOSED' OR EndDate IS NOT NULL),
    CONSTRAINT ck_group_version CHECK (Version > 0),
    CONSTRAINT fk_group_church_v2 FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_group_type FOREIGN KEY (GroupTypeID) REFERENCES tblGroupType(ID),
    CONSTRAINT fk_group_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_group_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tblGroupMembership (
    ID int NOT NULL AUTO_INCREMENT,
    GroupID int NOT NULL,
    PersonID int NOT NULL,
    StartDate date NOT NULL,
    EndDate date NULL,
    StatusReason varchar(100) NULL,
    Notes varchar(500) NULL,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    KEY ix_group_membership_current (GroupID, EndDate, StartDate, PersonID),
    KEY ix_group_membership_person (PersonID, EndDate, StartDate, GroupID),
    CONSTRAINT ck_group_membership_dates CHECK (EndDate IS NULL OR EndDate >= StartDate),
    CONSTRAINT ck_group_membership_version CHECK (Version > 0),
    CONSTRAINT fk_group_membership_group FOREIGN KEY (GroupID) REFERENCES tblGroup(ID),
    CONSTRAINT fk_group_membership_person FOREIGN KEY (PersonID) REFERENCES tblPerson(ID),
    CONSTRAINT fk_group_membership_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_group_membership_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tblGroupMembershipRole (
    ID bigint NOT NULL AUTO_INCREMENT,
    GroupMembershipID int NOT NULL,
    GroupRoleID int NOT NULL,
    StartDate date NOT NULL,
    EndDate date NULL,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    KEY ix_group_membership_role_current (GroupMembershipID, EndDate, StartDate),
    KEY ix_group_role_current (GroupRoleID, EndDate, StartDate),
    CONSTRAINT ck_group_membership_role_dates CHECK (EndDate IS NULL OR EndDate >= StartDate),
    CONSTRAINT ck_group_membership_role_version CHECK (Version > 0),
    CONSTRAINT fk_group_membership_role_membership FOREIGN KEY (GroupMembershipID) REFERENCES tblGroupMembership(ID),
    CONSTRAINT fk_group_membership_role_role FOREIGN KEY (GroupRoleID) REFERENCES tblGroupRole(ID),
    CONSTRAINT fk_group_membership_role_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_group_membership_role_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO tblGroupType
    (ChurchID,GroupTypeKey,Label,Description,DisplayOrder,DefaultPrivacyClass,Active,CreatedByUserID,UpdatedByUserID)
SELECT c.ID,s.GroupTypeKey,s.Label,s.Description,s.DisplayOrder,'STANDARD',1,@group_migration_user,@group_migration_user
FROM tblChurch c JOIN (
    SELECT 'governance-body' GroupTypeKey,'Governance Body' Label,'Council, board, or other governance body.' Description,10 DisplayOrder UNION ALL
    SELECT 'committee','Committee','Standing or temporary committee.',20 UNION ALL
    SELECT 'bible-study','Bible Study','Bible study or other study group.',30 UNION ALL
    SELECT 'class','Class','Sunday school, confirmation, or other class.',40 UNION ALL
    SELECT 'music-group','Music Group','Choir, handbells, or other music group.',50 UNION ALL
    SELECT 'service-team','Service Team','Service, outreach, or support team.',60 UNION ALL
    SELECT 'fellowship-group','Fellowship Group','Fellowship or community group.',70 UNION ALL
    SELECT 'temporary-team','Temporary Team','Short-term ministry or project team.',80
) s;

INSERT IGNORE INTO tblGroupType
    (ChurchID,GroupTypeKey,Label,Description,DisplayOrder,DefaultPrivacyClass,Active,CreatedByUserID,UpdatedByUserID)
SELECT DISTINCT g.ChurchID,CONCAT('imported-',LOWER(LPAD(HEX(CRC32(TRIM(g.GroupType))),8,'0'))),
       TRIM(g.GroupType),'Imported from the previous Group category.',900,'STANDARD',1,@group_migration_user,@group_migration_user
FROM tblGroupPre106 g WHERE TRIM(COALESCE(g.GroupType,''))<>'';

INSERT INTO tblGroupRole
    (ChurchID,GroupRoleKey,Label,Description,LeadershipRole,WarningLimit,DisplayOrder,Active,CreatedByUserID,UpdatedByUserID)
SELECT c.ID,s.GroupRoleKey,s.Label,s.Description,s.LeadershipRole,s.WarningLimit,s.DisplayOrder,1,@group_migration_user,@group_migration_user
FROM tblChurch c JOIN (
    SELECT 'member' GroupRoleKey,'Member' Label,'Ordinary Group member.' Description,0 LeadershipRole,NULL WarningLimit,10 DisplayOrder UNION ALL
    SELECT 'chair','Chair','Group chair.',1,1,20 UNION ALL
    SELECT 'leader','Leader','Group leader.',1,NULL,30 UNION ALL
    SELECT 'secretary','Secretary','Group secretary.',1,1,40 UNION ALL
    SELECT 'teacher','Teacher','Class or study teacher.',1,NULL,50 UNION ALL
    SELECT 'treasurer','Treasurer','Group treasurer.',1,1,60 UNION ALL
    SELECT 'elder','Elder','Elder serving in the Group.',1,NULL,70
) s;

INSERT IGNORE INTO tblGroupRole
    (ChurchID,GroupRoleKey,Label,Description,LeadershipRole,WarningLimit,DisplayOrder,Active,CreatedByUserID,UpdatedByUserID)
SELECT DISTINCT g.ChurchID,CONCAT('imported-',LOWER(LPAD(HEX(CRC32(TRIM(m.GroupRole))),8,'0'))),
       TRIM(m.GroupRole),'Imported from the previous Group role.',0,NULL,900,1,@group_migration_user,@group_migration_user
FROM tblGroupMemberPre106 m JOIN tblGroupPre106 g ON g.ID=m.GroupID
WHERE TRIM(COALESCE(m.GroupRole,''))<>'';

INSERT INTO tblGroup
    (ID,ChurchID,GroupKey,Name,GroupTypeID,Status,StartDate,PrivacyClass,Notes,CreatedByUserID,UpdatedByUserID)
SELECT g.ID,g.ChurchID,
       CONCAT('group-',COALESCE(CAST(g.Number AS CHAR),CAST(g.ID AS CHAR))),
       TRIM(g.Description),t.ID,'ACTIVE',g.DateStarted,t.DefaultPrivacyClass,
       NULLIF(TRIM(g.Notes),''),@group_migration_user,@group_migration_user
FROM tblGroupPre106 g JOIN tblGroupType t
  ON t.ChurchID=g.ChurchID
 AND t.Label=CONVERT(TRIM(g.GroupType) USING utf8mb4) COLLATE utf8mb4_unicode_ci;

INSERT INTO tblGroupMembership
    (ID,GroupID,PersonID,StartDate,EndDate,Notes,CreatedByUserID,UpdatedByUserID)
SELECT m.ID,m.GroupID,m.PersonID,m.StartDate,m.EndDate,NULLIF(TRIM(m.Notes),''),
       @group_migration_user,@group_migration_user
FROM tblGroupMemberPre106 m;

INSERT INTO tblGroupMembershipRole
    (GroupMembershipID,GroupRoleID,StartDate,EndDate,CreatedByUserID,UpdatedByUserID)
SELECT m.ID,r.ID,m.StartDate,m.EndDate,@group_migration_user,@group_migration_user
FROM tblGroupMemberPre106 m
JOIN tblGroupPre106 g ON g.ID=m.GroupID
JOIN tblGroupRole r ON r.ChurchID=g.ChurchID
 AND r.Label=CONVERT(TRIM(m.GroupRole) USING utf8mb4) COLLATE utf8mb4_unicode_ci
WHERE LOWER(TRIM(m.GroupRole))<>'member';

DROP TABLE tblGroupMemberPre106;
DROP TABLE tblGroupPre106;

INSERT IGNORE INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('groups.view','View standard Groups and membership.',0,1),
('groups.edit','Create and update standard Groups.',0,1),
('groups.define_types','Administer Group types.',0,1),
('groups.view_restricted','View restricted Groups and membership.',1,1),
('groups.edit_restricted','Create and update restricted Groups.',1,1),
('groups.membership.view','View Group membership terms.',0,1),
('groups.membership.edit','Create and update Group membership terms.',0,1),
('groups.roles.define','Administer Group roles.',0,1),
('groups.roles.assign','Assign dated Group roles.',0,1),
('groups.reports.view','Run approved Group reports.',0,1),
('groups.export','Export authorized Group data.',1,1);

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r JOIN tblPermission p ON p.Name LIKE 'groups.%'
WHERE r.Name='Master Administrator';
