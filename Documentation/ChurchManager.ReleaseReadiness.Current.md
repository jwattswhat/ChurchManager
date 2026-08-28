# ChurchManager Current Release Readiness

Status date: August 28, 2026

This is the current-state companion to the historical evidence retained in the
installation specification and roadmap.

## Current verified baseline

- Application line: `0.3.0-beta.2`
- Canonical schema: 121 represented migrations
- Starter data: 125 statements
- Schema SHA-256: `f95153beb456e8ab25064476299fb466a7a675550e15069c814c7ec78d3f6ad4`
- Starter-data SHA-256: `288316835c44f9dd2a5f5646350baf9fe60bf74e10326458979593d761db5352`
- Fresh setup, guarded upgrade, and guarded restore services have passed
  isolated live rehearsals. Restore acceptance includes confidential Giving
  contributor and envelope records.

## Accepted workflows

- The complete source suites pass: 1,063 ChurchManager tests with 25 intentional
  database/environment skips, and 399 JSForm tests with 2 intentional skips.
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
- Release `v0.3.0-beta.2` is being prepared with distinct clean-installation
  and fictional beta-test kits. Public installer downloads remain halted until
  the final MSI upgrade/uninstall acceptance passes.
- The approved static project site, exact application screenshots, release
  links, documentation links, support route, privacy statement, and licensing
  notice are live at `https://jwattswhat.github.io/ChurchManager/`.
- The website and release describe the build as beta and do not claim that the
  remaining production-only or packaging-only gates have passed.

## Remaining release gates

- Same-version beta MSI upgrade and uninstall ownership acceptance
- Code signing
- Independent clean-machine installation and visual acceptance

The local Windows MSI, repair flow, installed login, main menu, Documents
screen, registered document opening, and isolated fresh-database baseline have
been exercised successfully. Code signing and independent-computer acceptance
remain distinct from these local checks.

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
