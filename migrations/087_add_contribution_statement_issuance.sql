-- Identify issued contribution statements without storing duplicate PDF content.

CREATE TABLE IF NOT EXISTS tblContributionStatementIssue (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    ContributorID bigint NOT NULL,
    PeriodStart date NOT NULL,
    PeriodEnd date NOT NULL,
    GeneratedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    GeneratedByUserID int NOT NULL,
    TemplateVersion varchar(50) NOT NULL,
    DocumentHash char(64) NOT NULL,
    OutputFileName varchar(255) NOT NULL,
    RevisionOfID bigint NULL,
    RevisionNumber int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    KEY ix_contribution_statement_contributor (ContributorID, PeriodStart, PeriodEnd, RevisionNumber),
    KEY ix_contribution_statement_church_time (ChurchID, GeneratedAt),
    CONSTRAINT ck_contribution_statement_period CHECK (PeriodEnd >= PeriodStart),
    CONSTRAINT ck_contribution_statement_revision CHECK (RevisionNumber > 0),
    CONSTRAINT fk_contribution_statement_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_contribution_statement_contributor FOREIGN KEY (ContributorID) REFERENCES tblContributionContributor(ID),
    CONSTRAINT fk_contribution_statement_user FOREIGN KEY (GeneratedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_contribution_statement_revision FOREIGN KEY (RevisionOfID) REFERENCES tblContributionStatementIssue(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
