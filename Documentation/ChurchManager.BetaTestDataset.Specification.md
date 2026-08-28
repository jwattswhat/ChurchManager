# ChurchManager Beta Test Dataset Specification

Status: Packaged optional beta component implemented; isolated end-to-end acceptance pending
Dataset identifier: `churchmanager-beta-test-data`  
Current dataset version: `1.1.0`

## 1. Purpose

ChurchManager beta testers need the same fictional, internally consistent data
so defects can be reproduced and reports can be compared. This package is
separate from the ordinary installation seed. A real congregation installation
must never receive fictional beta records unless the installer explicitly
chooses the beta dataset.

## 2. Safety boundary

- Installation or reset requires an explicit **Install Fictional Beta Test
  Dataset** choice and a second confirmation naming the target database.
- The target must be local MariaDB, must not be `ChurchDB`, and must not have
  production mode enabled.
- Reset creates and verifies a complete SQL backup before deleting data.
- The normal setup path remains unchanged and clean.
- Dataset records use fictional names, addresses, email domains, references,
  account numbers, and document names. No real congregation or donor data is
  packaged.
- The dataset package contains no passwords. Setup asks the tester to establish
  the Master Administrator password through the normal secure workflow.

## 3. Installation and reset behavior

The beta installer may offer the dataset after the baseline database, Master
Administrator, and selected public catalog packages have been installed. The
same dataset service is available later from protected setup maintenance.

Two operations are supported:

1. **Install into a fresh beta database** - verify the database contains only
   baseline/setup records, then add the fictional dataset.
2. **Reset an existing beta database** - create a verified backup, remove all
   prior beta activity in dependency order, and reinstall the exact versioned
   dataset.

The operation is transactional after the backup. Failure rolls back the data
changes and reports the failed stage. A successful run prints or displays the
dataset version, record counts, verification results, and backup location.

## 4. Canonical fictional organization

- Congregation: Reformation Lutheran Church
- Location: Wittenberg, Minnesota
- Clearly marked test logo and `example.invalid` contact addresses
- Complete accounting organization, open fiscal year and periods, chart of
  accounts, funds, functions, bank account, and approved giving purposes

## 5. Required coverage

### People, families, and security

- Several households with adults, children, addresses, phone/email examples,
  dates, photos, and both listed and unlisted contact examples
- At least one outside participant and one outside contributor who have no
  member/person record
- Representative inactive record
- Role coverage for Pastor/Staff, Treasurer/Giving Administrator, Volunteer,
  Auditor, and report/design permissions without packaging known passwords

### Worship and attendance

- Installed redistributable lectionary and available hymnal metadata
- Order of Service templates and weekly service examples
- Hymn selections, required/open participant positions, preparation checklist,
  attendance event, members present/absent, and visitor counts
- Prayers and announcements with natural-language schedules

### Accounting

- Balanced opening and operating transactions across the test fiscal year
- Posted, Ready, and Draft examples
- Bank-import and reconciliation samples, budget, and year-end-ready scenario
- No confidential Giving identity in general-ledger descriptions or audit JSON

### Giving

- Person, family, and outside contributors plus anonymous gifts
- Envelope assignments, approved purposes, split gifts, Draft and Ready batches
- Posted contributions in all four quarters
- At least two statement-eligible contributors per quarter
- One intentionally ineligible gift that must be excluded from statements
- One description-only non-cash gift that appears without value on a statement
- Four Posted memorial/honor gifts covering every independent donor-name and
  amount-disclosure consent combination
- Privacy-safe summarized accounting transactions linked to Posted batches
- No pre-issued statement history; testers create issuance and revision records
  during acceptance

### Reports and designers

- Sufficient rows to exercise multi-page, all/single selection, empty-state,
  confidential, accounting, attendance, worship, and Giving reports
- Starter report/screen definitions remain recoverable; a small number of
  clearly blue-marked custom examples may be included for designer testing

## 6. Verification manifest

The package contains a machine-readable manifest with:

- dataset ID and semantic version;
- compatible ChurchManager schema/release range;
- ordered installation stages;
- expected minimum/exact counts by subsystem;
- invariant queries for foreign keys, balanced accounting, statement quarters,
  anonymous/outside records, and unlisted-contact suppression; and
- SHA-256 hashes of the package source and manifest.

Installation succeeds only when all manifest checks pass. Automated acceptance
must install the package into an isolated fresh database, verify it, reset it,
verify it again, and remove the isolated database.

## 7. Release handling

The dataset is source-controlled but excluded from ordinary baseline seed SQL.
Updating the dataset does not require changing normal installation defaults. A
dataset version change and its verification manifest are committed together.

The canonical manifest is `TestData/BetaDataset/manifest.json`. Its ordered
stages use the existing guarded reset/seed services, each of which refuses
non-local production targets.

Release `0.3.0-beta.2` provides two folders built from the same MSI:

- **Clean-Installation** contains only the ordinary installer and never loads
  fictional congregation records.
- **Beta-Test-With-Fictional-Data** contains the same installer plus guarded
  launchers for installing the version-matched dataset into local
  `ChurchDBTest` and starting ChurchManager in test mode.

The packaged beta utility does not contain shared ChurchManager login
passwords. The tester creates the Master Administrator through the normal
setup workflow.
