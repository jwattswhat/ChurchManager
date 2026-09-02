-- Store the congregation-owned ChurchManager password policy.
CREATE TABLE IF NOT EXISTS tblSecuritySettings (
    ID tinyint NOT NULL DEFAULT 1,
    MinimumPasswordLength smallint NOT NULL DEFAULT 8,
    UpdatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    CONSTRAINT ck_security_settings_singleton CHECK (ID=1),
    CONSTRAINT ck_security_password_minimum CHECK (MinimumPasswordLength BETWEEN 8 AND 128)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO tblSecuritySettings (ID, MinimumPasswordLength) VALUES (1, 8);
