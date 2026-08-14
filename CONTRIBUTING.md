# Contributing to ChurchManager

ChurchManager welcomes changes that make congregational administration safer,
clearer, and more useful to small churches.

## Project boundaries

- Work only in this ChurchManager repository and its documented JSForm
  dependency.
- Never modify or depend on the frozen ChurchManager-Legacy project.
- Develop against `ChurchDBTest`, never production `ChurchDB`.
- Put reusable form, layout, report, value-conversion, and designer behavior in
  JSForm. Keep church workflows, permissions, database schema, and domain rules
  in ChurchManager.

## Workflow

1. Describe the user workflow and acceptance behavior.
2. Add a forward-only migration for database changes; never edit an applied
   migration.
3. Add or update automated tests.
4. Update relevant user, developer, database, screen, and specification docs.
5. Run `python run_churchmanager_tests.py`.
6. Verify changed GUI workflows using isolated data and record what was checked.

## Code documentation standard

- New Python modules need a module docstring.
- Public classes, services, repositories, dialogs, and functions need useful
  docstrings covering their contract and important side effects.
- Add comments for policy, security, accounting, privacy, or migration decisions
  whose reason is not obvious from the code.
- Prefer type hints on service boundaries and data structures.
- Do not add redundant comments that merely translate Python into English.
- User-visible behavior changes and renamed fields must update documentation in
  the same commit.

## Safety and data handling

Use parameterized SQL and transactions for multi-step writes. Authorization and
audit rules belong in service code, not only in buttons. Never commit passwords,
OAuth tokens, database dumps, logs, generated reports, or member information.
Financial operations require the safeguards described in the accounting
specifications and must be tested only in isolated data.

## Licensing contributions

By contributing, you agree that your contribution is licensed under
GPL-3.0-or-later, the license used by ChurchManager.
