-- Establish the authoritative key version used for restricted pastoral notes.

CREATE TABLE IF NOT EXISTS tblPastoralEncryptionState (
    ID tinyint unsigned NOT NULL,
    ActiveKeyVersion int unsigned NOT NULL DEFAULT 1,
    RecoveryVerified tinyint(1) NOT NULL DEFAULT 0,
    UpdatedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    CONSTRAINT ck_pastoral_encryption_state_id CHECK (ID=1),
    CONSTRAINT ck_pastoral_encryption_active_version CHECK (ActiveKeyVersion > 0),
    CONSTRAINT ck_pastoral_encryption_recovery_verified
        CHECK (RecoveryVerified IN (0,1))
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO tblPastoralEncryptionState
    (ID, ActiveKeyVersion, RecoveryVerified)
VALUES (1, 1, 0);
