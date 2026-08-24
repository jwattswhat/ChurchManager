# ChurchManager groups and membership specification

**Status:** Approved  
**Version:** 1.0  
**Date:** August 22, 2026  
**Approved by:** Rev. Jonathan C. Watt  
**Target application:** ChurchManager  
**Application framework:** JSForm  
**Database:** MariaDB/MySQL

## 1. Purpose

This specification defines first-class congregational Groups and their
membership in ChurchManager. A Group is an identifiable body of people with a
purpose, membership, leadership, and history. Examples include:

- Board of Elders;
- Church Council and standing or temporary committees;
- Ladies Bible Study and other study groups;
- Sunday school classes and confirmation classes;
- choir, handbells, and other music groups;
- altar guild, ushers, outreach, and service teams; and
- fellowship groups and short-term project teams.

The subsystem answers practical questions such as:

1. What Groups exist and which are currently active?
2. Who currently belongs to each Group?
3. Who serves in each role, and during what term?
4. When did a person join or leave a Group?
5. Who attended a particular Group meeting?
6. Which authorized contact methods may be used for Group communication?

Groups are independent of worship-participant roles, custom profile fields,
tags, mailing-list labels, and application security roles.

## 2. Scope

Version 1 includes:

- controlled Group types;
- Group identity, status, purpose, dates, and ordinary administrative notes;
- Person membership with dated history;
- controlled Group roles and dated role assignments;
- leadership and vacancy information;
- Group meetings and Person attendance;
- reviewed Group communication recipient lists;
- rosters, membership history, attendance, and participation reports;
- searching and filtering;
- permissions, privacy, auditing, import, export, backup, and restore; and
- modernization of the existing development `tblGroup` and `tblGroupMember`
  structures through guarded migrations.

Version 1 excludes:

- nested Groups or Groups as members of other Groups;
- Family records as Group members;
- application users, roles, or permissions derived automatically from Group
  membership;
- worship scheduling or worship-participant qualification;
- a complete calendar, room-reservation, learning-management, child check-in,
  safeguarding-case, or mass-marketing system;
- dues, budgets, funds, or accounting ownership;
- files, minutes, curricula, lesson content, or document attachments; and
- full liturgical or musical content.

A nonmember or community participant may belong to a Group if that individual
has a normal `tblPerson` record with the appropriate nonmember status. Version
1 does not create a second kind of unlinked Group contact.

## 3. Design principles

1. **A Group is a domain entity.** Meaningful membership is represented by a
   relational membership record, not by text, a tag, or a custom field.
2. **History is preserved.** Ending membership, a leadership role, or a Group
   does not delete its historical record.
3. **Terms are explicit.** Start and end dates distinguish present membership
   from past service and support term-based leadership.
4. **Names and choices are controlled.** Group types and roles use stable
   catalog keys and editable labels rather than unrestricted spelling variants.
5. **Security is enforced at the operation boundary.** Hiding a menu, screen,
   button, field, report column, or recipient is not sufficient authorization.
6. **Communication is reviewed.** ChurchManager prepares an authorized
   recipient list and preview; it does not silently message everyone matching a
   changing query.
7. **Privacy follows the Person record.** Group access never overrides unlisted
   or restricted Person contact information.
8. **Specialized systems remain separate.** Group membership does not replace
   attendance at worship, participant scheduling, pastoral care, accounting,
   application security, or custom profile fields.
9. **No executable configuration.** Group types, roles, and settings cannot
   contain Python, SQL, commands, arbitrary callbacks, or template code.

## 4. Ownership boundary

### 4.1 JSForm owns

JSForm provides reusable, application-neutral support for:

- Group, membership, role-assignment, meeting, and attendance screen layout;
- typed controls and control-level validation;
- protected and read-only controls;
- master-detail lists and ordinary record navigation;
- application-provided search choices;
- authorization and audit hooks;
- report layout and rendering from approved datasets; and
- consistent validation and database-error presentation.

### 4.2 ChurchManager owns

ChurchManager owns:

- Group, membership, role, meeting, and attendance meaning;
- database schema and constraints;
- Group type and role catalogs;
- term, overlap, status, and lifecycle rules;
- authorization and privacy policy;
- application services and transactions;
- recipient resolution and communication review;
- report and export datasets;
- audit attribution and safe audit content;
- migration, backup, restore, and installation behavior; and
- every integration with Persons, attendance, and mail.

JSForm does not infer a Person's authority, worship qualification, pastoral
responsibility, or application role from Group membership.

## 5. Terminology

| Term | Meaning |
| --- | --- |
| Group | A named congregational body with a purpose and membership. |
| Group type | A controlled category such as governance body, committee, Bible study, class, music group, service team, or fellowship group. |
| Membership | A dated relationship between one Person and one Group. |
| Group role | A controlled function within a Group, such as member, chair, leader, secretary, teacher, or elder. |
| Role assignment | A dated assignment of one Group role to one membership. |
| Term | The inclusive start and optional end dates of membership or a role assignment. |
| Current | Started on or before the effective date and not ended before that date. |
| Group meeting | A dated occurrence associated with one Group. |
| Group attendance | A Person's attendance status at one Group meeting. |

The word `Group` in this specification does not mean a menu grouping, report
band, accounting statement group, lectionary option group, or security role.

## 6. Group record

Each Group contains at least:

| Field | Rule |
| --- | --- |
| `ID` | Immutable database identifier. |
| `ChurchID` | Owning congregation; required and immutable after creation. |
| `GroupKey` | Stable, case-insensitively unique machine key within the Church. |
| `Name` | Required user-facing name. |
| `GroupTypeID` | Required active controlled type. |
| `Description` | Concise statement of purpose. |
| `Status` | Draft, Active, Inactive, or Closed. |
| `StartDate` | Optional date on which the Group began. |
| `EndDate` | Required when status is Closed; otherwise blank. |
| `UsualMeetingDescription` | Optional short planning description, not a recurrence engine. |
| `DefaultLocation` | Optional short location label. |
| `CommunicationEnabled` | Whether reviewed Group recipient preparation is allowed. |
| `PrivacyClass` | Standard or Restricted. |
| `Notes` | Bounded ordinary administrative notes only. |
| Audit fields | Creator, creation time, last editor, and last edit time. |

`GroupKey` is used by imports, reports, and integrations and does not change
when the display name changes. A Group name is unique among current Groups
within a Church unless an authorized administrator confirms a clearly
distinguished name.

Draft Groups may be configured without admitting members. Active Groups accept
current memberships and meetings. Inactive Groups temporarily stop new
membership and meetings but may later reactivate. Closed Groups retain history
and cannot accept new activity.

## 7. Group types

Group types are Church-scoped controlled catalog records containing a stable
key, label, description, display order, active flag, privacy default, and audit
fields.

Initial starter types may include:

- Governance Body;
- Committee;
- Bible Study;
- Class;
- Music Group;
- Service Team;
- Fellowship Group; and
- Temporary Team.

Starter types are editable only through the supported catalog rules. Local
types may be added. A type referenced by any Group may be retired but not
physically deleted. Retiring a type does not close its existing Groups.

Group type is descriptive and may supply safe defaults. It does not grant
permissions or impose theological, constitutional, employment, safeguarding,
or financial authority.

## 8. Membership

A membership joins exactly one `tblPerson` record to exactly one Group and
contains:

| Field | Rule |
| --- | --- |
| `ID` | Immutable database identifier. |
| `GroupID` | Required Group foreign key. |
| `PersonID` | Required Person foreign key. |
| `StartDate` | Required beginning of membership. |
| `EndDate` | Optional inclusive final date. |
| `StatusReason` | Optional controlled reason for ending or correcting membership. |
| `Notes` | Bounded administrative note; not pastoral-care narrative. |
| Audit fields | Creator, creation time, last editor, and last edit time. |

Rules:

- the Person and Group must belong to the same Church;
- `EndDate` cannot precede `StartDate`;
- membership cannot begin before a closed Group's beginning or after its end;
- a Person cannot have overlapping membership terms in the same Group;
- sequential, non-overlapping terms are permitted and preserve history;
- ending a membership also ends any still-open role assignments no later than
  the membership end date in the same transaction;
- deleting a Person or Group through any future supported workflow must not
  silently erase historically material membership; and
- ordinary corrections retain audit attribution.

Moving a Person between Groups ends one membership and creates another. It does
not rewrite the original membership's Group ID.

## 9. Group roles and leadership

Roles use controlled definitions. A role contains a stable key, label,
description, leadership flag, display order, active flag, and audit fields. A
role may be available Church-wide or limited to a Group type. A Group may also
activate a permitted local role without changing historical assignments.

Each membership receives a basic `member` role implicitly for the duration of
membership. Additional roles use dated role-assignment records so a Person may,
for example, remain a committee member after completing a term as chair.

A role assignment contains membership ID, role ID, start date, optional end
date, and audit fields. Its dates must fall within the membership term.
Overlapping duplicate assignments of the same role to the same membership are
rejected.

A role definition may specify a warning limit such as one current chair. This
produces a validation warning or vacancy indicator, not an automatic transfer
of authority. Constitutional or policy requirements are not hard-coded merely
because a role is named `Elder`, `Treasurer`, or `President`.

ChurchManager displays current leaders separately from the full roster and can
report vacancies and terms ending within a selected date range.

## 10. Privacy and safeguarding

Group membership may reveal sensitive religious association, age cohort,
leadership status, or care-related participation. Access therefore follows
least privilege.

Standard Groups are visible to authorized Group users. Restricted Groups
require explicit restricted-Group permission. An unauthorized user must not
learn a restricted Group's name, existence, membership count, members,
meetings, roles, attendance, or recipient list through screens, searches,
reports, exports, logs, errors, or report-designer metadata.

Person privacy continues to govern addresses, phone numbers, and email
addresses. Group membership never turns an unlisted contact method into a
listed one. Communication recipient preparation uses only contact methods the
current user and communication surface are authorized to use.

For Groups involving minors:

- ordinary membership may record the Person and dates;
- the Group note and membership note do not store safeguarding allegations,
  medical details, custody restrictions, counseling content, or background
  check documents;
- authorized communication follows the approved Person/Family contact model;
  and
- ChurchManager does not claim to be a child check-in or safeguarding case
  system.

## 11. Meetings and attendance

A Group meeting is a dated occurrence containing Group ID, start date and time,
optional end time, short title, location, status, attendance-recording mode,
bounded administrative note, and audit fields.

Meeting status is Scheduled, Held, Cancelled, or Rescheduled. Rescheduling
preserves the original record and links it to the replacement meeting rather
than silently rewriting historical notices or attendance.

Group attendance is stored separately from worship attendance. Each attendance
record identifies a meeting, a Person with a current or permitted guest
relationship, attendance status, optional arrival or departure information,
bounded note, recording user, and time.

Initial attendance statuses are Present, Absent, Excused, and Unknown. A
meeting may also retain an optional total head count. A head count does not
create unnamed Person records.

Rules:

- a Person is recorded at most once per meeting;
- the default attendance list is the membership roster effective on the
  meeting date;
- authorized users may add an existing Person as a guest without creating a
  Group membership;
- adding a guest does not silently enroll that Person in the Group;
- attendance edits are audited; and
- Group attendance is not counted as worship attendance, communion attendance,
  or service participation.

Version 1 does not generate a complete recurring calendar. A later calendar
integration may create or link individual Group meeting records through an
approved interface without changing membership history.

## 12. Group communication

ChurchManager may prepare a recipient list for a selected Group and effective
date. The user chooses current members, selected roles, or explicitly selected
members and then chooses an approved contact method.

Before any message is sent, the review screen shows:

- the exact Group;
- the effective membership date;
- included roles or selected members;
- recipient count;
- excluded members and non-sensitive reasons;
- the sender identity and approved account;
- subject and message preview; and
- the proposed send action.

Sending requires explicit confirmation after review. Recipient resolution is
repeated immediately before sending, and material changes return the user to
review. ChurchManager records a bounded audit summary and delivery outcome
without copying unnecessary private recipient details or full sensitive
message content into audit JSON.

Version 1 does not maintain a separate marketing subscription database, send
unsolicited bulk messages, or treat Group membership as consent for every
communication purpose. Email transport and credentials follow the existing
mail specification and protected credential mechanism.

Implemented behavior requires communication to be deliberately enabled on the
selected Group. Recipient review uses membership and role terms effective on
the chosen date, shows non-sensitive exclusion reasons, never reveals an
unlisted email address, and deduplicates shared addresses. Sending requires a
separate permission and explicit confirmation. The recipient snapshot is
resolved again immediately before delivery; any membership or contact change
returns the user to review. TEST MODE remains fail-closed and cannot transmit
email.

## 13. Worship roles and application security

Group membership does not automatically create a worship participant, assign a
worship role, establish availability, or make someone eligible for scheduling.
An explicit approved link may help an authorized scheduler find candidates,
but worship-participant qualification and assignments remain in the worship
subsystem.

Group roles do not create ChurchManager application roles or permissions. A
Person becoming an elder, treasurer, committee chair, or teacher never changes
software access automatically.

## 14. Permissions

The permission catalog includes at least:

- `groups.view`;
- `groups.edit`;
- `groups.define_types`;
- `groups.view_restricted`;
- `groups.edit_restricted`;
- `groups.membership.view`;
- `groups.membership.edit`;
- `groups.roles.define`;
- `groups.roles.assign`;
- `groups.meetings.view`;
- `groups.meetings.edit`;
- `groups.attendance.view`;
- `groups.attendance.record`;
- `groups.communication.prepare`;
- `groups.communication.send`;
- `groups.reports.view`; and
- `groups.export`.

Permission names are registered centrally. Group types or records cannot invent
permission strings. Sensitive operations require both the general operation
permission and any restricted-Group permission. Services recheck authorization
immediately before database commit, report generation, export, recipient
resolution, and send.

## 15. Proposed data model

The normalized logical tables are:

- `tblGroupType`;
- `tblGroup`;
- `tblGroupRole`;
- `tblGroupRoleAvailability` when a role is limited by Group type;
- `tblGroupMembership`;
- `tblGroupMembershipRole`;
- `tblGroupMeeting`;
- `tblGroupMeetingAttendance`; and
- append-only Group-related events in the approved security audit system.

Key database protections include:

- foreign keys for Church, Group, Person, type, membership, role, meeting, and
  attendance references;
- Church-scoped uniqueness for stable Group and catalog keys;
- one attendance row per Person and meeting;
- one role assignment per membership, role, and non-overlapping term;
- date-order checks;
- supported status checks;
- indexes for current membership, Person participation, leader lookup, term
  expiration, meeting date, and attendance reporting; and
- guarded deletion behavior that preserves history.

ChurchManager services additionally enforce same-Church relationships,
cross-table date containment, overlapping-term rules, privacy, authorization,
and lifecycle policy immediately before commit.

## 16. Screen behavior

The Groups workspace includes:

1. **Group list:** searchable by name, type, status, leader, and effective date.
2. **Group details:** identity, type, purpose, status, dates, meeting summary,
   current leaders, current roster, and history tabs.
3. **Membership editor:** Person search, membership dates, roles, and validation
   of duplicate or overlapping terms.
4. **Role and type catalogs:** controlled administration with retirement rather
   than destructive deletion.
5. **Meeting list and editor:** meeting status and attendance entry.
6. **Communication review:** exact recipient resolution and confirmation.
7. **Reports:** approved filters and preview before output.

The Group screen favors ordinary language. It shows `Current members`, `Past
members`, `Leaders`, and `Terms ending soon` rather than exposing database
concepts.

Closing a Group presents unresolved memberships, open roles, future meetings,
and unsent communication drafts for review. The user
must resolve or explicitly retain each applicable item before closure commits.

## 17. Search and reports

Authorized searches support:

- Group name, stable key, type, status, and date range;
- current or historical membership on an effective date;
- Person membership across Groups;
- current leader or role holder;
- vacant leadership roles;
- terms ending within a date range;
- meeting date and attendance status; and
- participation counts within an explicit period.

Approved starter reports include:

- Current Group Roster;
- Group Leadership and Terms;
- Person Group Participation History;
- Group Membership Changes;
- Group Meeting Attendance;
- Group Participation Summary; and
- Leadership Vacancies and Terms Ending.

Every report states the Group, effective date or reporting period, status scope,
and generation time. Restricted Groups and private contact fields require
explicitly approved datasets and permissions. Report definitions never query
unrestricted application tables directly.

## 18. Import and export

Imports are preview-and-commit operations. Stable keys identify Group types,
Groups, roles, and Persons where available. A proposed import reports creates,
changes, ended terms, unknown Persons, duplicate or overlapping memberships,
invalid dates, unknown roles, cross-Church references, and authorization errors
before any write.

Imports do not create Persons, types, roles, or Groups implicitly unless the
user selected an explicit authorized catalog-import workflow. Commit repeats
validation and authorization in one bounded transaction or documented batch
units with a complete result summary.

Exports require an approved dataset, explicit effective date or period,
permission, preview, and confirmation. They honor Person contact privacy and
restricted Group rules. Export history records the user, time, filters, row
count, output type, and outcome without copying the full export into audit
storage.

## 19. Audit behavior

ChurchManager records at least:

- Group and catalog creation, edit, retirement, reactivation, closure, and
  permitted deletion;
- membership creation, date correction, ending, and reactivation;
- role assignment and ending;
- meeting creation, rescheduling, cancellation, and attendance changes;
- communication recipient preparation, confirmation, send, and outcome;
- report and export operations involving restricted Groups;
- import and bulk-change summaries; and
- authorization denials for sensitive Group operations.

Audit events identify the user, time, session or workstation, action, Group ID,
affected record IDs, and outcome. Audit storage does not copy passwords,
credentials, private contact lists, message bodies, pastoral narrative,
safeguarding content, or unnecessary restricted values.

## 20. Lifecycle and deletion

An unused Draft Group with no memberships, roles, meetings, attendance,
communications, links, report dependencies, or meaningful audit dependency may
be physically deleted through an authorized workflow.

An Active, Inactive, or historically used Group is closed rather than deleted.
Closing preserves membership, leadership, meeting, attendance, report, and
audit history. A closed Group may be reopened only by an authorized user after
reviewing dates and unresolved linked records.

Catalog records and historical membership are retired or corrected with audit;
they are not silently reused for a different meaning.

## 21. Migration of existing development data

The current development baseline contains minimal `tblGroup` and
`tblGroupMember` tables. Their free-text `GroupType` and `GroupRole` fields and
limited constraints are not the final version 1 design.

Implementation uses a guarded, versioned migration against `ChurchDBTest` that:

1. inventories existing Group and membership rows;
2. rejects cross-Church, orphaned, invalid-date, and ambiguous duplicate data
   until reviewed;
3. creates stable Group, type, and role keys through a previewed mapping;
4. preserves existing IDs where safe or records durable old-to-new mappings;
5. converts free-text types and roles into controlled catalog records;
6. converts existing membership dates and notes without fabricating facts;
7. reports every rejected, merged, or corrected row;
8. verifies counts, relationships, dates, and representative reports; and
9. updates the installation baseline only after migration acceptance.

This work applies to the current independent ChurchManager system.

## 22. Backup, restore, and installation

Groups, catalogs, memberships, roles, meetings, attendance, communication
history, and audits are congregation-owned data included in normal backup and
restore coverage.

Installation and restore validation checks:

- table, index, and foreign-key presence;
- same-Church relationships;
- stable-key uniqueness;
- date and status validity;
- orphaned or overlapping membership terms;
- invalid role assignments;
- duplicate meeting attendance;
- permission catalog entries; and
- backup round-trip preservation.

Migrations, baseline schema and seed data, manifests, installer acceptance,
database inventories, public guides, screen inventories, docstrings, and tests
are updated together when implementation begins.

## 23. Performance and limits

The implementation uses bounded set queries rather than one query per Group or
member. Current roster, Person participation, leader, term-ending, and meeting
attendance searches receive appropriate indexes.

Version 1 documents and enforces practical limits for result size, bulk
membership operations, recipient review, exports, note lengths, and meeting
attendance entry. Exact numerical limits are selected from measured
ChurchDBTest behavior before implementation acceptance.

## 24. Acceptance criteria

The subsystem is accepted only when all of the following are demonstrated:

1. An authorized user can create each supported Group type and representative
   Groups including Elders, a committee, and a Bible study.
2. Group names, stable keys, types, statuses, and dates validate correctly.
3. A Person can hold sequential membership terms while overlapping duplicate
   terms are rejected.
4. Multiple dated roles can be assigned within a membership, and role dates
   cannot exceed membership dates.
5. Ending membership closes open role assignments atomically without deleting
   history.
6. Current and historical rosters are correct for selected effective dates.
7. Leadership vacancies and ending terms are reported correctly.
8. Group meetings and attendance remain distinct from worship attendance.
9. A guest attendance entry does not silently create Group membership.
10. Restricted Groups cannot be inferred through screens, searches, counts,
    reports, exports, logs, errors, or report-designer metadata.
11. Unlisted or unauthorized Person contact information is never revealed by
    Group membership or communication preparation.
12. Communication requires an exact recipient preview and explicit confirmation
    and returns to review after a material recipient change.
13. Group membership never grants an application role, permission, worship
    role, or scheduling eligibility.
14. Closing a Group preserves history and requires review of current members,
    future meetings, open roles, and linked work.
15. Database constraints prevent orphaned records, cross-Church references,
    duplicate attendance, and invalid supported statuses.
16. Application services enforce cross-table term, lifecycle, privacy, and
    permission rules immediately before commit.
17. Import preview identifies all invalid, unknown, duplicate, overlapping, and
    unauthorized rows before writing.
18. Exports identify their effective date or period and honor restricted Group
    and Person privacy policy.
19. Audit tests verify attribution without copying private recipient lists,
    message bodies, or prohibited sensitive content unnecessarily.
20. Backup and restore preserve stable keys, history, roles, meetings,
    attendance, and audit relationships.
21. Existing development Group data migrates through a reviewed mapping with
    reconciled counts and no fabricated facts.
22. The guarded migration and baseline installation operate only against the
    approved development/test configuration and never access the separate
    Frozen application.
23. JSON forms and report definitions pass canonical schema and structure
    validation.
24. Group, membership, meeting, attendance, communication, and report screens
    are rendered and visually inspected at supported window sizes before visual
    verification is claimed.
25. Specifications, inventories, public guidance, database terminology,
    docstrings, and tests agree.

## 25. Implementation sequence

1. Approve this specification and settle the decisions in section 26.
2. Inventory and characterize existing development Group data in
   `ChurchDBTest` without changing it.
3. Add controlled Group type and role catalogs, normalized membership and role
   tables, constraints, permissions, and migration tests.
4. Implement ChurchManager Group, membership, meeting, attendance, search,
   communication, report, import, export, and audit services.
5. Add JSForm screens using the approved service contracts.
6. Add approved report datasets and starter layouts.
7. Complete security, privacy, transaction, migration, backup, restore, and
   performance tests.
8. Render and visually inspect all affected screens and representative reports.
9. Update baseline artifacts, inventories, user and developer documentation,
   and roadmap status in the same implementation commit.

## 26. Approved implementation decisions

1. Core Groups, membership, and roles form the first increment. Meetings and
   attendance follow as the second increment of the same approved subsystem.
2. A Person may hold sequential, non-overlapping historical memberships in the
   same Group; reactivation creates a new term rather than rewriting history.
3. Fresh installations include the Group types listed in section 7 and the
   roles Member, Chair, Leader, Secretary, Teacher, Treasurer, and Elder.
4. Ordinary rosters exclude contact information. An authorized contact-roster
   report provides permitted contact fields separately.
5. Restricted Groups are included in version 1 and require their dedicated
   permissions at every operation boundary.
6. Group communication prepares and reviews the exact recipient list before
   sending. Protected TEST MODE behavior and explicit send confirmation received
   functional and visual acceptance on August 24, 2026.
7. Temporary Groups may have an optional expected closure date and reminder.
