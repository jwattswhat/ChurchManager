# ChurchManager development guide

## Safe environment

Use `ChurchManager-Test.bat`, `.runtime-venv`, and `ChurchDBTest`. Confirm the
window title identifies test mode before changing data. Production `ChurchDB`
and the frozen ChurchManager-Legacy directory are never development targets.

Install or refresh dependencies from `requirements-runtime.txt`. Credentials
belong in Windows Credential Manager. Local connection files, OAuth tokens,
dumps, generated output, and logs are ignored and must remain untracked.

## Database changes

Add the next numbered SQL migration and make it repeat-safe where practical.
Never edit a migration after it has been recorded as applied. Run:

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

## Documentation maintenance

Documentation is shipped behavior. Every change should review:

- `README.md` for installation or capability changes;
- `ChurchManager.Application.md` for runtime and operational changes;
- `DATABASE_STRUCTURE_INVENTORY.md` and migration docs for schema changes;
- `SCREEN_INVENTORY.md` for screen ownership or replacement;
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
