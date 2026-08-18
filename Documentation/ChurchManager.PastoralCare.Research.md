# Pastoral care systems research and ChurchManager recommendations

Status: Research complete; proposed design specification prepared

Prepared: August 18, 2026

## Purpose

This research compares current pastoral-care and church-management workflows
and recommends a small-congregation design for ChurchManager. The goal is not
to create an electronic counseling file. The goal is to help authorized people
remember who needs care, coordinate the next appropriate action, and avoid
letting people fall through the cracks.

## Executive recommendation

ChurchManager should add a distinct **Pastoral Care** subsystem built around
three deliberately separate records:

1. **Care need** — the person or family, a broad reason, responsible caregiver,
   priority, current status, and next follow-up date.
2. **Care action** — a dated phone call, visit, card, meal, email, prayer, or
   other action, including a brief outcome.
3. **Restricted note** — optional minimum-necessary pastoral information with
   stronger permission, audit, export, and retention controls than the care
   task itself.

The first release should emphasize an assigned-care queue and brief action
history. It should not attempt clinical case management, counseling transcripts,
automated spiritual judgments, or a general repository for everything a pastor
knows.

## What current systems commonly provide

### Follow-up assignments

Breeze uses reusable follow-up options with a default assignee and completion
time, then lets users assign, reassign, complete, search, and report on those
items. Permissions distinguish items assigned to the current user, items the
user assigned, and assignments across the organization. It can also begin a
later follow-up when an earlier one is completed. This demonstrates the value
of a simple template plus assignment model, but ChurchManager does not need the
full automation chain initially.

Sources:

- [Breeze: Getting Started with Follow Ups](https://support.breezechms.com/hc/en-us/articles/360049978273-Getting-Started-with-Follow-Ups)
- [Breeze: Follow Up Progression](https://support.breezechms.com/hc/en-us/articles/360006145153-Follow-Up-Progression)

### Care-centered tasks, updates, milestones, and reporting

Notebird centers its product on care updates, person-centered tasks, life
milestones, an activity view, access restrictions, and care reports. Its
reporting can summarize calls, visits, and other interactions by date, type,
person, group, or caregiver. This is the clearest specialized comparison for
ChurchManager: the important unit is a care action connected to a person, not a
generic project task.

Sources:

- [Notebird pastoral care overview](https://guide.notebird.app/en/articles/15140083-welcome-to-notebird)
- [Notebird care reports](https://www.notebird.app/features/reports)

### Configurable requests and workflows

Rock RMS supports connection requests with an assignee, state, status,
activities, future follow-up dates, transfer, history, and optional workflows.
Rock's prayer-request system also distinguishes categories, urgency, public
display, administrative review, and a focused text limit. These features show
how a flexible system can grow, but Rock's workflow engine is substantially
larger than ChurchManager needs for a small-congregation first release.

Sources:

- [Rock RMS connection workflows](https://community.rockrms.com/documentation/engagement/connections/connections-tools/connection-workflows)
- [Rock RMS connection request view](https://community.rockrms.com/documentation/engagement/connections/connection-requests/connections-views?Version=v19.0)
- [Rock RMS prayer request entry](https://community.rockrms.com/documentation/engagement/prayer/prayer-requests/enter-prayer-requests)

### Notes and access controls

Breeze permits dated person notes and an optional private flag, while noting
that exported notes require especially careful export permissions. ChurchCRM
supports private or shared notes on people and families with timeline filters.
These systems confirm that note access and export access must be treated as
separate security decisions.

Sources:

- [Breeze: Using Notes](https://support.breezechms.com/hc/en-us/articles/360012185814-Using-Notes)
- [ChurchCRM feature overview](https://docs.churchcrm.io/getting-started/features-overview)

## Recommended ChurchManager first release

### 1. Pastoral Care dashboard

The main screen should default to **Assigned to Me** and show:

- overdue;
- due today;
- due this week;
- waiting;
- unassigned, for users permitted to coordinate care; and
- recently completed.

Each row should show only the person's name, broad care category, responsible
caregiver, due date, priority, and status. Confidential narrative must not
appear in the dashboard, main menu, email reminders, or operating-system
notifications.

### 2. Care needs

Create a care need manually or from an explicit action on an attendance or
prayer screen. Store:

- optional Person or Family relationship;
- a short display subject when the person is not yet in the congregation
  database;
- broad category selected from maintained choices;
- source such as Manual, Attendance Follow-up, Prayer Request, Hospital Notice,
  or Life Event;
- assigned ChurchManager user;
- Normal or Urgent priority;
- Open, Waiting, Completed, or Closed - Not Needed status;
- opened, due, next-follow-up, completed, and closed dates;
- a short non-sensitive action summary; and
- creator, modifier, timestamps, and optimistic version.

Suggested starting categories are Hospital, Homebound, Bereavement, New
Visitor, Attendance Concern, Prayer Follow-up, Family Need, Milestone, and
Other. Categories should come from the maintained choices catalog so a
congregation can add ordinary categories without changing code.

“Urgent” must mean pastoral scheduling priority. The application must clearly
state that it is not an emergency, crisis-response, or mandated-reporting
system.

### 3. Care actions

One care need may have many actions. Store the date and time, caregiver,
action type, completion result, next follow-up date, and an optional brief
restricted note. Suggested action types are Call, Visit, Card, Meal, Email,
Prayer, Referral, and Other.

Double-clicking a care need should open its history and the next-action editor.
Completing an action may set another follow-up date, but it should not silently
create chains of tasks. A future enhancement may add reusable care-plan
templates after actual congregation use demonstrates the need.

Regular shut-in and homebound Communion visits are a first-release exception to
that deferral. A continuing care need may use the same validated natural-language
schedule control as Prayers and Announcements, for example `Every fourth
Tuesday` or `Every 6 weeks`. The normalized recurrence rule determines the next
due visit after a completed action; it does not create a chain of future task
records or a backlog of missed visits.

### 4. Security

Use distinct permissions rather than ordinary People, Tasks, or report access:

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

The system should fail closed. A person permitted to complete an assigned care
action does not automatically receive access to restricted notes or all care
history. Access, creation, changes, assignment, completion, closure, viewing of
restricted notes, and exports should be auditable.

Restricted pastoral narrative must be encrypted by ChurchManager before it is
sent to MariaDB. Use authenticated encryption (AES-256-GCM), a unique random
nonce for every encrypted value, and a mature cryptographic library. Store only
the ciphertext, nonce, authentication tag, key version, and necessary record
binding in the database. Never store the encryption key in the database,
application source, ordinary configuration, logs, diagnostics, or repository.

Operational fields should remain readable so the system can schedule and report
without decrypting pastoral notes. These include the person or family link,
category, assignee, priority, status, due dates, action type, and audit
identifiers. Restricted note text and confidential outcome detail must not be
searchable, sortable, included in ordinary reports, or exposed through the
screen and report designers.

ChurchManager needs an installation-specific data-encryption key protected by
the operating system. Windows data protection can protect the working key on
the installed computer, but machine-only protection is insufficient by itself:
a verified, separately protected recovery-key package must accompany the
complete backup so an authorized administrator can restore the database on a
replacement computer. Backup and restore acceptance tests must verify that an
encrypted note survives restoration and remains unreadable without the recovery
key. Key rotation, compromise recovery, and recovery-key replacement must be
designed before pastoral notes are enabled.

Encryption supplements rather than replaces least-privilege permissions,
auditing, secure Windows accounts, full-disk encryption, secure backups, and
minimum-necessary note content. If the encryption and recoverable-key design is
not installed and verified, ChurchManager may track non-sensitive care tasks but
must not accept restricted pastoral narrative.

Email reminders should contain only a safe message such as “A pastoral care
follow-up is due in ChurchManager.” They should not include a person's name,
care category, medical detail, prayer wording, or note content.

### 5. Reports

Provide two different report classes:

- **Care work list** — authorized operational list of open and upcoming items,
  without restricted note text.
- **Care activity summary** — counts by action type, category, caregiver, and
  period, without identifying narrative. This can support an elders' or annual
  ministry report without revealing confidential details.

An individual care history with restricted notes should be an on-screen
pastoral view, not a default printable report. Any later print or export must
require a stronger permission, explicit warning, audit event, and safe output
handling.

## Privacy and legal boundary

Church records are not automatically protected from legal process. Legal
sources note that clergy-penitent privilege varies by jurisdiction and may
protect some confidential counseling communications or a pastor's notes, but
ordinary church records generally do not gain blanket privilege merely because
the church stores them. Confidential information can also create liability if
it is accessible to people who should not receive it.

Sources:

- [Church Law & Tax: counseling session notes and clergy-penitent privilege](https://www.churchlawandtax.com/legal-developments/counseling-session-notes-and-the-clergy-penitent-privilege/)
- [Church Law & Tax: church records and subpoenas](https://www.churchlawandtax.com/manage-finances/charitable-contributions/qa-must-we-comply-with-a-subpoena-for-giving-records/)
- [Church Law & Tax: counseling confidentiality](https://www.churchlawandtax.com/pastor-church-law/church-legal-liability/counseling-in-general/)

ChurchManager should therefore enforce a **minimum-necessary record rule**:

- do not store a confession or counseling transcript;
- do not record clinical diagnoses, speculation, gossip, or unnecessary family
  detail;
- do not store abuse-investigation evidence or substitute this subsystem for a
  congregation's mandated-reporting and safeguarding procedures;
- do not attach audio, video, clinical records, legal correspondence, or
  photographs to a care need;
- prefer “Hospital visit completed; follow up next week” over medical detail;
- prefer “Family requested pastoral contact” over the substance of a private
  conversation;
- correct factual errors without silently rewriting the audit history; and
- apply a congregation-approved retention policy reviewed for its state and
  denominational context.

This document is product research, not legal advice. Before operational use, a
congregation should have its access, confidentiality, mandated-reporting, and
records-retention policies reviewed by qualified counsel and its insurer or
denominational risk resource as appropriate.

## Integration with existing ChurchManager areas

### Attendance

Keep the existing missed-weeks report. Add an explicit **Create Care Follow-up**
action for an authorized user. Do not automatically create a pastoral record
for every attendance warning; absences can be incorrect, expected, or already
known.

### Prayer requests

Allow an authorized user to create a linked care need from a prayer request,
but do not copy the full prayer text into the care record by default. Preserve
the prayer's own privacy and publication choices.

### People and families

Show a small authorized care summary on the person or family screen: open item
count, next due date, and a button to the Pastoral Care subsystem. Do not expose
restricted notes through ordinary person reports, the screen designer, or
general data export.

### Tasks and projects

Do not reuse the existing general task table. General tasks have different
permissions, reports, and retention expectations. Pastoral care may reuse
neutral UI patterns, but it needs separate tables and authorization.

### Milestones

Existing person and family dates can later offer manual reminders for births,
anniversaries, bereavement, homebound Communion, or other congregation-defined
milestones. The first release should not infer a care need automatically from
age, marital status, giving, attendance, or other profile data.

### Remote access

ChurchManager remains a local desktop system. Any future remote caregiver
access must use the roadmap's secure VPN boundary and must not expose MariaDB or
a pastoral-care web endpoint directly to the internet.

## Features to defer or reject

Defer until real use demonstrates a need:

- multi-step automated care plans;
- recurring task chains beyond the approved single regular-visitation schedule;
- care teams and workload balancing beyond ordinary assignment;
- SMS or mobile push notifications;
- member self-submission portal;
- configurable forms or arbitrary care fields;
- integrations with outside pastoral-care services.

Reject as contrary to the ChurchManager design:

- AI-generated pastoral assessments or suggested spiritual diagnoses;
- scoring members by “engagement,” giving, or perceived care risk;
- using contribution history to initiate pastoral contact;
- automatic care actions based on private data;
- clinical treatment records;
- unrestricted full-text note search;
- dashboards that display confidential narrative; and
- sharing care details in ordinary email notifications.

## Recommended implementation sequence

See [ChurchManager pastoral care specification](ChurchManager.PastoralCare.Specification.md).

1. Approve the Pastoral Care specification and minimum-necessary documentation
   policy.
2. Define permissions, default roles, audit events, and safe notification text.
3. Add normalized care-need and care-action tables with no attachment fields.
4. Build the Assigned to Me dashboard and care history/editor.
5. Add explicit attendance and prayer-request handoff actions.
6. Add safe operational and aggregate reports.
7. Add retention and authorized export controls.
8. Perform database, security, usability, backup/restore, and visual acceptance
   with fictional care data only.

## Current ChurchManager cleanup finding

`Documentation/ChurchManager.Application.md` still lists `tblFamilyVisit`, but
no matching table, migration, form, or current implementation was found in the
development source. The pastoral-care project should not revive that apparent
obsolete structure. The application and database inventories should be
corrected when the new specification establishes the replacement design.
