# ChurchManager development guide

## Safe environment

Use `ChurchManager-Test.pyw`, `.runtime-venv`, and `ChurchDBTest`. Confirm the
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

`reset_giving_test_data.py` replaces only the confidential Giving subsystem in
local `ChurchDBTest`. It creates a verified pre-reset SQL dump, removes any
user-entered Giving records and their linked summarized accounting transaction,
then installs the maintained fictional Giving acceptance dataset. Prior
statement-issuance identifiers are removed before contributors so this remains
a repeatable beta-test reset. Preview and apply it with the commands below.
Batch dates are derived from open fiscal periods so all four quarterly
statement paths and the Ready accounting handoff can be exercised.

`reset_worship_test_services.py --seed` replaces Worship Services and their
dependent weekly Orders of Service in local `ChurchDBTest`. It creates three
fictional services covering complete, planned, and incomplete weekly plans;
participant responses; one intentional availability conflict; preparation
checklists; and a completed attendance count. Like the other guarded resets, it
creates and verifies a complete SQL backup before changing data. Run it without
an action first to review the current counts.

```powershell
.\.runtime-venv\Scripts\python.exe reset_giving_test_data.py
.\.runtime-venv\Scripts\python.exe reset_giving_test_data.py --apply
```

```powershell
.\.runtime-venv\Scripts\python.exe reset_worship_test_services.py
.\.runtime-venv\Scripts\python.exe reset_worship_test_services.py --seed
```

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
Required non-congregation starter records are maintained separately in
`installation/baseline_seed.sql` and its manifest. The seed is deterministically
derived from approved catalog mutations in immutable migrations plus explicitly
reviewed current-schema worship roles. It must never contain a church, person,
family, user, activity record, test fixture, or optional hymnal, lectionary, or
Order of Service package.

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

The normal suite includes the deterministic `gui-structural` profile for Login,
Participant Notifications, Project Plan, and Asset Editor. Run it alone with:

```powershell
.\.runtime-venv\Scripts\python.exe -m unittest tests.test_gui_structural -v
```

This profile constructs native wxPython windows, checks stable control
identities and geometry, exercises representative guarded behavior, and cleans
up its windows. It does not use a live database, compare approved screenshots,
exercise an installed package, or establish human visual acceptance. Those
profiles remain explicit release checks.

To attempt unapproved visual candidates under the canonical Windows profile:

```powershell
.\.runtime-venv\Scripts\python.exe generate_gui_visual_candidates.py
```

Results go to the ignored `.gui-test-artifacts\visual-candidates` directory.
Uniform black capture, failure of the bounded Windows fallback capture,
incompatible scaling, or unavailable interactive desktop state is reported as
environment-incompatible. Unusable images are removed. This command never
creates, updates, or approves a version-controlled baseline.

When desktop capture is unavailable, present the same four fictional-data
screens sequentially for human inspection:

```powershell
.\.runtime-venv\Scripts\python.exe generate_gui_visual_candidates.py --review
```

Close each screen to advance to the next. The command records no approval; the
reviewer must explicitly report whether the screens are visually accepted.

The write-capable database profile requires explicit opt-in and the configured
LocalTestAdmin credential:

```powershell
$env:CHURCHMANAGER_GUI_DATABASE='1'
.\.runtime-venv\Scripts\python.exe run_gui_database_profile.py
```

It refuses non-local, non-`ChurchDBTest`, and production credential targets.
The fictional Project Plan save is read back through `ProjectService`, while
repository commits are suppressed and the entire scenario is rolled back.
Missing protected credentials produce a recorded skip before connection.

The packaged profile always verifies the current development bundle's packaged
resources. Native UI driving is an explicit opt-in and uses the separately
pinned test-only dependency:

```powershell
.\.runtime-venv\Scripts\python.exe -m pip install -r requirements-gui-test.txt
$env:CHURCHMANAGER_GUI_PACKAGED='1'
.\.runtime-venv\Scripts\python.exe run_gui_packaged_profile.py
```

The runner accepts only `dist\ChurchManagerBundle\ChurchManager.exe`, uses the
protected LocalTestAdmin database credential, creates a temporary fictional
application login, verifies the authenticated main window, exits, and removes
the temporary login. It focuses the accessible Projects and Scheduling button
by stable name, presses Enter, detects and closes the native child window, and
then exits. Missing automation support or credentials is recorded as a skip;
the Frozen application is never an eligible target.

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

### Windows executable bundles

Install the development-only builder from `requirements-build.txt`, then create
the shared release folder containing both entry points:

```powershell
.\.runtime-venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --distpath dist --workpath build packaging\ChurchManagerBundle.spec
```

The results are `dist\ChurchManagerBundle\ChurchManager.exe` and
`dist\ChurchManagerBundle\ChurchManagerSetup.exe`, sharing one compatible
runtime. Before constructing an MSI,
run each executable with `--package-check <evidence.json>` and require a zero
exit code plus `"passed": true`. The check is noninteractive, opens no database,
and verifies the release number, forms, schema, seed, migrations, catalogs,
report definitions, and User Guide. Build output is reproducible release input
and is not committed.

`packaging\ChurchManager.wxs` is the maintained WiX v5 source for the
traditional per-machine MSI. It harvests the verified bundle, creates ordinary
and protected-setup shortcuts, supports major upgrades, and owns no database,
backup, attachment, custom definition, preference, or log location.
Because prerelease labels are not represented in Windows Installer's numeric
version, same-version upgrades are enabled so a corrected beta MSI replaces an
earlier build instead of creating parallel product registrations.

With the repository-local .NET and WiX tools installed, the complete Windows
release build is one command:

```powershell
.\.runtime-venv\Scripts\python.exe build_windows_release.py
```

The command rebuilds the shared bundle, runs the noninteractive proof through
both executables, builds the versioned MSI, and writes
`dist\windows-release-evidence.json` with byte counts and the MSI SHA-256.
WiX ICE validation additionally requires the Windows Installer service; run it
on the clean Windows acceptance computer before release signing.

Remove `-dev` only for a supported release. Run all tests, apply migrations to a
fresh test database, exercise backup and restore, inspect representative reports,
review ignored sensitive files, and confirm ChurchManager and required JSForm
versions are documented together.
