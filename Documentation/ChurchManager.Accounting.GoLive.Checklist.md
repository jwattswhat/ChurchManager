# ChurchManager Accounting Go-Live Checklist

This checklist controls the first production use of ChurchManager fund accounting. Development and legacy ChurchManager remain independent programs until the authorized cutover date.

## 1. Release readiness

- [x] Core double-entry transaction workflow tested in `ChurchDBTest`.
- [x] Posting, reversal, approval, audit, reconciliation, budgets, period close, year-end close/reopen, and opening balances implemented.
- [x] Automated suite passes: 226 tests on August 12, 2026; 12 database integration tests skipped by the standard runner.
- [ ] Run the database integration suite against a fresh production-like test clone.
- [ ] Complete the planned accounting reports review.
- [ ] Resolve all release-blocking defects found during final user acceptance testing.
- [ ] Create a signed release tag or otherwise record the exact approved commit.

## 2. Backup and recovery

- [x] Local `ChurchDBTest` and `JSFormTest` backups created with SHA-256 manifests.
- [x] `ChurchDBTest` backup restored into an isolated temporary database on August 12, 2026.
- [x] Restored database contained 73 tables/views, 21 accounting transactions, 60 transaction lines, and 77 audit events.
- [x] Restored posted ledger difference was `$0.00`.
- [x] Restored fiscal-year closing references had zero errors.
- [x] Temporary verification database was removed after certification.
- [ ] Create and verify a final pre-cutover production backup.
- [ ] Confirm the backup destination is separate from the MariaDB data directory and local storage failure domain.
- [ ] Perform a production-environment restore rehearsal without overwriting production.
- [ ] Document the person responsible for backups and the restore procedure.

Certified local backup:

- Folder: `LocalTestMigrationBackups/20260812-045129`
- `ChurchDBTest` SHA-256: `40775299ef6b46cd12befe658610e13fda6d90ca9f0ce54f22d56ec7712f4a4d`
- Certification result: `PASS`

## 3. Production isolation and database preparation

- [ ] Confirm the legacy program still points only to its legacy production database.
- [ ] Confirm development/test ChurchManager points only to `ChurchDBTest` and `JSFormTest`.
- [ ] Choose the new production database names and hosting computer.
- [ ] Confirm production is not hosted on removable SD-card storage.
- [ ] Create least-privilege production application credentials.
- [ ] Apply all versioned migrations through the guarded migration runner.
- [ ] Verify migration checksums and table engines.
- [ ] Confirm no test organization, synthetic transaction, bank file, or test user exists in production.

## 4. Organization and accounting configuration

- [ ] Confirm legal organization name, reporting basis, fiscal-year start month, and currency.
- [ ] Approve the chart of accounts.
- [ ] Approve funds, donor-restriction classifications, and board designations.
- [ ] Assign an active, postable net-asset account to every active fund.
- [ ] Approve ministry/function classifications.
- [ ] Define the first fiscal year and all fiscal periods.
- [ ] Configure bank accounts and verify masked account identification.
- [ ] Set approval and attachment thresholds.
- [ ] Choose `Independent Required` or `Independent Preferred` approval policy.

## 5. Users and permissions

- [ ] Create the master administrator account and verify emergency access.
- [ ] Create each accounting user as an individual account; do not share credentials.
- [ ] Assign only the roles needed for entry, approval, posting, reconciliation, reporting, and administration.
- [ ] Verify the solo-approval override is available only to explicitly authorized users.
- [ ] Confirm inactive or departed users cannot sign in.
- [ ] Record the support email and phone number for each user when those fields are implemented.

## 6. Cutover and opening balances

- [ ] Choose and document the cutover date.
- [ ] Complete all legacy activity through the day before cutover.
- [ ] Reconcile every bank account through the cutover date.
- [ ] Obtain approved account-and-fund opening balances from the legacy records.
- [ ] Enter one balanced `Opening Balances` transaction using only asset, liability, and net-asset accounts.
- [ ] Attach the approved source balance report.
- [ ] Independently approve or use the documented small-congregation override.
- [ ] Post the opening-balance transaction.
- [ ] Confirm trial balance difference is `$0.00`.
- [ ] Confirm financial position and fund balances agree with approved legacy reports.
- [ ] Confirm bank reconciliation beginning balances agree with statements.

## 7. Report and workflow acceptance

- [ ] Transaction entry, approval, posting, and reversal accepted by the accounting user.
- [ ] Bank import, matching, reconciliation, and reconciliation report accepted.
- [ ] Trial balance and general ledger accepted.
- [ ] Statement of financial position accepted.
- [ ] Statement of activities accepted.
- [ ] Fund balances and functional expenses accepted.
- [ ] Budget entry, adoption, amendments, and budget-to-actual accepted.
- [ ] Period close/reopen accepted.
- [ ] Year-end preview, close, and reopen accepted using test data.
- [ ] Printed/exported report formatting reviewed, including right-aligned monetary amounts.

## 8. Final authorization

- [ ] Treasurer/accounting operator signoff obtained.
- [ ] Congregational officer or authorized reviewer signoff obtained.
- [ ] Backup/restore certification reviewed and accepted.
- [ ] Cutover date and responsible persons recorded.
- [ ] Legacy system designated read-only after cutover, with retention period documented.
- [ ] Go-live authorized.

### Signoff

| Responsibility | Name | Date | Signature/record |
| --- | --- | --- | --- |
| Accounting operator |  |  |  |
| Authorized reviewer |  |  |  |
| ChurchManager administrator |  |  |  |

