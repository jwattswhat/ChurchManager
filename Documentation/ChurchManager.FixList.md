# ChurchManager development roadmap

Last reviewed: August 14, 2026

This is the maintained ChurchManager development backlog. Priorities reflect
the needs of a small congregation and a comparison with current paid and
open-source church-management systems. The independent Frozen ChurchManager
application is outside this roadmap and must not be changed.

## Authoritative priority sequence

| Order | Priority | Project | Reason for placement |
|---:|---|---|---|
| 1 | Immediate | User contact information | Small, foundational change required by communication and support workflows. |
| 2 | Immediate | Email and participant notification review | Completes an existing weekly workflow and depends on reliable contact data. |
| 3 | Immediate | Release, installation, and recovery readiness | Stabilizes what already exists before adding more major subsystems. |
| 4 | Next | Pastoral follow-up | Highest-value ministry addition and a natural extension of attendance. |
| 5 | Next | Import, export, and duplicate management | Protects data quality and makes adoption and recovery practical. |
| 6 | Next | Groups, committees, classes, and ministry teams | Adds the most broadly missing congregational structure. |
| 7 | Next | Volunteer availability and responses | Builds on the completed worship scheduling foundation. |
| 8 | Later | Confidential contributions and pledges | Valuable, but requires a separate privacy-sensitive specification and subledger. |
| 9 | Later | General events and calendar integration | Useful, but Google Calendar should remain the primary calendar platform. |
| 10 | Later | Custom profile fields and controlled tags | Adds flexibility after the core normalized relationships are settled. |
| Triggered | Conditional | Two-factor authentication | Required if remote, browser, or member access is introduced. |

Items 1 through 3 should be completed before beginning a new major subsystem.
Items 4 through 7 form the next ministry-development phase. Items 8 through 10
should not delay a stable ChurchManager release.

### 1. User contact information

- Add email address and phone number to ChurchManager user accounts.
- Update User Administration, database migrations, validation, auditing, and
  tests.
- Keep administrative user contact details separate from congregation member
  records.
- Define which security roles may view or edit this information.

### 2. Email and participant notification review

- Modernize the shared ChurchManager email configuration and sending service.
- Review Notify Participants from recipient selection through delivery.
- Show recipients, missing addresses, subject, message, and attachment before
  sending.
- Generate and attach the current Worship Planning report.
- Prevent duplicate recipients and report delivery failures clearly.
- Record a safe communication history without storing credentials or
  unnecessarily duplicating sensitive message content.
- Preserve the rule that sending email is an explicit user action.

### 3. Release, installation, and recovery readiness

- Complete the formal visual acceptance review of all official reports.
- Record final acceptance of active ChurchManager screens and workflows.
- Build a repeatable new-install and upgrade process.
- Ask which hymnals and lectionary systems the congregation wants installed.
- Permit multiple selections and an explicit "None" choice for each catalog.
- Install only selected starter datasets.
- Choose the church's primary hymnal and default lectionary independently.
- Keep the installer denomination-neutral: LSB and its lectionaries are
  optional packages, not hard-coded requirements.
- Install and verify database structure, numbered migrations, starter reports,
  starter screens, permissions, runtime dependencies, and the first master
  administrator.
- Certify installation against a fresh local database rather than a copy of the
  development database.
- Document ordinary backup and restore procedures and the complete-backup
  format.
- Confirm the permanent backup location is separate from MariaDB's data storage
  and from the same local-storage failure domain.
- Review and archive or remove obsolete historical development SQL only after
  the installer and numbered migrations are independently sufficient.

### 4. Pastoral follow-up

- Create follow-up items from attendance warnings or manually.
- Assign a follow-up to the pastor, an elder, or another authorized caregiver.
- Record contact attempts, outcome, next-follow-up date, and completion.
- Protect pastoral notes with a separate sensitive permission.
- Show actionable overdue follow-ups without exposing confidential detail on
  the main menu.
- Provide a printable or exportable authorized follow-up list.

### 5. Import, export, and duplicate management

- Add a central Data Management screen.
- Import people and families from CSV with a preview and explicit field mapping.
- Detect likely duplicate people, families, email addresses, and phone numbers.
- Require review before merging records.
- Export only approved datasets and always enforce unlisted/private contact
  restrictions.
- Record import results, rejected rows, and export history.
- Provide a complete portable archive format where appropriate.

### 6. Groups, committees, classes, and ministry teams

- Add general groups independent of worship-participant roles.
- Support leaders, members, group roles, active dates, notes, and categories.
- Accommodate boards, committees, Bible studies, Sunday school, choir,
  confirmation, altar guild, outreach, and temporary teams.
- Permit group attendance and authorized group communication.
- Add group rosters and participation reports.

### 7. Volunteer availability and responses

- Add participant availability and blockout dates.
- Send explicit serve requests and reminders.
- Record accepted, declined, and pending responses.
- Show last-served information and scheduling conflicts.
- Preserve manual scheduling and small-congregation flexibility.
- Consider optional scheduling suggestions, but never silently replace existing
  assignments.

### 8. Confidential contributions and pledges

- Design this as a separate confidential subledger with its own permissions.
- Support contribution batches, donor accounts, funds/designations, pledges,
  non-cash gifts, corrections, and year-end statements.
- Import contribution files where practical.
- Post summarized, balanced deposits into fund accounting without exposing
  donor identity in the general ledger.
- Specify privacy, retention, audit, backup, and statement-delivery rules before
  implementation.

### 9. General events and calendar integration

- Add non-worship events with one-time or recurring dates.
- Support simple invitations, RSVP/registration lists, attendance, and notes.
- Integrate with Google Calendar rather than duplicating a complete calendar
  platform.
- Consider simple room or resource reservations only when a demonstrated need
  exists.

### 10. Custom profile fields and controlled tags

- Allow authorized administrators to define optional person and family fields
  or tags.
- Keep common values controlled and searchable.
- Include privacy and report-export behavior in each field definition.
- Avoid using arbitrary custom fields where a normalized ChurchManager
  relationship is more appropriate.

### Conditional: two-factor authentication if remote access is introduced

- Two-factor authentication is not required for the current local-only use.
- Require it as part of any future remote, browser, or member-portal project.
- Include recovery codes, administrative recovery, auditing, and clear account
  ownership rules in its specification.

## Integration candidates rather than native subsystems

ChurchManager should exchange data with established services instead of
handling these high-risk or specialized functions itself:

- online, card, text, or ACH giving and payment processing;
- payroll calculation, tax filing, and direct deposit;
- mass SMS and push notifications;
- background-check processing;
- website publishing and livestream services;
- copyrighted music, sheet music, rehearsal audio, and CCLI reporting.

## Deliberately outside the present scope

- a social network, chat, reactions, or congregation newsfeed;
- a native mobile application;
- a full website builder;
- multi-campus administration;
- a full child check-in, badge, and secure-pickup system unless a congregation
  demonstrates a need;
- advanced facility management beyond possible simple reservations.

## Roadmap maintenance rules

1. Prepare and approve a specification before beginning a new numbered item.
2. Use isolated test data and guarded migrations.
3. Complete automated checks and user acceptance before marking an item done.
4. Update the screen, report, and database inventories when ownership changes.
5. Prefer a focused integration over recreating an established external
   platform.
6. Do not expand scope merely to match a commercial product's feature list.
