# ChurchManager Member Giving Acceptance Audit

**Audit date:** August 22, 2026  
**Application version:** 0.3.0-dev  
**Specification:** [Member giving and envelope tracking specification](ChurchManager.MemberGiving.Specification.md)  
**Audit result:** First-release implementation complete; final acceptance pending

## Executive result

The implemented Giving subsystem is suitable for continued guarded beta
development. Its contributor, envelope, approved-purpose, batch-entry,
accounting-handoff, posted-correction, CSV-import, statement, and envelope-box
workflows are real rather than prototypes. Focused automated acceptance passes,
and the user has visually accepted the Giving screens and reports exercised
during development.

The approved first-release functionality is structurally implemented, with
authorization enforced independently at screen, report-provider, service, and
repository boundaries. Applying the last migrations, regenerating the
installation baseline, backup/restore rehearsal, full-suite acceptance, and
rendered inspection of the newest reports remain release gates.

## Audited implementation inventory

| Area | Result | Evidence and limits |
| --- | --- | --- |
| Database foundation | Pass for current scope | Migrations 085-095 provide contributors, dated envelopes, purposes, batches, gifts, allocations, safe audits, statement issuance, accounting dimensions, corrections, import evidence, directed-gift review, returned-check evidence, and contributor-merge provenance. The installation baseline must be regenerated after migrations 094-095 are accepted. |
| Contributor identities | Pass structurally; visual acceptance pending | Person, family, and external identities are supported; statement identity and dated envelope history are maintained. Directory contact refresh is previewed, and duplicate merge is guarded against envelope and statement-history collisions. |
| Envelope assignments | Pass | Date-effective assignment, overlap validation, canonical numeric comparison, annual resequencing/keep-current preview, labels, and register are implemented and visually accepted. |
| Approved purposes | Pass for basic workflow | Approval facts, control-and-discretion confirmation, effective dates, and accounting mappings are stored and maintained. |
| Draft batch entry | Pass for monetary and non-cash gifts | Anonymous gifts, contributor/envelope resolution, split allocations, description-only donated property, optional unverified donor estimates, control totals, editing, deletion, fiscal-period guidance, and Ready-to-Draft recovery are implemented. ChurchManager never assigns donated-property value, and donor estimates are excluded from accounting and statements. |
| Accounting handoff | Pass | A privacy-safe summarized transaction is created, posting state is synchronized, and donor/envelope identity is excluded from the ledger handoff. |
| Posted corrections | Pass structurally; visual acceptance pending | The original batch becomes Void only after the linked reversal posts, the replacement remains linked, and the returned-check action omits only the returned check from its replacement. |
| CSV import | Pass | Mapping, non-writing preview, row validation, duplicate-file prevention, protected evidence, Draft creation, and reset cleanup are implemented and accepted. |
| Statements | Pass for current scope | One/all contributor quarterly, annual, and custom-period PDFs plus issuance hash and revision history are implemented. Non-cash property is described without a printed value and excluded from monetary totals. Goods/services, intangible-benefit, statement-review, and memorial/honor facts are retained. |
| Reports | Pass structurally; rendered acceptance pending | The protected inventory includes controls, detail, donor-free fund totals, printable history, statement exceptions, reconciliation, envelope exceptions, memorial/honor acknowledgments, and directed-gift review. |
| Backup and reset | Pass for current scope | Whole-database backup/restore includes Giving. The fictitious Giving reset covers current tables and removes protected test import evidence only after database commit. |
| Documentation and inventories | Pass for current behavior | The user guide and acceptance inventory cover the current workflows, reports, privacy behavior, and remaining release acceptance. |

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
| 14 | Backup/restore preserves Giving | Pass structurally; live rehearsal pending | The isolated restore rehearsal now creates, backs up, deletes, restores, and verifies a fictitious confidential contributor and envelope alongside the canonical migration ledger. |
| 15 | Support logs exclude confidential detail | Pass (automated) | Forced Giving errors verify that contributor, check/reference, envelope, address, and imported-row values are removed from both the local error log and generated support ZIP. |
| 16 | Automated and rendered acceptance | Partial | Focused checks pass and previously exercised surfaces are accepted; the newest administration actions and operational PDFs still require visual acceptance, followed by the full post-baseline suite. |

## Required report inventory audit

| Required output | Status |
| --- | --- |
| Envelope Assignment Register | Implemented |
| Unassigned and Conflicting Envelopes | Implemented; visual acceptance pending |
| Envelope Box Labels | Implemented |
| Contribution Batch Detail | Implemented; visual acceptance pending |
| Contribution Batch Control Summary | Implemented |
| Giving by Fund and Period, donor-free | Implemented; visual acceptance pending |
| Contributor History | Interactive and printable; visual acceptance pending |
| Single/all Contribution Statements | Implemented |
| Statement Exception List | Implemented; visual acceptance pending |
| Accounting Posting Reconciliation | Implemented; visual acceptance pending |
| Memorial and Honor Gift Acknowledgment List | Implemented |
| Directed Gift Review List | Implemented; visual acceptance pending |

## Prioritized remaining work

1. **Rehearse backup and restore.** Run the isolated post-migration rehearsal
   and retain its evidence that confidential Giving records survive restore.
2. **Run final rendered and user acceptance.** Exercise every criterion with the
   fictitious dataset, inspect each protected PDF, update the inventories, and
   record release sign-off.

## Release decision

Continue beta development. The first-release Giving implementation is complete,
but retain its beta qualification until the last migrations, installation
baseline, restore rehearsal, full suite, and rendered acceptance are complete.
