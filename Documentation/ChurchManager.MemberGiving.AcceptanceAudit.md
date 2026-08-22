# ChurchManager Member Giving Acceptance Audit

**Audit date:** August 22, 2026  
**Application version:** 0.3.0-dev  
**Specification:** [Member giving and envelope tracking specification](ChurchManager.MemberGiving.Specification.md)  
**Audit result:** Accepted for the first-release beta scope

## Executive result

The implemented Giving subsystem is suitable for continued guarded beta
development. Its contributor, envelope, approved-purpose, batch-entry,
accounting-handoff, posted-correction, CSV-import, statement, and envelope-box
workflows are real rather than prototypes. Focused automated acceptance passes,
and the user has visually accepted the Giving screens and reports exercised
during development.

The approved first-release functionality is implemented and accepted, with
authorization enforced independently at screen, report-provider, service, and
repository boundaries. Migrations, installation baseline, confidential-data
restore rehearsal, the full automated suite, and rendered inspection of the
protected reports have passed.

## Audited implementation inventory

| Area | Result | Evidence and limits |
| --- | --- | --- |
| Database foundation | Pass for current scope | Migrations 085-095 provide contributors, dated envelopes, purposes, batches, gifts, allocations, safe audits, statement issuance, accounting dimensions, corrections, import evidence, directed-gift review, returned-check evidence, and contributor-merge provenance. The installation baseline represents all 95 migrations. |
| Contributor identities | Pass | Person, family, and external identities are supported; statement identity and dated envelope history are maintained. Directory contact refresh is previewed, and duplicate merge is guarded against envelope and statement-history collisions. |
| Envelope assignments | Pass | Date-effective assignment, overlap validation, canonical numeric comparison, annual resequencing/keep-current preview, labels, and register are implemented and visually accepted. |
| Approved purposes | Pass for basic workflow | Approval facts, control-and-discretion confirmation, effective dates, and accounting mappings are stored and maintained. |
| Draft batch entry | Pass for monetary and non-cash gifts | Anonymous gifts, contributor/envelope resolution, split allocations, description-only donated property, optional unverified donor estimates, control totals, editing, deletion, fiscal-period guidance, and Ready-to-Draft recovery are implemented. ChurchManager never assigns donated-property value, and donor estimates are excluded from accounting and statements. |
| Accounting handoff | Pass | A privacy-safe summarized transaction is created, posting state is synchronized, and donor/envelope identity is excluded from the ledger handoff. |
| Posted corrections | Pass | The original batch becomes Void only after the linked reversal posts, the replacement remains linked, and the returned-check action omits only the returned check from its replacement. |
| CSV import | Pass | Mapping, non-writing preview, row validation, duplicate-file prevention, protected evidence, Draft creation, and reset cleanup are implemented and accepted. |
| Statements | Pass for current scope | One/all contributor quarterly, annual, and custom-period PDFs plus issuance hash and revision history are implemented. Non-cash property is described without a printed value and excluded from monetary totals. Goods/services, intangible-benefit, statement-review, and memorial/honor facts are retained. |
| Reports | Pass | The protected inventory includes controls, detail, donor-free fund totals, printable history, statement exceptions, reconciliation, envelope exceptions, memorial/honor acknowledgments, and directed-gift review. |
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
| 8 | Returned check reconciles Giving and accounting | Pass | The protected return record links the original gift and batch, replacement batch, summarized accounting reversal, date, reason, and statement result. |
| 9 | Unauthorized users cannot invoke services or reports | Pass | Menus, dialogs, report providers, repositories, and services independently require the applicable Giving permission. Direct-invocation denial tests fail closed before database or storage access. |
| 10 | Complete statement content and selection behavior | Pass for current scope | Contributor/date selection, eligible posted gifts, benefit wording, issuance hashes, revisions, acknowledgment facts, and description-only non-cash presentation are implemented. Non-cash values remain blank and outside monetary totals. |
| 11 | Privacy-safe memorial/honor acknowledgments | Pass | The protected Posted-gift acknowledgment list includes the donor and amount only when their separate disclosure flags explicitly authorize each value. |
| 12 | Imports detect mappings and duplicates before writes | Pass | Preview is non-writing; confirmed import creates a new Draft batch and records evidence. |
| 13 | Named-person directed gifts are held and clarified | Pass | Entry records instruction, disposition and resolution; completed reviews capture user/time; returned directions are excluded from deposit, ledger and statements; the protected review PDF is implemented. |
| 14 | Backup/restore preserves Giving | Pass | The isolated restore rehearsal created, backed up, deleted, restored, and verified a fictitious confidential contributor and envelope alongside the canonical 95-migration ledger on August 22, 2026. |
| 15 | Support logs exclude confidential detail | Pass (automated) | Forced Giving errors verify that contributor, check/reference, envelope, address, and imported-row values are removed from both the local error log and generated support ZIP. |
| 16 | Automated and rendered acceptance | Pass | The 794-test post-baseline suite passed with 25 intentional skips and no failures. The protected Giving screens and operational PDFs passed user visual acceptance on August 22, 2026. |

## Required report inventory audit

| Required output | Status |
| --- | --- |
| Envelope Assignment Register | Accepted |
| Unassigned and Conflicting Envelopes | Accepted |
| Envelope Box Labels | Accepted |
| Contribution Batch Detail | Accepted |
| Contribution Batch Control Summary | Accepted |
| Giving by Fund and Period, donor-free | Accepted |
| Contributor History | Interactive and printable; accepted |
| Single/all Contribution Statements | Accepted |
| Statement Exception List | Accepted |
| Accounting Posting Reconciliation | Accepted |
| Memorial and Honor Gift Acknowledgment List | Accepted |
| Directed Gift Review List | Accepted |

## Release decision

The first-release Giving scope is accepted for beta. Pledges, provider-hosted
online giving, and statement email delivery remain explicitly deferred rather
than incomplete first-release requirements.
