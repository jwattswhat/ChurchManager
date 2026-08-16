# ChurchManager Screen Inventory

Last reviewed: August 14, 2026

This is the maintained inventory of user-facing screens in ChurchManager and JSForm. Update this
table whenever a screen is added, replaced, retired, or changes ownership.

Status meanings:

- **Active**: reachable in the current application.
- **Supporting**: opened from another active screen.
- **Removed**: obsolete development definition was deleted after dependency review.
- **Verify visually**: structurally tested, but awaiting the user's current visual check.

## Current and removed development JSON screens

Active entries are ChurchManager definitions rendered by JSForm. Removed rows are retained here as development cleanup history.

| Screen | Development ownership | Status | Why ChurchManager-only? |
|---|---|---|---|
| `frmMain` | ChurchManager + JSForm | Active; visually approved | Not CM-only; JSForm renders the ChurchManager menu definition. |
| `frmChurch` | ChurchManager + JSForm | Active | Not CM-only; ordinary database form with CM-specific linked records. |
| `frmFamily` | ChurchManager + JSForm | Active | Not CM-only; JSForm supplies record editing and child forms. |
| `frmFamilyAddress` | ChurchManager + JSForm | Supporting | Not CM-only. |
| `frmFamilyContact` | ChurchManager + JSForm | Supporting | Not CM-only. |
| `frmFamilyDate` | ChurchManager + JSForm | Supporting | Not CM-only. |
| `frmPerson` | ChurchManager + JSForm | Active | Not CM-only; CM adds image handling. |
| `frmPersonAddress` | ChurchManager + JSForm | Supporting | Not CM-only. |
| `frmPersonContact` | ChurchManager + JSForm | Supporting | Not CM-only. |
| `frmPersonDate` | ChurchManager + JSForm | Supporting | Not CM-only. |
| `frmAttendanceEvent` | ChurchManager + JSForm | Compatibility only | Replaced in ordinary use by the combined Attendance screen. |
| `frmAttendance` | ChurchManager + JSForm | Compatibility only | Direct row maintenance bypasses attendance synchronization rules. |
| `frmRecordAttendance` | ChurchManager + JSForm | Retired | Insert-only entry was replaced by the combined Attendance screen. |
| Attendance | ChurchManager only | Active | Transactionally coordinates event metadata, hand counts, known-person attendance, Communion validation, searching, and service-derived locking. |
| `frmDocument` | ChurchManager + JSForm | Active | Not CM-only. |
| `frmJournal` | ChurchManager + JSForm | Active | Not CM-only. |
| `frmProject` | ChurchManager + JSForm | Active | Not CM-only. |
| `frmTask` | ChurchManager + JSForm | Active | Not CM-only. |
| `frmTaskWorker` | ChurchManager + JSForm | Supporting | Not CM-only. |
| `frmOptions` | ChurchManager + JSForm | Active | Not CM-only. |
| `frmHymnal` | ChurchManager + JSForm | Active | Not CM-only. |
| `frmHymn` | ChurchManager + JSForm | Active | Not CM-only; CM adds hymn refresh behavior. |
| `frmLectionarySystem` | ChurchManager + JSForm | Supporting | Not CM-only. |
| `frmPropers` | ChurchManager + JSForm | Active | Not CM-only. |
| `frmProperHymnSuggestion` | ChurchManager + JSForm | Supporting | Not CM-only; CM refreshes the parent Propers screen. |
| `frmSermon` | ChurchManager + JSForm | Active | Not CM-only. |
| `frmReports` | ChurchManager + JSForm | Active | Not CM-only; JSForm renders the picker and CM securely runs reports. |
| `frmNotifyviaeMail` | ChurchManager + JSForm | Active | Not CM-only; CM supplies the notification action. |
| `frmAccountingAccount` | ChurchManager + JSForm | Supporting | Not CM-only; opened by Accounting Setup. |
| `frmAccountingBankAccount` | ChurchManager + JSForm | Supporting | Not CM-only; opened by Accounting Setup. |
| `frmAccountingFiscalPeriod` | ChurchManager + JSForm | Supporting | Not CM-only; opened by Accounting Setup. |
| `frmAccountingFiscalYear` | ChurchManager + JSForm | Supporting | Not CM-only; opened by Accounting Setup. |
| `frmAccountingFunction` | ChurchManager + JSForm | Supporting | Not CM-only; opened by Accounting Setup. |
| `frmAccountingFund` | ChurchManager + JSForm | Supporting | Not CM-only; opened by Accounting Setup. |
| `frmAccountingPayee` | ChurchManager + JSForm | Supporting | Not CM-only; opened by Accounting Setup. |
| `frmAltReading` | ChurchManager + JSForm | Removed from development | Not CM-only; alternate readings were removed from the current workflow. |
| `frmAnnouncementKiosk` | ChurchManager + JSForm | Removed from development | Not CM-only. |
| `frmAsset` | ChurchManager + JSForm | Removed from development | Not CM-only. |
| `frmChecklist` | ChurchManager + JSForm | Removed from development | Not CM-only; replaced by native checklist maintenance. |
| `frmchoices` | ChurchManager + JSForm | Removed from development | Not CM-only; replaced by JSForm Choice Manager. |
| `frmEditCheckList` | ChurchManager + JSForm | Removed from development | Not CM-only; replaced by native preparation checklist. |
| `frmGenerateOS` | ChurchManager + JSForm | Removed from development | Not CM-only; replaced by unified worship planning. |
| `frmGenerateWorshipPlanning` | ChurchManager + JSForm | Removed from development | Not CM-only; replaced by unified worship planning. |
| `frmHymnHistory` | ChurchManager + JSForm | Removed from development | Not CM-only. |
| `frmHymnSearch` | ChurchManager + JSForm | Removed from development | Not CM-only; replaced by the native hymn picker. |
| `frmHymnUsage` | ChurchManager + JSForm | Removed from development | Not CM-only; usage is handled by the unified workflow. |
| `frmHymnUsageDisplay` | ChurchManager + JSForm | Removed from development | Not CM-only. |
| `frmMembershipMain` | ChurchManager + JSForm | Removed from development | Not CM-only; old container screen. |
| `frmNote` | ChurchManager + JSForm | Removed from development | Not CM-only. |
| `frmOpenMembership` | ChurchManager + JSForm | Removed from development | Not CM-only; old menu/container screen. |
| `frmOpenWorship` | ChurchManager + JSForm | Removed from development | Not CM-only; old menu/container screen. |
| `frmPersonDateGrid` | ChurchManager + JSForm | Removed from development | Not CM-only. |
| `frmReading` | ChurchManager + JSForm | Removed from development | Not CM-only; current Propers workflow owns readings. |
| `frmReadingList` | ChurchManager + JSForm | Removed from development | Not CM-only. |
| `frmSchedule` | ChurchManager + JSForm | Removed from development | Not CM-only; replaced by native schedule-pattern management. |
| `frmService` | ChurchManager + JSForm | Removed from development | Not CM-only; replaced by unified Worship Service editor. |
| `frmServiceSchedule` | ChurchManager + JSForm | Removed from development | Not CM-only; replaced by native Service Participants. |

## ChurchManager-only workflow screens

These are handwritten wxPython screens. JSForm still supplies shared database
and application infrastructure where appropriate, but it does not construct
these screen layouts. The replacement column identifies retired JSForm-era screens or behavior within development.

| Screen or screen family | Replaces old JSForm screen | Status | Why ChurchManager-only? |
|---|---|---|---|
| Worship Services list | None | Active | Fast service picker, protected deletion, weekly-order status, and creation/discard workflow. |
| Unified Worship Service editor | Retired `frmService` | Active | Coordinates service fields, template application, Propers, hymns, participants, checklist, duplicate checks, and one transactional save. |
| Hymn Picker | Retired `frmHymnSearch` | Supporting | Search/sort, selected-hymnal filtering, tune data, and duplicate-hymn warnings require service context. |
| Read-only Propers display | None | Supporting | Presents the selected Proper inside the service workflow without allowing accidental changes. |
| Bulletin Order Templates | Retired `frmOS`/`frmOSList` | Active | Maintains protected starters, custom copies, ordered lines, hymnal association, and required positions. |
| Bulletin Order Line editor | Retired `frmOS` | Supporting | Edits typed and conditional ordered content belonging to a template. |
| Weekly Order of Service | Retired generated OS screens | Active | Creates the service-specific outline and applies readings and hymns while preserving overrides. |
| Weekly Line editor | None | Supporting | Edits one service-specific outline line with contextual validation. |
| Weekly Worship Plan | Retired `frmGenerateWorshipPlanning` | Supporting | Combines the saved outline with service-specific planning state. |
| Prepare Bulletin Order | Retired generation screen | Active | Generates plain-text or formatted outline output from resolved weekly data. |
| Participants manager/editor | Retired `frmParticipant` | Active | Supports members and nonmembers, contact data, active status, and multiple roles. |
| Roles/Positions manager | None | Active | Enforces protected-in-use roles and manages user-defined positions. |
| Schedule Patterns manager/editor | Retired `frmSchedule` | Active | Handles recurring assignments and role eligibility. |
| Service Participants and Assignment editor | Retired `frmServiceSchedule` | Active | Shows required positions, permits multiple assignments, and evaluates fulfillment for a specific service. |
| Required Positions | None | Supporting | Edits role counts attached to a specific Order of Service template. |
| Preparation Checklist | Retired checklist forms | Active | Combines automatic hymn/participant checks with manual, not-needed, and one-time tasks. |
| Checklist Maintenance and Task editor | Retired checklist forms | Active | Maintains reusable tasks while protecting historical service results. |
| Prayers manager/editor | Retired `frmPrayer` | Active | Natural recurrence rules, categories, active dates, and weekly service applicability exceed a simple record form. |
| Announcements manager/editor | Retired `frmAnnouncement` | Active | Same recurrence and weekly-preview requirements as Prayers. |
| Schedule Rule editor | None | Supporting | Edits structured recurrence rules and produces readable schedule descriptions. |
| Sunday Content Preview | None | Supporting | Evaluates rules for a week before generating prayer or announcement output. |
| Login and Initial Master User | None | Active | Authentication, password hashing, lockout, initialization, and audit behavior must not be editable form metadata. |
| Change Password | None | Active | Requires secure verification, hashing, and test/production password policies. |
| User Administration and New User | None | Active | Coordinates users, roles, status, password reset, and contact information securely. |
| Role Permissions | None | Supporting | Edits security grants with authorization and audit enforcement. |
| Security Audit | None | Supporting | Read-only protected security history. |
| Backup and Restore | None | Active; backup and temporary-clone restore verified 2026-08-14 | Runs external database tools, validates database identity, creates pre-restore backups, and requires protected confirmations. |
| Support and Diagnostics | None | Active; structural tests passed | Creates a local privacy-safe diagnostic package from JSForm error logs without transmitting it or exposing ChurchManager records. |
| Accounting Setup | None | Active | Launches and coordinates the seven JSForm accounting master-data forms. |
| Transaction Entry and Draft List | None | Active | Owns balanced transaction editing, concurrency, guided workflows, attachments, and state transitions. |
| Transaction Line editor | None | Supporting | Enforces debit/credit semantics and accounting dimensions in transaction context. |
| Guided Cash, Transfer, and Deposit | None | Supporting | Converts small-church workflows into balanced accounting entries. |
| Deposit Receipt and Attachment manager | None | Supporting | Manages transaction evidence and receipt allocation. |
| Transaction Review | None | Active | Applies approval policy, solo override rules, reasons, and auditing. |
| Transaction Posting | None | Active | Performs atomic posting with period, approval, balance, and concurrency protections. |
| Posted Register, Reversal, and Journal Entry | None | Active | Coordinates immutable history, controlled reversals, and report-driven navigation. |
| Bank File Import and Staged Activity | None | Active | Parses external files and maintains staged bank data. |
| Bank Matching and Reconciliation | None | Active | Requires contextual matching, uniqueness, date/amount logic, and protected completion. |
| Trial Balance | None | Active | Interactive report filters, secure data service, PDF preview, and customizable layout. |
| General Ledger | None | Active | Interactive account/fund/date filtering plus visual-report output. |
| Financial Position | None | Active | Accounting-specific classification, totals, and secure reporting. |
| Statement of Activities | None | Active | Accounting-specific activity aggregation and reporting. |
| Fund Balances | None | Active | Fund restrictions and balance calculations require accounting services. |
| Reconciliation Report | None | Active | Produces reconciliation-specific balances and detail. |
| Budgets and Budget Line editor | None | Active | Handles draft/proposed/adopted states, amendments, periods, detail modes, and deletion rules. |
| Budget to Actual | None | Active | Supports both general-account and detailed-line reporting. |
| Functional Expenses | None | Active | Cross-classifies expenses by function for reporting. |
| Accounting Audit History | None | Active | Protected, confidential inspection of accounting audit events. |
| Close Checklist | None | Active | Evaluates accounting close prerequisites and controlled overrides. |
| Year-End Close | None | Active | Performs preview, close, reopening, synthetic entries, and audit-controlled recovery. |

## JSForm-owned screens used by ChurchManager

| Screen or family | ChurchManager integration | Status | Why ChurchManager-only? |
|---|---|---|---|
| Choice Manager and Choice editor | CM supplies allowed choice categories | Active | Not CM-only; reusable JSForm facility. |
| Report Catalog | CM supplies report starters and custom directory | Active | Not CM-only. |
| Visual Report Designer | CM supplies approved datasets, permissions, starters, and audit hook | Active | Not CM-only; core designer belongs to JSForm. |
| Report Preview | CM supplies report data | Active | Not CM-only. |
| Page Setup, Repeating Columns, Sort, Group, and Totals dialogs | Used by CM reports | Supporting | Not CM-only; reusable report-design tools. |
| Screen Catalog | CM supplies screen starter/custom directories | Active | Not CM-only. |
| Visual Screen Designer and Preview | CM supplies permissions, starters, and audit hook | Active | Not CM-only; core designer belongs to JSForm. |
| Form Size dialog | Used by CM screen designer | Supporting | Not CM-only. |
| Dirty-record, required-field, and database credential dialogs | Used by CM forms | Supporting | Not CM-only; reusable framework behavior. |

## Maintenance rule

When changing a screen:

1. Update its status and ownership here.
2. Explain why any new handwritten ChurchManager-only screen cannot reasonably
   be expressed as a reusable JSForm capability.
3. Remove obsolete definitions from development only after checking their dependencies.
4. Distinguish automated structural validation from user-confirmed visual QA.
