# ChurchManager development roadmap

Last reviewed: August 17, 2026

This is the maintained ChurchManager development backlog. Priorities reflect
the needs of a small congregation and a comparison with current paid and
open-source church-management systems.

## Authoritative priority sequence

| Order | Priority | Project | Reason for placement |
|---:|---|---|---|
| 1 | Completed | User contact information | Foundational contact fields and administration are implemented. |
| 2 | Completed | Email and participant notification review | The weekly participant-notification workflow has been modernized. |
| 3 | In acceptance | Optional user-to-person relationship | Source, migration, administration UI, safe auditing, and welcome email are implemented; database and visual acceptance remain. |
| 4 | Immediate | Secure SMTP connection and email settings | Welcome and participant email require deliberate, testable, credential-safe configuration. |
| 5 | In progress | Hymnal, lectionary, and Order of Service catalogs | Order of Service packaging is implemented; permanent hymn IDs and hymnal packaging are in database acceptance, followed by lectionary packaging. |
| 6 | Immediate | Release, installation, and recovery readiness | Stabilizes and packages the researched catalogs and existing application. |
| 7 | Next | Pastoral follow-up | Highest-value ministry addition and a natural extension of attendance. |
| 8 | Next | Import, export, and duplicate management | Protects data quality and makes adoption and recovery practical. |
| 9 | Next | Groups, committees, classes, and ministry teams | Adds the most broadly missing congregational structure. |
| 10 | Next | Volunteer availability and responses | Builds on the completed worship scheduling foundation. |
| 11 | Later | Confidential contributions and pledges | Valuable, but requires a separate privacy-sensitive specification and subledger. |
| 12 | Later | General events and calendar integration | Useful, but Google Calendar should remain the primary calendar platform. |
| 13 | Later | Custom profile fields and controlled tags | Adds flexibility after the core normalized relationships are settled. |
| Triggered | Conditional | Secure remote access and two-factor authentication | Require a safely configured VPN for desktop access and 2FA for any future remote, browser, or member-access design. |

Items 1 through 6 should be completed before beginning a new major subsystem.
Items 7 through 10 form the next ministry-development phase. Items 11 through 13
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

### 4. Secure SMTP connection and email settings

- Approved design: [Secure SMTP connection specification](ChurchManager.SMTPConnection.Specification.md).
- Review findings: [SMTP connection review](ChurchManager.SMTPConnection.Review.md).
- Move authentication secrets out of database configuration and into Windows
  Credential Manager with strict test/production separation.
- Add a protected Email Settings screen, offline validation, and an explicit
  confirmed test-email workflow.
- Require TLS, safe failure categories, redacted diagnostics, and one shared
  mail factory for welcome and participant messages.
- Revoke and remove any credential exposed in development source before testing
  the replacement.
- Implemented: migration 071 stores only non-secret settings, the protected
  Email Settings screen manages the Windows credential, and mail entry points
  fail closed before database, credential, or network access in test mode.
- Remaining deployment action: revoke any historical provider credential that
  may remain in repository history and enter a new application password through
  Email Settings outside test mode.

### 5. Hymnal, lectionary, and Order of Service catalog design

#### Hymnal catalog and import workstream

- Migration 074, `hymnal_packages.py`, and `local_hymns.py` implement the
  permanent registry foundation, fail-closed LSB conversion, package preflight,
  transactional import, local 5,001-9,999 allocation, retirement, passive
  copyright/source metadata, and import/conversion logging.
- Migration 074 removes the former ChurchDBTest synthetic hymnals, their sample
  entries, and disposable worship-service data instead of assigning permanent
  identities to fixtures. It also removes LSB entries outside the approved
  printed-edition range of 1-966. The test-data seeder no longer creates a fake
  distributable hymnal.
- Hymnal and hymn titles are normalized to Title Case during conversion and
  package import. Common connecting words remain lowercase inside a title, and
  intentional uppercase abbreviations remain uppercase.
- Migration 074 is accepted on `ChurchDBTest`, and local hymn creation and
  retirement have passed visual acceptance. The deterministic LSB package
  builder and 636-row stanza-review ledger are implemented. Remaining catalog
  work is human verification of every printed stanza count; the builder refuses
  to publish the final package while any row remains pending or lacks evidence.

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
- The package loader, fail-closed metadata-only validator, reference exporter,
  additive versioned-catalog migration, and transactional package importer are
  implemented. Service-owned reading snapshots are implemented for newly saved
  services and used by the Worship Planning report. Installer integration,
  clean cutover, and candidate package provenance remain in progress. The
  bounded calendar resolver, explicit Worship Service candidate-selection UI,
  and protected package installation screen are implemented; approved package
  calendar data remains to be supplied. The provenance-gated reproducible
  package builder and authoring guide are implemented; no candidate package is
  approved merely by this tooling.
- The official CCT and CPH policies were reviewed August 17, 2026. Public LSB
  and RCL packages are blocked pending written electronic-redistribution
  permission. Narrow permission-request drafts and the local-only fallback are
  documented in `ChurchManager.LectionaryPackageProvenance.md`.
- The redistributable ChurchManager Historic One-Year Lectionary package is
  complete. It contains 62 Sundays and major days with 124 citation-only
  Epistle and Gospel appointments derived from the public-domain 1919 Common
  Service Book. The package manager opens in the included-package directory so
  an administrator can install it without locating an internal source folder.
- Remaining acceptance for the included package is installation through the
  protected package screen, selection as the church default edition, creation
  of a new Worship Service, and verification of its Proper, readings,
  liturgical date, color, and Worship Planning report.
- Migration 083 removes the obsolete required `tblLectionarySystem.OldID`
  column found on databases upgraded from the original application. Package
  installation now creates systems solely through their stable package keys.
- Migration 084 removes the corresponding obsolete required
  `tblReading.OldID` column. Imported citation appointments now use their stable
  package appointment keys without requiring an unused historical identifier.
- Church Information presents the primary hymnal and default lectionary as one
  aligned, consistently sized catalog-selection column rather than separate
  responsive-grid columns.
- Worship Service saving no longer references the removed
  `tblServiceBulletinOrder.GeneratedHtml` field. Weekly Orders of Service remain
  outline-only and invalidate only their permitted generated plain-text cache.
- Worship Service line actions now use the package-defined line type rather
  than an obsolete `SERVICE_HYMN` source value. Included Order of Service
  packages can select hymns and apply Proper readings and hymn suggestions
  while preserving exact suggested-use matching after harmless key formatting.
- Migration 081 removes the former LSB lectionary catalog, its dependent
  Propers/readings/suggestions, and related development service snapshots.
  Services themselves remain, with their Proper selection cleared. Obsolete
  production-import utilities were removed so the catalog cannot be
  accidentally reintroduced.
- Migration 082 clears all disposable worship-service records and their linked
  attendance events only when the active database is exactly `ChurchDBTest`.
  It is inert on every production or differently named database.
- Preserve the reviewed distribution scope inside every checksum-protected
  lectionary package and installed package record. `LOCAL_ONLY` is displayed in
  the package manager and cannot be silently treated as redistributable.
- Local Lectionaries now provides protected, nontechnical maintenance of
  congregation-owned systems, editions, cycles, Propers, and citation-only
  reading appointments, including automatic A/B/C cycles and reversible
  retirement. Appointment entry enforces the metadata-only boundary by storing
  biblical references rather than Scripture text.
- Local reading maintenance supports data-defined alternatives, tracks, option
  groups, defaults, and optional same-Proper response pairing. It prevents
  self-pairing and rejects pairings outside the active local Proper.
- An active installed edition can be copied into a new congregation-owned
  system and edition. The transaction assigns new local keys to every copied
  cycle, Proper, and appointment, remaps paired responses, and leaves the
  protected source and saved services unchanged.
  When no approved package edition is installed, the copy action is visibly
  disabled and explains that prerequisite instead of appearing to do nothing.
- Migration 080 completes the runtime cutover to an edition-only congregation
  default. Church Information presents one unambiguous active-edition selector,
  and Worship Planning no longer falls back to the obsolete system-level
  setting. Local appointment roles and citations are used when a Proper is
  applied.
- A future redistributable ChurchManager lectionary may provide independently
  authored three-year and one-year citation metadata, but it must not reproduce
  or claim to be Lutheran Service Book data. Exact publisher-specific editions
  remain local-only unless written electronic-redistribution permission is
  obtained.
- The current ChurchDBTest lectionary catalog is reference-only. Export it for
  citation, role, color, and hymn-suggestion reconciliation, then replace it
  cleanly; do not preserve its IDs or obsolete structure.
- Implement the
  [Lectionary Catalog Specification](ChurchManager.LectionaryCatalog.Specification.md),
  including stable package keys, flexible cycles, service-owned reading
  snapshots, local customization, and the hard metadata-only boundary.

#### Order of Service catalog workstream

- Approved companion design: [Order of Service Catalog Specification](ChurchManager.OrderOfServiceCatalog.Specification.md).
- Migrations 072-073, the metadata-only preflight validator, transactional
  importer, guarded installer, and complete 22-template/338-line LSB package
  implement the first Order of Service catalog. Fresh-install selection remains
  part of the release installer workstream.
- The LSB Order of Service package must include every supported LSB service
  outline, and imported names use the `LSB ` prefix. Future service-book packages
  use their own uppercase abbreviation followed by one space.
- Maintained scope inventory: [LSB Order of Service Package Inventory](ChurchManager.LSBOrderOfService.Inventory.md).
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

### 6. Release, installation, and recovery readiness

- Approved design:
  [Installation, Upgrade, and Beta Release Specification](ChurchManager.InstallationRelease.Specification.md).
- The read-only installation readiness inspector is implemented. It verifies
  the Windows/runtime prerequisites, MariaDB client and backup tools, free
  space, bundled package integrity, and unresolved catalog dependencies without
  opening a database, requesting a credential, or changing the computer.
- The password-free installation-plan engine is implemented. It validates the
  congregation, safe database and administrator identifiers, optional package
  selections, catalog dependencies, and independent default catalogs before
  any installation action is permitted.
- The numbered migration runner now delegates to a reusable checksum-verified
  migration service. The existing development command retains its strict
  ChurchDBTest target guard, while the future setup executable must supply its
  own explicitly opened fresh-database connection.
- Guarded fresh-database provisioning is implemented. It requires exact-name
  confirmation, refuses existing databases and accounts, creates a local
  database-scoped application account with a parameterized generated password,
  and cleans up only newly created resources if provisioning fails. It has not
  yet been exercised against a live isolated database.
- Fresh-install review confirmed that migration 001 assumes the original base
  tables and therefore cannot initialize an empty database. The installer must
  use a reviewed, checksum-protected canonical baseline schema, seed accurate
  migration history for the migrations represented by that baseline, and then
  apply only later pending migrations. Creating and verifying this baseline is
  the next release-readiness step.
- Baseline generation includes an explicit schema-hygiene gate for `OldID`,
  retired conversion fields and tables, obsolete JSForm database structures,
  test-only objects, development-account definers, and machine-specific values.
  Findings must be removed or individually documented and approved before a
  release baseline is accepted. The guarded baseline loader/installer now
  verifies the schema checksum and exact represented-migration ledger before
  operating and refuses a nonempty target database.
- The automated schema-hygiene gate is implemented and tested. It reports exact
  line numbers for obsolete identifiers and retired tables, test database
  names, account definers and grants, database-selection statements, fixture
  data, destructive dump statements, persisted auto-increment state, and
  machine-specific paths.
- The deterministic baseline generator is implemented. It operates only on
  fully migrated local ChurchDBTest, exports structure rather than records,
  keeps the database password off the process command line, canonicalizes
  permitted dump state, enforces schema hygiene, and produces a schema checksum
  plus the exact represented-migration ledger. Live candidate generation and
  review remain. The 0.2.0-dev candidate contains 84 represented migrations;
  its schema SHA-256 is
  `3333f3ade00a89c944462b95581990fa83612458ef31e49695296ecb4869e375`.
- Disposable live-baseline acceptance is implemented. It creates only a unique
  `CMFreshAcceptance_...` database and `cm_accept_...` local account, verifies
  the baseline and migration ledger through that account, and removes both on
  success or failure. Live acceptance passed August 17, 2026: 84 migration
  checksums and the canonical schema digest verified, and cleanup completed.
- The first task-oriented User Guide is maintained as Markdown and rendered as
  a visually inspected PDF. A signed-in **Help - User Guide** control opens it
  from the main menu without requiring an administrative permission. Installer
  packaging and installed-build acceptance remain.
- A guarded routine test-activity reset preserves the reusable ChurchDBTest
  baseline while clearing worship and accounting activity. It previews counts,
  creates and verifies a complete SQL backup, runs only against local
  `ChurchDBTest`, and verifies that every covered activity table is empty.

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
- Conduct a structured beta-testing phase after the fresh-install dress
  rehearsal and before the first stable release:
  - recruit a small group representing pastors, office staff, worship planners,
    treasurers, and congregations with one-person administration;
  - provide a documented test installation and sample database rather than any
    congregation's production records;
  - give testers task-based acceptance scripts covering installation, people,
    worship planning, attendance, reports, backup and restore, user security,
    and the accounting workflows appropriate to their role;
  - collect defects, usability observations, environment details, and safe
    diagnostic packages through one maintained feedback list;
  - classify findings as release-blocking, important, or post-release rather
    than expanding the beta without limit;
  - require explicit permission before receiving a tester's database or other
    potentially confidential congregation data;
  - repeat regression tests after every beta correction and verify upgrades
    from the prior beta build; and
  - define beta exit criteria: no unresolved release-blocking defects, clean
    installation and upgrade, verified backup and restore, accepted core
    workflows, reconciled documentation, and an identified release commit.
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

### 7. Pastoral follow-up

- Create follow-up items from attendance warnings or manually.
- Assign a follow-up to the pastor, an elder, or another authorized caregiver.
- Record contact attempts, outcome, next-follow-up date, and completion.
- Protect pastoral notes with a separate sensitive permission.
- Show actionable overdue follow-ups without exposing confidential detail on
  the main menu.
- Provide a printable or exportable authorized follow-up list.

### 8. Import, export, and duplicate management

- Add a central Data Management screen.
- Import people and families from CSV with a preview and explicit field mapping.
- Detect likely duplicate people, families, email addresses, and phone numbers.
- Require review before merging records.
- Export only approved datasets and always enforce unlisted/private contact
  restrictions.
- Record import results, rejected rows, and export history.
- Provide a complete portable archive format where appropriate.

### 9. Groups, committees, classes, and ministry teams

- Add general groups independent of worship-participant roles.
- Support leaders, members, group roles, active dates, notes, and categories.
- Accommodate boards, committees, Bible studies, Sunday school, choir,
  confirmation, altar guild, outreach, and temporary teams.
- Permit group attendance and authorized group communication.
- Add group rosters and participation reports.

### 10. Volunteer availability and responses

- Add participant availability and blockout dates.
- Send explicit serve requests and reminders.
- Record accepted, declined, and pending responses.
- Show last-served information and scheduling conflicts.
- Preserve manual scheduling and small-congregation flexibility.
- Consider optional scheduling suggestions, but never silently replace existing
  assignments.

### 11. Confidential contributions and pledges

- Design this as a separate confidential subledger with its own permissions.
- Support contribution batches, donor accounts, funds/designations, pledges,
  non-cash gifts, corrections, and year-end statements.
- Import contribution files where practical.
- Post summarized, balanced deposits into fund accounting without exposing
  donor identity in the general ledger.
- Specify privacy, retention, audit, backup, and statement-delivery rules before
  implementation.

### 12. General events and calendar integration

- Add non-worship events with one-time or recurring dates.
- Support simple invitations, RSVP/registration lists, attendance, and notes.
- Integrate with Google Calendar rather than duplicating a complete calendar
  platform.
- Consider simple room or resource reservations only when a demonstrated need
  exists.

### 13. Custom profile fields and controlled tags

- Allow authorized administrators to define optional person and family fields
  or tags.
- Keep common values controlled and searchable.
- Include privacy and report-export behavior in each field definition.
- Avoid using arbitrary custom fields where a normalized ChurchManager
  relationship is more appropriate.

### Conditional: secure remote access and two-factor authentication

- Two-factor authentication is not required for the current local-only use.
- Require it as part of any future remote, browser, or member-portal project.
- Include recovery codes, administrative recovery, auditing, and clear account
  ownership rules in its specification.
- For remote use of the desktop application, recommend a professionally and
  safely configured VPN appropriate to the congregation's network. Keep the
  recommendation vendor-neutral.
- Never expose MariaDB, its administration port, Windows file sharing, or an
  unrestricted remote-desktop service directly to the public internet.
- Require least-privilege VPN accounts, encrypted transport, revocable access,
  endpoint updates, and documented removal of access when a user leaves a role.
- A VPN protects the network path but does not replace individual ChurchManager
  accounts, application permissions, database least privilege, auditing, or
  future 2FA requirements.

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
