# ChurchManager

ChurchManager is a Windows desktop application for the administrative, worship,
membership, attendance, reporting, and fund-accounting work of a congregation.
It is written in Python, uses wxPython, stores data in MariaDB, and uses the
separately licensed JSForm framework for JSON-defined screens and reports.

## Project status

The authoritative development version is in
[`churchmanager_version.py`](churchmanager_version.py). ChurchManager is under
active pre-release development. Development and testing use `ChurchDBTest`;
production data must never be used as a development target.

This repository is a self-contained ChurchManager application. Runtime files,
configuration, database structures, tests, and launchers must remain within its
documented application and JSForm boundaries.

## Capabilities

- Congregations, families, people, contacts, and private-directory controls
- Worship services, orders of service, propers, hymns, sermons, and checklists
- Participant roles, scheduling, required positions, and notifications
- Attendance events, members, Communion, visitors, and follow-up reports
- Prayers and announcements with natural-language weekly schedules
- Projects, tasks, documents, journal entries, and assets
- User accounts, roles, permissions, auditing, and support diagnostics
- Fund accounting, bank import and reconciliation, budgets, and year-end close
- Visual screen and report customization built on JSForm
- Protected database backup and restore

## Development setup

ChurchManager uses a project-owned `.runtime-venv` and a local MariaDB test
database. Install the packages in [`requirements-runtime.txt`](requirements-runtime.txt)
into a fresh environment. Database structure is advanced by the ordered,
checksum-protected migrations in [`migrations`](migrations/README.md).

Start the development application with `ChurchManager-Test.bat`.

Never put passwords on a command line or in configuration committed to Git.
ChurchManager retrieves database secrets from Windows Credential Manager.

## Tests

Run the safe application suite from this directory:

```powershell
python run_churchmanager_tests.py
```

The default suite does not connect to a database, open the GUI, send messages,
or write operational data. See [`tests/README.md`](tests/README.md) for optional
read-only database checks and manual verification boundaries.

## Documentation map

- [User Guide source](Documentation/ChurchManager.UserGuide.md) - the application
  opens the maintained PDF edition from **Help - User Guide** on the main menu.
- [Installation, upgrade, and beta release specification](Documentation/ChurchManager.InstallationRelease.Specification.md)
- [Application guide](Documentation/ChurchManager.Application.md)
- [Architecture](Documentation/ARCHITECTURE.md)
- [Development guide](Documentation/DEVELOPMENT.md)
- [Database inventory](Documentation/DATABASE_STRUCTURE_INVENTORY.md)
- [Screen inventory](Documentation/SCREEN_INVENTORY.md)
- [LimeReports retirement](Documentation/ChurchManager.LimeReports.Retirement.md)
- [Migrations](migrations/README.md)
- [Versioning](Documentation/VERSIONING.md)
- [Public website specification](Documentation/ChurchManager.Website.Specification.md)
- [Visual identity specification](Documentation/ChurchManager.VisualIdentity.Specification.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Support](SUPPORT.md)
- [Specifications](Documentation/)

## Privacy

ChurchManager can contain personal contact information, attendance, pastoral
notes, financial records, credentials, and generated directories. Use fictional
or explicitly isolated data for development. Dumps, reports, support packages,
and logs must be treated as confidential until reviewed and redacted.

## License

Copyright (C) 2026 Rev. Jonathan C. Watt.

ChurchManager is licensed under the GNU General Public License v3.0 or later.
See [`LICENSE`](LICENSE). JSForm remains a separate LGPL-3.0-or-later dependency.
