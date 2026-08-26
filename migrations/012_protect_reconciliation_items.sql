-- A bank row and posted ledger line may belong to only one reconciliation.
ALTER TABLE tblAccountingReconciliationItem
 ADD UNIQUE KEY uq_acct_recon_transaction_line (TransactionLineID),
 ADD UNIQUE KEY uq_acct_recon_import_row (ImportRowID);
