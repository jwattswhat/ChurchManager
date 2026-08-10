# ChurchManager Double-Entry Fund Accounting Specification

**Status:** Approved
**Version:** 1.0
**Date:** August 10, 2026  
**Target application:** ChurchManager  
**Application framework:** JSForm  
**Database:** MariaDB/MySQL

## 1. Purpose

This document specifies a double-entry fund accounting module for a church. The module will be built as part of ChurchManager and will use JSForm for its desktop forms, controls, record navigation, configuration, and LimeReport integration.

The module must provide reliable books of account for a small congregation without requiring the user to understand database internals. It must preserve a complete audit trail, prevent unbalanced or retrospective changes to posted entries, track resources by fund and donor-restriction class, support budgeting and bank reconciliation, and produce useful congregational and accountant-ready reports.

This is a new accounting system. Historical ChurchManager financial, donor, giving, envelope, and posting artifacts are unfinished prototypes and are not the design or data source for this module. No historical financial data will be migrated unless a separate, reviewed migration plan is approved.

## 2. Accounting and compliance basis

The system is designed for a United States not-for-profit church. Its reporting model will use the current not-for-profit terminology:

- Net assets without donor restrictions.
- Net assets with donor restrictions.
- Governing-board designations recorded separately from donor restrictions.

The system will maintain records that identify sources of receipts, purposes of expenditures, account classifications, funds, restrictions, supporting documents, and changes made by users. It will support, but will not itself guarantee, compliance with GAAP, tax law, payroll law, congregational policy, grant terms, or donor restrictions. Final account setup and reporting policies should be reviewed by the church's accountant or treasurer.

## 3. Design principles

1. **Double entry is mandatory.** Every posted transaction has at least two lines, and total debits equal total credits.
2. **Each fund balances.** Within a posted transaction, debits and credits must balance for each fund. Transfers use explicit transfer-in and transfer-out accounts.
3. **Funds are not bank accounts.** A fund describes the purpose or restriction of resources; a bank account describes where cash is held. One bank account may contain cash belonging to several funds.
4. **Restrictions are not board designations.** Donor restrictions and governing-board designations are distinct attributes.
5. **Posted history is immutable.** A posted transaction is never edited or deleted. Errors are corrected by a linked reversal and, when needed, a replacement transaction.
6. **Drafts are editable.** Draft transactions may be changed or deleted by authorized users and have no ledger effect.
7. **Posting is atomic.** Header, lines, audit records, numbering, and derived updates succeed or fail as one database transaction.
8. **Money uses decimal arithmetic.** Monetary columns use `DECIMAL`, never `FLOAT`.
9. **Reports derive from journal lines.** Balances are calculated from posted transaction lines, not maintained as manually editable totals.
10. **Least privilege applies.** Users receive only the permissions needed for their role.
11. **Sensitive data is minimized.** The general ledger will not store bank credentials, Social Security numbers, or full payment-card data.
12. **JSForm is the presentation framework.** Accounting rules live in a dedicated service layer and database constraints, not solely in JSON form definitions.

## 4. Definitions

| Term | Meaning in this specification |
| --- | --- |
| Account | A chart-of-accounts category such as Checking, Contributions, Utilities, or Accounts Payable. |
| Fund | A self-balancing set of resources tracked for a purpose, restriction, or internal reporting need. |
| Natural account | The economic nature of a transaction: cash, contribution revenue, salary expense, and so forth. |
| Functional classification | The program or supporting activity served by an expense, such as Worship, Education, Outreach, Management and General, or Fundraising. |
| Transaction | A journal-entry header plus two or more debit/credit lines. |
| Posting | The controlled action that validates a draft and makes it part of the permanent ledger. |
| Transfer | A movement between funds that does not create external revenue or expense for the church as a whole. |
| Restriction | A donor-imposed limit based on purpose or time. |
| Designation | A governing-board decision to set aside otherwise unrestricted resources. |
| Fiscal period | A month or other posting interval within a fiscal year. |
| Source document | An invoice, receipt, deposit record, bank statement, authorization, or other supporting evidence. |

## 5. Scope

### 5.1 Minimum viable release

The first operational release will include:

- Organization and fiscal-year settings.
- Chart of accounts.
- Funds and restriction classification.
- Functional expense categories.
- Fiscal years and periods.
- Draft journal entry, review, posting, reversal, and copying.
- Cash receipt, cash disbursement, and fund-transfer entry templates.
- Vendors/payees.
- Bank accounts and bank reconciliation.
- Annual budgets by account, fund, and function.
- Source-document attachment references.
- Role-based permissions and audit history.
- General ledger, trial balance, statement of financial position, statement of activities, budget-to-actual, fund-balance, transaction-register, and reconciliation reports.
- Opening-balance import through a controlled balanced journal entry.

### 5.2 Later releases

The following are valuable but are not required for the first operational release:

- Individual contribution and envelope tracking.
- Contribution acknowledgments and annual donor statements.
- Pledges.
- Accounts payable workflow and check printing.
- Recurring transactions.
- Fixed-asset depreciation.
- Grant management.
- Payroll import.
- Bank-statement import and matching suggestions.
- Cash-flow statement.
- Multi-entity consolidation.

### 5.3 Explicitly out of scope

- Payroll calculation or tax filing.
- Online banking or payment initiation.
- Credit-card storage or processing.
- Investment subledger accounting.
- Inventory accounting.
- Automatic tax, legal, or audit advice.
- Editing or repurposing the old financial prototype as if it were production data.

## 6. Accounting model

### 6.1 Chart of accounts

Every account has a stable code, name, type, normal balance, report grouping, and active state. Required account types are:

1. Asset.
2. Liability.
3. Net Asset.
4. Revenue.
5. Expense.

The congregation-neutral starter chart is:

| Range | Starter accounts |
| --- | --- |
| Assets | 1000 Checking; 1100 Savings; 1200 Accounts Receivable; 1300 Prepaid Expenses; 1500 Property and Equipment; 1590 Accumulated Depreciation |
| Liabilities | 2000 Accounts Payable; 2100 Payroll and Other Withholdings; 2200 Accrued Expenses; 2300 Deferred Revenue; 2500 Loans Payable |
| Net assets | 3000 Net Assets Without Donor Restrictions; 3100 Board-Designated Net Assets; 3200 Net Assets With Donor Restrictions |
| Revenue | 4000 General Contributions; 4100 Restricted Contributions; 4200 Grants; 4300 Program and Event Income; 4400 Interest and Investment Income; 4900 Other Income |
| Expenses | 5000 Pastoral Compensation; 5100 Other Salaries and Wages; 5200 Employee Benefits; 5300 Worship; 5400 Christian Education; 5500 Missions and Benevolence; 5600 Property and Utilities; 5700 Office and Administration; 5800 Insurance and Professional Services; 5900 Fundraising; 6000 Depreciation; 6900 Other Expenses |
| Transfers | 8000 Transfers Out; 8100 Transfers In |

Accounts Receivable, Accounts Payable, Deferred Revenue, Accumulated
Depreciation, and Depreciation begin inactive under the modified-cash starter
policy. A congregation reviews, renames, subdivides, activates, or deactivates
the starter accounts during setup.

Account codes are strings, not integers, so codes such as `1000`, `1000.10`, or `01-1000` retain their formatting. Codes must be unique within the organization.

An account may be a posting account or a heading. Only posting accounts may appear on journal lines. Accounts with posted activity cannot be deleted; they may be deactivated.

Each account defines:

- Normal balance: Debit or Credit.
- Financial-statement group and display order.
- Whether a function is required, optional, or prohibited.
- Whether a payee is required.
- Whether the account represents cash or a bank account.
- Whether the account is used for interfund transfers.
- Effective start and end dates, if any.

### 6.2 Funds and restrictions

Every journal line must identify one active fund. Each fund contains:

- Code and name.
- Description and purpose.
- Net-asset class: With Donor Restrictions or Without Donor Restrictions.
- Restriction type: None, Purpose, Time, or Purpose and Time.
- Board-designated flag, allowed only when the net-asset class is Without Donor Restrictions.
- Restriction or designation text.
- Start date and optional release/end date.
- Default net-asset account.
- Active and closed states.

A fund with posted activity cannot be deleted. Closing a fund prevents new postings after its closing date but does not hide history.

### 6.3 Functional expense classification

Expense lines must support functional classification. The initial configurable list should include:

- Worship and congregational life.
- Christian education.
- Outreach and missions.
- Mercy and benevolence.
- Property and facilities.
- Management and general.
- Fundraising.

An organization may add or deactivate functions. Posted history retains the original function.

### 6.4 Basis of accounting

The ledger supports accrual-basis double-entry accounting. A small church may use cash-oriented entry templates, but the underlying ledger must permit receivables, payables, prepaid expenses, deferred revenue, depreciation, and adjusting entries.

The organization's reporting-basis setting is descriptive; it must not weaken double-entry or audit controls.

### 6.5 Debit and credit rules

Each transaction line has either a positive debit or a positive credit, never both and never neither. Negative debits and credits are prohibited. Corrections use the opposite side or a reversal transaction.

The normal-balance presentation is:

| Account type | Increase | Decrease |
| --- | --- | --- |
| Asset | Debit | Credit |
| Liability | Credit | Debit |
| Net Asset | Credit | Debit |
| Revenue | Credit | Debit |
| Expense | Debit | Credit |

### 6.6 Fund balancing and transfers

Each posted transaction must balance by fund as well as in total. A transfer from the General Fund to the Building Fund uses four lines:

| Fund | Account | Debit | Credit |
| --- | --- | ---: | ---: |
| General | Transfer Out | 1,000.00 | 0.00 |
| General | Cash | 0.00 | 1,000.00 |
| Building | Cash | 1,000.00 | 0.00 |
| Building | Transfer In | 0.00 | 1,000.00 |

Transfer accounts must be separately identifiable so consolidated reports can eliminate them where appropriate.

### 6.7 Releases from donor restrictions

When a purpose or time restriction is satisfied, the system records an explicit release transaction using configured release accounts. The release must identify the restricted fund, receiving unrestricted fund, amount, date, explanation, authorizer, and related source documentation.

The system must not infer that a restriction has been satisfied merely because money was spent.

### 6.8 Fiscal years and periods

Fiscal years may differ from calendar years. Each fiscal year contains ordered periods with Open, Soft Closed, or Closed status.

- Open: authorized users may create and post.
- Soft Closed: only users with period-override permission may post, with a required reason.
- Closed: no posting is allowed.

Reopening a closed period requires administrator permission and creates an audit event. Reports show both transaction date and posting timestamp.

### 6.9 Year-end closing

The system will generate, preview, and post a year-end closing transaction that closes revenue, expense, and transfer accounts into each fund's configured net-asset account. The close cannot proceed while any period in the year is open, any draft is marked Ready for Review, or the trial balance is out of balance.

A year may be reopened only through an explicit controlled process. Reopening reverses the closing transaction, records the reason, and requires the year to be closed again after adjustments.

## 7. Transaction lifecycle

### 7.1 Statuses

Transactions use these statuses:

- `DRAFT` — editable and excluded from balances.
- `READY` — awaiting approval; lines are locked except by returning the transaction to Draft.
- `POSTED` — immutable and included in the ledger.
- `REVERSED` — posted transaction fully offset by a linked posted reversal.
- `VOID` — unused number or abandoned draft retained for numbering/audit purposes; never part of balances.

### 7.2 Required header data

Every transaction requires:

- Transaction date.
- Transaction type.
- Description.
- Fiscal period derived from the date.
- At least one source/reference value when required by the transaction type.
- Creator and creation timestamp.

Posting additionally requires:

- Two or more valid lines.
- Balanced debit and credit totals.
- Balance within each fund.
- Open or properly overridden fiscal period.
- Active accounts, funds, and functions valid on the transaction date.
- Required payee, function, reference, or attachment fields.
- Reviewer/approver when separation-of-duties policy requires it.

### 7.3 Numbering

Drafts receive a temporary internal ID. A permanent, gap-tolerant transaction number is assigned inside the posting transaction. Numbers are never reused. Voided or failed numbers remain explainable in the audit history.

The display format is configurable, with a default such as `2026-000001`.

### 7.4 Posting

The posting service must:

1. Lock the draft header and lines.
2. Re-read all values from the database.
3. Validate status, dates, master data, permissions, line rules, and balances.
4. Assign the next transaction number.
5. Stamp poster and posting time.
6. Change status to Posted.
7. Write the audit event.
8. Commit all changes together.

If any step fails, the database transaction is rolled back and the draft remains unposted.

### 7.5 Reversal

A reversal creates a new draft linked to the original transaction. It copies every original line with debit and credit exchanged. The user supplies reversal date and reason. After posting the reversal, the original status becomes Reversed. Reversing a reversal is prohibited; a new correcting entry is used instead.

### 7.6 Templates

The application will provide guided templates that still produce ordinary journal transactions:

- Cash receipt.
- Cash disbursement.
- Deposit comprising several receipts.
- Fund transfer.
- Restriction release.
- General journal/adjusting entry.
- Opening balances.

Templates may default accounts and fields but may not bypass posting validation.

## 8. Data model

All tables use InnoDB, integer `ID` primary keys for JSForm compatibility, foreign keys, timestamps, and `DECIMAL(19,4)` monetary columns. User-facing currency defaults to two decimal places, while four stored decimal places permit allocations and conversions without binary floating-point errors.

### 8.1 Core tables

| Table | Purpose | Important columns |
| --- | --- | --- |
| `tblAccountingOrganization` | Accounting settings | `ID`, `ChurchID`, `LegalName`, `FiscalYearStartMonth`, `BaseCurrency`, `ReportingBasis`, numbering settings |
| `tblAccountingAccount` | Chart of accounts | `ID`, `OrganizationID`, `Code`, `Name`, `AccountType`, `NormalBalance`, `PostingAllowed`, `StatementGroup`, `DisplayOrder`, flags, effective dates, `Active` |
| `tblAccountingFund` | Funds and restrictions | `ID`, `OrganizationID`, `Code`, `Name`, `NetAssetClass`, `RestrictionType`, `BoardDesignated`, restriction text, dates, `NetAssetAccountID`, `Active`, `ClosedDate` |
| `tblAccountingFunction` | Functional categories | `ID`, `OrganizationID`, `Code`, `Name`, `DisplayOrder`, `Active` |
| `tblAccountingFiscalYear` | Fiscal years | `ID`, `OrganizationID`, `Name`, `StartDate`, `EndDate`, `Status`, `ClosingTransactionID` |
| `tblAccountingFiscalPeriod` | Posting periods | `ID`, `FiscalYearID`, `PeriodNumber`, `Name`, `StartDate`, `EndDate`, `Status` |
| `tblAccountingTransaction` | Journal header | `ID`, `OrganizationID`, `TransactionNumber`, `TransactionDate`, `FiscalPeriodID`, `TransactionType`, `Status`, `Description`, `Reference`, original/reversal links, creator/reviewer/poster and timestamps |
| `tblAccountingTransactionLine` | Journal lines | `ID`, `TransactionID`, `LineNumber`, `AccountID`, `FundID`, `FunctionID`, `PayeeID`, `Description`, `Debit`, `Credit`, `ClearedState` |
| `tblAccountingPayee` | Vendors and other payees | `ID`, `OrganizationID`, `Name`, contact/reference data, `Active` |
| `tblAccountingAttachment` | Source-document metadata | `ID`, `TransactionID`, `StoredPath`, `OriginalName`, `DocumentType`, `FileHash`, `AddedBy`, `AddedAt` |
| `tblAccountingAuditEvent` | Append-only audit log | `ID`, `OrganizationID`, `EntityType`, `EntityID`, `Action`, `BeforeJSON`, `AfterJSON`, `Reason`, `UserID`, `OccurredAt` |

### 8.2 Budget tables

| Table | Purpose | Important columns |
| --- | --- | --- |
| `tblAccountingBudget` | Budget header | `ID`, `OrganizationID`, `FiscalYearID`, `Name`, `Version`, `Status`, approval data |
| `tblAccountingBudgetLine` | Budget amounts | `ID`, `BudgetID`, `FiscalPeriodID`, `AccountID`, `FundID`, `FunctionID`, `Amount`, `Note` |

Only one budget version may be designated Adopted for a fiscal year. Amendments create a new version or an auditable amendment; they never overwrite the originally adopted amounts.

### 8.3 Bank reconciliation tables

| Table | Purpose | Important columns |
| --- | --- | --- |
| `tblAccountingBankAccount` | Links a real bank account to a ledger account | `ID`, `OrganizationID`, `AccountID`, `Name`, masked account suffix, `Active` |
| `tblAccountingReconciliation` | Statement reconciliation header | `ID`, `BankAccountID`, `StatementDate`, `BeginningBalance`, `EndingBalance`, `Status`, preparer/reviewer and timestamps |
| `tblAccountingReconciliationItem` | Cleared transaction lines | `ID`, `ReconciliationID`, `TransactionLineID`, `ClearedAmount`, `ClearedDate` |

One transaction line may belong to at most one completed reconciliation. Completing a reconciliation locks its membership and figures. Corrections require reopening with authorization or creating the next period's reconciling entry.

### 8.4 Security tables

If ChurchManager does not yet provide reusable users and roles, add:

- `tblAccountingUserRole`.
- `tblAccountingRolePermission`.
- `tblAccountingApprovalRule`.

The accounting module must use a stable authenticated user identifier. A typed name is not sufficient for approval or audit attribution.

### 8.5 Database constraints and indexes

Required constraints include:

- Unique account code per organization.
- Unique fund code per organization.
- Unique function code per organization.
- Unique posted transaction number per organization.
- Unique line number per transaction.
- Nonnegative debit and credit values.
- Exactly one of debit or credit greater than zero.
- Valid foreign keys for all line dimensions.
- `BoardDesignated = 0` when net-asset class is With Donor Restrictions.
- Period start date not after end date.
- No overlapping fiscal periods within one organization.

Indexes must support transaction date, posting date, account, fund, function, payee, status, fiscal period, reference, and reconciliation queries.

Because database versions differ in their enforcement of `CHECK` constraints, critical accounting validation must also occur in the posting service. Direct database posting by ordinary application users is prohibited.

## 9. JSForm application design

### 9.1 Framework boundary

JSForm will provide:

- JSON-defined forms and responsive layout.
- Text, numeric, currency, date, combo, checklist, button, list, and data-view controls.
- Lookups and linked forms.
- Required-field and dirty-record behavior.
- MariaDB connectivity.
- Configuration access.
- LimeReport execution.

The following must be application services rather than ordinary JSForm record saves:

- Posting.
- Reversal.
- Period close/reopen.
- Year-end close/reopen.
- Reconciliation completion/reopen.
- Budget adoption/amendment.
- Attachment storage and hashing.
- Permission and approval checks.

### 9.2 Forms

| Form | Purpose | Special behavior |
| --- | --- | --- |
| `frmAccountingHome` | Dashboard and task entry | Shows open periods, drafts awaiting action, unreconciled accounts, and report shortcuts. |
| `frmAccountingAccount` | Chart-of-accounts maintenance | Prevents deletion after activity; conditionally requires function/payee settings. |
| `frmAccountingFund` | Fund/restriction maintenance | Validates net-asset class, designation, restriction dates, and default net-asset account. |
| `frmAccountingFunction` | Function maintenance | Simple active/inactive list. |
| `frmAccountingFiscalYear` | Year and period setup | Generates periods; close/reopen actions call services. |
| `frmAccountingTransaction` | Journal header and line editor | Parent header with line subform/data grid; live debit, credit, and per-fund difference display. |
| `frmAccountingTransactionList` | Search and review register | Filters by date, status, number, type, account, fund, payee, and amount. |
| `frmAccountingPostReview` | Posting confirmation | Read-only validation summary; Post button calls service. |
| `frmAccountingTransfer` | Guided fund transfer | Produces four or more balanced lines. |
| `frmAccountingRestrictionRelease` | Guided restriction release | Requires reason and supporting authority. |
| `frmAccountingPayee` | Payee maintenance | No bank credentials or tax IDs in MVP. |
| `frmAccountingBudget` | Budget header and lines | Period spread, copy, validation, approval, and adopted-version controls. |
| `frmAccountingBankAccount` | Bank-account mapping | Stores only descriptive name and masked suffix. |
| `frmAccountingReconciliation` | Bank reconciliation | Lists uncleared cash lines and calculates difference in real time. |
| `frmAccountingReports` | Report parameters | Date/period, fund, account, function, comparative, and detail options. |
| `frmAccountingAudit` | Audit inquiry | Read-only; filterable by user, action, date, and entity. |

### 9.3 Journal-entry screen

The transaction screen is the core workflow and must show:

- Header fields at the top.
- A line grid with account, fund, function, payee, description, debit, and credit.
- Debit total, credit total, and difference.
- A per-fund balance panel.
- Validation messages in plain language.
- Attachments and audit-history tabs or linked forms.
- Actions: Save Draft, Mark Ready, Return to Draft, Copy, Validate, Post, Reverse, Print, and Close according to status and permission.

Account and fund choices must be filtered to those active and effective on the transaction date. Function is required or prohibited according to the selected account. Debit and credit controls must clear the opposite value when the user enters an amount.

The screen may save a header and its lines as a draft through normal edit operations, but the final posting action must call the accounting posting service.

### 9.4 Menu integration

Add an Accounting menu to ChurchManager with:

- Dashboard.
- New Receipt.
- New Disbursement.
- New Transfer.
- General Journal.
- Transaction Register.
- Reconcile Bank Account.
- Budgets.
- Chart of Accounts.
- Funds and Restrictions.
- Fiscal Years and Periods.
- Reports.
- Accounting Administration.

Old financial prototype menu entries and deleted forms must not be restored.

## 10. Roles and permissions

The minimum roles are:

| Role | Typical permissions |
| --- | --- |
| Viewer | View posted transactions and reports. |
| Entry Clerk | Create and edit own drafts; attach documents; cannot post. |
| Treasurer | Create, review, and post; reconcile; run reports. |
| Approver | Approve transactions according to policy; cannot alter approved lines. |
| Accounting Administrator | Maintain accounts, funds, periods, roles, and settings; controlled reopen permissions. |
| Auditor | Read-only access to all accounting data and audit history. |

The system must support a policy in which the creator cannot approve or post the same transaction above a configurable amount. Permission checks are enforced in services, not merely by hiding buttons.

## 11. Audit and document controls

### 11.1 Audit events

The append-only audit log records at least:

- Draft creation and deletion.
- Status changes.
- Posting and reversal.
- Period and year close/reopen.
- Reconciliation completion/reopen.
- Master-record create/change/deactivate.
- Budget adoption and amendment.
- Permission and configuration changes.
- Attachment add/remove.

Audit events store the authenticated user, timestamp, action, affected record, reason where required, and before/after data when appropriate.

### 11.2 Attachments

The database stores attachment metadata and a cryptographic file hash. Files are stored in a configured protected directory outside the source tree and database-backup directory. Filenames are generated; original filenames are metadata only. The system must detect a missing or changed file when an attachment is opened or verified.

Allowed file types and size limits are configurable. Executable files are prohibited.

### 11.3 Backups

Before go-live, backup and restore procedures must be tested with accounting data and attachments. A successful backup command alone is insufficient; a test restore must demonstrate readable, balanced, reportable data.

## 12. Bank reconciliation

A reconciliation compares one cash ledger account with a bank statement.

Required workflow:

1. Select bank account and statement date.
2. Confirm prior completed ending balance as the new beginning balance.
3. Enter statement ending balance.
4. Display eligible posted cash-account lines through the statement date.
5. Mark cleared items and record cleared dates/amounts.
6. Display outstanding deposits, outstanding payments, ledger balance, statement balance, and reconciliation difference.
7. Require a zero difference before completion.
8. Record preparer and, if policy requires, reviewer.
9. Lock the completed reconciliation and produce a report.

Draft or reversed transactions are never eligible. A reversal and its original remain separately visible.

## 13. Budgeting

Budgets are entered by fiscal period, natural account, fund, and optional function. Revenue budgets are stored as positive planning amounts and expense budgets as positive planning amounts; report formulas interpret the account type so users do not enter credits as negative numbers.

Required capabilities:

- Annual amount spread evenly or by a configurable monthly pattern.
- Direct period editing.
- Copy from a prior budget version.
- Copy prior-year actuals into a draft budget.
- Validation against active posting accounts, funds, functions, and fiscal periods.
- Draft, Proposed, Adopted, and Superseded statuses.
- Adopted budget locking.
- Auditable amendments.

## 14. Reports

Reports will be registered through the existing ChurchManager/LimeReport catalog and rendered with LimeReport templates. Report queries must include only Posted transactions unless a report is explicitly labeled as a Draft/Workflow report.

### 14.1 Required reports

1. **General Ledger** — opening balance, dated activity, running balance, and closing balance by account, with fund/function filters.
2. **Trial Balance** — debit and credit balances by account; total debits must equal total credits.
3. **Statement of Financial Position** — assets, liabilities, net assets without donor restrictions, net assets with donor restrictions, and total net assets as of a date.
4. **Statement of Activities** — revenue, expenses, transfers/releases, and change in net assets for a period, split by restriction class with comparative options.
5. **Budget to Actual** — current period and year-to-date budget, actual, variance, and percentage by account/fund/function.
6. **Fund Balance Report** — beginning balance, revenue, expense, transfers, releases, and ending balance by fund.
7. **Functional Expense Report** — expenses by natural account and function.
8. **Transaction Register** — sortable transaction summary with drill-down/reference information.
9. **Journal Entry** — complete printable entry with lines, totals, approvals, reversal links, and attachments list.
10. **Bank Reconciliation** — statement figures, cleared items, outstanding items, and zero-difference proof.
11. **Audit Activity** — selected audit events by date, user, entity, and action.
12. **Period Close Checklist** — unposted drafts, unreconciled accounts, validation exceptions, and close status.

### 14.2 Reporting rules

- Every financial report displays organization, report title, period/as-of date, basis, generation timestamp, and filters.
- Reports show whole-dollar rounding only as presentation; underlying totals use stored precision.
- Comparative reports use the same account/fund mapping for all columns and flag mapping changes.
- Consolidated reports eliminate internal transfer-in and transfer-out accounts.
- Restricted and unrestricted net assets are never combined without also showing the separate classes.
- Empty or inactive accounts may be included through an explicit option.

## 15. Optional contribution subledger requirements

When individual contribution tracking is implemented, it will remain a subledger feeding balanced deposit transactions into the general ledger.

It must support:

- Contributor households and individuals without duplicating ChurchManager person data unnecessarily.
- Anonymous and loose offerings.
- Contribution batches and deposit reconciliation.
- Cash, check, electronic, and noncash contribution types.
- Fund/designation selection at receipt.
- Quid pro quo and intangible religious benefit fields.
- Corrected and reissued acknowledgment history.
- Annual statements and single-contribution acknowledgments.
- Restricted access distinct from general-ledger viewing.

The general ledger transaction must not reveal contributor identity in ordinary reports. Contribution detail is confidential and separately permissioned.

## 16. Security and privacy

- Database credentials are stored in the existing protected credential mechanism, not JSON forms, source code, or SQL scripts.
- All accounting connections use a least-privilege database account.
- Ordinary users cannot directly update Posted transactions or audit tables.
- Attachment paths are validated to remain within the configured attachment root.
- Reports containing contributor, payee, payroll-import, or bank details are permission restricted.
- Logs must not contain credentials, full bank account numbers, or confidential contribution detail.
- Session timeout and workstation locking remain operating-environment responsibilities but should be documented for deployment.

## 17. Migration and opening balances

The MVP migration path is opening balances, not conversion of historical prototype tables.

Required process:

1. Configure and approve the chart of accounts, funds, functions, fiscal year, and periods.
2. Choose a cutover date.
3. Prepare account and fund opening balances from approved external records.
4. Import or enter one balanced opening transaction by account and fund.
5. Reconcile bank accounts to statements as of cutover.
6. Compare statements of financial position and fund balances to the approved source.
7. Obtain treasurer/accountant signoff.
8. Preserve the source file, import result, and signoff as attachments/audit evidence.

Any future transaction-level migration requires a separate mapping, duplicate-detection, reconciliation, backup, and rollback specification.

## 18. Service architecture

Create an `accounting/` application package within ChurchManager, separate from JSForm itself. Suggested components are:

| Component | Responsibility |
| --- | --- |
| `models.py` | Typed transaction, line, validation, reconciliation, and budget data objects. |
| `repository.py` | Parameterized database reads/writes; no UI logic. |
| `validation.py` | Pure validation rules and readable error messages. |
| `posting_service.py` | Atomic posting, numbering, locking, and reversal. |
| `period_service.py` | Period/year close and reopen. |
| `reconciliation_service.py` | Reconciliation lifecycle. |
| `budget_service.py` | Budget validation, adoption, and amendment. |
| `attachment_service.py` | Safe storage, hashing, retrieval, and integrity checks. |
| `permissions.py` | Role, action, amount-threshold, and separation-of-duties decisions. |
| `report_queries.py` | Parameterized datasets for LimeReport. |

SQL must be parameterized. Existing framework code that constructs SQL strings must not be used to perform accounting posting or authorization-sensitive updates.

## 19. Validation messages

Errors must identify the transaction and line where possible and explain what the user can correct. Examples:

- `Line 3 must contain either a debit or a credit.`
- `Transaction is out of balance by $25.00.`
- `Building Fund is out of balance by $100.00.`
- `Account 6100 Utilities requires a functional classification.`
- `The March 2027 period is closed.`
- `This transaction was changed after you opened it. Reload before posting.`
- `You cannot approve a transaction you created under the current approval policy.`

Database exceptions must be logged safely and translated into nontechnical user messages without hiding the fact that posting failed.

## 20. Concurrency

Draft headers include a version number or update timestamp used for optimistic concurrency. An update fails if another user changed the draft after it was loaded. Posting obtains row locks on the transaction, its lines, the fiscal period, and the numbering record.

Two simultaneous posting attempts must never:

- Post the same draft twice.
- Assign the same transaction number.
- Partially save lines.
- Bypass a newly closed period.

## 21. Testing requirements

### 21.1 Unit tests

- Debit/credit line validation.
- Whole-transaction and per-fund balancing.
- Account/function/payee rules.
- Restriction/designation rules.
- Period selection and status rules.
- Permission and separation-of-duties rules.
- Report sign and balance formulas.
- Budget variance formulas.

### 21.2 Database integration tests

- Atomic successful posting.
- Rollback after failure at each posting stage.
- Concurrent numbering.
- Duplicate-post prevention.
- Immutable posted entries.
- Reversal linkage and amounts.
- Close/reopen controls.
- Foreign-key and uniqueness enforcement.
- Completed reconciliation locking.

### 21.3 End-to-end tests

- Record an offering deposit across two funds.
- Pay a utility bill from the General Fund.
- Transfer resources between funds.
- Release a satisfied donor restriction.
- Correct a posted entry by reversal and replacement.
- Reconcile a bank statement with outstanding items.
- Adopt a budget and run budget-to-actual.
- Close a month and reject a backdated posting.
- Close a fiscal year and verify opening net assets.
- Restore a backup and reproduce the trial balance and reports.

### 21.4 Invariant tests

For every test database state:

- Total posted debits equal total posted credits.
- Posted debits equal posted credits within every transaction and fund.
- No posted transaction contains an invalid or inactive-on-date dimension.
- No closed period contains a posting made without a recorded override or reopen event.
- Report totals reconcile to transaction lines.
- Assets equal liabilities plus net assets as of every tested date.

## 22. Acceptance criteria for MVP

The MVP is accepted only when all of the following are demonstrated:

1. A user can configure an organization, chart of accounts, funds, functions, and fiscal periods.
2. An entry clerk can create a balanced draft but cannot post it.
3. An authorized treasurer can review and post the draft atomically.
4. The system refuses an unbalanced transaction and identifies both overall and per-fund differences.
5. Posted entries cannot be edited or deleted through the application or ordinary database account.
6. A posted entry can be corrected only through a linked reversal and replacement.
7. Closed periods reject postings; authorized reopen actions are audited.
8. A bank account can be reconciled to zero and the completed reconciliation is locked.
9. An adopted budget can be compared to posted actuals.
10. Required reports agree with one another and with a known test ledger.
11. The statement of financial position balances.
12. Fund balances and donor-restriction classes remain distinct.
13. Two concurrent postings receive different transaction numbers and do not corrupt data.
14. Audit history identifies who created, reviewed, posted, reversed, closed, reopened, and configured records.
15. Backup plus attachments can be restored to a clean test environment and reproduce the same trial balance.
16. JSON forms pass schema/structure checks and are visually reviewed at supported window sizes.
17. LimeReport outputs are visually reviewed for clipping, pagination, grouping, totals, and filter labels.
18. No credentials or live financial data are committed to source control or test fixtures.

## 23. Delivery phases

### Phase 0 — Policy decisions and prototypes

- Confirm fiscal year, accounting basis, fund list, restriction policy, chart structure, approval thresholds, and report set.
- Build a test chart and sample transactions with no live data.
- Prototype the journal line grid and per-fund balance display in JSForm.
- Confirm that JSForm subform/data-grid behavior meets journal-entry needs; extend JSForm only where the capability is generally reusable.

### Phase 1 — Ledger foundation

- Core schema and migrations.
- Accounts, funds, functions, years, and periods.
- Draft journal entry.
- Posting service, reversal, audit, and permissions.
- Trial balance, general ledger, transaction register, and journal-entry printout.

### Phase 2 — Operational cash management

- Receipt, disbursement, deposit, transfer, and release templates.
- Payees and attachments.
- Bank accounts and reconciliation.
- Statement of financial position, statement of activities, fund balance, and close checklist.

### Phase 3 — Planning and close

- Budgets and budget-to-actual.
- Functional expense reporting.
- Period close, year-end close, and opening-balance workflow.
- Backup/restore certification and go-live checklist.

### Phase 4 — Optional subledgers

- Contributions and acknowledgments.
- Accounts payable/check workflow.
- Recurring entries, fixed assets, bank import, or payroll import as separately approved work.

## 24. Approved starter policies

ChurchManager is congregation-neutral. These are configurable starter defaults,
not assumptions about Life in Christ or any other specific congregation.

1. The fiscal year is January 1 through December 31.
2. Operational reporting uses modified cash basis while the double-entry ledger
   remains accrual-capable.
3. The starter account ranges are 1000-1999 Assets, 2000-2999 Liabilities,
   3000-3999 Net Assets, 4000-4999 Revenue, 5000-7999 Expenses, and 8000-8999
   Interfund Transfers and Other Activity.
4. The starter funds are General Operating, Operating Reserve, Building / Capital
   Projects, Missions / Outreach, Benevolence, Memorials / Special Gifts, and an
   optional inactive Endowment. General Operating begins without donor
   restrictions and Operating Reserve begins board-designated without donor
   restrictions. Every other special-purpose fund requires an explicit
   classification during setup; classification is never inferred from its name.
5. The starter functions are Worship, Christian Education, Outreach and
   Missions, Pastoral Care and Mercy, Fellowship, Management and General, and
   Fundraising. Congregations may rename, add, or deactivate them.
6. Transactions below $500 may be posted by an authorized Treasurer without a
   second user. Transactions of $500 or more normally require approval by a
   different authorized user. Reversals, restricted-fund releases, period
   reopening, and year-end closing also normally require independent approval.
   Each organization chooses either `INDEPENDENT_REQUIRED` or
   `INDEPENDENT_PREFERRED`. Under the preferred policy, an authorized solo
   operator may approve with a required written reason; the audit event and
   reports must identify the override. The threshold is configurable.
7. Every disbursement requires a source-document reference. A digital receipt,
   invoice, or voucher is required at $250 or more. An authorized exception must
   include an audited reason. The threshold is configurable.
8. The first release uses direct cash-disbursement entries. Full accounts payable
   is deferred.
9. Individual contribution tracking is deferred to a confidential subledger.
   The first release records summarized contribution deposits in the ledger.
10. Initial reports are actual-versus-budget for month and year to date,
    current-versus-prior year, statement of financial position, statement of
    activities, fund activity and balances, general ledger, trial balance,
    transaction register, and bank reconciliation summary. Reports support
    congregation-friendly and accountant-detail presentation where appropriate.
11. Posted ledger entries, reversals, audit history, annual statements, closing
    records, restriction and endowment records, and relevant property-basis
    records are permanent. Routine financial support records are retained for
    seven years after fiscal-year close. The first release never deletes records
    automatically; authorized disposition is documented and congregation policy,
    law, grant terms, insurance requirements, and legal holds may extend retention.
12. The initial deployment is a Windows desktop client with MariaDB/MySQL on the
    same computer or a congregation-controlled server. Attachments use a protected
    configurable folder outside source code. Backups include a local copy and an
    encrypted second copy on a different device or approved cloud service. Test
    databases and attachment folders remain separate. No server address, account,
    drive, or cloud provider is assumed.

These defaults do not change the core requirement for an immutable, balanced,
auditable double-entry ledger.

## 25. Authoritative references

- Financial Accounting Standards Board, Accounting Standards Update 2016-14, *Not-for-Profit Entities (Topic 958): Presentation of Financial Statements of Not-for-Profit Entities*.
- Internal Revenue Service, *Recordkeeping Requirements for Exempt Organizations*.
- Internal Revenue Service, Publication 1771, *Charitable Contributions—Substantiation and Disclosure Requirements* (for the optional contribution subledger).
- Internal Revenue Service, Publication 1828, *Tax Guide for Churches and Religious Organizations*.

These references establish reporting and recordkeeping context. The church's accountant, governing documents, adopted policies, donor instruments, grant terms, and applicable law remain authoritative for the church's particular accounting decisions.
