CREATE TABLE tblWorshipChecklistTemplate (
    ID int NOT NULL AUTO_INCREMENT,
    ChurchID int NULL,
    Name varchar(255) NOT NULL,
    IsStarter tinyint(1) NOT NULL DEFAULT 0,
    Active tinyint(1) NOT NULL DEFAULT 1,
    Note text NULL,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_worship_checklist_template (ChurchID,Name),
    CONSTRAINT fk_worship_checklist_template_church FOREIGN KEY (ChurchID)
        REFERENCES tblChurch (ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tblWorshipChecklistTemplateItem (
    ID int NOT NULL AUTO_INCREMENT,
    TemplateID int NOT NULL,
    Sequence int NOT NULL,
    Task varchar(255) NOT NULL,
    CompletionSource varchar(30) NOT NULL DEFAULT 'MANUAL',
    Required tinyint(1) NOT NULL DEFAULT 1,
    Active tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_worship_checklist_template_item (TemplateID,Sequence),
    CONSTRAINT fk_worship_checklist_item_template FOREIGN KEY (TemplateID)
        REFERENCES tblWorshipChecklistTemplate (ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tblServiceChecklistItem (
    ID bigint NOT NULL AUTO_INCREMENT,
    ServiceID int NOT NULL,
    TemplateItemID int NULL,
    Sequence int NOT NULL,
    Task varchar(255) NOT NULL,
    CompletionSource varchar(30) NOT NULL DEFAULT 'MANUAL',
    Required tinyint(1) NOT NULL DEFAULT 1,
    Status varchar(20) NOT NULL DEFAULT 'NOT_DONE',
    Note text NULL,
    CompletedAt datetime NULL,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_service_checklist_item (ServiceID,Sequence),
    CONSTRAINT fk_service_checklist_service FOREIGN KEY (ServiceID)
        REFERENCES tblService (ID) ON DELETE CASCADE,
    CONSTRAINT fk_service_checklist_template_item FOREIGN KEY (TemplateItemID)
        REFERENCES tblWorshipChecklistTemplateItem (ID) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE tblService
    ADD COLUMN WorshipChecklistTemplateID int NULL AFTER CheckListID,
    ADD CONSTRAINT fk_service_worship_checklist_template FOREIGN KEY (WorshipChecklistTemplateID)
        REFERENCES tblWorshipChecklistTemplate (ID) ON DELETE SET NULL;

INSERT INTO tblWorshipChecklistTemplate (ChurchID,Name,IsStarter,Active,Note)
VALUES (NULL,'Standard Worship Preparation',1,1,
        'A flexible reminder list. Items may be marked not needed for a particular service.');

INSERT INTO tblWorshipChecklistTemplateItem
    (TemplateID,Sequence,Task,CompletionSource,Required,Active)
SELECT t.ID,source.ItemOrder,source.Task,source.CompletionSource,1,1
FROM tblWorshipChecklistTemplate t
JOIN (
    SELECT 1 ItemOrder,'Complete weekly Order of Service' Task,'ORDER' CompletionSource UNION ALL
    SELECT 2,'Select hymns','HYMNS' UNION ALL
    SELECT 3,'Assign participants','PARTICIPANTS' UNION ALL
    SELECT 4,'Prepare sermon','MANUAL' UNION ALL
    SELECT 5,'Review prayers','MANUAL' UNION ALL
    SELECT 6,'Prepare bulletin','MANUAL' UNION ALL
    SELECT 7,'Proofread bulletin','MANUAL' UNION ALL
    SELECT 8,'Complete bulletin','MANUAL' UNION ALL
    SELECT 9,'Print or distribute bulletin','MANUAL' UNION ALL
    SELECT 10,'Notify participants','MANUAL'
) source
WHERE t.ChurchID IS NULL AND t.Name='Standard Worship Preparation';

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_checklist AS
SELECT i.ServiceID,i.Sequence,i.Task,i.Required,i.Status,
       COALESCE(i.Note,'') AS Note,i.CompletionSource
FROM tblServiceChecklistItem i;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_worship_planner_checklist_summary AS
SELECT ID AS ServiceID,COALESCE(CheckListComplete,0) AS ManuallyConfirmed
FROM tblService;
