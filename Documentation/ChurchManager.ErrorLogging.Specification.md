# ChurchManager error logging and support specification

**Status:** Approved

**Date:** August 14, 2026

**Approved by:** Rev. Jonathan C. Watt

**Target application:** Development ChurchManager

**Framework dependency:** JSForm centralized error reporting

**Excluded application:** Independent Frozen ChurchManager

## 1. Purpose

ChurchManager shall integrate the centralized JSForm error-reporting service so
unexpected Python, wxPython, database, report, background-operation, and
external-tool failures are recorded consistently and can be supplied safely to
support.

ChurchManager will provide application-specific context, workflow boundaries,
test/production classification, menu integration, and privacy rules. JSForm
will provide the underlying capture, redaction, rotation, error dialog, and
support-package facilities.

This specification applies only to the current development ChurchManager
project. It must not read, modify, launch, or install files in the independent
Frozen ChurchManager project.

## 2. Dependency

Implementation depends on the approved version of:

[JSForm centralized error logging and support package specification](../../JSForm/Documentation/JSForm.ErrorLogging.Specification.md)

If the specifications conflict, ChurchManager may impose stricter privacy or
authorization rules, but it may not weaken JSForm's mandatory redaction,
bounded storage, or no-automatic-transmission rules.

## 3. Goals

1. Record unexpected ChurchManager failures with complete Python tracebacks.
2. Give the user a short error ID and understandable next step.
3. Capture errors consistently across ordinary forms, ChurchManager-only
   workflows, reports, accounting, attendance, worship planning, backup and
   restore, and application shutdown.
4. Distinguish development/test operation from production operation without
   exposing credentials.
5. Create a safe support package that the user controls and deliberately saves.
6. Prevent church records, financial details, pastoral notes, passwords, and
   database contents from entering diagnostic logs.
7. Preserve existing security and accounting audit requirements independently.

## 4. Non-goals

ChurchManager error reporting shall not:

- send email or upload logs automatically;
- replace security, accounting, posting, reconciliation, backup, or restore
  audit records;
- record successful ordinary operations merely for diagnostic purposes;
- include database dumps, report PDFs, attachments, images, bulletins, sermons,
  or email messages in support packages;
- expose raw SQL parameters or current screen-field values;
- recover or continue after an operation whose transactional state is unknown;
- access the Frozen ChurchManager application or its database configuration;
- permit a test support operation to connect to or alter production data.

## 5. Ownership boundary

### JSForm owns

- unhandled Python, wxPython, and worker-thread exception hooks;
- structured JSONL log records and traceback capture;
- mandatory redaction and error-ID generation;
- rotating local log files and retention cleanup;
- the standard recoverable/fatal error dialog;
- support-package assembly, hashing, and ZIP verification;
- public reporting APIs and framework tests.

### ChurchManager owns

- installing the JSForm service during application startup;
- supplying the ChurchManager name, version, and safe operation names;
- classifying the active database as test, production, or unknown;
- deciding which workflow boundaries report caught exceptions;
- adding ChurchManager-specific redaction rules;
- deciding whether a failed operation may continue or requires restart;
- placing **Support and Diagnostics** on the main menu;
- ChurchManager integration and privacy tests;
- end-user support instructions.

## 6. Startup integration

Error reporting must begin before ChurchManager attempts a database connection
so startup and credential-access failures can be diagnosed.

Required startup order:

1. Resolve the local ChurchManager application-data directory.
2. Configure JSForm error reporting with application name `ChurchManager` and
   error-ID prefix `CM`.
3. Install the Python main-thread and worker-thread hooks.
4. Create the wxPython application and install the wx event-loop integration.
5. Load the ChurchManager version from one authoritative version source.
6. Attempt credential retrieval and database connections.
7. Classify database scope using the resolved database name and existing
   production/test safeguards.
8. Add only the approved safe session context after login succeeds.
9. Construct and show the main menu.

Failure to determine a version or database scope must not disable logging. The
record shall use `unknown`.

## 7. Approved ChurchManager context

ChurchManager may attach only these standard fields:

| Field | Example | Rule |
|---|---|---|
| `application_mode` | `test` | `test`, `production`, or `unknown`. |
| `database_name` | `ChurchDBTest` | Name only; no server, port, username, or connection string. |
| `screen` | `UnifiedWorshipServiceEditor` | Stable class/form name only. |
| `operation` | `worship_service.save` | Stable allowlisted operation name. |
| `authenticated` | `true` | Boolean only. |
| `permission_scope` | `accounting.post` | Permission being evaluated, never the full role or grant set. |
| `record_type` | `WORSHIP_SERVICE` | Type name only. |
| `record_id` | `42` | Optional numeric identifier; never record contents. |
| `transaction_state` | `rolled_back` | Approved state label only. |
| `external_tool` | `mariadb-dump` | Executable product name only, not its full command line. |

The application user ID, username, display name, church name, workstation name,
email address, phone number, and IP/server address are excluded by default.
They may not be added merely for convenience. If future support experience
proves one necessary, this specification must be revised and approved first.

## 8. ChurchManager-specific redaction

In addition to JSForm's mandatory rules, ChurchManager shall redact:

- database service usernames and passwords;
- Windows Credential Manager targets and returned secrets;
- SMTP usernames, passwords, application passwords, recipient addresses, and
  message bodies;
- church, family, person, participant, visitor, and user contact information;
- unlisted phone, address, and email data;
- pastoral, prayer, announcement, sermon, journal, document, and task text;
- hymn or publisher content that may be copyrighted;
- transaction descriptions, references, attachments, payees, donor identities,
  amounts when embedded in exception text, and accounting before/after values;
- backup command arguments, temporary credential files, and restore paths when
  they reveal private usernames or locations.

File paths shall be reduced to a safe application-relative component or a
filename when practical. User-profile directory names shall be replaced with
`[USERPROFILE]` before serialization or export.

## 9. Operation boundaries

ChurchManager shall use stable operation names. At minimum, explicit reporting
boundaries shall cover:

### 9.1 Application and ordinary forms

- `application.startup`
- `application.login`
- `application.main_menu`
- `application.shutdown`
- `form.open`
- `form.load`
- `form.save`
- `form.delete`
- `form.linked_open`

Ordinary JSForm form behavior should be captured by framework boundaries where
possible. ChurchManager must not duplicate the same exception at both the
framework and dispatcher levels.

### 9.2 Worship and attendance

- `worship_service.open`
- `worship_service.save`
- `worship_template.apply`
- `weekly_order.save`
- `participants.assign`
- `checklist.update`
- `attendance.open`
- `attendance.save`
- `attendance.report`

### 9.3 Reports and designers

- `report.dataset`
- `report.render`
- `report.preview`
- `report.export`
- `report_designer.open`
- `report_designer.save`
- `screen_designer.open`
- `screen_designer.save`

### 9.4 Accounting

- `accounting.draft.save`
- `accounting.approve`
- `accounting.post`
- `accounting.reverse`
- `accounting.bank_import`
- `accounting.reconcile`
- `accounting.budget.save`
- `accounting.period_close`
- `accounting.year_end_close`

Accounting exceptions shall include transaction state such as `not_started`,
`rolled_back`, `committed`, or `unknown`. If commit status is unknown, the user
must be told not to repeat the operation until the record is reviewed.

### 9.5 Backup, restore, and external tools

- `database.backup`
- `database.backup_verify`
- `database.restore_prepare`
- `database.restore`
- `database.restore_verify`
- `external_tool.execute`

The external command line, environment, database password, and dump contents
must never be logged. Exit code and a redacted, bounded diagnostic excerpt may
be recorded. Restore-related logs must remain usable after ChurchManager closes
its database connections.

## 10. Error classification and recovery

### Recoverable

Examples include a failed report preview, rejected file import, or failure to
open a supporting screen when no transaction was started. ChurchManager may
keep the application open after recording the error and clearly explaining
what did not complete.

### Operation-aborted

The operation failed but its transaction is confirmed rolled back. The user may
return to the screen and correct or retry the operation.

### Restart required

Examples include database connections intentionally closed for restore, lost
database session state, failed application initialization, or a failure after
which screen state cannot be trusted. ChurchManager shall close child windows
and request restart.

### State unknown

If the application cannot determine whether a financial, restore, or other
material operation committed, it shall not invite an immediate retry. The user
message shall request record review or support assistance and show the error ID.

Application cancellation, expected validation, permission denial, and the user
answering No to a confirmation are not exceptions.

## 11. User interface

The main menu shall include **Support and Diagnostics** within ChurchManager
Settings. It shall open a simple screen containing:

- the location of the diagnostic logs;
- the most recent error ID and time, when available;
- **Create Support Package**;
- **Open Log Folder**;
- a plain-language statement that packages are not sent automatically;
- a plain-language list of what the package includes and excludes;
- Close.

All authenticated users may create a support package because a user who
encounters an error must be able to provide it. Opening the raw log folder may
also be allowed locally, but logs must not reveal protected application data.
Deleting or changing logs through ChurchManager is not required.

Unexpected-error dialogs shall use JSForm's standard presentation and may add a
ChurchManager-specific next step. They shall never show a Python traceback to
the ordinary user.

## 12. Storage

Default location:

```text
%LOCALAPPDATA%\ChurchManager\Logs\
```

Support packages default to:

```text
%USERPROFILE%\Documents\ChurchManager\Support\
```

The user may choose another package destination. Logs must not default to:

- the ChurchManager source directory;
- the Frozen ChurchManager directory;
- MariaDB's data directory;
- the database backup directory;
- a report or attachment directory.

JSForm's default 2 MiB rotation, five retained files, and 30-day retention apply
unless later evidence supports an approved change.

## 13. Support-package contents

ChurchManager may add one generated file named
`churchmanager-diagnostics.json` containing only:

- ChurchManager version;
- JSForm version;
- schema migration numbers applied and pending;
- database scope and database name;
- counts of active form/report starters and customizations;
- whether required runtime components are available;
- last successful backup timestamp, but not its path or contents;
- safe feature flags required for diagnosis.

It must not include table contents, migration SQL, user/role lists, audit rows,
report definitions, screen definitions, credentials, or full filesystem paths.

The package shall be created locally, verified, and left for the user to send
through a separately chosen support channel.

## 14. Audit separation

Diagnostic logs and support packages are not ChurchManager audit records.

- Security events continue to use the security audit service.
- Accounting events continue to use the accounting audit service.
- Posting, approval, reversal, close, reopen, backup, and restore audit rules do
  not change.
- An error record may contain the corresponding audit event identifier only if
  it is a non-sensitive stable identifier and the audit event already exists.
- Failure of diagnostic logging must not prevent a required audit record from
  being written, and failure of auditing must not be treated as successfully
  completed merely because it was logged diagnostically.

## 15. Test and production isolation

- ChurchDBTest is always classified as test.
- ChurchDB is always classified as production in the development application's
  safety logic, regardless of the application's displayed mode.
- Support-package creation is read-only and may not open another database.
- Automated tests may use only temporary logs and approved test databases.
- No automated error test may connect to production ChurchDB.
- The development application must not use error logging to inspect or modify
  the Frozen ChurchManager project.

## 16. Testing requirements

ChurchManager tests shall deliberately trigger fictional failures at these
boundaries:

1. startup before a database connection exists;
2. login and credential retrieval;
3. ordinary JSON form open and save;
4. ChurchManager-only wxPython button handler;
5. worker-thread/background operation;
6. report dataset and renderer;
7. worship-service transaction rollback;
8. attendance save rollback;
9. accounting posting rollback and unknown-state simulation;
10. backup executable failure;
11. restore after active database connections are released;
12. support-package generation with a locked destination;
13. normal shutdown and restart-required shutdown.

The test suite shall inject fictional passwords, tokens, email addresses,
person names, pastoral notes, financial descriptions, and user-profile paths.
None may appear anywhere in the resulting log or ZIP bytes.

Tests must also prove that one failure creates one diagnostic occurrence rather
than duplicate framework and application records.

## 17. Acceptance criteria

The ChurchManager integration is complete when:

1. Logging begins before the first database connection attempt.
2. Python, wxPython, worker-thread, database, report, accounting, backup, and
   restore test failures produce searchable error IDs and complete redacted
   tracebacks.
3. Ordinary users see a short explanation and never a raw traceback.
4. Recoverable, rolled-back, restart-required, and unknown-state failures show
   the correct next step.
5. The Support and Diagnostics screen creates and verifies a local package.
6. The package is never transmitted automatically.
7. Injected private and credential values are absent from logs and packages.
8. Diagnostic logging works when the ChurchManager database is unavailable or
   intentionally disconnected.
9. Security and accounting audit tests continue to pass independently.
10. Test/production guards and the Frozen-project boundary remain intact.
11. JSForm and ChurchManager automated suites pass.
12. The user approves the error dialog and Support and Diagnostics screen.

## 18. Implementation sequence

1. Approve and implement the JSForm error-reporting specification.
2. Add one authoritative ChurchManager version source.
3. Install logging at the beginning of ChurchManager startup.
4. Add the approved context provider and ChurchManager redactors.
5. Wrap high-risk ChurchManager service and dispatcher boundaries without
   double-reporting.
6. Add Support and Diagnostics to ChurchManager Settings.
7. Add safe ChurchManager diagnostics to support packages.
8. Run deliberate failure, redaction, transaction-state, and isolation tests.
9. Complete user acceptance and update the application manual.
