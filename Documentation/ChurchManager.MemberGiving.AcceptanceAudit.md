# ChurchManager Member Giving Acceptance Audit

**Audit date:** August 22, 2026  
**Application version:** 0.3.0-dev  
**Specification:** [Member giving and envelope tracking specification](ChurchManager.MemberGiving.Specification.md)  
**Audit result:** Operational foundation accepted; full specification not yet complete

## Executive result

The implemented Giving subsystem is suitable for continued guarded beta
development. Its contributor, envelope, approved-purpose, batch-entry,
accounting-handoff, posted-correction, CSV-import, statement, and envelope-box
workflows are real rather than prototypes. The current automated suite passes
778 tests with 25 intentional skips, and the user has visually accepted the
implemented Giving screens and reports exercised during development.

It is not yet accurate to call the entire approved Member Giving specification
complete. Several first-release workflows and reports remain unimplemented,
but authorization is now enforced independently at screen, report-provider,
service, and repository boundaries. The remaining incomplete workflows,
reports, and privacy acceptance remain release gates.

## Audited implementation inventory

| Area | Result | Evidence and limits |
| --- | --- | --- |
| Database foundation | Pass for current scope | Migrations 085-092 provide contributors, dated envelopes, purposes, batches, gifts, allocations, safe audits, statement issuance, accounting dimensions, corrections, import evidence, zero-value non-cash purpose classification, and optional unverified donor estimates. The installation baseline must be regenerated after migrations 091-092 are accepted. |
| Contributor identities | Pass for basic workflow | Person, family, and external identities are supported; statement identity and dated envelope history are maintained. Duplicate merge and explicit directory-contact refresh are not implemented. |
| Envelope assignments | Pass | Date-effective assignment, overlap validation, canonical numeric comparison, annual resequencing/keep-current preview, labels, and register are implemented and visually accepted. |
| Approved purposes | Pass for basic workflow | Approval facts, control-and-discretion confirmation, effective dates, and accounting mappings are stored and maintained. |
| Draft batch entry | Pass for monetary and non-cash gifts | Anonymous gifts, contributor/envelope resolution, split allocations, description-only donated property, optional unverified donor estimates, control totals, editing, deletion, fiscal-period guidance, and Ready-to-Draft recovery are implemented. ChurchManager never assigns donated-property value, and donor estimates are excluded from accounting and statements. |
| Accounting handoff | Pass | A privacy-safe summarized transaction is created, posting state is synchronized, and donor/envelope identity is excluded from the ledger handoff. |
| Posted corrections | Pass structurally; visual acceptance pending | The original batch becomes Void only after the linked reversal posts, the replacement remains linked, and the returned-check action omits only the returned check from its replacement. |
| CSV import | Pass | Mapping, non-writing preview, row validation, duplicate-file prevention, protected evidence, Draft creation, and reset cleanup are implemented and accepted. |
| Statements | Pass for current scope | One/all contributor quarterly, annual, and custom-period PDFs plus issuance hash and revision history are implemented. Non-cash property is described without a printed value and excluded from monetary totals. Goods/services, intangible-benefit, statement-review, and memorial/honor facts are retained. |
| Reports | Partial | Batch Control Summary, Contribution Statement, Envelope Box Labels, Envelope Assignment Register, and protected Memorial and Honor Gift Acknowledgment List are implemented. The complete required inventory is not. |
| Backup and reset | Pass for current scope | Whole-database backup/restore includes Giving. The fictitious Giving reset covers current tables and removes protected test import evidence only after database commit. |
| Documentation and inventories | Partial, corrected by this audit | User, treasurer, database, and screen documentation cover current workflows. Final report/privacy documentation remains open with the missing functionality. An obsolete testing-procedure statement that said Giving was removed was corrected during this audit. |

## Acceptance criteria status

| # | Criterion | Status | Finding |
| --- | --- | --- | --- |
| 1 | Person, family, and outside contributors | Pass | Supported by the contributor workflow and link validation. |
| 2 | Date-effective, non-overlapping envelopes | Pass | Service validation and annual assignment workflow cover this. |
| 3 | Anonymous offerings without fabricated people | Pass | Draft entry permits an anonymous contributor. |
| 4 | Split gifts balance exactly | Pass | Allocation validation requires exact totals. |
| 5 | Controlled batch creates one balanced summary transaction | Pass | Implemented and exercised through accounting handoff. |
| 6 | No donor identity in accounting | Pass for implemented handoff | The summarized transaction carries batch/accounting dimensions, not donor or envelope data. |
| 7 | Posted history immutable with correction chain | Pass for current correction workflow | Reversal/replacement linkage and status synchronization are implemented. |
| 8 | Returned check reconciles Giving and accounting | Pass structurally; visual acceptance pending | The protected return record links the original gift and batch, replacement batch, summarized accounting reversal, date, reason, and statement result. |
| 9 | Unauthorized users cannot invoke services or reports | Pass | Menus, dialogs, report providers, repositories, and services independently require the applicable Giving permission. Direct-invocation denial tests fail closed before database or storage access. |
| 10 | Complete statement content and selection behavior | Pass for current scope | Contributor/date selection, eligible posted gifts, benefit wording, issuance hashes, revisions, acknowledgment facts, and description-only non-cash presentation are implemented. Non-cash values remain blank and outside monetary totals. |
| 11 | Privacy-safe memorial/honor acknowledgments | Pass | The protected Posted-gift acknowledgment list includes the donor and amount only when their separate disclosure flags explicitly authorize each value. |
| 12 | Imports detect mappings and duplicates before writes | Pass | Preview is non-writing; confirmed import creates a new Draft batch and records evidence. |
| 13 | Named-person directed gifts are held and clarified | Pass structurally; visual acceptance pending | Entry records instruction, disposition and resolution; completed reviews capture user/time; returned directions are excluded from deposit, ledger and statements; the protected review PDF is implemented. |
| 14 | Backup/restore preserves Giving | Pass structurally | Giving is in the complete database baseline and backup. A dedicated post-migration Giving restore rehearsal should be retained as release evidence. |
| 15 | Support logs exclude confidential detail | Partial; manual security review required | Giving audits are intentionally minimal. A focused redaction test for exception paths and support bundles is still needed. |
| 16 | Automated and rendered acceptance | Partial | Current suite and visually exercised surfaces pass; missing workflows and reports prevent full-specification sign-off. |

## Required report inventory audit

| Required output | Status |
| --- | --- |
| Envelope Assignment Register | Implemented |
| Unassigned and Conflicting Envelopes | Missing |
| Envelope Box Labels | Implemented |
| Contribution Batch Detail | Available interactively; dedicated printable detail is missing |
| Contribution Batch Control Summary | Implemented |
| Giving by Fund and Period, donor-free | Missing |
| Contributor History | Implemented interactively; dedicated printable output is missing |
| Single/all Contribution Statements | Implemented |
| Statement Exception List | Missing |
| Accounting Posting Reconciliation | Missing |
| Memorial and Honor Gift Acknowledgment List | Implemented |
| Directed Gift Review List | Implemented; visual acceptance pending |

## Prioritized remaining work

1. **Add the missing protected reports.** Start with donor-free Giving by Fund
   and Period and Accounting Posting Reconciliation, followed by exceptions,
   directed gifts and printable confidential histories.
2. **Complete contributor administration.** Add guarded duplicate merge and an
   explicit previewed refresh from linked person/family contact data.
3. **Perform privacy-focused acceptance.** Force errors containing check,
   contributor, address, and imported-row values and verify support logs and
   bundles redact them. Rehearse backup/restore with the full Giving schema.
4. **Run final rendered and user acceptance.** Exercise every criterion with the
   fictitious dataset, inspect each protected PDF, update the inventories, and
   record release sign-off.

## Release decision

Continue beta development. Do not represent Member Giving as fully complete or
remove its beta qualification until the required special-gift workflows,
required reports, privacy tests, and final acceptance run are complete.
