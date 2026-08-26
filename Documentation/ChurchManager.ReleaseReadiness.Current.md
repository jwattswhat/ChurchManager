# ChurchManager Current Release Readiness

Status date: August 26, 2026

This is the current-state companion to the historical evidence retained in the
installation specification and roadmap.

## Current verified baseline

- Application line: `0.3.0-beta.1`
- Canonical schema: 95 represented migrations
- Starter data: 73 statements
- Schema SHA-256: `ef460b0f5f99d80b08a8ac8a992ef119ba88de42142081477cff16da8789277b`
- Starter-data SHA-256: `f551760bc150d50ba8d0c73850f6cf95c2325c1a2db37c655c0e145dad715795`
- Fresh setup, guarded upgrade, and guarded restore services have passed
  isolated live rehearsals. Restore acceptance includes confidential Giving
  contributor and envelope records.

## Accepted workflows

- The complete source suite passes: 800 tests, 25 intentional
  database/environment skips, and zero failures on August 22, 2026.
- The owned-child cleanup regression confirms tracked JSForm child forms close
  and deleted native panels are safely ignored during application shutdown.
- The source-construction audit reports 43 reviewed structural SQL exceptions,
  zero unexpected interpolated SQL sites, and zero `shell=True` execution sites.

- Accounting entry through reports, reconciliation, budgets, period controls,
  and year-end workflows were accepted using fictional test data.
- Giving entry, accounting transfer, corrections, imports, statements,
  disclosure controls, returned checks, merges, reports, and restore evidence
  were accepted.
- LimeReports is retired. Official reports use JSForm JSON definitions and the
  internal PDF renderer.

## Deliberately deferred until the next beta installer

- Rebuilding the MSI and packaged executables
- MSI repair rehearsal
- Code signing
- Clean-machine installation and upgrade visual acceptance

These packaging-only gates do not require rebuilding the installer during
ordinary beta correction work.

## Production-only gates

The Accounting Go-Live Checklist retains congregation-specific configuration,
opening balances, responsible-person assignments, final backup, and signatures
as unchecked production cutover work. Test acceptance must never be presented
as authorization to use a congregation's live books.

## Backup location rule

The selected permanent backup folder must not be inside the MariaDB data
directory. Prefer a separate physical device or independently protected network
location. `D:` is the approved development complete-backup destination; a real
installation must record its own destination and responsible person before
go-live.
