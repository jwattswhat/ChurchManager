-- Package display prefixes and package-owned role metadata for safe importing.
ALTER TABLE tblOrderOfServicePackage
    ADD COLUMN IF NOT EXISTS TemplatePrefix varchar(20) NOT NULL DEFAULT '' AFTER Title;

CREATE TABLE IF NOT EXISTS tblOrderOfServicePackageRoleRequirement (
    ID int NOT NULL AUTO_INCREMENT,
    PackageID int NOT NULL,
    TemplateID int NOT NULL,
    RoleKey varchar(100) NOT NULL,
    RequiredCount smallint unsigned NOT NULL DEFAULT 1,
    PRIMARY KEY (ID),
    UNIQUE KEY uq_order_service_package_role (TemplateID,RoleKey),
    KEY ix_order_service_package_role_owner (PackageID),
    CONSTRAINT fk_order_service_package_role_package FOREIGN KEY (PackageID)
        REFERENCES tblOrderOfServicePackage(ID) ON DELETE CASCADE,
    CONSTRAINT fk_order_service_package_role_template FOREIGN KEY (TemplateID)
        REFERENCES tblBulletinOrderTemplate(ID) ON DELETE CASCADE,
    CONSTRAINT ck_order_service_package_role_count CHECK (RequiredCount BETWEEN 0 AND 99)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tblOrderOfServicePackageImport (
    ID bigint NOT NULL AUTO_INCREMENT,
    PackageID int NOT NULL,
    PackageVersion varchar(50) NOT NULL,
    Checksum char(64) NOT NULL,
    Action varchar(20) NOT NULL,
    TemplateCount int NOT NULL,
    LineCount int NOT NULL,
    RoleCount int NOT NULL,
    ImportedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    KEY ix_order_service_import_package (PackageID,ImportedAt),
    CONSTRAINT fk_order_service_import_package FOREIGN KEY (PackageID)
        REFERENCES tblOrderOfServicePackage(ID) ON DELETE RESTRICT,
    CONSTRAINT ck_order_service_import_action CHECK (Action IN ('INSTALL','UPGRADE'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
