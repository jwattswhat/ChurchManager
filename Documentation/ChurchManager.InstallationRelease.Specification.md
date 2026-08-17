# ChurchManager Installation, Upgrade, and Beta Release Specification

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
6. Apply every numbered migration in order and verify their checksums.
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

## 5. Catalog selection

The selection screen groups packages by Hymnals, Lectionaries, and Orders of
Service. Each entry displays title, version, publisher or source, distribution
scope, notice, dependencies, and whether it is already installed.

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
- the application and JSForm schema/resources are compatible;
- exactly one initial active master administrator exists;
- selected packages and dependencies are installed at the selected versions;
- unselected optional packages were not installed;
- starter screens and reports validate;
- the application can authenticate and open its main menu;
- a nonempty SQL backup was created and its SHA-256 digest verified; and
- test mode cannot send email.

The report contains no credentials or confidential congregation data.

## 8. Beta testing

After a clean-install and upgrade dress rehearsal, ChurchManager enters a
bounded beta phase. Beta builds use a versioned release candidate and provide a
sample database plus task-based scripts for pastors, office staff, worship
planners, treasurers, and one-person administrators.

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
3. Add guarded database/account creation and migration execution.
4. Add first-master-administrator creation.
5. Add transactional catalog installation and congregation defaults.
6. Add the nontechnical wizard around the tested services.
7. Add backup proof, final verification, and safe failure recovery.
8. Exercise fresh install, upgrade, repair, and restore in isolated databases.
9. Prepare the beta kit and complete beta acceptance.

## 10. Acceptance criteria

The installation work is complete when a nontechnical administrator can install
ChurchManager on a clean supported computer without development files or manual
SQL, log in with the new master account, use only the catalogs selected during
setup, create and restore a verified backup, and receive an accurate readiness
report. The same release must upgrade the preceding supported version without
losing congregation data, custom layouts, custom templates, audit history, or
saved weekly service snapshots.
