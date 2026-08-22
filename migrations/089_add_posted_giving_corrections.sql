-- Link immutable posted Giving batches to their accounting reversals and replacements.

ALTER TABLE tblContributionBatch
    ADD COLUMN ReversalAccountingTransactionID bigint NULL AFTER AccountingTransactionID,
    ADD COLUMN CorrectionReason varchar(1000) NULL AFTER CorrectionBatchID,
    ADD UNIQUE KEY uq_contribution_batch_reversal_transaction (ReversalAccountingTransactionID),
    ADD CONSTRAINT fk_contribution_batch_reversal_transaction
        FOREIGN KEY (ReversalAccountingTransactionID) REFERENCES tblAccountingTransaction(ID);

ALTER TABLE tblContribution
    ADD COLUMN CorrectionOfContributionID bigint NULL AFTER BatchID,
    ADD KEY ix_contribution_correction_source (CorrectionOfContributionID),
    ADD CONSTRAINT fk_contribution_correction_source
        FOREIGN KEY (CorrectionOfContributionID) REFERENCES tblContribution(ID);
