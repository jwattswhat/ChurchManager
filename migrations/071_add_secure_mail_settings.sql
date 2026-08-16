-- Store non-secret email configuration. Passwords remain in Windows Credential Manager.
CREATE TABLE IF NOT EXISTS tblMailSettings (
    ID tinyint NOT NULL DEFAULT 1,
    Enabled tinyint(1) NOT NULL DEFAULT 0,
    Provider varchar(50) NOT NULL DEFAULT 'SMTP',
    Server varchar(255) NOT NULL DEFAULT '',
    Port int NOT NULL DEFAULT 587,
    Security varchar(20) NOT NULL DEFAULT 'STARTTLS',
    UserName varchar(255) NOT NULL DEFAULT '',
    SenderAddress varchar(255) NOT NULL DEFAULT '',
    SenderName varchar(255) NOT NULL DEFAULT 'ChurchManager',
    ReplyTo varchar(255) NOT NULL DEFAULT '',
    CredentialTarget varchar(255) NOT NULL DEFAULT 'ChurchManager/SMTP',
    TimeoutSeconds int NOT NULL DEFAULT 30,
    LastTestAt datetime NULL,
    LastTestStatus varchar(255) NULL,
    UpdatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    CONSTRAINT ck_mail_settings_singleton CHECK (ID=1),
    CONSTRAINT ck_mail_settings_port CHECK (Port BETWEEN 1 AND 65535),
    CONSTRAINT ck_mail_settings_security CHECK (Security IN ('STARTTLS','SSL'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO tblMailSettings (ID) VALUES (1);
