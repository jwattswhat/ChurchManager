# ChurchManager member giving and envelope tracking specification

**Status:** Approved

**Version:** 1.0

**Date:** August 18, 2026

**Approved by:** Rev. Jonathan C. Watt

**Implementation audit:** [Member Giving acceptance audit](ChurchManager.MemberGiving.AcceptanceAudit.md), August 22, 2026

**Target application:** Development ChurchManager

**Treasurer guidance:** [ChurchManager congregation treasurer guide](ChurchManager.CongregationTreasurerGuide.md)

## 1. Purpose

ChurchManager will provide a confidential contribution subledger for small
congregations. It will record envelope and other gifts by contributor, preserve
the fund or designation selected by the giver, assist with deposit control, and
produce contribution histories and donor statements.

The subsystem is not a replacement for the general ledger. It supplies a
summarized, balanced deposit transaction to the existing fund-accounting module
without exposing contributor identity in ordinary accounting screens or
reports.

## 2. Design boundaries

1. Contribution detail is confidential and receives permissions separate from
   membership and ordinary accounting access.
2. A contributor is a stable giving identity. An envelope number is only a
   dated assignment and is never the contributor's primary key.
3. A contributor may represent a person, a family, or an outside donor who has
   no congregation person record.
4. Loose or anonymous offerings are supported without creating a fictitious
   member.
5. Posted contribution history is corrected, not silently edited or deleted.
6. Donor identity and envelope number do not appear in the general ledger.
7. Online giving, card processing, ACH initiation, tax advice, and enforcement
   of charitable-contribution law remain outside ChurchManager.
8. Existing prototype envelope and giving tables are not the approved design
   and will not be used as an implementation shortcut or migrated without a
   separately approved conversion plan.
9. A donor may select an approved congregational fund or charitable purpose,
   but may not use ChurchManager to require payment to a named individual. The
   congregation must retain control and discretion over the use and recipient.

## 3. Terminology

| Term | Meaning |
| --- | --- |
| Contributor | Permanent giving account for a person, family, or outside donor. |
| Envelope assignment | An envelope number assigned to a contributor for a defined period. |
| Batch | A controlled group of contributions normally representing one service, collection, or deposit. |
| Contribution | One gift received from one contributor or anonymously. |
| Allocation | The portion of a contribution directed to one accounting fund or approved designation. |
| Posted batch | A balanced, locked batch whose summarized deposit has been posted or linked to fund accounting. |
| Statement | A contributor-facing record of qualifying gifts for a selected period. |

## 4. Scope

### 4.1 First operational release

- Contributor accounts linked optionally to a person or family.
- Outside contributors with a name and statement contact information stored in
  the giving subsystem.
- Active and inactive contributors.
- Effective-dated envelope-number assignments.
- Contribution batches for services, special collections, and other deposits.
- Cash, check, electronic, and non-cash contribution methods.
- Anonymous or loose offerings.
- Multiple allocations within one contribution.
- Accounting-fund selection for each monetary allocation.
- Memorial and honor gifts with an optional acknowledgment contact.
- Congregation-controlled statement eligibility and required acknowledgment
  facts, including goods or services and intangible religious benefits.
- Returned or refunded gift corrections.
- Batch control totals, validation, posting, and corrections.
- Summarized posting to the existing accounting transaction service.
- Contributor history, envelope register, batch report, and annual or
  date-range contribution statements.
- CSV import through a preview, validation, and explicit confirmation process.
- Complete authorization and safe audit history.

### 4.2 Deferred capabilities

- Pledge campaigns and pledge-versus-giving reports.
- Electronic-giving imports, provider transaction IDs, processing-fee expense,
  refunds or chargebacks originating with a provider, and net-payout
  reconciliation.
- Household statement preferences more complex than the selected contributor
  account.
- Quid pro quo receipt calculations and detailed non-cash acknowledgment
  workflows.
- Email delivery of statements.
- Recurring gift instructions or integrations with online-giving vendors.

The schema should leave room for these additions without placing unused fields
on the first-release screens.

### 4.3 Explicitly excluded

- Payment-card, bank-login, or ACH credential storage.
- Initiating or processing payments.
- Payroll deductions beyond importing an already completed contribution.
- Appraising the value of donated property.
- Determining whether a gift is tax deductible.
- Producing tax, legal, or accounting advice.
- Publishing contributor rankings or giving information to ordinary users.

## 5. Data model

New tables will use ChurchManager's current naming, audit, character-set, and
foreign-key conventions. Exact migration names and column sizes are finalized
during implementation, but the following relationships are required.

### 5.1 Contributor

`tblContributionContributor` stores the permanent giving identity.

| Field | Requirement |
| --- | --- |
| `ID` | Stable primary key. |
| `ChurchID` | Required church boundary. |
| `ContributorType` | `PERSON`, `FAMILY`, or `EXTERNAL`. |
| `PersonID` | Nullable foreign key; present only for a person contributor. |
| `FamilyID` | Nullable foreign key; present only for a family contributor. |
| `DisplayName` | Required statement and lookup name. |
| `StatementName` | Optional formal addressee when different. |
| `Address`, `Address2`, `City`, `State`, `PostalCode` | Optional giving-statement address, primarily for outside donors or an explicit override. |
| `Email` | Optional future statement-delivery address. |
| `IsActive` | Prevents new entry without erasing history. |
| `StatementEnabled` | Whether routine statements are generated. |
| `Note` | Restricted administrative note; never printed automatically. |

Exactly one of `PersonID` and `FamilyID` may be present. An `EXTERNAL`
contributor uses neither. Person and family deletion must not erase giving
history; linked contributors are retained and their stored display/statement
identity remains available.

ChurchManager will warn before creating a likely duplicate contributor, but an
authorized user may confirm two distinct accounts when necessary.

### 5.2 Envelope assignment

`tblContributionEnvelopeAssignment` stores dated assignments.

| Field | Requirement |
| --- | --- |
| `ID` | Primary key. |
| `ChurchID` | Required church boundary. |
| `ContributorID` | Required contributor. |
| `EnvelopeNumber` | Required normalized text. Numeric values discard leading zeroes so equivalent numbers cannot overlap. |
| `EffectiveFrom` | Required start date. |
| `EffectiveThrough` | Nullable inclusive end date. |
| `Note` | Optional restricted administrative note. |

The same envelope number may be reassigned in a later non-overlapping period.
It may not belong to two contributors in the same church on overlapping dates.
A contributor may have no envelope or may receive a replacement number during
the year. Historical contributions retain the resolved contributor and the
envelope text entered at the time, so later reassignment never changes history.

### 5.3 Contribution batch

`tblContributionBatch` stores the control record.

Required data includes church, batch date, description, optional worship
service or attendance-event reference, deposit date, accounting organization,
bank account, status, expected/control total, calculated total, entry user,
posting user and timestamps, version, and optional correction relationship.

Statuses are `DRAFT`, `READY`, `POSTED`, and `VOID`. A posted batch is immutable.
`VOID` is reserved for a documented reversal/correction workflow and is not a
hard delete.

### 5.4 Contribution

`tblContribution` records one received gift within a batch.

Required data includes batch, optional contributor, entered envelope number,
method, optional check/reference value, received date, gift amount, optional
non-cash description, statement eligibility, acknowledgment facts, optional
tribute information, and a restricted note.

A blank contributor means anonymous/loose offering. Anonymous contributions do
not appear on a contributor statement. Check and electronic reference values
must be masked or omitted from ordinary reports and support logs.

Statement eligibility is based on the congregation's controlled designation
policy, not an automatic ChurchManager tax opinion. Each gift records whether
goods or services were provided, their congregation-entered good-faith value
when applicable, or whether the only benefit was an intangible religious
benefit. An authorized override requires a reason and audit entry.

Optional tribute data supports `IN_MEMORY_OF` and `IN_HONOR_OF`, the displayed
honoree name, and a separate acknowledgment contact. A tribute acknowledgment
must not disclose the donor or amount unless the contributor explicitly
authorized that disclosure.

Implementation status (August 22, 2026): the contribution editor exposes these
goods/services, intangible-benefit, statement-review, memorial/honor, contact,
and separate donor/amount disclosure facts in a compact protected dialog. The
same fields survive draft edits and posted-batch correction copies. A protected
Posted-gift acknowledgment list now suppresses donor identity and amount
independently unless their corresponding consent flags explicitly authorize
disclosure.

### 5.5 Contribution allocation

`tblContributionAllocation` divides a contribution among accounting funds or
approved contribution designations. Monetary allocations use `DECIMAL` and
must total the contribution amount exactly. Each allocation identifies the
accounting organization, fund, contribution-revenue account, optional or
required functional classification, amount, and optional donor-restriction
note. The revenue account's functional-dimension rule is enforced before the
batch may be marked ready.

The first release should use existing active accounting funds and a controlled
mapping to contribution-revenue accounts rather than create a second chart of
accounts.

### 5.6 Approved contribution purpose

`tblContributionPurpose` controls the purposes donors may select. Required data
includes church, name, description, approval date, approving authority,
effective dates, active state, accounting fund/revenue/function mapping, congregation
control-and-discretion confirmation, and congregation-controlled statement
treatment. It never contains a required individual recipient.

The distribution recipient, when the congregation needs to record one for its
own administration, belongs to a separate restricted disbursement or benevolence
process and is not copied onto the donor's contribution or statement.

### 5.7 Posting link and audit

The posted batch stores the resulting accounting transaction ID. The accounting
transaction stores only a batch reference, date, summarized fund totals, cash
or undeposited-funds account, and an appropriate description. It stores no
contributor, family, envelope, check, or statement identity.

Giving audits record safe identifiers and actions. They must not copy complete
contribution detail, addresses, check numbers, or statement contents into
general support logs.

## 6. Contributor and envelope workflows

### 6.1 Contributor maintenance

Authorized users can:

- create a contributor from an existing person or family;
- create an outside contributor without a membership record;
- update statement identity and contact information;
- deactivate or reactivate a contributor;
- view envelope history and confidential giving history; and
- merge duplicate contributors only through a guarded, audited operation that
  preserves every contribution and envelope assignment.

The system must not silently synchronize member-directory and giving contact
fields. A user may explicitly refresh selected statement fields from the linked
person or family after previewing the changes.

### 6.2 Envelope maintenance

The envelope screen shows current, upcoming, expired, and unassigned numbers.
It supports individual assignment and a guarded annual assignment/import tool.
Validation occurs against the batch or contribution date, not merely today's
date.

The annual assignment tool offers two explicit strategies:

- **Assign a new sequence** closes the applicable old assignments and assigns
  consecutive box numbers for the new period in the selected contributor sort
  order.
- **Keep current numbers** carries forward nonconflicting current assignments;
  newly eligible contributors receive the lowest available gaps before numbers
  are appended to the end of the sequence.

Both strategies show a complete preview with conflicts, additions, retained
numbers, effective dates, and the resulting highest box number before changing
the database. Applying the preview is one audited transaction. The tool never
changes historical contribution ownership or entered envelope text.

The annual assignment screen is available from contributor maintenance. It
includes only active contributors, sorts them by statement display order,
refuses to overwrite assignments that already begin in the selected year, and
requires a fresh preview whenever its options or underlying data change.

Envelope-box labels are a protected Giving report. The user selects the annual
assignment period, label-sheet format, and whether inactive or outside
contributors are included. Each label contains the box number and statement
name, with optional congregation name; it contains no contribution amounts or
giving history. A printable assignment register accompanies the labels for
verification.

The first supported sheet is Avery 5160 or compatible: 30 labels on US Letter
paper in three columns and ten rows. The PDF must be printed at Actual Size /
100 percent. The protected Giving Reports screen produces both the label sheet
and a dated assignment register from the same selection.

Typing or importing an envelope number in contribution entry resolves the
contributor for the contribution date. Unknown or ambiguous numbers remain
flagged until corrected or deliberately recorded as anonymous.

### 6.3 Batch entry

1. Create a draft batch and identify the collection, deposit date, accounting
   organization, and receiving bank account.
2. Enter the expected/control total when one is available.
3. Enter each envelope, outside contribution, or loose offering.
4. Allocate each contribution among funds/designations.
5. Compare calculated gifts, control totals, and the actual deposit.
6. Review unresolved envelopes, missing mappings, negative amounts, duplicate
   references, and allocation differences.
7. Mark the batch ready and post it through the accounting service.

The entry screen is optimized for keyboard use and repeated envelope entry.
The current batch remains visible, and totals refresh after every saved entry.
Double-clicking a draft line opens it for editing.

### 6.4 Corrections

- Draft entries may be edited or deleted by an authorized user.
- Posted entries are never edited or deleted.
- A posted error is corrected with a linked reversing entry or correcting batch
  and, when necessary, a linked accounting reversal/replacement.
- ChurchManager creates the accounting reversal in Ready status and copies the
  original gifts into an editable Draft replacement batch. The original Giving
  batch becomes Void only after the reversal is approved and posted. The
  replacement cannot be sent to accounting before that posting is complete.
- A returned check is recorded as a linked correction; the original receipt is
  retained.
- The contributor's statement shows the corrected result while retaining an
  internal audit chain.
- Every posted correction requires a reason.

### 6.5 Directed gifts and approved purposes

ChurchManager distinguishes an approved congregational purpose from a gift
earmarked for a particular person.

An approved purpose or fund records its approval date, authorizing body or
authorized user, purpose, active dates, accounting mapping, statement treatment,
and confirmation that the congregation retains control and discretion over its
use. Only active, approved purposes are available during ordinary contribution
entry.

For example, a congregation may establish a **Student Support** fund, select the
student to be supported through its own authorized process, and accept gifts for
that congregational purpose. The donor selects Student Support; the congregation,
not the donor, controls the recipient and distribution.

If a donor attempts to direct Student Support or another gift to a named
individual:

1. Do not silently record it as an ordinary statement-eligible contribution.
2. Place the entry in a documented review state or return the payment.
3. An authorized church representative may explain that the congregation must
   retain control and discretion.
4. If the donor affirmatively removes the person-specific condition, record the
   gift to the approved purpose and document the date, representative, method,
   and a concise account of the clarification.
5. If the donor retains the condition, return the payment or record it under the
   congregation's separately approved non-contribution policy; do not include it
   as a charitable contribution on the ordinary statement.

ChurchManager does not decide deductibility. It enforces the congregation's
approved-purpose workflow and preserves the facts needed for review. Policies
and acknowledgment wording should be reviewed by the congregation's qualified
tax or legal adviser.

A proposed restriction for a new congregational purpose, such as trees on church
property, is not treated as a person-specific gift. Because the purpose is not
yet approved, ChurchManager places it in review. An authorized congregation
decision may accept and establish the purpose, obtain and document the donor's
permission to redesignate the gift to an existing purpose, or return the gift.
The system does not label the gift deductible or nondeductible merely because
the proposed purpose was not approved before the payment arrived.

## 7. Accounting integration

Posting a batch is one controlled operation:

1. Revalidate status, permissions, allocations, totals, accounting mappings,
   fiscal period, and optimistic version.
2. Create a balanced accounting transaction grouped by bank/clearing account,
   revenue account, fund, and any required functional dimension.
3. Post or link the accounting transaction under the approved accounting
   posting policy.
4. Store its ID on the contribution batch.
5. Mark the contribution batch posted and write both audit records.
6. Commit all changes atomically or roll back all changes.

The accounting deposit total must equal the contribution batch monetary total.
Non-cash contributions store a description and approved purpose classification
but no ChurchManager-assigned monetary value. An optional donor-provided
estimate may be retained as explicitly unverified internal information; it is
excluded from deposits, accounting handoff, contribution totals, and statement
valuation. Non-cash gifts do not enter a cash deposit.
A non-cash-only batch completes in the Giving subledger after review without
creating a zero-dollar accounting transaction. A mixed batch sends only its
positive monetary allocations to accounting.

Whether a giving user may post directly or must hand the ready batch to an
accounting user follows the congregation's existing accounting approval policy.
Small-congregation solo-operation overrides remain explicit and audited.

## 8. Security and privacy

The subsystem introduces separate operation-boundary permissions:

| Permission | Purpose |
| --- | --- |
| `giving.contributors.manage` | Maintain contributors and envelope assignments. |
| `giving.batches.enter` | Create and edit draft batches and contributions. |
| `giving.batches.review` | Review totals and mark a batch ready. |
| `giving.batches.post` | Post or correct a batch. |
| `giving.history.view` | View contributor-level giving history. |
| `giving.statements.generate` | Generate contribution statements. |
| `giving.reports.summary` | View giving totals without contributor identity. |
| `giving.reports.confidential` | Run donor-identifying giving reports. |
| `giving.purposes.manage` | Approve and maintain congregational giving purposes and their statement treatment. |

Menu visibility is not authorization. Services and report datasets recheck the
permission and church scope for every operation.

Implementation status (August 22, 2026): contributor, purpose, batch, import,
correction, annual-envelope, accounting-handoff, and protected-report services
now enforce these permissions at their own public operation boundaries.
Direct-invocation tests verify denial before database or file access.

Additional safeguards:

- No giving detail is included in routine error logs, telemetry, email, or the
  general report catalog.
- Confidential reports are labeled accordingly and are never available to the
  unrestricted visual report designer.
- Database dumps and exported statements are treated as confidential files.
- Unlisted member contact information is never printed. A statement uses the
  confidential statement address explicitly selected for that contributor.
- The application does not automatically email statements in the first
  release.
- Printed or saved statements should be produced only through an explicit user
  action and a clearly selected destination.
- External payment credentials and reusable payment tokens are never stored.

## 9. Statements and reports

### 9.1 Required reports

- Envelope Assignment Register.
- Unassigned and Conflicting Envelopes.
- Envelope Box Labels for a selected assignment period and supported label
  sheet format.
- Contribution Batch Detail.
- Contribution Batch Control Summary.
- Giving by Fund and Period, without donor identity.
- Contributor History, permission restricted.
- Contribution Statement for one contributor.
- Contribution Statements for all eligible contributors.
- Statement Exception List for missing names or delivery addresses.
- Accounting Posting Reconciliation by batch and transaction.
- Memorial and Honor Gift Acknowledgment List, permission restricted.
- Directed Gift Review List showing unresolved person-specific instructions and
  their disposition, permission restricted.

### 9.2 Contribution statements

Statements support one contributor or all eligible contributors for a selected
quarter, calendar year, or explicit custom date range. Quarter selection uses a
year and Quarter 1 through Quarter 4 and prints the resulting covered dates.

A statement includes church identity and contact information, contributor
statement name/address, covered period, eligible monetary contributions by date
and optionally fund, total eligible monetary contributions, separately labeled
non-cash descriptions without a ChurchManager-assigned value, generation date,
and an approved acknowledgment message.

For applicable contributions, the statement also reports whether no goods or
services were provided, describes and reports the congregation's good-faith
value of goods or services when present, or states that only intangible
religious benefits were provided. It describes donated property but never
assigns its fair-market value.

The wording must be configurable and reviewed by the congregation. The system
must support the congregation's recordkeeping but must not claim that every
listed amount is deductible. Statement-eligible and other payments are clearly
separated. Corrections and reissues carry a revision date and audit reference.
The system records the covered period, recipient, generation time, template
version, revision relationship, and document hash so an issued statement can be
identified without storing a second uncontrolled copy inside the audit log.

## 10. Import and export

CSV import supports contributor/envelope, date, amount, method, reference,
fund/designation, and source description where provided.

The import workflow must:

1. preserve the original file outside the database as controlled evidence;
2. preview parsed rows without changing data;
3. identify unknown envelopes, contributors, funds, malformed amounts,
   duplicates, and total differences;
4. permit explicit mappings and corrections;
5. import into a new draft batch only after confirmation; and
6. record file hash, row counts, totals, user, and timestamp without copying
   confidential row contents into the general audit log.

Exports containing contributor identities require the confidential-report
permission and display a privacy warning. Summary exports exclude donor and
envelope identity.

## 11. User interface

The main menu will place the subsystem in a distinct **Giving** group, separate
from ordinary membership and accounting daily work. Proposed entries are:

- Contribution Batches
- Contributors and Envelopes
- Giving Reports
- Contribution Statements

The first release uses dedicated ChurchManager dialogs and services for the
privacy-sensitive workflows, while reusable validated controls remain in
JSForm. The visual screen designer must not expose confidential datasets or
bypass giving permissions.

## 12. Validation rules

- Amounts are nonnegative in normal entry; corrections use the correction
  workflow rather than negative draft gifts.
- A monetary contribution must have one or more allocations whose amounts equal
  its gift amount.
- A posted batch total must be positive and equal its calculated monetary
  contribution total.
- A batch with an expected/control total must balance to it before posting.
- Every accounting mapping and fiscal period must be active and valid on the
  posting date.
- Every selected purpose must be active and congregation approved on the gift
  date.
- An unapproved but non-person-specific proposed purpose is held for documented
  acceptance, donor-approved redesignation, or return; it is not automatically
  classified as nondeductible.
- A person-specific direction cannot be marked statement eligible unless the
  donor has affirmatively removed that condition and the clarification has been
  documented.
- Envelope assignments may not overlap for the same church and number.
- Person, family, and external contributor types enforce their link rules.
- A contribution and all allocations belong to the same church as their batch.
- Posted records and posting links are protected from ordinary update or
  deletion.
- Statement date ranges are inclusive and use contribution received dates.
- Goods/services and intangible-religious-benefit choices are mutually
  consistent and validated before an acknowledgment is generated.

## 13. Backup, retention, and recovery

Giving tables are included in ChurchManager's verified database backup and
restore process. A restore remains whole-database recovery; the subsystem will
not offer a casual donor-only restore.

Retention and destruction periods are congregation policy decisions. The
application may later support an authorized retention tool, but the first
release never automatically deletes contribution history. Test-data reset must
generate fictitious donors and contributions and must never copy production
giving data.

## 14. Migration and rollout

Implementation will use new guarded migrations and a new schema. Existing
prototype `tblEnvelope`, `tblGivingRegister`, or similarly named historical
objects are neither authoritative nor automatically converted.

Rollout sequence:

1. Approve this specification.
2. Confirm permissions and accounting mappings.
3. Implement schema and service-level validation. *(Implemented through draft
   batch creation and monetary gift allocation.)*
4. Implement contributor/envelope and batch-entry screens. *(Contributor,
   envelope, approved-purpose, and draft monetary batch entry are implemented.)*
5. Implement posting integration and corrections. *(Implemented: the Ready
   review gate, draft corrections and deletion, receiving bank account,
   complete accounting dimensions, privacy-safe summarized transaction
   creation, atomic posting synchronization, and linked posted-batch
   reversal/replacement workflow.)*
6. Implement reports and statements. *(The protected donor-free `GIVE-BATCH`
   Batch Control Summary PDF and quarterly single/all-contributor statement
   previews, calendar-year and custom ranges, and identifiable issuance history
   are implemented. The remaining report inventory continues next.)*
7. Add CSV mapping, non-writing preview, validation, protected source evidence,
   duplicate-file prevention, and confirmed import into a new Draft batch.
   *(Implemented and accepted in ChurchDBTest.)*
8. Create isolated test data and complete automated regression tests.
   *(Implemented for the current operational surface; the reset includes CSV
   import evidence and the full suite passes. Extend the dataset and tests as
   the remaining first-release workflows are implemented.)*
9. Perform user acceptance with a sample collection, split gift, anonymous
   gift, reassigned envelope, correction, accounting reconciliation, and annual
   statement. *(The implemented batch, posting, correction, import, report,
   statement, and envelope workflows have received iterative visual acceptance.
   The formal full-specification acceptance remains open.)*
10. Update installation, user guide, database inventory, screen inventory,
    report inventory, and privacy documentation before release. *(Current
    surfaces are documented; final release documentation remains open until the
    outstanding report and special-gift workflows are complete.)*

## 15. Acceptance criteria

The subsystem is ready for beta acceptance when all of the following pass:

1. A person, family, and outside donor can each be a contributor without
   duplicating congregation records.
2. Envelope numbers resolve by contribution date and can be reused only in
   non-overlapping periods.
3. Anonymous offerings require no person or contributor record.
4. A gift can be split across funds and cannot save or post with unequal
   allocations.
5. A complete batch reconciles to its control total and produces one balanced
   summarized accounting transaction.
6. No donor, person, family, envelope, check, or statement identity appears in
   the general ledger transaction or ordinary accounting reports.
7. Posted giving records cannot be edited or deleted, and a correction preserves
   the audit chain.
8. A returned check remains linked to the original gift and reconciles both
   contributor history and accounting.
9. Users lacking giving permissions cannot open screens, invoke services, query
   confidential report datasets, or generate statements.
10. Statements include only the selected contributor and date range, handle
   statement eligibility, goods/services facts, non-cash descriptions, and
   anonymous gifts correctly.
11. Memorial and honor acknowledgments do not expose donor identity or gift
   amount without explicit authorization.
12. Imports detect unknown mappings and duplicates before changing the database.
13. A gift for an approved Student Support purpose can be entered without naming
   a recipient, while a donor instruction naming a student is held for review
   until returned or affirmatively clarified and documented.
14. Backup and restore preserve contributions, assignments, posting links, and
   audits.
15. Error logs and support bundles contain no confidential contribution detail.
16. All automated tests pass, and GUI/report layout is accepted through actual
   rendered inspection.

## 16. Decisions established by this specification

- Giving is a confidential ChurchManager subledger, not a JSForm feature and
  not part of the ordinary member record.
- Envelope numbers are reusable dated identifiers, not permanent keys. Numeric
  values have one canonical form (`001`, `01`, and `1` are equivalent).
- Contributors may link to a person or family but are not required to do so.
- Loose offerings do not require fabricated people.
- Fund accounting receives summarized balanced deposits only.
- Posted contributions are immutable and corrections are linked and audited.
- Statement eligibility and acknowledgment facts are controlled congregation
  data, not a ChurchManager tax determination.
- Donors may support approved congregational purposes, but the congregation
  retains control over recipients and use; named-person directions require
  return or documented donor clarification.
- Online payment processing and legal/tax determinations remain outside scope.

## 17. Research-informed feature review

The design was compared on August 18, 2026 with current official documentation
for Planning Center Giving, Breeze, CiviCRM, and United States IRS charitable
contribution guidance.

The review confirmed the value of batch entry, split funds, pledges, statement
customization, imports, and contributor-level reporting already present in this
specification. It identified the following features that were easy to overlook:

- returned, rejected, refunded, and charged-back gifts;
- statement-eligible versus other payments;
- per-gift goods/services and intangible religious benefit facts;
- memorial and honor gifts with privacy-safe acknowledgments;
- provider transaction IDs for import duplicate detection; and
- identifiable statement revisions and reissues.

Returned checks, statement treatment, acknowledgment facts, memorial and honor
gifts, and statement revisions are included in the approved first release.
Provider transaction IDs and the other electronic-provider details are deferred
with electronic-giving integration.

ChurchManager intentionally does not adopt payment processing, stored payment
tokens, fundraising pages, donor rankings, or automated tax determinations.
Electronic-giving import, fee, refund, chargeback, and payout reconciliation are
useful researched features but are deferred until an external giving service is
actually integrated.

Official sources consulted:

- [IRS: Charitable contributions—written acknowledgments](https://www.irs.gov/charities-non-profits/charitable-organizations/charitable-contributions-written-acknowledgments)
- [IRS Publication 1771](https://www.irs.gov/pub/irs-pdf/p1771.pdf)
- [Planning Center: importing data and donations](https://support.planningcenteronline.com/hc/en-us/articles/115011570067-Can-I-import-data-from-another-system)
- [Breeze: donor-covered fees](https://support.breezechms.com/hc/en-us/articles/360048148713-Understanding-Donor-Covered-Fees)
- [Breeze: tax-deductible and other funds](https://support.breezechms.com/hc/en-us/articles/360046363013-Tax-Deductible-Funds-Vs-Non-Tax-Deductible-Funds)
- [Breeze: giving statements](https://support.breezechms.com/hc/en-us/articles/27806429354647-Complete-Guide-to-Creating-Giving-Statements)
- [CiviCRM: batch and manual contribution entry](https://docs.civicrm.org/user/en/latest/contributions/manual-entry-of-contributions/)
- [CiviCRM: soft credits and tribute attribution](https://docs.civicrm.org/user/en/latest/contributions/soft-credits/)
