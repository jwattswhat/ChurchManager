# ChurchManager architecture

ChurchManager is an application built on JSForm.

```text
wxPython application and main menu
  -> ChurchManager dialogs and domain services
       -> authorization and audit policy
       -> worship, attendance, communication, and accounting rules
       -> report dataset providers
       -> migrations and MariaDB data
  -> JSForm public APIs
       -> JSON forms, controls, layouts, choices, designers, and rendering
```

## Ownership boundary

| Concern | Owner |
| --- | --- |
| Generic JSON controls, layout, designers, report renderer | JSForm |
| Congregational schema and migrations | ChurchManager |
| User roles, permissions, privacy rules, audit policy | ChurchManager |
| Worship, attendance, communications, and accounting workflows | ChurchManager |
| Starter and customized ChurchManager forms/reports | ChurchManager assets using JSForm formats |

## Application composition

`cm.py` is the entry point. Startup creates an `ApplicationContext`, database
connections, authentication and authorization services, error reporting, the
form factory, reporting services, and the main menu. JSON forms handle regular
record editing. ChurchManager-owned dialogs implement workflows that require
domain-specific coordination or validation.

## Data evolution

The database is changed only through ordered files in `migrations`. The runner
records checksums and refuses an applied migration whose contents changed.
Create a new migration to correct prior behavior. Test and production database
identities remain explicit so a test dump cannot silently replace production.

## Security and reporting

Authorization is enforced in ChurchManager services and menu visibility.
Reports consume approved datasets or safe database views rather than arbitrary
SQL. Unlisted contact information must never enter a report dataset. Accounting
posting, reversal, close, and restore operations keep independent validation and
auditing even when a small congregation uses a single authorized person.

For the detailed runtime description, see
[`ChurchManager.Application.md`](ChurchManager.Application.md).
