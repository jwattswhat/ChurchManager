CREATE TABLE IF NOT EXISTS tblServiceBulletinOrderLine (
    ID int NOT NULL AUTO_INCREMENT,
    ServiceID int NOT NULL,
    TemplateLineID int NULL,
    Sequence int NOT NULL,
    Included tinyint(1) NOT NULL DEFAULT 1,
    LineType varchar(40) NOT NULL DEFAULT 'TEXT',
    Label varchar(500) NOT NULL DEFAULT '',
    ValueSource varchar(40) NULL,
    ValueKey varchar(100) NULL,
    WeeklyValue varchar(500) NULL,
    ReferenceText varchar(255) NULL,
    StyleName varchar(60) NOT NULL DEFAULT 'Normal',
    LabelBold tinyint(1) NOT NULL DEFAULT 0,
    ValueBold tinyint(1) NOT NULL DEFAULT 0,
    Italic tinyint(1) NOT NULL DEFAULT 0,
    IndentLevel tinyint unsigned NOT NULL DEFAULT 0,
    TabPosition decimal(6,2) NULL,
    TabAlignment varchar(20) NOT NULL DEFAULT 'LEFT',
    TabLeader varchar(20) NOT NULL DEFAULT 'NONE',
    Note text NULL,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_service_bulletin_line_sequence (ServiceID,Sequence),
    KEY ix_service_bulletin_template_line (TemplateLineID),
    CONSTRAINT fk_service_bulletin_line_service FOREIGN KEY (ServiceID)
        REFERENCES tblService(ID) ON DELETE CASCADE,
    CONSTRAINT fk_service_bulletin_line_template_line FOREIGN KEY (TemplateLineID)
        REFERENCES tblBulletinOrderLine(ID) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;
