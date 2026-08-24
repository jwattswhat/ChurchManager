-- Church-scoped typed custom fields and controlled tags for Person and Family.

CREATE TABLE IF NOT EXISTS tblCustomFieldDefinition (
    ID int NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    EntityType varchar(10) NOT NULL,
    FieldKey varchar(64) NOT NULL,
    Label varchar(100) NOT NULL,
    HelpText varchar(500) NULL,
    SectionLabel varchar(100) NOT NULL DEFAULT 'Additional Information',
    DataType varchar(20) NOT NULL,
    LifecycleStatus varchar(10) NOT NULL DEFAULT 'DRAFT',
    PrivacyClass varchar(12) NOT NULL DEFAULT 'STANDARD',
    DisplayOrder int NOT NULL DEFAULT 0,
    Required tinyint(1) NOT NULL DEFAULT 0,
    Searchable tinyint(1) NOT NULL DEFAULT 0,
    ReportAllowed tinyint(1) NOT NULL DEFAULT 0,
    ExportAllowed tinyint(1) NOT NULL DEFAULT 0,
    MaxLength int NULL,
    MinimumValue decimal(18,4) NULL,
    MaximumValue decimal(18,4) NULL,
    DecimalPlaces tinyint NOT NULL DEFAULT 2,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_custom_field_key (ChurchID,EntityType,FieldKey),
    KEY ix_custom_field_display (ChurchID,EntityType,LifecycleStatus,SectionLabel,DisplayOrder),
    CONSTRAINT ck_custom_field_entity CHECK (EntityType IN ('PERSON','FAMILY')),
    CONSTRAINT ck_custom_field_type CHECK (DataType IN ('SHORT_TEXT','LONG_TEXT','INTEGER','DECIMAL','DATE','BOOLEAN','SINGLE_CHOICE','MULTIPLE_CHOICE')),
    CONSTRAINT ck_custom_field_lifecycle CHECK (LifecycleStatus IN ('DRAFT','ACTIVE','RETIRED')),
    CONSTRAINT ck_custom_field_privacy CHECK (PrivacyClass IN ('STANDARD','RESTRICTED')),
    CONSTRAINT ck_custom_field_order CHECK (DisplayOrder >= 0),
    CONSTRAINT ck_custom_field_places CHECK (DecimalPlaces BETWEEN 0 AND 4),
    CONSTRAINT ck_custom_field_range CHECK (MinimumValue IS NULL OR MaximumValue IS NULL OR MinimumValue <= MaximumValue),
    CONSTRAINT ck_custom_field_text_length CHECK (
        MaxLength IS NULL OR
        (DataType='SHORT_TEXT' AND MaxLength BETWEEN 1 AND 255) OR
        (DataType='LONG_TEXT' AND MaxLength BETWEEN 1 AND 2000)
    ),
    CONSTRAINT ck_custom_field_version CHECK (Version > 0),
    CONSTRAINT fk_custom_field_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_custom_field_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_custom_field_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblCustomFieldOption (
    ID int NOT NULL AUTO_INCREMENT,
    DefinitionID int NOT NULL,
    OptionKey varchar(64) NOT NULL,
    Label varchar(100) NOT NULL,
    DisplayOrder int NOT NULL DEFAULT 0,
    Active tinyint(1) NOT NULL DEFAULT 1,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_custom_field_option_key (DefinitionID,OptionKey),
    KEY ix_custom_field_option_display (DefinitionID,Active,DisplayOrder),
    CONSTRAINT ck_custom_field_option_order CHECK (DisplayOrder >= 0),
    CONSTRAINT fk_custom_field_option_definition FOREIGN KEY (DefinitionID) REFERENCES tblCustomFieldDefinition(ID),
    CONSTRAINT fk_custom_field_option_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_custom_field_option_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblPersonCustomFieldValue (
    ID bigint NOT NULL AUTO_INCREMENT,
    PersonID int NOT NULL,
    DefinitionID int NOT NULL,
    TextValue varchar(2000) NULL,
    IntegerValue bigint NULL,
    DecimalValue decimal(18,4) NULL,
    DateValue date NULL,
    BooleanValue tinyint(1) NULL,
    OptionID int NULL,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_person_custom_value (PersonID,DefinitionID),
    KEY ix_person_custom_definition (DefinitionID),
    CONSTRAINT ck_person_custom_one_value CHECK ((TextValue IS NOT NULL)+(IntegerValue IS NOT NULL)+(DecimalValue IS NOT NULL)+(DateValue IS NOT NULL)+(BooleanValue IS NOT NULL)+(OptionID IS NOT NULL)=1),
    CONSTRAINT ck_person_custom_version CHECK (Version > 0),
    CONSTRAINT fk_person_custom_person FOREIGN KEY (PersonID) REFERENCES tblPerson(ID) ON DELETE CASCADE,
    CONSTRAINT fk_person_custom_definition FOREIGN KEY (DefinitionID) REFERENCES tblCustomFieldDefinition(ID),
    CONSTRAINT fk_person_custom_option FOREIGN KEY (OptionID) REFERENCES tblCustomFieldOption(ID),
    CONSTRAINT fk_person_custom_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_person_custom_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblFamilyCustomFieldValue (
    ID bigint NOT NULL AUTO_INCREMENT,
    FamilyID int NOT NULL,
    DefinitionID int NOT NULL,
    TextValue varchar(2000) NULL,
    IntegerValue bigint NULL,
    DecimalValue decimal(18,4) NULL,
    DateValue date NULL,
    BooleanValue tinyint(1) NULL,
    OptionID int NULL,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_family_custom_value (FamilyID,DefinitionID),
    KEY ix_family_custom_definition (DefinitionID),
    CONSTRAINT ck_family_custom_one_value CHECK ((TextValue IS NOT NULL)+(IntegerValue IS NOT NULL)+(DecimalValue IS NOT NULL)+(DateValue IS NOT NULL)+(BooleanValue IS NOT NULL)+(OptionID IS NOT NULL)=1),
    CONSTRAINT ck_family_custom_version CHECK (Version > 0),
    CONSTRAINT fk_family_custom_family FOREIGN KEY (FamilyID) REFERENCES tblFamily(ID) ON DELETE CASCADE,
    CONSTRAINT fk_family_custom_definition FOREIGN KEY (DefinitionID) REFERENCES tblCustomFieldDefinition(ID),
    CONSTRAINT fk_family_custom_option FOREIGN KEY (OptionID) REFERENCES tblCustomFieldOption(ID),
    CONSTRAINT fk_family_custom_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_family_custom_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblPersonCustomFieldOptionValue (
    PersonID int NOT NULL,
    DefinitionID int NOT NULL,
    OptionID int NOT NULL,
    AssignedByUserID int NOT NULL,
    AssignedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (PersonID,DefinitionID,OptionID),
    CONSTRAINT fk_person_multi_person FOREIGN KEY (PersonID) REFERENCES tblPerson(ID) ON DELETE CASCADE,
    CONSTRAINT fk_person_multi_definition FOREIGN KEY (DefinitionID) REFERENCES tblCustomFieldDefinition(ID),
    CONSTRAINT fk_person_multi_option FOREIGN KEY (OptionID) REFERENCES tblCustomFieldOption(ID),
    CONSTRAINT fk_person_multi_assigner FOREIGN KEY (AssignedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblFamilyCustomFieldOptionValue (
    FamilyID int NOT NULL,
    DefinitionID int NOT NULL,
    OptionID int NOT NULL,
    AssignedByUserID int NOT NULL,
    AssignedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (FamilyID,DefinitionID,OptionID),
    CONSTRAINT fk_family_multi_family FOREIGN KEY (FamilyID) REFERENCES tblFamily(ID) ON DELETE CASCADE,
    CONSTRAINT fk_family_multi_definition FOREIGN KEY (DefinitionID) REFERENCES tblCustomFieldDefinition(ID),
    CONSTRAINT fk_family_multi_option FOREIGN KEY (OptionID) REFERENCES tblCustomFieldOption(ID),
    CONSTRAINT fk_family_multi_assigner FOREIGN KEY (AssignedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblProfileTagDefinition (
    ID int NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    EntityType varchar(10) NOT NULL,
    TagKey varchar(64) NOT NULL,
    Label varchar(100) NOT NULL,
    Description varchar(500) NULL,
    PrivacyClass varchar(12) NOT NULL DEFAULT 'STANDARD',
    DisplayColor varchar(7) NULL,
    DisplayOrder int NOT NULL DEFAULT 0,
    Active tinyint(1) NOT NULL DEFAULT 1,
    ReportAllowed tinyint(1) NOT NULL DEFAULT 0,
    ExportAllowed tinyint(1) NOT NULL DEFAULT 0,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_profile_tag_key (ChurchID,EntityType,TagKey),
    KEY ix_profile_tag_display (ChurchID,EntityType,Active,DisplayOrder),
    CONSTRAINT ck_profile_tag_entity CHECK (EntityType IN ('PERSON','FAMILY')),
    CONSTRAINT ck_profile_tag_privacy CHECK (PrivacyClass IN ('STANDARD','RESTRICTED')),
    CONSTRAINT ck_profile_tag_color CHECK (DisplayColor IS NULL OR DisplayColor REGEXP '^#[0-9A-Fa-f]{6}$'),
    CONSTRAINT ck_profile_tag_order CHECK (DisplayOrder >= 0),
    CONSTRAINT fk_profile_tag_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_profile_tag_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_profile_tag_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblPersonTag (
    PersonID int NOT NULL,
    TagDefinitionID int NOT NULL,
    AssignedByUserID int NOT NULL,
    AssignedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (PersonID,TagDefinitionID),
    CONSTRAINT fk_person_tag_person FOREIGN KEY (PersonID) REFERENCES tblPerson(ID) ON DELETE CASCADE,
    CONSTRAINT fk_person_tag_definition FOREIGN KEY (TagDefinitionID) REFERENCES tblProfileTagDefinition(ID),
    CONSTRAINT fk_person_tag_assigner FOREIGN KEY (AssignedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblFamilyTag (
    FamilyID int NOT NULL,
    TagDefinitionID int NOT NULL,
    AssignedByUserID int NOT NULL,
    AssignedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (FamilyID,TagDefinitionID),
    CONSTRAINT fk_family_tag_family FOREIGN KEY (FamilyID) REFERENCES tblFamily(ID) ON DELETE CASCADE,
    CONSTRAINT fk_family_tag_definition FOREIGN KEY (TagDefinitionID) REFERENCES tblProfileTagDefinition(ID),
    CONSTRAINT fk_family_tag_assigner FOREIGN KEY (AssignedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblProfileCustomAuditEvent (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    UserID int NOT NULL,
    Action varchar(80) NOT NULL,
    EntityType varchar(20) NOT NULL,
    EntityID bigint NULL,
    DefinitionID int NULL,
    Outcome varchar(20) NOT NULL DEFAULT 'SUCCESS',
    SafeSummary varchar(500) NULL,
    OccurredAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    KEY ix_profile_custom_audit_church_time (ChurchID,OccurredAt),
    KEY ix_profile_custom_audit_entity (EntityType,EntityID,OccurredAt),
    CONSTRAINT ck_profile_custom_audit_outcome CHECK (Outcome IN ('SUCCESS','REJECTED','FAILED')),
    CONSTRAINT fk_profile_custom_audit_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_profile_custom_audit_user FOREIGN KEY (UserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_profile_custom_audit_definition FOREIGN KEY (DefinitionID) REFERENCES tblCustomFieldDefinition(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('profiles.custom_fields.define','Define and administer custom Person and Family fields.',1,1),
('profiles.custom_fields.view','View standard custom Person and Family fields.',0,1),
('profiles.custom_fields.edit','Edit standard custom Person and Family fields.',1,1),
('profiles.custom_fields.view_restricted','View restricted custom Person and Family fields.',1,1),
('profiles.custom_fields.edit_restricted','Edit restricted custom Person and Family fields.',1,1),
('profiles.tags.define','Define and administer controlled profile tags.',1,1),
('profiles.tags.view','View authorized controlled profile tags.',0,1),
('profiles.tags.assign','Assign authorized controlled profile tags.',1,1);

INSERT IGNORE INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r JOIN tblPermission p ON p.Name LIKE 'profiles.%'
WHERE r.Name='Master Administrator';
