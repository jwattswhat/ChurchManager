-- Approved simple congregational asset register and preserved activity history.

CREATE TABLE IF NOT EXISTS tblAssetLocation (
  ID INT NOT NULL AUTO_INCREMENT,
  ChurchID INT NOT NULL,
  LocationName VARCHAR(120) NOT NULL,
  ParentLocationID INT NULL,
  Address VARCHAR(255) NULL,
  IsActive TINYINT(1) NOT NULL DEFAULT 1,
  Note TEXT NULL,
  Version INT NOT NULL DEFAULT 1,
  PRIMARY KEY (ID),
  CONSTRAINT fk_asset_location_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
  CONSTRAINT fk_asset_location_parent FOREIGN KEY (ParentLocationID) REFERENCES tblAssetLocation(ID),
  UNIQUE KEY uq_asset_location_name (ChurchID,ParentLocationID,LocationName),
  KEY ix_asset_location_church (ChurchID,IsActive,LocationName)
) ENGINE=InnoDB;

-- tblAsset predates this subsystem. Convert its small legacy register in place
-- so identifiers, names, purchase dates, and notes remain available.
UPDATE tblAsset
SET AssetID=LEFT(AssetID,40), Description=LEFT(Description,160);

UPDATE tblAsset a
JOIN (SELECT MIN(ID) AS ChurchID FROM tblChurch) church
SET a.ChurchID=church.ChurchID
WHERE a.ChurchID IS NULL;

ALTER TABLE tblAsset DROP FOREIGN KEY fk_asset_church;

ALTER TABLE tblAsset
  CHANGE COLUMN AssetID AssetNumber VARCHAR(40) NOT NULL,
  CHANGE COLUMN Description AssetName VARCHAR(160) NOT NULL,
  CHANGE COLUMN PurchaseDate AcquisitionDate DATE NULL,
  MODIFY COLUMN ChurchID INT NOT NULL,
  ADD COLUMN Category VARCHAR(80) NOT NULL DEFAULT 'Other' AFTER AssetName,
  ADD COLUMN Description VARCHAR(500) NULL AFTER Category,
  ADD COLUMN Quantity INT NOT NULL DEFAULT 1 AFTER Description,
  ADD COLUMN Manufacturer VARCHAR(120) NULL AFTER Quantity,
  ADD COLUMN Model VARCHAR(120) NULL AFTER Manufacturer,
  ADD COLUMN SerialNumber VARCHAR(120) NULL AFTER Model,
  ADD COLUMN LocationID INT NULL AFTER SerialNumber,
  ADD COLUMN ResponsiblePersonID INT NULL AFTER LocationID,
  ADD COLUMN ResponsibleGroupID INT NULL AFTER ResponsiblePersonID,
  ADD COLUMN AcquisitionMethod VARCHAR(40) NULL AFTER ResponsibleGroupID,
  ADD COLUMN ReferenceValue DECIMAL(13,2) NULL AFTER AcquisitionDate,
  ADD COLUMN `Condition` VARCHAR(40) NOT NULL DEFAULT 'Unknown' AFTER ReferenceValue,
  ADD COLUMN Status VARCHAR(40) NOT NULL DEFAULT 'Active' AFTER `Condition`,
  ADD COLUMN WarrantyExpires DATE NULL AFTER Status,
  ADD COLUMN NextMaintenanceDate DATE NULL AFTER WarrantyExpires,
  ADD COLUMN ReplacementReviewDate DATE NULL AFTER NextMaintenanceDate,
  ADD COLUMN RetiredDate DATE NULL AFTER ReplacementReviewDate,
  ADD COLUMN Version INT NOT NULL DEFAULT 1 AFTER Note,
  DROP COLUMN Reserve,
  DROP COLUMN Depreciate,
  ADD CONSTRAINT fk_asset_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
  ADD CONSTRAINT fk_asset_location FOREIGN KEY (LocationID) REFERENCES tblAssetLocation(ID),
  ADD CONSTRAINT fk_asset_person FOREIGN KEY (ResponsiblePersonID) REFERENCES tblPerson(ID),
  ADD CONSTRAINT fk_asset_group FOREIGN KEY (ResponsibleGroupID) REFERENCES tblGroup(ID),
  ADD CONSTRAINT ck_asset_quantity CHECK (Quantity > 0),
  ADD CONSTRAINT ck_asset_reference_value CHECK (ReferenceValue IS NULL OR ReferenceValue >= 0),
  ADD UNIQUE KEY uq_asset_number (ChurchID,AssetNumber),
  ADD KEY ix_asset_due (ChurchID,Status,NextMaintenanceDate,ReplacementReviewDate);

CREATE TABLE IF NOT EXISTS tblAssetActivity (
  ID INT NOT NULL AUTO_INCREMENT,
  AssetID INT NOT NULL,
  ActivityDate DATE NOT NULL,
  ActivityType VARCHAR(50) NOT NULL,
  Summary VARCHAR(500) NOT NULL,
  Cost DECIMAL(13,2) NULL,
  LocationID INT NULL,
  NextActionDate DATE NULL,
  DocumentID INT NULL,
  RecordedByUserID INT NOT NULL,
  CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (ID),
  CONSTRAINT fk_asset_activity_asset FOREIGN KEY (AssetID) REFERENCES tblAsset(ID),
  CONSTRAINT fk_asset_activity_location FOREIGN KEY (LocationID) REFERENCES tblAssetLocation(ID),
  CONSTRAINT fk_asset_activity_document FOREIGN KEY (DocumentID) REFERENCES tblDocument(ID),
  CONSTRAINT fk_asset_activity_user FOREIGN KEY (RecordedByUserID) REFERENCES tblUser(ID),
  CONSTRAINT ck_asset_activity_cost CHECK (Cost IS NULL OR Cost >= 0),
  KEY ix_asset_activity_history (AssetID,ActivityDate,ID)
) ENGINE=InnoDB;

INSERT INTO tblPermission (Name,Description,IsSensitive,Active) VALUES
('assets.view','View congregational assets, locations, history, and reports.',0,1),
('assets.manage','Create and update assets, locations, and activities.',0,1),
('assets.retire','Retire, mark lost, dispose of, or restore an asset.',1,1)
ON DUPLICATE KEY UPDATE Description=VALUES(Description),IsSensitive=VALUES(IsSensitive),Active=1;

INSERT INTO tblRolePermission (RoleID,PermissionID)
SELECT r.ID,p.ID FROM tblRole r CROSS JOIN tblPermission p
WHERE r.Name='Master Administrator' AND p.Name IN ('assets.view','assets.manage','assets.retire')
ON DUPLICATE KEY UPDATE RoleID=VALUES(RoleID);

INSERT INTO tblChoices (Field,Choices,Note) VALUES
('AssetCategory','[Audio/Visual\nBuilding Equipment\nFurniture\nKitchen Equipment\nMusical Instrument\nOffice Equipment\nTechnology\nVehicle\nOther]','Congregation-maintained asset categories.'),
('AssetCondition','[Excellent\nGood\nFair\nPoor\nUnknown]','Current physical condition of an asset.'),
('AssetAcquisitionMethod','[Purchased\nDonated\nTransferred\nOther]','How an asset came into congregational care.'),
('AssetActivityType','[Maintenance\nInspection\nRepair\nTransfer\nCondition Review\nRetirement\nDisposal\nLoss\nNote]','Append-only asset activity types.')
ON DUPLICATE KEY UPDATE Note=VALUES(Note);

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_asset_register AS
SELECT a.ChurchID,a.ID AssetID,a.AssetNumber,a.AssetName,a.Category,a.Quantity,
       l.LocationName,TRIM(CONCAT_WS(' ',p.FirstName,p.LastName)) ResponsiblePerson,
       g.Name ResponsibleGroup,a.`Condition`,a.Status,a.NextMaintenanceDate,a.ReplacementReviewDate
FROM tblAsset a LEFT JOIN tblAssetLocation l ON l.ID=a.LocationID
LEFT JOIN tblPerson p ON p.ID=a.ResponsiblePersonID LEFT JOIN tblGroup g ON g.ID=a.ResponsibleGroupID;

-- Replace the obsolete generic asset view so no retired column names remain.
CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_asset AS
SELECT ID,ChurchID,AssetNumber,AssetName,Category,Description,Quantity,
       Manufacturer,Model,SerialNumber,LocationID,ResponsiblePersonID,
       ResponsibleGroupID,AcquisitionMethod,AcquisitionDate,ReferenceValue,
       `Condition`,Status,WarrantyExpires,NextMaintenanceDate,
       ReplacementReviewDate,RetiredDate,Note,Version
FROM tblAsset;

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_asset_maintenance_due AS
SELECT a.ChurchID,a.ID AssetID,a.AssetNumber,a.AssetName,l.LocationName,a.`Condition`,a.Status,
       a.NextMaintenanceDate,a.ReplacementReviewDate,
       LEAST(COALESCE(a.NextMaintenanceDate,'9999-12-31'),COALESCE(a.ReplacementReviewDate,'9999-12-31')) DueDate
FROM tblAsset a LEFT JOIN tblAssetLocation l ON l.ID=a.LocationID
WHERE a.Status NOT IN ('Retired','Lost','Disposed')
  AND (a.NextMaintenanceDate IS NOT NULL OR a.ReplacementReviewDate IS NOT NULL);

CREATE OR REPLACE SQL SECURITY DEFINER VIEW rpt_asset_history AS
SELECT a.ChurchID,a.ID AssetID,a.AssetNumber,a.AssetName,h.ActivityDate,h.ActivityType,h.Summary,
       h.Cost,l.LocationName,h.NextActionDate,h.CreatedAt
FROM tblAssetActivity h JOIN tblAsset a ON a.ID=h.AssetID
LEFT JOIN tblAssetLocation l ON l.ID=h.LocationID;

INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMAM01','Asset Management - Asset Register','[ChurchID]',NULL,'Current congregational asset register.',1,p.ID
FROM tblPermission p WHERE p.Name='assets.view'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);
INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMAM02','Asset Management - Maintenance Due','[ChurchID]',NULL,'Due and upcoming asset work.',1,p.ID
FROM tblPermission p WHERE p.Name='assets.view'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);
INSERT INTO tblReports (Report,Title,Params,Batch,Note,Available,RequiredPermissionID)
SELECT 'CMAM03','Asset Management - Asset History','[ChurchID\r\nAssetID]',NULL,'Dated history for one selected asset.',1,p.ID
FROM tblPermission p WHERE p.Name='assets.view'
ON DUPLICATE KEY UPDATE Title=VALUES(Title),Params=VALUES(Params),Note=VALUES(Note),Available=1,RequiredPermissionID=VALUES(RequiredPermissionID);
