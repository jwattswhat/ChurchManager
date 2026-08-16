# ChurchManager development roadmap

Last reviewed: August 16, 2026

This is the maintained ChurchManager development backlog. Priorities reflect
the needs of a small congregation and a comparison with current paid and
open-source church-management systems.

## Authoritative priority sequence

| Order | Priority | Project | Reason for placement |
|---:|---|---|---|
| 1 | Completed | User contact information | Foundational contact fields and administration are implemented. |
| 2 | Completed | Email and participant notification review | The weekly participant-notification workflow has been modernized. |
| 3 | In acceptance | Optional user-to-person relationship | Source, migration, administration UI, safe auditing, and welcome email are implemented; database and visual acceptance remain. |
| 4 | Immediate | Hymnal, lectionary, and Order of Service catalog design | Defines what the installer can safely and legally offer. |
| 5 | Immediate | Release, installation, and recovery readiness | Stabilizes and packages the researched catalogs and existing application. |
| 6 | Next | Pastoral follow-up | Highest-value ministry addition and a natural extension of attendance. |
| 7 | Next | Import, export, and duplicate management | Protects data quality and makes adoption and recovery practical. |
| 8 | Next | Groups, committees, classes, and ministry teams | Adds the most broadly missing congregational structure. |
| 9 | Next | Volunteer availability and responses | Builds on the completed worship scheduling foundation. |
| 10 | Later | Confidential contributions and pledges | Valuable, but requires a separate privacy-sensitive specification and subledger. |
| 11 | Later | General events and calendar integration | Useful, but Google Calendar should remain the primary calendar platform. |
| 12 | Later | Custom profile fields and controlled tags | Adds flexibility after the core normalized relationships are settled. |
| Triggered | Conditional | Two-factor authentication | Required if remote, browser, or member access is introduced. |

Items 1 through 5 should be completed before beginning a new major subsystem.
Items 6 through 9 form the next ministry-development phase. Items 10 through 12
should not delay a stable ChurchManager release.

## Completed foundations retained for regression protection

These completed areas remain part of release testing even though they are not
future roadmap projects:

- application authentication, roles, permissions, security auditing, user
  contact information, and password-change enforcement;
- fund accounting through entry, review, posting, reporting, reconciliation,
  budgets, close, and year-end close;
- JSForm visual report generation and design, report security, ChurchManager
  visual screen design, and starter/custom definition separation;
- unified worship planning, weekly Orders of Service, hymn selection and stanza
  selection, Propers/readings, participants, scheduling, required positions,
  preparation checklists, and worship-planning reports;
- natural-language prayer and announcement scheduling;
- synchronized attendance entry and attendance reporting;
- participant notification email, Gmail thread separation, and safe delivery
  history;
- protected backup/restore, automatic exit backup, single-instance startup,
  responsive main menu, and support-diagnostics/error capture.

### Completed worship enhancement: hymn stanza selection

- Implemented design: [Hymn stanza selection specification](ChurchManager.HymnStanzaSelection.Specification.md).
- The planner records selected stanzas for each hymn occurrence in a
  weekly Order of Service.
- Stanza selections remain attached to the individual weekly service line so the
  same hymn can have different selections in different positions.
- Planning and bulletin-outline output include the selection.
- Historical free-form notes are not treated as stanza selections.

### 1. User contact information

- Implemented design: [ChurchManager user contact information specification](ChurchManager.UserContact.Specification.md).
- User accounts store validated email and phone values.
- User Administration, migrations, auditing, permissions, display formatting,
  and automated tests cover the fields.
- Administrative contact details remain separate from congregation member
  records.

### 2. Email and participant notification review

- The shared ChurchManager email configuration and sending service are
  implemented.
- Notify Participants shows recipients, missing addresses, subject, message,
  and the current Worship Planning report attachment before sending.
- Duplicate recipients are suppressed and delivery failures are reported.
- Safe communication history excludes credentials and unnecessary message
  content.
- Sending remains an explicit user action, and unique message identifiers avoid
  Gmail incorrectly joining unrelated notices into one conversation.

### 3. Optional user-to-person relationship

- Implemented design: [User-to-person link and welcome email specification](ChurchManager.UserPersonLink.Specification.md).
- Migration 070 adds nullable `tblUser.PersonID` with a unique foreign key to
  `tblPerson.ID`.
- Permit users who are not congregation members by allowing the link to remain
  blank.
- Use `ON DELETE SET NULL` so removing a person record cannot remove or disable
  an application account.
- Add an optional Linked Person selector to User Administration.
- Keep user email and phone independent from member contact records; linking must
  not silently copy or synchronize contact information.
- Audit linking, changing, and unlinking a person from a user account.
- Add an optional new-user welcome email that reuses the shared ChurchManager
  email service. Include the username, instructions for opening ChurchManager,
  notice that the temporary password must be changed at first login, and an
  administrator contact; do not include the temporary password.
- Require the administrator to communicate the temporary password through a
  separate channel, while retaining `MustChangePassword=1` until the user
  successfully replaces it.
- Record only safe delivery metadata for the welcome message; never store the
  temporary password in email history, logs, or audit JSON.
- Cover existing databases, fresh installation, uniqueness, unlinking, User
  Administration, welcome-email delivery, password separation, and authorization
  with automated tests.
- Preserve the already completed participant design: `tblParticipant.PersonID`
  remains optional so worship participants may be members or outside people.
- Source implementation and focused automated tests are complete. Remaining
  acceptance work is applying migration 070 to `ChurchDBTest` and visually
  checking create, edit, unlink, and welcome-email actions.

### 4. Hymnal, lectionary, and Order of Service catalog design

#### Hymnal catalog and import workstream

- Use [Hymnal Research and Recommendations](ChurchManager.HymnalResearchAndRecommendations.md)
  as the starting point for the multi-hymnal catalog design.
- Implement the approved
  [Permanent Hymn Identifier Specification](ChurchManager.PermanentHymnIdentifiers.Specification.md):
  permanent 5,000-entry hymnal blocks, a reserved local-user range, transactional
  collision checks, and retirement rather than ID reuse or cascade deletion.
- Implement the approved
  [Suggested Hymnal Import Process](ChurchManager.HymnalImportProcess.md), keeping
  curated permanent-ID packages separate from congregation-supplied local CSV
  imports.
- Distinguish an underlying hymn from its numbered and titled appearance in a
  particular hymnal.
- Define how Proper hymn suggestions resolve against the congregation's selected
  hymnal without assuming LSB numbering.
- Define, validate, and test the permanent hymnal registry and reserved local-user
  range before importing any additional hymnal package.
- Build the curated hymnal-package validator and staged import workflow before
  adding hymnal selection to installation.

#### Lectionary catalog workstream

- Use [Revised Common Lectionary Research](ChurchManager.RevisedCommonLectionary.Research.md)
  as the starting point for denomination-neutral lectionary support.
- After product-owner approval, implement the
  [Lectionary Catalog Specification](ChurchManager.LectionaryCatalog.Specification.md),
  including stable package keys, flexible cycles, service-owned reading
  snapshots, local customization, and the hard metadata-only boundary.

#### Order of Service catalog workstream

- Complete a companion Order of Service research and specification document
  before designing the installer catalog-selection pages.
- Define separately installable Order of Service packages with stable identity,
  version, source, license, dependencies, and supported update behavior.
- Define how an Order of Service may reference a hymnal or service book while
  still permitting "No hymnal."
- Make Order of Service packages metadata-only. Their schema may contain sequence,
  short outline labels, item types, references, conditions, inclusion choices,
  required positions, and brief planning notes, but no full liturgical or musical
  content fields.
- Exclude full liturgical wording, published prayers or collects, responsive text,
  meaningful-length verbatim rubrics, psalm or canticle text, tones, musical
  settings, hymn lyrics, notation, accompaniment material, publisher artwork, and
  page images from packages, database records, customized templates, weekly
  copies, and generated output.
- Add package-schema and import validation that rejects unapproved content fields,
  long-form body fields, HTML or rich-text bodies, and embedded or linked media;
  cover every rejection rule with automated tests.
- Preserve customized catalog records and weekly service copies when starter
  packages are installed or upgraded.
- Define and test starter installation, upgrade, retirement, and removal behavior
  without changing congregation-created templates or saved weekly services.

#### Shared catalog completion criteria

- Define separately installable packages for hymnals, lectionaries, and Orders
  of Service, including package identity, version, source, license, dependencies,
  and supported update behavior.
- Approve the catalog schema and package contents before installation development
  begins.

### 5. Release, installation, and recovery readiness

#### LimeReports retirement workstream

- Source implementation completed August 14, 2026.
- All supported catalog reports use JSForm visual report definitions and the
  internal PDF renderer.
- The external LimeReports fallback, templates, diagnostics, and configuration
  have been removed from ChurchManager.
- Migration 065 disables obsolete catalog codes and removes obsolete path
  settings.
- Remaining acceptance work is the representative report-family visual review
  documented in [LimeReports retirement](ChurchManager.LimeReports.Retirement.md).

- Error logging and protected Support and Diagnostics are implemented from the
  [ChurchManager error logging and support specification](ChurchManager.ErrorLogging.Specification.md);
  retain them in release regression testing.
- Complete the formal visual acceptance review of all official reports.
- Record final acceptance of active ChurchManager screens and workflows.
- Verify with a regression test that closing the main ChurchManager window closes
  every owned child form and dialog without leaving hidden processes or database
  connections open.
- Audit remaining dynamically constructed SQL and external-command strings;
  replace value interpolation with parameterized SQL and validated argument lists
  before a public release.
- Build a repeatable new-install and upgrade process.
- Ask which hymnals and lectionary systems the congregation wants installed.
- Review available Orders of Service and ask which starter templates should be installed.
- Permit multiple selections and an explicit "None" choice for each catalog.
- Install only selected starter datasets.
- Choose the church's primary hymnal and default lectionary independently.
- Keep the installer denomination-neutral: LSB and its lectionaries are
  optional packages, not hard-coded requirements.
- Treat Orders of Service as a separate selectable catalog that may be associated
  with a hymnal or service book but may also use no hymnal.
- Research representative Lutheran and non-Lutheran service outlines, distinguish
  reusable structure from copyrighted full text, and import only content that may
  legally be distributed with ChurchManager.
- Preserve user-created Order of Service templates independently of installed
  starter packages and never replace weekly service copies during catalog updates.
- Install and verify database structure, numbered migrations, starter reports,
  starter screens, permissions, runtime dependencies, and the first master
  administrator.
- Certify installation against a fresh local database rather than a copy of the
  development database.
- Document ordinary backup and restore procedures and the complete-backup
  format.
- Perform a full fresh-install, upgrade, automatic-exit-backup, restore, and
  restart dress rehearsal using non-production data.
- Complete and sign off the
  [Accounting Go-Live Checklist](ChurchManager.Accounting.GoLive.Checklist.md),
  including opening balances, permissions, audit behavior, representative
  reports, period controls, backup/restore evidence, and the exact approved
  release commit or tag.
- Confirm the permanent backup location is separate from MariaDB's data storage
  and from the same local-storage failure domain.
- The obsolete historical development SQL tree and database model have been
  removed from the current source tree; numbered migrations are authoritative.
- Before configuring any public Git remote, purge the removed private SQL exports
  from local Git history, verify they are absent from every reachable commit, and
  retain a private recovery backup outside the public repository.
- Reconcile specification status labels and operational documentation with the
  implemented source so completed work is not presented as merely proposed and
  current backup/restore behavior is described accurately.

### 6. Pastoral follow-up

- Create follow-up items from attendance warnings or manually.
- Assign a follow-up to the pastor, an elder, or another authorized caregiver.
- Record contact attempts, outcome, next-follow-up date, and completion.
- Protect pastoral notes with a separate sensitive permission.
- Show actionable overdue follow-ups without exposing confidential detail on
  the main menu.
- Provide a printable or exportable authorized follow-up list.

### 7. Import, export, and duplicate management

- Add a central Data Management screen.
- Import people and families from CSV with a preview and explicit field mapping.
- Detect likely duplicate people, families, email addresses, and phone numbers.
- Require review before merging records.
- Export only approved datasets and always enforce unlisted/private contact
  restrictions.
- Record import results, rejected rows, and export history.
- Provide a complete portable archive format where appropriate.

### 8. Groups, committees, classes, and ministry teams

- Add general groups independent of worship-participant roles.
- Support leaders, members, group roles, active dates, notes, and categories.
- Accommodate boards, committees, Bible studies, Sunday school, choir,
  confirmation, altar guild, outreach, and temporary teams.
- Permit group attendance and authorized group communication.
- Add group rosters and participation reports.

### 9. Volunteer availability and responses

- Add participant availability and blockout dates.
- Send explicit serve requests and reminders.
- Record accepted, declined, and pending responses.
- Show last-served information and scheduling conflicts.
- Preserve manual scheduling and small-congregation flexibility.
- Consider optional scheduling suggestions, but never silently replace existing
  assignments.

### 10. Confidential contributions and pledges

- Design this as a separate confidential subledger with its own permissions.
- Support contribution batches, donor accounts, funds/designations, pledges,
  non-cash gifts, corrections, and year-end statements.
- Import contribution files where practical.
- Post summarized, balanced deposits into fund accounting without exposing
  donor identity in the general ledger.
- Specify privacy, retention, audit, backup, and statement-delivery rules before
  implementation.

### 11. General events and calendar integration

- Add non-worship events with one-time or recurring dates.
- Support simple invitations, RSVP/registration lists, attendance, and notes.
- Integrate with Google Calendar rather than duplicating a complete calendar
  platform.
- Consider simple room or resource reservations only when a demonstrated need
  exists.

### 12. Custom profile fields and controlled tags

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
