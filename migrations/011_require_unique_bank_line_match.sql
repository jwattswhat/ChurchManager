-- A posted ledger line may be matched to at most one imported bank row.
ALTER TABLE tblAccountingBankImportRow
 ADD UNIQUE KEY uq_acct_import_matched_line (MatchedTransactionLineID);
