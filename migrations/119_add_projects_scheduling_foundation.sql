-- Normalized bounded congregational projects; this does not restore tblProject/tblTask.
CREATE TABLE tblMinistryProject (
    ID int NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    ProjectNumber varchar(40) NOT NULL,
    Name varchar(160) NOT NULL,
    Purpose varchar(1000) NULL,
    OwnerType varchar(10) NULL,
    OwnerID int NULL,
    Status varchar(12) NOT NULL DEFAULT 'Planned',
    Priority varchar(10) NOT NULL DEFAULT 'Normal',
    PlannedStartDate date NULL,
    TargetDate date NULL,
    CompletedDate date NULL,
    CalendarEligible tinyint(1) NOT NULL DEFAULT 0,
    Note varchar(2000) NULL,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_ministry_project_number (ChurchID,ProjectNumber),
    KEY ix_ministry_project_work (ChurchID,Status,TargetDate,Priority),
    CONSTRAINT fk_ministry_project_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_ministry_project_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_ministry_project_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT ck_ministry_project_owner CHECK ((OwnerType IS NULL AND OwnerID IS NULL) OR (OwnerType IN ('Person','Group','User') AND OwnerID IS NOT NULL)),
    CONSTRAINT ck_ministry_project_status CHECK (Status IN ('Planned','Active','On Hold','Completed','Cancelled')),
    CONSTRAINT ck_ministry_project_priority CHECK (Priority IN ('Low','Normal','High','Urgent')),
    CONSTRAINT ck_ministry_project_dates CHECK (TargetDate IS NULL OR PlannedStartDate IS NULL OR TargetDate >= PlannedStartDate),
    CONSTRAINT ck_ministry_project_completed CHECK ((Status='Completed' AND CompletedDate IS NOT NULL) OR (Status<>'Completed' AND CompletedDate IS NULL)),
    CONSTRAINT ck_ministry_project_version CHECK (Version > 0)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tblMinistryProjectStep (
    ID int NOT NULL AUTO_INCREMENT,
    ProjectID int NOT NULL,
    Sequence int NOT NULL,
    Title varchar(200) NOT NULL,
    AssigneeType varchar(10) NULL,
    AssigneeID int NULL,
    Status varchar(15) NOT NULL DEFAULT 'Not Started',
    DueDate date NULL,
    CompletedDate date NULL,
    CalendarEligible tinyint(1) NOT NULL DEFAULT 0,
    Note varchar(1000) NULL,
    CreatedByUserID int NOT NULL,
    UpdatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    Version int NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_ministry_project_step_order (ProjectID,Sequence),
    KEY ix_ministry_project_step_due (Status,DueDate,AssigneeType,AssigneeID),
    CONSTRAINT fk_ministry_project_step_project FOREIGN KEY (ProjectID) REFERENCES tblMinistryProject(ID),
    CONSTRAINT fk_ministry_project_step_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT fk_ministry_project_step_updater FOREIGN KEY (UpdatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT ck_ministry_project_step_sequence CHECK (Sequence > 0),
    CONSTRAINT ck_ministry_project_step_assignee CHECK ((AssigneeType IS NULL AND AssigneeID IS NULL) OR (AssigneeType IN ('Person','Group','User') AND AssigneeID IS NOT NULL)),
    CONSTRAINT ck_ministry_project_step_status CHECK (Status IN ('Not Started','In Progress','Blocked','Complete','Not Needed')),
    CONSTRAINT ck_ministry_project_step_completed CHECK ((Status='Complete' AND CompletedDate IS NOT NULL) OR (Status<>'Complete' AND CompletedDate IS NULL)),
    CONSTRAINT ck_ministry_project_step_blocked CHECK (Status<>'Blocked' OR (Note IS NOT NULL AND TRIM(Note)<>'')),
    CONSTRAINT ck_ministry_project_step_version CHECK (Version > 0)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tblMinistryProjectStepDependency (
    ID bigint NOT NULL AUTO_INCREMENT,
    StepID int NOT NULL,
    PredecessorStepID int NOT NULL,
    CreatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_ministry_step_dependency (StepID,PredecessorStepID),
    CONSTRAINT fk_ministry_dependency_step FOREIGN KEY (StepID) REFERENCES tblMinistryProjectStep(ID) ON DELETE CASCADE,
    CONSTRAINT fk_ministry_dependency_predecessor FOREIGN KEY (PredecessorStepID) REFERENCES tblMinistryProjectStep(ID) ON DELETE CASCADE,
    CONSTRAINT fk_ministry_dependency_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID),
    CONSTRAINT ck_ministry_dependency_not_self CHECK (StepID<>PredecessorStepID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tblMinistryProjectDocument (
    ID bigint NOT NULL AUTO_INCREMENT,
    ProjectID int NOT NULL,
    StepID int NULL,
    DocumentID int NOT NULL,
    CreatedByUserID int NOT NULL,
    CreatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_ministry_project_document (ProjectID,StepID,DocumentID),
    CONSTRAINT fk_ministry_document_project FOREIGN KEY (ProjectID) REFERENCES tblMinistryProject(ID),
    CONSTRAINT fk_ministry_document_step FOREIGN KEY (StepID) REFERENCES tblMinistryProjectStep(ID),
    CONSTRAINT fk_ministry_document_document FOREIGN KEY (DocumentID) REFERENCES tblDocument(ID),
    CONSTRAINT fk_ministry_document_creator FOREIGN KEY (CreatedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('projects.view','View congregational projects, steps, and safe reports.',0,1),
('projects.manage','Create and update projects, steps, dependencies, and document links.',0,1),
('projects.assign','Assign project ownership and step responsibility.',0,1),
('projects.complete','Complete, reopen, cancel, or restore project work.',0,1),
('projects.admin','Administer project choices and guarded draft deletion.',1,1),
('projects.reports','Create congregational project reports.',0,1),
('projects.calendar','Publish eligible project dates through Calendar Integration.',1,1)
ON DUPLICATE KEY UPDATE Description=VALUES(Description),IsSensitive=VALUES(IsSensitive),Active=1;

INSERT INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Master Administrator' AND p.Name LIKE 'projects.%'
ON DUPLICATE KEY UPDATE RoleID=VALUES(RoleID);

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_ministry_project_summary AS
SELECT p.ChurchID,p.ID ProjectID,p.ProjectNumber,p.Name ProjectName,p.Purpose,p.OwnerType,p.OwnerID,
       p.Status,p.Priority,p.PlannedStartDate,p.TargetDate,p.CompletedDate,p.CalendarEligible,
       CASE WHEN p.Status IN ('Planned','Active','On Hold') AND p.TargetDate<CURRENT_DATE THEN 1 ELSE 0 END IsOverdue,
       SUM(CASE WHEN s.Status='Complete' THEN 1 ELSE 0 END) CompletedSteps,
       SUM(CASE WHEN s.Status IN ('Not Started','In Progress','Blocked') THEN 1 ELSE 0 END) OpenSteps
FROM tblMinistryProject p LEFT JOIN tblMinistryProjectStep s ON s.ProjectID=p.ID
GROUP BY p.ID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_ministry_project_due AS
SELECT p.ChurchID,p.ID ProjectID,p.ProjectNumber,p.Name ProjectName,s.ID StepID,s.Sequence,
       s.Title StepTitle,s.AssigneeType,s.AssigneeID,s.Status,s.DueDate,s.CalendarEligible,
       CASE WHEN s.Status IN ('Not Started','In Progress','Blocked') AND s.DueDate<CURRENT_DATE THEN 1 ELSE 0 END IsOverdue
FROM tblMinistryProjectStep s JOIN tblMinistryProject p ON p.ID=s.ProjectID
WHERE p.Status IN ('Planned','Active','On Hold') AND s.Status IN ('Not Started','In Progress','Blocked');

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_ministry_project_plan AS
SELECT p.ChurchID,p.ID ProjectID,p.ProjectNumber,p.Name ProjectName,p.Status ProjectStatus,
       p.Priority,s.ID StepID,s.Sequence,s.Title StepTitle,s.AssigneeType,s.AssigneeID,
       s.Status StepStatus,s.DueDate,s.CompletedDate,s.Note
FROM tblMinistryProject p LEFT JOIN tblMinistryProjectStep s ON s.ProjectID=p.ID;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_ministry_project_completed AS
SELECT ChurchID,ID ProjectID,ProjectNumber,Name ProjectName,Purpose,Priority,
       PlannedStartDate,TargetDate,CompletedDate
FROM tblMinistryProject WHERE Status='Completed';
