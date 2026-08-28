# ChurchManager Installation, Upgrade, and Beta Release Specification

Current implementation evidence is summarized in
[ChurchManager Current Release Readiness](ChurchManager.ReleaseReadiness.Current.md).
The dated 0.2.0 and 84-migration figures below are retained as historical beta
acceptance evidence; they are not the current 0.3.0-dev baseline.

**Status:** Approved

**Date:** August 17, 2026

**Scope:** Fresh installation, upgrades, catalog selection, recovery validation,
and beta-release qualification for ChurchManager

## 1. Purpose

ChurchManager needs one repeatable, nontechnical installation process. It must
create a clean application database, establish the first master administrator,
install only the catalogs the congregation chooses, and prove that backup and
restore work before the installation is accepted.

The installer must not depend on ChurchDBTest, copied development data, or any
previous ChurchManager installation.

## 2. Safety boundaries

1. Fresh installation creates a new explicitly named database. It never
   overwrites an existing database.
2. Upgrade operates only on a recognized ChurchManager database after a
   verified backup.
3. Restore is a separate protected operation and is never an implicit response
   to an installation error.
4. Test and production credentials, attachments, logs, backups, and database
   names remain separate.
5. Passwords are entered privately and are never written to plans, logs,
   diagnostics, command lines, or configuration files.
6. Package installation is transactional and uses the existing validators.
7. A failed stage leaves either the previous valid state or a clearly identified
   incomplete new database that can be safely removed and retried.
8. Installation never imports congregation records unless the user separately
   selects a reviewed import or restore operation.

## 3. Supported workflows

### 3.0 Windows packaging boundary

ChurchManager shall use a signed traditional Windows Installer (`.msi`) package
for application-owned files, shortcuts, version registration, repair, upgrade,
and uninstall. The MSI may be produced with WiX or another standards-compliant
Windows Installer toolchain.

The MSI and the ChurchManager Setup Wizard have separate responsibilities:

- the MSI installs the ChurchManager application, its compatible JSForm runtime,
  bundled Python runtime and dependencies, icons, shortcuts, and uninstaller;
- the Setup Wizard configures MariaDB, congregation information, the first
  master administrator, catalogs, writable data locations, and backup proof.

The Setup Wizard is titled **ChurchManager Installation** and displays the
approved horizontal ChurchManager banner above its page headings. This is an
installer presentation treatment only; it does not replace the application
icon, congregation branding, shortcuts, website identity, or product colors.
The installed wizard must construct successfully against the bundled wxPython
runtime before applying its preferred window size. Its page area must remain
large enough to show the full banner, instructions, readiness results, and
navigation controls without clipping.
The packaged resource proof must also verify every runtime component used by
the Setup Wizard readiness check so a dependency present only in development
cannot produce a false installation block.

The installed user-facing entry points are `ChurchManager.exe` for ordinary
operation and `ChurchManagerSetup.exe` for first-run or protected maintenance
setup. Both include the compatible Python and JSForm runtime; an end user does
not install Python, activate a virtual environment, or run a batch file.

Uninstalling ChurchManager must not delete a congregation database, attachments,
backups, custom reports, custom screens, or other congregation-owned data.
Application binaries are installed in a protected program location. Mutable
preferences, logs, attachments, backups, and user customizations are stored in
documented writable data locations rather than beside installed binaries.

MSIX is not the initial packaging target because ChurchManager is a traditional
desktop application that coordinates an external database, helper programs, and
writable operational resources. It may be reconsidered only after the MSI-based
release is stable and an identified distribution need justifies it.

### 3.1 Fresh installation

The installer shall:

1. Check the operating system, runtime, free space, MariaDB availability, and
   required external tools.
2. Collect the congregation name and proposed database name.
3. Confirm that the database does not already exist.
4. Test an administrative MariaDB connection without retaining its credential.
5. Create the database and a least-privilege ChurchManager database account.
6. Install the release's checksum-protected canonical baseline schema, record
   the numbered migrations represented by that baseline with their exact
   checksums, and then apply any later pending migrations in order. Historical
   upgrade migrations are not assumed to create an empty database.

The baseline is not accepted merely because a schema-only export succeeds. A
schema-hygiene gate must reject obsolete compatibility residue, including
`OldID` columns, retired source-conversion fields, retired tables, obsolete
JSForm database structures, test-only objects or defaults, database-account
definitions, machine-specific paths, and object definers tied to a development
account. Any exception must be named, justified, and approved; broad words such
as "legacy" in a current identifier are treated as a finding rather than being
silently retained.
7. Create the first master administrator with a temporary password that must be
   changed at first login.
8. Present separately selectable hymnal, lectionary, and Order of Service
   packages, including an explicit **None** choice for every catalog family.
9. Explain dependencies before confirmation. An Order of Service package that
   requires a hymnal cannot be installed unless that hymnal is selected or
   already installed.
10. Install only the confirmed packages.
11. Let the congregation choose its primary hymnal and default lectionary from
    the installed catalogs, independently; either may remain unset.
12. Install and validate starter screens, reports, permissions, choices, and
    required JSForm resources.
13. Create the attachment, backup, log, and local-preference directories with
    appropriate user access.
    Installed configuration is copied from a non-secret application template
    into `%LOCALAPPDATA%\ChurchManager`; development continues to use the
    repository configuration. The installed executable never needs to modify
    files under Program Files.
14. Create and verify a first SQL backup.
15. Run a readiness check and present a plain-language completion report.

### 3.2 Upgrade

The upgrader shall identify the installed application and schema versions,
preview pending migrations and package changes, create and verify a backup,
apply changes in a deterministic order, and run post-upgrade checks. It shall
not silently add optional catalogs or replace congregation-created templates.

### 3.3 Repair

Repair may reinstall application-owned runtime files, starter definitions, or
permissions after validation. It does not alter congregation data or reset
custom layouts without a separate, explicit choice.

## 4. Installer stages and resumability

The process uses named stages:

1. **System Check**
2. **Database Connection**
3. **Congregation Setup**
4. **Master Administrator**
5. **Catalog Selection**
6. **Installation Review**
7. **Install and Verify**
8. **Backup Proof**
9. **Finish**

Before database creation, Back and Cancel are always safe. After database
creation begins, Cancel finishes or rolls back the active transaction and
records the incomplete stage. A password-free installation journal may store
stage names, versions, checksums, timestamps, and safe error identifiers so the
installer can explain whether retry or cleanup is appropriate.
If a fresh installation fails, the visible error identifies the failed stage
and reports a password-redacted underlying cause after cleanup.
When setup refuses a pre-existing database or account before creating anything,
the message states that no existing data was changed rather than claiming that
an incomplete database was removed.
Configuration saving normally uses atomic replacement. On Windows systems that
permit updating an existing owned configuration file but deny replacement of
its directory entry, setup falls back to a bounded in-place update and removes
the completed temporary copy.
Installed launchers accept JSForm only from their own packaged `_internal`
bundle. Source development continues to require the separate adjacent JSForm
project, and neither mode accepts the Frozen application's framework copy.
Windows packages include MySQL Connector's English localization data, and the
supported Connector authentication plugins, and the noninteractive package
check verifies both the English error module and `mysql_native_password` before
release.
An installed launch with no explicit database arguments resolves its server,
database, framework database, port, and account from the saved production
configuration. Explicit command-line values remain available for supported
administrative use and test mode retains its isolated configuration.
Starter-data extraction preserves approved bounded temporary helper tables when
later catalog mutations in the same migration depend on them.

## 5. Catalog selection

The selection screen groups packages by Hymnals, Lectionaries, and Orders of
Service. Each entry displays title, version, publisher or source, distribution
scope, notice, dependencies, and whether it is already installed.
The three package lists and both default selectors remain fully visible within
the supported installer page size on a standard Windows display. Field labels
use their native positive text height so packaged Windows builds paint the
complete label without overlap.

The installer must not imply that owning a printed publication authorizes
distribution of protected text or music. Packages remain metadata-only and are
subject to the approved hymnal, lectionary, and Order of Service specifications.

Package files are validated before they appear as installable. An invalid,
unapproved, locally restricted, or dependency-incomplete package is identified
clearly and cannot be silently installed.

## 6. First master administrator

The first administrator supplies a unique username, display name, optional
contact information, and temporary password. The installer creates the active
master account and role assignment atomically. `MustChangePassword` remains set
until the first successful password change.

The installer recommends creating a second master administrator after initial
login but does not require it for a small congregation.

## 7. Verification report

Successful installation requires evidence that:

- all numbered migrations are applied with expected checksums;
- the installed baseline schema version and checksum match the release;
- the baseline schema-hygiene scan reports no unapproved obsolete identifiers,
  retired structures, test fixtures, account definers, or machine-specific
  values;
- the application and JSForm schema/resources are compatible;
- exactly one initial active master administrator exists;
- selected packages and dependencies are installed at the selected versions;
- unselected optional packages were not installed;
- starter screens and reports validate;
- the version-matched User Guide PDF is installed and opens from the main menu;
- the application can authenticate and open its main menu;
- a nonempty SQL backup was created and its SHA-256 digest verified; and
- test mode cannot send email.

The report contains no credentials or confidential congregation data.

## 8. Beta testing

After a clean-install and upgrade dress rehearsal, ChurchManager enters a
bounded beta phase. Beta builds use a versioned release candidate and provide a
sample database plus task-based scripts for pastors, office staff, worship
planners, treasurers, and one-person administrators.

ChurchManager officially entered beta testing on August 17, 2026 as release
`0.2.0-beta.1`. Beta findings are corrected on the existing development line,
covered by regression tests, and recorded in the maintained fix list.

Feedback is recorded in one maintained list with environment, reproducible
steps, safe diagnostic ID, severity, resolution, and regression result. A
tester database or confidential record is accepted only with explicit
permission and a documented secure transfer and deletion plan.

The beta is complete only when:

1. no release-blocking defect remains unresolved;
2. fresh installation and upgrade from the preceding beta both pass;
3. backup, restore, restart, and automatic-exit backup pass;
4. representative core workflows and official reports are accepted;
5. documentation matches the delivered behavior; and
6. the exact release commit and version are identified.

## 9. Implementation sequence

1. Build a read-only readiness inspector and package inventory. **Completed.**
2. Build and test an installation plan model with dependency validation.
   **Completed.**
3. Add guarded database/account creation and migration execution. The reusable
   checksum-verified migration service and guarded fresh-database provisioner
   are complete. Isolated live acceptance passed on August 17, 2026.
4. Generate, review, and checksum a canonical current baseline schema that is
   independent of development data, account definers, and machine-specific
   paths; scan it for obsolete compatibility structures such as `OldID`; prove
   that it creates an empty database and establishes accurate migration history.
   The fail-closed schema-hygiene scanner and deterministic structure-only
   generator are complete. The 0.2.0-dev candidate and manifest have been
   generated and independently checked. The guarded disposable-database command
   installed and verified the candidate and its separate non-congregation
   starter-data baseline against local MariaDB on August 17, 2026, then removed
   its isolated database and account successfully. The accepted seed contains
   67 statements and established 43 active permissions.
5. Add first-master-administrator creation. **Completed and accepted against an
   isolated fresh database on August 17, 2026.**
6. Add transactional catalog installation and congregation defaults.
   **Completed.** Hymnal, lectionary, and Order of Service packages use their
   validated transactional importers; dependencies are checked before
   installation; and primary hymnal and default lectionary choices are stored
   independently and may remain unset.
7. Add the nontechnical wizard around the tested services. **Implemented for
   safe preview and development acceptance.** The wizard covers system checks,
   local database credentials, congregation identity, the first Master
   Administrator and optional contact information, optional catalog selection,
   a password-free review, guarded installation, cleanup, and verification.
   Visual acceptance remains. The isolated service-level `--apply` dress
   rehearsal passed August 17, 2026.
8. Add backup proof, final verification, and safe failure recovery.
   **Implemented.** A fresh installation creates a labeled SQL dump, verifies
   its database identity, minimum size, table definitions, and SHA-256 digest,
   and includes the proof in its password-free completion report. Database and
   account creation are removed after incomplete setup; configuration and the
   Windows credential are restored together if final persistence fails.
9. Exercise fresh install, upgrade, repair, and restore in isolated databases.
   The complete fresh-install service rehearsal passed August 17, 2026. It
   created an isolated database and least-privilege account, installed 138
   database objects, represented 84 migrations, established 43 active
   permissions, created and authenticated the initial Master Administrator,
   installed the distributable historic one-year lectionary, verified a
   277,721-byte first backup and its SHA-256 digest, and then removed the
   isolated database, account, and backup. A guarded upgrade service now
   previews immutable migration history, requires and verifies a pre-upgrade
   backup, applies only pending migrations through the same approved conversion
   hooks as the migration runner, and preserves the backup if verification
   fails. The isolated upgrade rehearsal passed August 17, 2026: it detected
   exactly one acceptance-only pending migration, verified a 277,823-byte
   pre-upgrade backup and SHA-256 digest, applied and re-verified the change,
   and removed the disposable database, account, and backups. The isolated
   restore rehearsal passed August 17, 2026: it restored a deliberately changed
   congregation record from the verified first-install backup, verified all 84
   migration records, verified the pre-restore safety backup, and removed all
   disposable resources. The repair rehearsal remains.
10. Prepare the beta kit and complete beta acceptance. The reproducible
    PyInstaller 6.21 shared onedir build for `ChurchManager.exe` and
    `ChurchManagerSetup.exe` is implemented. Both packaged executables passed
    the noninteractive resource proof on August 17, 2026: release 0.2.0-dev,
    34 forms, 84 migrations, two catalog packages, and no missing required
    resources. The combined release folder contains 390 files totaling
    88,067,288 bytes. WiX v5 MSI source now defines per-machine installation,
    major-upgrade protection, application and setup shortcuts, and an
    application-file-only uninstall boundary. The first compiled MSI was
    decompiled successfully on August 17, 2026 and contained all 390 release
    files, 390 components, both entry-point executables, and all three intended
    shortcuts. The verified repeat build was 37,025,537 bytes with SHA-256
    `55ada55b111a8f4ed562c7615446f3fbec037617527551cb735cc455f52c8c67`.
    ICE validation could not run because the Windows Installer service was
    unavailable on the development computer; clean-machine ICE validation,
    MSI repair rehearsal, signing, and visual acceptance remain.
11. Ship the visually verified, version-matched User Guide PDF and verify the
    main-menu Help control on an installed build.

## 10. Acceptance criteria

The installation work is complete when a nontechnical administrator can install
ChurchManager on a clean supported computer without development files or manual
SQL, log in with the new master account, use only the catalogs selected during
setup, create and restore a verified backup, and receive an accurate readiness
report. The same release must upgrade the preceding supported version without
losing congregation data, custom layouts, custom templates, audit history, or
saved weekly service snapshots.
