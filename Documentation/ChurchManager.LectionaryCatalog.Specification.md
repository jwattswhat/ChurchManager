# ChurchManager Lectionary Catalog Specification

**Status:** Approved; implementation in progress

**Prepared:** August 16, 2026

**Scope:** Development ChurchManager lectionary catalogs, installer packages,
worship planning, and ChurchDBTest

**Out of scope:** Production ChurchDB

## 1. Purpose

Provide a denomination-neutral way to install, maintain, select, and use one or
more lectionaries without storing Scripture text or other published liturgical
content. A congregation installs only the catalogs it uses, selects a primary
lectionary, and may override that choice for an individual service.

The catalog supplies calendar identity, reading roles, biblical citations,
alternatives, pairings, colors, and planning metadata. ChurchManager uses those
records to prepare a weekly worship outline and preserve the selections actually
used.

## 2. Core decisions

1. Lectionaries are separately installable, versioned catalog packages.
2. Installation offers one or more approved packages and an explicit `None`
   choice.
3. Only installed catalogs are stored in the congregation database.
4. The church may select one installed edition as its primary lectionary.
5. A service may use a different installed lectionary or no lectionary.
6. Package schemas are denomination-neutral and do not hard-code LCMS, RCL,
   A/B/C, or any publisher into application logic.
7. Packaged appointments are protected starter data. Users may create local
   systems and appointments from scratch or copy packaged records into editable
   local records.
8. Applying a Proper creates service-owned reading selections. Later package
   changes cannot change a planned or historical service.
9. Lectionary packages and ChurchManager output contain references and planning
   metadata only, never full Scripture or liturgical text.

## 3. Terminology

| Term | Meaning |
|---|---|
| Package | The signed or checksum-verified installable catalog artifact |
| Lectionary system | A recognizable tradition or family, such as LSB Three-Year or RCL |
| Edition | A versioned publication or approved dataset within a system |
| Cycle | A named repeating division such as A, B, C, or a custom label |
| Proper | One Sunday, feast, festival, weekday, or other liturgical occasion |
| Appointment | One reading role and biblical citation belonging to a Proper |
| Option group | A set of mutually related choices or alternatives |
| Track | A sustained selection path, such as complementary or semicontinuous |
| Service selection | The reading appointment actually chosen for one service |
| Starter | Protected data installed from an approved package |
| Local record | A congregation-created editable record not owned by a package |

## 4. Stable identity

MariaDB integer keys remain local implementation keys. Distributed packages do
not depend on those integers having the same value in every database.

Every packaged entity instead carries an immutable, case-insensitive stable key:

```text
PackageCode       example: cct-rcl-1992
SystemCode        example: rcl
EditionCode       example: rcl-1992
CycleCode         example: A
ProperKey         example: advent-1
AppointmentKey    example: advent-1-a-gospel-default
```

Stable keys are unique within their documented scope. They are assigned by the
approved package manifest and cannot be changed or reused by an upgrade. Local
records use generated keys beginning with `local-` and can never claim an
official package namespace.

References between package records use stable keys during validation and import.
The installer resolves them to ordinary integer foreign keys inside the user
database. Weekly service selections do not rely on a package remaining installed.

## 5. Proposed catalog structure

This is the target logical structure. Exact migration names may be adjusted to
fit established ChurchManager naming conventions, but the relationships and
constraints are required.

### 5.1 Lectionary package registry

`tblLectionaryPackage` records an installed package:

| Field | Requirement |
|---|---|
| `ID` | Local integer primary key |
| `PackageCode` | Immutable unique stable code |
| `PackageVersion` | Installed semantic or source version |
| `Title` | User-facing package title |
| `SourceName` | Responsible body or approved source |
| `SourceReference` | Short source citation or URL |
| `PackageNotice` | Passive provenance note, not license enforcement |
| `InstalledAt` | Installation timestamp |
| `IsActive` | Available for new selections |

### 5.2 Lectionary system and edition

`tblLectionarySystem` represents the user-facing lectionary family. Its current
`Name`, `CycleType`, `Active`, and `Note` fields are retained or migrated as
appropriate, with these additions:

| Field | Requirement |
|---|---|
| `SystemCode` | Immutable stable code for packaged systems; generated for local systems |
| `PackageID` | Nullable owner package; `NULL` for local systems |
| `IsStarter` | Packaged and protected when true |

`tblLectionaryEdition` distinguishes stable, trial, revised, and local editions:

| Field | Requirement |
|---|---|
| `ID` | Local integer primary key |
| `LectionarySystemID` | Parent system |
| `EditionCode` | Immutable stable code |
| `Name` | User-facing edition name |
| `EditionYear` | Optional year label |
| `Status` | `STABLE`, `TRIAL`, `RETIRED`, or `LOCAL` |
| `ValidFrom`, `ValidThrough` | Optional applicability dates |
| `PackageID` | Nullable package owner |
| `IsStarter`, `IsActive` | Protection and selection state |
| `SourceNote` | Brief passive provenance note |

A provisional update is a separate edition or overlay. It never silently
replaces a stable edition.

### 5.3 Cycles

`tblLectionaryCycle` replaces application assumptions about A/B/C:

| Field | Requirement |
|---|---|
| `ID` | Local integer primary key |
| `LectionaryEditionID` | Parent edition |
| `CycleCode` | Stable code such as `A`, `B`, `C`, `ONE_YEAR`, or a local value |
| `DisplayName` | User-facing label |
| `Sequence` | Order within the repeating cycle |
| `IsActive` | Available for selection |

An edition may have no cycle rows, one cycle, three cycles, or another number.
No business rule may assume exactly three.

### 5.4 Propers and occasions

`tblPropers` remains the appointment container and is normalized to reference an
edition and optional cycle. Required logical fields are:

| Field | Requirement |
|---|---|
| `ID` | Local integer primary key |
| `LectionaryEditionID` | Parent edition |
| `LectionaryCycleID` | Nullable cycle |
| `ProperKey` | Immutable package key or generated local key |
| `LiturgicalDate` | Fully written printable occasion name |
| `Season` | Normalized season choice |
| `Sort` | Ordering within the edition and cycle |
| `DefaultColor` | Optional value resolved against the Liturgical Color choices |
| `AlternateColor` | Optional alternative |
| `CalendarRule` | Optional structured resolver rule or reference |
| `PackageID` | Nullable package owner |
| `IsStarter`, `IsActive` | Protection and selection state |
| `Note` | Brief planning or source note only |

Packaged systems, editions, cycles, and Propers cannot be edited in place. A user
may copy one into a local system or create a local record from scratch.

### 5.5 Reading appointments

The current `tblReading` model is expanded or replaced with normalized
appointments containing:

| Field | Requirement |
|---|---|
| `ID` | Local integer primary key |
| `PropersID` | Parent Proper |
| `AppointmentKey` | Immutable package key or generated local key |
| `Role` | Normalized role such as `FIRST_READING`, `PSALM_CANTICLE`, `SECOND_READING`, or `GOSPEL` |
| `DisplayRole` | Edition-appropriate user label such as Old Testament or Epistle |
| `DisplayCitation` | Citation shown to the user |
| `NormalizedCitation` | Search and comparison form |
| `TrackCode` | Nullable track identifier |
| `OptionGroupCode` | Nullable mutually related choice group |
| `OptionType` | `DEFAULT`, `ALTERNATE`, `OPTIONAL_EXTENSION`, or `VARIANT` |
| `PairedAppointmentKey` | Nullable link for a psalm/canticle paired with a first reading |
| `Sequence` | Normal worship order |
| `IsDefault` | Default within its option group |
| `PackageID` | Nullable package owner |
| `IsStarter`, `IsActive` | Protection and selection state |
| `Note` | Brief planning or source note only |

The model must permit Acts to appear in the role assigned by the edition rather
than inferring role from the biblical book.

## 6. Tracks, choices, and pairings

Tracks are data, not hard-coded application concepts. An edition may define no
tracks or any number of named tracks.

When a first reading and psalm/canticle are paired:

1. Selecting the first reading selects its paired response by default.
2. Changing tracks updates both candidates together.
3. The user may still make an explicit service-level override.
4. The saved service records exactly what was selected.

Option groups identify mutually related alternatives without implying that all
rows should print. Optional extensions preserve both the normal and extended
citation as explicit choices rather than embedding publisher punctuation rules
in application code.

## 7. Congregation settings

`tblChurch` retains a nullable primary lectionary selection, migrated from
`PrimaryLectionarySystemID` to the installed edition where necessary.

Optional congregation defaults may include:

- primary lectionary edition;
- preferred track for an edition;
- preferred display terminology;
- preferred Bible-translation name as a short planning label; and
- whether trial editions appear in ordinary selection lists.

These are defaults only. They do not store Bible text and do not prevent an
explicit service override.

## 8. Service planning and historical snapshots

Selecting a Proper for a service loads candidate appointments from the selected
edition. Applying it creates or replaces service-owned rows in
`tblServiceReadingSelection`.

Each service row stores:

- `ServiceID`;
- source Proper and appointment IDs when still available;
- snapshot system, edition, cycle, Proper, and role labels;
- selected display and normalized citations;
- selected track and option information;
- sequence;
- whether the user overrode the catalog default; and
- a brief local planning note.

The service-owned snapshot is authoritative after save. Reports, bulletin
outlines, sermon matching, and historical views read the same snapshot. A
catalog update, retirement, or removal cannot change it.

Changing the service's template does not change its readings. Changing the
Proper presents a clear replace-and-review action; it does not silently discard
confirmed service selections.

## 9. Calendar resolution

The calendar resolver is a separate service consuming lectionary metadata. It
returns candidates and an explanation; it does not silently decide ambiguous
precedence.

Its result may contain:

- civil date;
- liturgical date;
- season;
- edition and cycle;
- Proper or ordinary-time identity;
- feast, festival, transferred-day, or local alternatives; and
- the rule that produced each candidate.

Cycle boundaries, moveable dates, Proper numbering, and precedence rules belong
to edition data or a versioned resolver rule set. They are not inferred from the
name of the lectionary.

## 10. Package format

An approved package contains:

```text
manifest.json
systems.json
editions.json
cycles.json
propers.json
appointments.json
```

The manifest contains package identity, version, dependencies, source notes,
checksums, minimum ChurchManager schema version, and declared entity counts.

Package files contain only approved fields. Unknown fields cause validation to
fail rather than being ignored. External file references, HTML bodies, rich text,
embedded media, binary payloads, and arbitrary attachments are forbidden.

## 11. Hard metadata-only boundary

Lectionary packages, database records, local customizations, weekly service
selections, reports, and generated output must not store or reproduce:

- Scripture text from any translation;
- psalm or canticle text;
- prayers or collects copied from a publication;
- full liturgical wording;
- responsive pastor-and-congregation text;
- meaningful-length verbatim rubrics;
- publisher commentary, introductions, or study notes;
- psalm tones or musical settings;
- hymn lyrics, music notation, or accompaniment material; or
- publisher artwork, page images, or document scans.

Allowed content is limited to stable identities, short names and labels,
biblical citations, reading roles, cycles, tracks, option relationships,
calendar rules, liturgical colors, short source notes, and service-planning
metadata.

This is a schema and validation boundary, not a user-selectable licensing mode.
ChurchManager does not manage or enforce copyright licenses. Package maintainers
must approve a reference compilation for redistribution before it is offered by
the installer.

## 12. Installation

The installer presents approved lectionary packages independently from hymnals
and Orders of Service. The user may select multiple packages or `None` and then
choose one installed edition as the church default.

Installation occurs in one database transaction:

1. Verify the package checksum or signature and manifest schema.
2. Verify package and stable-key namespaces.
3. Reject forbidden, unknown, content-bearing, or attachment fields.
4. Validate every system, edition, cycle, Proper, and appointment relationship.
5. Validate roles, tracks, option groups, defaults, and pairings.
6. Validate biblical citation syntax without retrieving Scripture text.
7. Preview entity counts, changes, warnings, and source information.
8. Insert or update only records owned by that package.
9. Set the selected primary edition if requested.
10. Roll back the entire installation if any validation or database step fails.

Installation order cannot change stable identity or redirect an existing
relationship.

## 13. Updates, removal, and local records

A package update may correct metadata, add appointments, or retire package-owned
records. It may not:

- change or reuse a stable key;
- overwrite a local record;
- convert a local record into packaged data;
- alter a saved service selection;
- silently replace a stable edition with a trial or newer edition; or
- introduce a field prohibited by the metadata-only boundary.

Retired package records remain readable when referenced by history and are
excluded from ordinary new selection. Removing a package retires or removes only
unreferenced package-owned catalog data. It never deletes local records or
service snapshots. A primary edition must be changed or cleared before its
package can be removed.

Users may create local lectionary systems, editions, cycles, Propers, and
appointments from scratch or by copying starter data. Local records are clearly
marked as customized and are fully editable. They remain subject to the same
metadata-only validation rules.

## 14. Initial supported packages

The first implementation should support the package framework before assuming a
particular package is distributable. Candidate packages are:

- LSB Three-Year Lectionary;
- LSB One-Year Lectionary; and
- Revised Common Lectionary (1992).

Each package requires separately documented source provenance and permission to
redistribute its citation compilation. The RCL provisional trial material, if
approved later, is installed as a separate edition or overlay and never replaces
the 1992 edition silently.

## 15. Replacement of current development data

The current ChurchDBTest lectionary catalog is disposable reference material,
not data that must retain identity. It is replaced cleanly:

1. Create and verify a ChurchDBTest backup.
2. Export each current system, Proper, reading, color, and Proper hymn suggestion
   into a read-only staging inventory.
3. Compare that inventory with the approved package source to find useful
   corrections, omissions, role mappings, and hymn suggestions.
4. Record every accepted correction in the maintained package source, not as an
   undocumented database exception.
5. Produce a reconciliation report listing accepted, rejected, duplicate, and
   unresolved reference records.
6. Delete the disposable current lectionary catalog and its dependent test
   planning data in a guarded development migration.
7. Install the approved packages into the clean normalized structure.
8. Verify row counts, relationships, citations, colors, and Proper hymn
   suggestions against the package manifests.
9. Do not preserve old auto-increment IDs, old schema assumptions, or obsolete
   lectionary records merely for compatibility.

No existing ChurchDBTest worship-service history requires conversion. The new
service-reading snapshot model becomes authoritative for services created after
the replacement.

## 16. Validation and tests

Automated tests must prove:

- packages with unknown or prohibited fields are rejected;
- HTML, rich-text bodies, media, attachments, and full-text fields are rejected;
- package keys are unique, immutable, and namespace-safe;
- local keys cannot claim a package namespace;
- editions may define zero, one, three, or another number of cycles;
- applications do not assume A/B/C based on system names;
- every appointment resolves to its Proper, edition, and package;
- option groups have valid defaults;
- paired readings and psalms remain paired when tracks change;
- alternative and optional citations remain visibly distinguishable;
- service selections survive package updates, retirement, and removal;
- reports and worship screens use the same service-owned selections;
- changing the church default does not rewrite existing services;
- local records are not overwritten by package installation or upgrades;
- installation failures roll back completely;
- package removal cannot orphan references;
- LSB and RCL data remain separate even where appointments coincide; and
- no test or migration touches production ChurchDB.

Representative calendar tests must include Advent cycle boundaries, Easter-based
dates, Sundays after Pentecost, festivals, competing candidates, and an RCL
complementary/semicontinuous pairing.

## 17. Acceptance criteria

The design is ready for implementation when:

- the product owner approves this specification;
- the stable-key and package schemas are finalized;
- the metadata-only validator and rejection tests are designed;
- at least one candidate package has documented redistribution authority;
- current ChurchDBTest data has a complete proposed mapping with no silent data
  loss;
- service-owned reading snapshots have one authoritative consumer path for all
  screens and reports;
- installation, update, removal, rollback, and local-customization behaviors are
  covered by tests; and
- implementation remains denomination-neutral.

## 18. Implementation status

The checksum-protected package loader and denomination-neutral, metadata-only
validator are implemented in `lectionary_packages.py`. They enforce stable
package namespaces, flexible data-defined cycles, citation-only appointments,
valid alternatives and pairings, bounded passive metadata, and rejection of
unknown or content-bearing fields. The proposed database tables, importer,
calendar resolver, and service-reading snapshots remain future implementation.
Existing ChurchManager behavior remains in place until their migrations and
application changes are completed and verified.
