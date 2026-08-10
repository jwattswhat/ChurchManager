# ChurchManager automated tests

This folder contains safe automated checks for ChurchManager-owned modules and
assets. The suite does not connect to ChurchDB, launch the graphical application,
send email, access Google Calendar, generate reports, or test JSForm internals.

Run from the ChurchManager folder:

```powershell
python run_churchmanager_tests.py
```

The initial suite checks:

- compilation of operational ChurchManager Python modules;
- controlled date and week-of-month logic used by prayers and announcements;
- participant-role list conversion and order-of-service placeholder helpers;
- sermon DOCX-to-Blogger text conversion using disposable test documents;
- required ChurchManager configuration structure without printing credentials;
- parsing and basic structure of all ChurchManager `Forms/*.json` definitions;
- local targets for open-file and linked-form actions, file-picker directories,
  and main-menu controls bound by `cm.py`;
- XML validity and code uniqueness of LimeReport patterns.

A passing run ends with `OK` and returns exit code 0. A failing run identifies the
specific module or asset and returns exit code 1.

Manual database, graphical workflow, email, calendar, PDF-content, sermon-link,
backup, and restore tests remain in `Documentation/ChurchManager.Testing.Procedures.docx`.

## Optional read-only test-database checks

Database checks are disabled by default. They use direct read-only queries and do
not use JSForm. The safety guard refuses a database named `ChurchDB` and requires
the database name to contain `test`.

Confirm Windows Credential Manager contains `ChurchManager/Test`, then enable
the read-only checks:

```powershell
$env:CHURCHMANAGER_RUN_DB_TESTS = "1"
python run_churchmanager_tests.py
```

Connection settings come from `churchmanager.json`; the password comes from the
`ChurchManager/Test` Windows Credential Manager entry. Never put it in an
environment variable or command line. A missing or mismatched credential stops
the test before connecting.

The database layer verifies required operational tables, sermon ID integrity,
report-code uniqueness, report-template availability, and basic table readability.
It performs no inserts, updates, deletes, email, calendar, or file changes.
