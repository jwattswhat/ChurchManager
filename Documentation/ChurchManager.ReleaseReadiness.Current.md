# ChurchManager Current Release Readiness

Status date: August 30, 2026

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

- The complete source suites pass: 1,099 ChurchManager tests with 25 intentional
  database/environment skips, and 460 JSForm tests with 2 intentional skips.
- The owned-child cleanup regression confirms tracked JSForm child forms close
  and deleted native panels are safely ignored during application shutdown.
- The source-construction audit reports 39 reviewed structural SQL exceptions,
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
- Release `v0.3.0-beta.2` has distinct clean-installation and fictional
  beta-test kits. Local and independent Windows 11 VM installation, same-version upgrade, uninstall,
  reinstall, login, main-menu, Documents-screen, and registered document-opening
  acceptance passed. The release is ready for public beta publication.
- The approved static project site, exact application screenshots, release
  links, documentation links, support route, privacy statement, and licensing
  notice are live at `https://jwattswhat.github.io/ChurchManager/`.
- The website and release describe the build as beta and do not claim that the
  remaining production-only or packaging-only gates have passed.

The accepted compact all-button dashboard was rebuilt into the exact beta.2
bundle on August 30, 2026. The corrected bundle contains 466 files totaling 111,273,487
bytes and bundles JSForm `0.1.0-beta.6`. All three packaged resource proofs
passed, including an explicit check for `Menus/main.menu.json`. The rebuilt MSI
is 51,878,318 bytes with SHA-256
`5cdf22ee8b95062f12ae3475726dc04c50fa6c5b1c0c281791bc64bc68f18ef4`.
The clean-installation and fictional-beta release kits were regenerated from
that exact MSI.

## Deferred distribution enhancement

- Code signing is deliberately deferred for the current small, informed beta.
  The unsigned installer must be distributed only through the official project
  release page with its published SHA-256 checksum. Public-trust signing should
  be reconsidered before broad public adoption.

Independent clean-machine installation and visual acceptance passed on August
30, 2026 in a clean Windows 11 25H2 Hyper-V VM. The rehearsal established that
MariaDB Server and its client/backup tools are external prerequisites. MariaDB
12.3.2 LTS was installed from its official, signature-verified Windows MSI.
The first ChurchManager bundle exposed a missing `Menus/main.menu.json`
packaging defect; the bundle specifications and packaged resource proof were
corrected, a same-version replacement MSI was installed, and the user accepted
the resulting application visually. The VM retains a clean pre-ChurchManager
checkpoint for repeat acceptance.

The source GUI milestone separately passed guarded database and packaged
profiles plus manual review of Login, Participant Notifications, Project Plan,
and Asset Editor on August 30, 2026. Login review geometry was corrected before
acceptance. Automated desktop capture remains environment-incompatible and no
screenshot-regression baseline is claimed.

After the accepted main-dashboard width adjustment, unattended packaged GUI
automation passed again against the final corrected rebuilt executable: package proof,
temporary fictional login, compact main-screen discovery, accessible-name
keyboard activation of Projects and Scheduling, native Projects-window
detection and closure, clean application exit, and temporary-login cleanup.
The embedded `frmMain` proof reports a `52x40` form, 32 native buttons, and
14-character-unit action widths.

The local Windows MSI, same-version upgrade, uninstall, reinstall, repair,
installed login, main menu, Documents screen, registered document opening,
configuration preservation, and isolated fresh-database baseline have been
exercised successfully. On August 30, 2026, the repair rehearsal moved the
installed `ChurchManagerBetaData.exe` aside, ran Windows Installer `/fa`,
verified that the restored SHA-256 exactly matched, and verified that the
writable Local AppData configuration SHA-256 was unchanged. The verbose log is
`dist/msi-beta2-repair.log`. No installer-validation gate remains for the
current bounded beta; public-trust code signing is a deferred distribution
enhancement.

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
