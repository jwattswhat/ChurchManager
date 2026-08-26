CREATE TABLE IF NOT EXISTS tblBulletinOrderTemplate (
    ID int NOT NULL AUTO_INCREMENT,
    ChurchID int NULL,
    Name varchar(255) NOT NULL,
    Description text NULL,
    Active tinyint(1) NOT NULL DEFAULT 1,
    IsStarter tinyint(1) NOT NULL DEFAULT 0,
    SourceLegacyName varchar(255) NULL,
    Version int NOT NULL DEFAULT 1,
    CreatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_bulletin_order_source (SourceLegacyName),
    KEY ix_bulletin_order_church_name (ChurchID, Name),
    CONSTRAINT fk_bulletin_order_church FOREIGN KEY (ChurchID)
        REFERENCES tblChurch(ID) ON DELETE CASCADE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

CREATE TABLE IF NOT EXISTS tblBulletinOrderLine (
    ID int NOT NULL AUTO_INCREMENT,
    TemplateID int NOT NULL,
    Sequence int NOT NULL,
    LineType varchar(40) NOT NULL DEFAULT 'TEXT',
    Label varchar(500) NOT NULL DEFAULT '',
    ValueSource varchar(40) NULL,
    ValueKey varchar(100) NULL,
    ReferenceText varchar(255) NULL,
    StyleName varchar(60) NOT NULL DEFAULT 'Normal',
    LabelBold tinyint(1) NOT NULL DEFAULT 0,
    ValueBold tinyint(1) NOT NULL DEFAULT 0,
    Italic tinyint(1) NOT NULL DEFAULT 0,
    IndentLevel tinyint unsigned NOT NULL DEFAULT 0,
    TabPosition decimal(6,2) NULL,
    TabAlignment varchar(20) NOT NULL DEFAULT 'LEFT',
    TabLeader varchar(20) NOT NULL DEFAULT 'NONE',
    ConditionType varchar(40) NOT NULL DEFAULT 'ALWAYS',
    ConditionValue varchar(100) NULL,
    Note text NULL,
    LegacyContent longtext NULL,
    NeedsReview tinyint(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_bulletin_order_line_sequence (TemplateID, Sequence),
    KEY ix_bulletin_order_line_type (LineType),
    CONSTRAINT fk_bulletin_order_line_template FOREIGN KEY (TemplateID)
        REFERENCES tblBulletinOrderTemplate(ID) ON DELETE CASCADE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

CREATE TABLE IF NOT EXISTS tblServiceBulletinOrder (
    ServiceID int NOT NULL,
    TemplateID int NOT NULL,
    GeneratedPlainText longtext NULL,
    GeneratedHtml longtext NULL,
    GeneratedAt datetime NULL,
    PRIMARY KEY (ServiceID),
    KEY ix_service_bulletin_order_template (TemplateID),
    CONSTRAINT fk_service_bulletin_order_service FOREIGN KEY (ServiceID)
        REFERENCES tblService(ID) ON DELETE CASCADE,
    CONSTRAINT fk_service_bulletin_order_template FOREIGN KEY (TemplateID)
        REFERENCES tblBulletinOrderTemplate(ID) ON DELETE RESTRICT
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;
