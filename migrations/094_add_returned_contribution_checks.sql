-- Preserve an auditable link from a returned donor check to the Giving batch
-- replacement and the summarized accounting reversal. Donor identity remains
-- confined to Giving.

CREATE TABLE IF NOT EXISTS tblContributionReturn (
    ID bigint NOT NULL AUTO_INCREMENT,
    ChurchID int NOT NULL,
    OriginalContributionID bigint NOT NULL,
    OriginalBatchID bigint NOT NULL,
    ReplacementBatchID bigint NOT NULL,
    ReversalAccountingTransactionID bigint NOT NULL,
    ReturnDate date NOT NULL,
    Reason varchar(1000) NOT NULL,
    RecordedByUserID int NOT NULL,
    RecordedAt datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (ID),
    UNIQUE KEY uq_contribution_return_original (OriginalContributionID),
    KEY ix_contribution_return_batch (OriginalBatchID, ReplacementBatchID),
    CONSTRAINT fk_contribution_return_church FOREIGN KEY (ChurchID) REFERENCES tblChurch(ID),
    CONSTRAINT fk_contribution_return_gift FOREIGN KEY (OriginalContributionID) REFERENCES tblContribution(ID),
    CONSTRAINT fk_contribution_return_original_batch FOREIGN KEY (OriginalBatchID) REFERENCES tblContributionBatch(ID),
    CONSTRAINT fk_contribution_return_replacement_batch FOREIGN KEY (ReplacementBatchID) REFERENCES tblContributionBatch(ID),
    CONSTRAINT fk_contribution_return_reversal FOREIGN KEY (ReversalAccountingTransactionID) REFERENCES tblAccountingTransaction(ID),
    CONSTRAINT fk_contribution_return_user FOREIGN KEY (RecordedByUserID) REFERENCES tblUser(ID)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
