-- Provider-neutral publication bindings. Credentials never belong in MariaDB.

CREATE TABLE IF NOT EXISTS tblCalendarPublication (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    SourceType varchar(24) NOT NULL,
    SourceID bigint NOT NULL,
    StableUID varchar(255) NOT NULL,
    Provider varchar(32) NOT NULL,
    DestinationIdentifier varchar(255) NOT NULL,
    ProviderEventID varchar(255) NULL,
    LastPublishedVersion varchar(255) NULL,
    LastPublishedHash char(64) NULL,
    LastPublishedAt datetime(6) NULL,
    LastResult varchar(20) NOT NULL DEFAULT 'PENDING',
    SafeDiagnosticCode varchar(100) NULL,
    Active tinyint(1) NOT NULL DEFAULT 1,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_calendar_publication_binding (Provider,DestinationIdentifier,StableUID),
    KEY ix_calendar_publication_source (ChurchID,SourceType,SourceID,Active),
    CONSTRAINT ck_calendar_publication_source CHECK (
        SourceType IN ('CHURCH_EVENT','WORSHIP_SERVICE','GROUP_MEETING','PROJECT_MILESTONE')
    ),
    CONSTRAINT ck_calendar_publication_result CHECK (
        LastResult IN ('PENDING','SUCCESS','ERROR','CANCELLED','REMOVED')
    ),
    CONSTRAINT ck_calendar_publication_source_id CHECK (SourceID > 0),
    CONSTRAINT fk_calendar_publication_church FOREIGN KEY (ChurchID)
        REFERENCES tblChurch(ID) ON UPDATE RESTRICT ON DELETE CASCADE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
