-- Versioned metadata-only Order of Service package ownership and stable keys.
CREATE TABLE IF NOT EXISTS tblOrderOfServicePackage (
    ID int NOT NULL AUTO_INCREMENT,
    PackageCode varchar(100) NOT NULL,
    PackageVersion varchar(50) NOT NULL,
    Title varchar(255) NOT NULL,
    SourceName varchar(255) NOT NULL DEFAULT '',
    SourceReference varchar(500) NOT NULL DEFAULT '',
    PackageNotice varchar(500) NOT NULL DEFAULT '',
    HymnalPackageCode varchar(100) NULL,
    MinimumHymnalVersion varchar(50) NULL,
    SchemaVersion int NOT NULL,
    Checksum char(64) NOT NULL,
    InstalledAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    IsActive tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_order_service_package_code (PackageCode),
    CONSTRAINT ck_order_service_package_schema CHECK (SchemaVersion > 0),
    CONSTRAINT ck_order_service_package_checksum CHECK (Checksum REGEXP '^[0-9a-fA-F]{64}$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE tblBulletinOrderTemplate
    ADD COLUMN IF NOT EXISTS TemplateKey varchar(150) NULL AFTER ID,
    ADD COLUMN IF NOT EXISTS PackageID int NULL AFTER TemplateKey;

UPDATE tblBulletinOrderTemplate
SET TemplateKey=CASE
    WHEN SourceLegacyName='STARTER:LCMS-DS1' THEN 'divine-service-setting-one'
    WHEN IsStarter=1 THEN CONCAT('starter-existing-',ID)
    ELSE CONCAT('local-',ID)
END
WHERE TemplateKey IS NULL OR TRIM(TemplateKey)='';

ALTER TABLE tblBulletinOrderTemplate
    MODIFY COLUMN TemplateKey varchar(150) NOT NULL,
    ADD UNIQUE KEY IF NOT EXISTS uq_bulletin_order_template_key (TemplateKey),
    ADD KEY IF NOT EXISTS ix_bulletin_order_package (PackageID),
    ADD CONSTRAINT fk_bulletin_order_package FOREIGN KEY (PackageID)
        REFERENCES tblOrderOfServicePackage(ID) ON DELETE RESTRICT;

ALTER TABLE tblBulletinOrderLine
    ADD COLUMN IF NOT EXISTS LineKey varchar(150) NULL AFTER ID;

UPDATE tblBulletinOrderLine
SET LineKey=CONCAT('line-existing-',ID)
WHERE LineKey IS NULL OR TRIM(LineKey)='';

DELIMITER $$
CREATE PROCEDURE enforce_order_service_metadata_lengths()
BEGIN
    IF EXISTS (
        SELECT 1 FROM tblBulletinOrderTemplate
        WHERE CHAR_LENGTH(COALESCE(Description,'')) > 250
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT='Order of Service template descriptions over 250 characters must be shortened';
    END IF;
    IF EXISTS (
        SELECT 1 FROM tblBulletinOrderLine
        WHERE CHAR_LENGTH(COALESCE(Label,'')) > 120
           OR CHAR_LENGTH(COALESCE(ReferenceText,'')) > 80
           OR CHAR_LENGTH(COALESCE(Note,'')) > 250
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT='Order of Service line metadata exceeds approved outline lengths';
    END IF;
END$$
CALL enforce_order_service_metadata_lengths()$$
DROP PROCEDURE enforce_order_service_metadata_lengths$$
DELIMITER ;

ALTER TABLE tblBulletinOrderTemplate
    MODIFY COLUMN Description varchar(250) NULL;

ALTER TABLE tblBulletinOrderLine
    MODIFY COLUMN LineKey varchar(150) NOT NULL,
    MODIFY COLUMN Label varchar(120) NOT NULL DEFAULT '',
    MODIFY COLUMN ReferenceText varchar(80) NULL,
    MODIFY COLUMN Note varchar(250) NULL,
    ADD UNIQUE KEY IF NOT EXISTS uq_bulletin_order_line_key (TemplateID,LineKey),
    DROP COLUMN IF EXISTS LegacyContent;

ALTER TABLE tblServiceBulletinOrder
    DROP COLUMN IF EXISTS GeneratedHtml;
