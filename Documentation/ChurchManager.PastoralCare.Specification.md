# ChurchManager pastoral care specification

**Status:** Approved

**Version:** 1.0

**Date:** August 18, 2026

**Approved by:** Rev. Jonathan C. Watt

**Implementation:** encryption/key-recovery service, migration 096 database,
permission and controlled-choice foundation, and protected backup sidecar
plumbing implemented. Restricted-note entry, administrator recovery-package
setup, service authorization, auditing, workflows, and restore acceptance remain
gated.

**Target:** ChurchManager

## 1. Purpose

Provide a simple, protected pastoral-care workflow that helps authorized
caregivers remember needs, record completed actions, and schedule the next
follow-up. This subsystem is a ministry work list, not an electronic counseling
record, clinical system, safeguarding case file, or repository for everything a
pastor knows.

The normal record should answer four questions:

1. Who needs care?
2. Who is responsible for the next action?
3. What needs to happen, and when?
4. Was it done, and is another follow-up needed?

## 2. Ownership boundary

### JSForm owns

- neutral hooks for authorization, audit, validation, error handling, and
  sensitive-control display;
- reusable controls and layout behavior that do not know pastoral-care policy;
- preventing hidden or unauthorized fields from being exposed through generic
  form behavior.

### ChurchManager owns

- pastoral-care identity, policy, permissions, screens, reports, and retention;
- care categories, action types, status rules, assignments, and notifications;
- encryption, key recovery, auditing, and backup/restore acceptance;
- every decision to reveal or withhold confidential information.

Pastoral-care tables and screens must not be implemented as ordinary JSForm
Tasks, Notes, or configurable report data.

## 3. Record model

### 3.1 Care need

A care need contains operational information only:

| Field | Rule |
| --- | --- |
| `ID` | Permanent database identifier |
| `ChurchID` | Required congregation boundary |
| `PersonID` | Optional link to a person |
| `FamilyID` | Optional link to a family |
| `DisplaySubject` | Required only when neither person nor family is linked |
| `Category` | Required maintained choice |
| `Source` | Manual, Attendance Follow-up, Prayer Request, Hospital Notice, Life Event, or Other |
| `AssignedUserID` | Optional until assigned; must reference an active user |
| `Priority` | Normal or Urgent |
| `Status` | Open, Waiting, Completed, or Closed - Not Needed |
| `OpenedDate` | Required |
| `DueDate` | Optional |
| `NextFollowUpDate` | Optional |
| `ScheduleText` | Optional natural-language recurring visitation schedule |
| `ScheduleRule` | Optional normalized recurrence rule generated from `ScheduleText` |
| `ScheduleStatus` | Active, Paused, or Ended when recurrence is configured |
| `CompletedDate` | Required when completed |
| `ClosedDate` | Required when closed |
| `SafeSummary` | Short, non-sensitive scheduling description |
| audit fields | Creator, modifier, timestamps, and optimistic version |

Exactly one of `PersonID`, `FamilyID`, or `DisplaySubject` must identify the
subject. A care need may have many care actions.

`Urgent` means scheduling priority only. The screen must state that
ChurchManager is not an emergency-response or mandated-reporting system.

### 3.2 Regular visitation schedules

A continuing care need, especially a shut-in or homebound Communion visit, may
have an optional recurring schedule. The user enters the schedule in the same
plain-language control used by Prayers and Announcements. Examples include:

- `Every fourth Tuesday`
- `Every 6 weeks`
- `First Thursday of every month`
- `Every year on October 1`

ChurchManager uses the approved natural-language scheduling grammar to validate
the phrase and stores both the friendly `ScheduleText` and its normalized
`ScheduleRule`. The structured rule is authoritative; the text is retained for
display. Unsupported or ambiguous language is rejected with examples rather
than guessed.

Pastoral-care recurrence uses exact due occurrences, not the service-week
inclusion behavior used when selecting Prayers and Announcements. After a
completed visit, ChurchManager calculates the first scheduled occurrence after
the completed action date and sets it as `NextFollowUpDate`. A late visit does
not create a backlog of missed visit records. Attempted, deferred, or postponed
actions leave the current follow-up due until the caregiver deliberately sets a
new date or records a completed visit.

The schedule may be Active, Paused, or Ended. Pausing or ending it retains all
past actions. A caregiver may override the next date without changing the
underlying schedule. The dashboard marks an active overdue visit but does not
automatically mark it completed, skipped, or not needed.

### 3.3 Care action

| Field | Rule |
| --- | --- |
| `ID` | Permanent database identifier |
| `CareNeedID` | Required parent |
| `ActionDateTime` | Required |
| `CaregiverUserID` | Required active user |
| `ActionType` | Call, Visit, Card, Meal, Email, Prayer, Referral, or Other |
| `Result` | Completed, Attempted, Deferred, or Not Needed |
| `SafeOutcome` | Optional brief non-sensitive outcome |
| `NextFollowUpDate` | Optional |
| audit fields | Creator, modifier, timestamps, and optimistic version |

Completing an action may update the care need's next-follow-up date. It must not
silently create a recurring chain of work.

### 3.4 Restricted note

A restricted note is optional and separate from the care need and care action.
It stores no plaintext narrative column. Its database representation contains:

- parent care-need ID and optional care-action ID;
- ciphertext;
- unique nonce;
- authentication tag;
- encryption-algorithm identifier;
- key version;
- creator and timestamps; and
- an optimistic version.

The authenticated record binding must include the congregation, note, care
need, and optional care-action identifiers so encrypted content cannot be moved
to another record undetected.

No attachments are allowed.

## 4. Confidential-note encryption

### 4.1 Encryption rules

- ChurchManager encrypts restricted narrative before MariaDB receives it.
- Use AES-256-GCM through a maintained cryptographic library.
- Generate a unique cryptographically random nonce for every encryption.
- Never reuse a nonce with the same key.
- Do not create custom cryptographic algorithms or deterministic note
  encryption.
- Decryption occurs only after authorization, for the shortest practical time,
  and only for the requested note.
- Plaintext must not be written to temporary files, logs, error reports,
  diagnostics, audit JSON, clipboard history, or SQL dumps.

### 4.2 Key storage

Each installation receives a randomly generated data-encryption key. The active
key is protected by Windows data-protection facilities and is never stored in
MariaDB, source control, ordinary configuration, or the executable.

Every encrypted row records its key version. The system must support replacing
a compromised key and re-encrypting existing notes. A user's ChurchManager
password must never serve as the encryption key.

### 4.3 Recovery and complete backups

A machine-protected key alone is not an acceptable design because a replacement
computer could not decrypt restored notes. ChurchManager complete backup must
therefore create:

1. the ordinary SQL dump, containing ciphertext only; and
2. a separately protected recovery-key package.

The recovery package requires a recovery password supplied by an authorized
administrator. It uses a recognized password-based key derivation function and
authenticated encryption. The recovery password is never stored by
ChurchManager and cannot be recovered by the project.

Backup completion must fail visibly when encrypted notes exist but no usable
recovery-key package was created. Restore must verify the package before
changing the active database and must require a ChurchManager restart after key
installation.

Acceptance testing must prove that:

- SQL alone cannot reveal a note;
- SQL alone cannot restore readable restricted notes on another machine;
- SQL plus the correct recovery package and password restores the notes;
- an incorrect or altered package fails without damaging the database;
- backup, restore, diagnostics, and error logs contain no plaintext; and
- key rotation preserves existing notes and older verified backups.

## 5. Authorization and audit

Use distinct permissions:

- `pastoral.care.view.assigned`
- `pastoral.care.view.all`
- `pastoral.care.create`
- `pastoral.care.assign`
- `pastoral.care.update`
- `pastoral.care.close`
- `pastoral.notes.view`
- `pastoral.notes.edit`
- `pastoral.care.report`
- `pastoral.care.admin`

Only the Master Administrator receives pastoral-care administration by default.
Other roles receive no pastoral permissions until explicitly configured.

Assignment access does not imply note access. Reporting access does not imply
note access. Authorization is checked in the service layer for every read and
write, not only by hiding buttons.

Audit creation, assignment, reassignment, status change, completion, closure,
restricted-note creation/change/view, report execution, recovery-key creation,
key restoration, and key rotation. Audit records identify the action and record
but never contain narrative or cryptographic secrets.

## 6. User experience

### 6.1 Pastoral Care dashboard

Default to **Assigned to Me**, grouped as Overdue, Due Today, Due This Week,
Waiting, and Recently Completed. Authorized coordinators may also view
Unassigned and All Open.

Rows show only the subject, broad category, assignee, due date, priority, and
status. Double-click opens the care history.

### 6.2 Care history and action editor

The upper area shows safe operational details. The history lists dated actions
without restricted narrative. A separate clearly marked **Restricted Note**
area appears only to authorized users and is closed or masked by default.

The screen should emphasize **Record Action**, **Set Next Follow-up**,
**Complete**, and **Close - Not Needed**. It must remain useful when no
restricted note is entered.

For recurring visitation, the screen displays the friendly schedule, current
next-due date, and Active, Paused, or Ended state. Recording a completed visit
shows the proposed next occurrence before it is saved.

### 6.3 Handoffs

Attendance and prayer-request screens may offer **Create Care Follow-up** to an
authorized user. This is always deliberate; a warning or prayer request never
automatically creates a care record. Full prayer wording is not copied.

People and family screens may show an authorized summary consisting only of the
open count, next due date, and a button to Pastoral Care.

## 7. Notifications and reports

Email and operating-system notifications contain no person name, category,
medical information, prayer wording, or note text. A suitable message is:
“A pastoral care follow-up is due in ChurchManager.” Test mode sends no email.

First-release reports are:

- **Pastoral Care - Work List**, restricted to authorized operational fields;
- **Pastoral Care - Activity Summary**, aggregate counts without identifying
  narrative.

Restricted notes are excluded from all report datasets, generic exports,
screen/report designers, support packages, and full-text search. An individual
restricted history remains an on-screen view in the first release.

## 8. Minimum-necessary and retention rules

ChurchManager must display concise guidance near restricted-note entry:

- do not store confessions or counseling transcripts;
- do not record clinical diagnoses, speculation, gossip, or unnecessary family
  detail;
- do not store safeguarding investigations, legal correspondence, medical
  records, audio, video, or photographs;
- use brief factual language about care and the next action; and
- use the congregation's approved retention and deletion policy.

Deletion must be authorized and audited. Deleting a database row does not prove
that copies vanished from older backups; user documentation must state this.
Retention defaults and any legal-hold procedure require congregation review
before the subsystem is enabled for operational use.

## 9. Failure behavior

The system fails closed when:

- the key is unavailable or invalid;
- ciphertext authentication fails;
- authorization is absent or indeterminate;
- backup recovery protection cannot be verified; or
- the application is in an unsupported key-version state.

Failure messages identify a support code but never echo note content, keys,
nonces, tags, passwords, or decrypted data. A cryptographic failure must not
silently replace or clear a note.

## 10. Implementation sequence

1. Approve this specification and the minimum-necessary policy.
2. Implement and independently test the encryption and recoverable-key service.
3. Integrate recovery-key handling into complete backup and restore acceptance.
4. Add permissions and safe audit events.
5. Add normalized care tables and maintained choices.
6. Build the dashboard, history, action editor, and restricted-note control.
7. Add deliberate attendance and prayer handoffs.
8. Add safe operational and aggregate reports.
9. Add user and administrator documentation.
10. Perform automated, security, restore, fictional-data, and rendered visual
    acceptance before enabling restricted notes.

## 11. Acceptance boundary

The subsystem is not complete merely because encrypted text can be saved and
read. It is complete only when authorization, audit, logging, diagnostics,
backup, restore to a replacement machine, key rotation, reports, designers,
test mode, and failure behavior have all been verified with fictional data.

If that boundary is not met, ChurchManager may release care scheduling without
restricted narrative, but it must not expose an unencrypted note field.
