# ChurchDB schema migrations

Migration files are applied in numeric filename order and recorded in the
`schema_migrations` table with a SHA-256 checksum. Applied files are immutable;
create a new numbered migration for every later schema change.

The runner is deliberately restricted to the database configured as
`testing.database`. It refuses `ChurchDB` and any database name that does not
contain `test`.

Preview pending migrations:

```powershell
.\.runtime-venv\Scripts\python.exe run_churchdb_migrations.py
```

Apply them after creating and verifying a current backup:

```powershell
.\.runtime-venv\Scripts\python.exe run_churchdb_migrations.py --apply
```

Do not edit a migration after it has been applied. The checksum guard will stop
if an applied file changes.
