# ChurchManager Current Release Readiness

Status date: August 26, 2026

This is the current-state companion to the historical evidence retained in the
installation specification and roadmap.

## Current verified baseline

- Application line: `0.3.0-beta.1`
- Canonical schema: 120 represented migrations
- Starter data: 122 statements
- Schema SHA-256: `f95153beb456e8ab25064476299fb466a7a675550e15069c814c7ec78d3f6ad4`
- Starter-data SHA-256: `73fc5604c3afe1920f8b240dd98a98ad1c41ccf268541eee718ee870e824329a`
- Fresh setup, guarded upgrade, and guarded restore services have passed
  isolated live rehearsals. Restore acceptance includes confidential Giving
  contributor and envelope records.

## Accepted workflows

- The complete source suite passes: 1,038 tests, 25 intentional
  database/environment skips, and zero failures on August 26, 2026.
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

## Public beta publication

- The audited source repository is public at
  `https://github.com/jwattswhat/ChurchManager`.
- Release `v0.3.0-beta.1` provides distinct clean-installation and fictional
  beta-test kits.
- The approved static project site, exact application screenshots, release
  links, documentation links, support route, privacy statement, and licensing
  notice are live at `https://jwattswhat.github.io/ChurchManager/`.
- The website and release describe the build as beta and do not claim that the
  remaining production-only or packaging-only gates have passed.

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
