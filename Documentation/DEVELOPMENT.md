# ChurchManager development guide

## Safe environment

Use `ChurchManager-Test.bat`, `.runtime-venv`, and `ChurchDBTest`. Confirm the
window title identifies test mode before changing data. Production `ChurchDB`
is never a development target.

Install or refresh dependencies from `requirements-runtime.txt`. Credentials
belong in Windows Credential Manager. Local connection files, OAuth tokens,
dumps, generated output, and logs are ignored and must remain untracked.

Before building or exercising the fresh-install workflow, run the read-only
readiness inspector:

```powershell
.\.runtime-venv\Scripts\python.exe inspect_installation_readiness.py
```

It checks the runtime, MariaDB command-line tools, free space, and bundled
catalog packages. It does not connect to a database, request a credential, or
change the computer. A valid catalog may be shown as blocked when a required
package, such as its associated hymnal, is not yet bundled.

## Resetting routine test activity

`reset_test_activity.py` preserves congregation, membership, users,
permissions, choices, installed catalogs, report and screen definitions, and
accounting setup. It removes Worship Services and their dependent attendance,
weekly orders, participants, hymn usage, reading snapshots, and checklist
results. It also removes accounting transactions, attachments, bank-import
activity, reconciliations, budgets, and accounting audit events, then reopens
the retained fiscal years and periods.

The command is restricted to local `ChurchDBTest`. Without `--apply` it only
prints counts. With `--apply` it first creates and SHA-256-verifies a complete
SQL dump under `BackupDB/ChurchDBTest.pre-activity-reset`.

```powershell
.\.runtime-venv\Scripts\python.exe reset_test_activity.py
.\.runtime-venv\Scripts\python.exe reset_test_activity.py --apply
```

## Database changes

Add the next numbered SQL migration and make it repeat-safe where practical.
Never edit a migration after it has been recorded as applied. Run:

`migration_service.py` is the reusable migration engine used by both the
development command and the future setup executable. It accepts an already-open
connection and never discovers a target or credential. Target safety remains
the caller's responsibility; `run_churchdb_migrations.py` therefore retains its
strict ChurchDBTest-only guard.

`database_provisioning.py` is reserved for the fresh-install setup workflow. It
refuses an existing database, requires exact-name confirmation, and initially
creates only a local MariaDB application account scoped to the new database.
Automated tests use fake connections; live acceptance must use a newly named,
isolated database and must never target ChurchDB or ChurchDBTest.

The numbered migrations preserve upgrade history; they are not an empty-
database bootstrap sequence. In particular, migration 001 expects the original
tables to exist. Fresh installation therefore uses a separately reviewed,
versioned baseline schema and records the exact migration checksums represented
by that baseline before applying newer pending migrations.

Never promote an unreviewed schema-only dump into the baseline. Run the
schema-hygiene checks for obsolete identifiers such as `OldID`, retired
conversion structures, test fixtures, account definers, and machine-specific
values. A finding must be removed or explicitly documented and approved.
The reusable enforcement is in `schema_hygiene.py`; baseline generation must
call `require_clean_schema` before writing an accepted release artifact.

Generate the candidate deterministically from the fully migrated local test
schema. The command previews and validates by default; `--write` creates
`installation/baseline_schema.sql` and its checksum/migration manifest:

```powershell
.\.runtime-venv\Scripts\python.exe generate_installation_baseline.py
.\.runtime-venv\Scripts\python.exe generate_installation_baseline.py --write
```

The export is structure-only. It verifies the complete migration ledger first
and never places the database password on the process command line.

Preview the disposable live acceptance target without connecting to MariaDB:

```powershell
.\.runtime-venv\Scripts\python.exe accept_fresh_install_baseline.py
```

With `--apply`, the command prompts privately for the local MariaDB root
password, creates a uniquely named `CMFreshAcceptance_...` database and scoped
account, installs and verifies the baseline, and removes both temporary objects.
It refuses cleanup unless both identifiers carry the acceptance-only prefixes.
Never use `--keep` except for a specifically reviewed isolated inspection.

```powershell
.\.runtime-venv\Scripts\python.exe run_churchdb_migrations.py --apply
```

Close ChurchManager before structural migrations. Review the reported target
before approval and verify the resulting workflow with isolated test records.

## Verification

```powershell
.\.runtime-venv\Scripts\python.exe run_churchmanager_tests.py
```

Then perform focused GUI verification. Tests intentionally avoid operational
database writes, mail, calendar operations, restores, and visual judgment.
Rendered reports must be inspected for clipping, wrapping, pagination, privacy,
and starter/custom fallback.

### User Guide

`Documentation/ChurchManager.UserGuide.md` is the maintained user-facing source.
After every user-visible workflow or label change, update that source and rebuild
the PDF that the main-menu **Help - User Guide** control opens:

```powershell
python tools\build_user_guide.py
```

The final artifact is `output/pdf/ChurchManager.UserGuide.pdf`. Render every
page to images and inspect it before release. The installer must place the same
verified PDF in its documented application resources; it must not generate a
different guide during setup.

## Documentation maintenance

Documentation is shipped behavior. Every change should review:

- `README.md` for installation or capability changes;
- `ChurchManager.Application.md` for runtime and operational changes;
- `DATABASE_STRUCTURE_INVENTORY.md` and migration docs for schema changes;
- `SCREEN_INVENTORY.md` for screen ownership or replacement;
- `ChurchManager.UserGuide.md` and its rendered PDF for user-visible changes;
- the applicable specification for policy or workflow changes;
- security and support guidance for sensitive behavior; and
- version notes for releases or compatibility changes.

Python module and public-interface docstrings must be updated with the code.
Labels in documentation, JSON, database choices, screens, and reports should use
the same user-facing term.

## Release preparation

Remove `-dev` only for a supported release. Run all tests, apply migrations to a
fresh test database, exercise backup and restore, inspect representative reports,
review ignored sensitive files, and confirm ChurchManager and required JSForm
versions are documented together.
