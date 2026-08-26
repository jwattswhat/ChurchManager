CREATE TABLE tblLectionarySystem (
    ID int NOT NULL AUTO_INCREMENT,
    Name varchar(255) NOT NULL,
    CycleType varchar(20) NOT NULL DEFAULT 'None',
    Active tinyint(1) NOT NULL DEFAULT 1,
    Note text NULL,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_lectionary_system_name (Name),
    CONSTRAINT chk_lectionary_system_cycle_type
        CHECK (CycleType IN ('None', 'ABC', 'Custom'))
) ENGINE=InnoDB;

INSERT INTO tblLectionarySystem (Name, CycleType)
SELECT DISTINCT
    TRIM(Lectionary),
    CASE
        WHEN LOWER(Lectionary) LIKE '%three-year%'
          OR LOWER(Lectionary) LIKE '%three year%'
          OR LOWER(Lectionary) LIKE '%revised common%'
        THEN 'ABC'
        ELSE 'None'
    END
FROM tblPropers
WHERE Lectionary IS NOT NULL AND TRIM(Lectionary) <> '';

INSERT INTO tblLectionarySystem (Name, CycleType)
SELECT 'Unspecified', 'Custom'
WHERE EXISTS (
    SELECT 1 FROM tblPropers
    WHERE Lectionary IS NULL OR TRIM(Lectionary) = ''
)
AND NOT EXISTS (
    SELECT 1 FROM tblLectionarySystem WHERE Name = 'Unspecified'
);

ALTER TABLE tblPropers
    ADD COLUMN LectionarySystemID int NULL AFTER ID,
    ADD COLUMN Cycle varchar(20) NULL AFTER LectionarySystemID;

UPDATE tblPropers p
JOIN tblLectionarySystem ls ON ls.Name = TRIM(p.Lectionary)
SET p.LectionarySystemID = ls.ID;

UPDATE tblPropers
SET LectionarySystemID = (SELECT ID FROM tblLectionarySystem WHERE Name = 'Unspecified')
WHERE LectionarySystemID IS NULL;

ALTER TABLE tblPropers
    MODIFY COLUMN LectionarySystemID int NOT NULL,
    ADD INDEX ix_propers_system_cycle_sort (LectionarySystemID, Cycle, Sort),
    ADD CONSTRAINT fk_propers_lectionary_system
        FOREIGN KEY (LectionarySystemID) REFERENCES tblLectionarySystem(ID),
    DROP COLUMN Lectionary;

CREATE VIEW vwPropersLookup AS
SELECT
    p.ID,
    CONCAT(
        ls.Name,
        CASE
            WHEN p.Cycle IS NULL OR TRIM(p.Cycle) = '' THEN ''
            ELSE CONCAT(' - Year ', p.Cycle)
        END,
        ' - ',
        p.LiturgicalDate
    ) AS DisplayName,
    ls.Name AS SystemName,
    p.Cycle,
    p.Sort
FROM tblPropers p
JOIN tblLectionarySystem ls ON ls.ID = p.LectionarySystemID;
