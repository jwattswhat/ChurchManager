# ChurchManager Order of Service Catalog Specification

**Status:** Approved August 16, 2026; schema, validator, and transactional importer implemented

**Prepared:** August 16, 2026

**Scope:** Development ChurchManager package catalogs, installation, worship
planning, and ChurchDBTest

## 1. Purpose

Provide a denomination-neutral way to install protected starter outlines and to
create congregation-owned Order of Service templates. An Order of Service is a
planning outline: it identifies the sequence and kinds of service elements but
does not reproduce the service itself.

The catalog must allow a congregation to install only the packages it uses,
copy a starter into an editable local template, apply a template to a weekly
service, and preserve that weekly service independently of later package
changes.

## 2. Non-negotiable boundary

An Order of Service package, database record, customized template, weekly copy,
and generated outline may store only planning metadata. It may not store or
distribute:

- full liturgical wording;
- full prayers, collects, responsive text, psalms, or canticles;
- meaningful-length verbatim rubrics from a publication;
- hymn lyrics or stanza text;
- psalm tones, musical settings, notation, accompaniment, or recordings;
- publisher artwork, scans, page images, or embedded media; or
- HTML, rich-text, or long-form body fields intended to reconstruct protected
  content.

This is a structural product boundary, not a copyright-management feature.
ChurchManager records short labels and references such as `Kyrie`, `Creed`,
`LSB p. 152`, or `Hymn of the Day`. It does not decide whether a congregation
has permission to reproduce external material.

## 3. Core decisions

1. Starter Orders of Service are separately installable, versioned packages.
2. Installation may offer packages associated with an installed hymnal or
   service book, plus packages requiring no hymnal.
3. A package is installed only when its dependencies are satisfied.
4. Starter templates are protected and cannot be edited in place.
5. Users create editable local templates from scratch or by copying a starter.
6. Local templates are never package-owned and cannot claim a package namespace.
7. Applying a template creates a complete service-owned weekly snapshot.
8. The weekly snapshot is not dependent on the source template remaining
   installed and is never altered by package update, retirement, or removal.
9. Reapplying a different template wholly replaces the weekly outline. Service
   hymn selections may refill matching hymn slots, but other weekly choices must
   be reviewed again.
10. Required participant roles belong to the template and are copied into the
    weekly planning context; additional service-specific assignments remain
    allowed.
11. Order is represented by an integer sequence. User moves are normalized to
    consecutive values when saved.
12. Packages and application logic are denomination-neutral.

## 4. Identity and ownership

MariaDB integer primary keys remain local implementation details. Distributed
packages use immutable, case-insensitive stable keys:

```text
PackageCode       example: lsb-ds-outlines
TemplateKey       example: divine-service-setting-one
LineKey           example: service-word.old-testament
RoleKey           example: reader
```

Stable keys are unique within their documented scope and never reused. Local
templates receive generated keys beginning with `local-`. A package upgrade
resolves stable keys to local integer keys transactionally.

Ownership is explicit:

| Record | Package ownership |
|---|---|
| Installed starter template | Required package owner |
| Starter line or role requirement | Same package owner as template |
| Local/custom template | No package owner |
| Weekly service snapshot | No package owner; historical service data |

## 5. Package registry

`tblOrderOfServicePackage` records each installed package:

| Field | Requirement |
|---|---|
| `ID` | Local integer primary key |
| `PackageCode` | Immutable unique stable code |
| `PackageVersion` | Installed semantic or source version |
| `Title` | User-facing package title |
| `TemplatePrefix` | Uppercase catalog abbreviation followed by one space, such as `LSB ` |
| `SourceName` | Responsible publisher, body, or package maintainer |
| `SourceReference` | Short provenance reference or URL |
| `PackageNotice` | Passive source/license note; not enforcement |
| `HymnalPackageCode` | Optional dependency on a hymnal package |
| `MinimumHymnalVersion` | Optional minimum compatible version |
| `SchemaVersion` | Required package-schema version |
| `Checksum` | Approved package checksum |
| `InstalledAt` | Installation timestamp |
| `IsActive` | Available for new template selection |

Installed package identity, ownership, checksum, and version are audit data and
cannot be casually edited through ordinary screens.

## 6. Template structure

The existing `tblBulletinOrderTemplate` remains the user-facing template table
and gains package-safe identity fields:

| Field | Requirement |
|---|---|
| `TemplateKey` | Immutable package key or generated `local-` key |
| `PackageID` | Nullable package owner; `NULL` for local templates |
| `IsStarter` | True only for protected package-owned templates |
| `HymnalID` | Nullable installed hymnal reference |
| `Name` | User-facing name |
| `Description` | Brief original planning description only |
| `Version` | Local optimistic-concurrency version |
| `Active` | Available for new services |

`ChurchID` identifies congregation-owned local templates. Package starters are
global catalog records and have no congregation owner. A starter cannot be
converted into a local template merely by changing flags; it must be copied.

## 7. Allowed line metadata

`tblBulletinOrderLine` represents ordered outline elements. A packaged line may
contain only:

- stable `LineKey`;
- integer sequence;
- short original outline label;
- controlled item type;
- controlled value source and key;
- short publication, page, or hymn-use reference;
- inclusion condition and short condition value;
- indentation, tab, emphasis, and outline-format metadata;
- a brief original planning note; and
- an active/retired flag.

Initial controlled item types are `HEADING`, `LITURGY`, `HYMN`, `READING`,
`SERMON`, `OFFERING`, `COMMUNION`, and `TEXT`. New types require schema review;
unknown package types are rejected rather than silently treated as text.

Allowed conditions are `ALWAYS`, `COMMUNION`, `NO_COMMUNION`,
`INCLUDE_SEASON`, `EXCLUDE_SEASON`, and an explicit user choice. Conditions
control whether a line is proposed for the weekly snapshot; they do not insert
published content.

## 8. Package content validator

Validation occurs before any database write. The importer rejects a package
when it contains:

- unknown manifest, template, line, role, or dependency fields;
- a long-form body, HTML, RTF, Markdown-body, binary, URL-to-content, image,
  audio, music, attachment, or embedded-media field;
- labels, notes, descriptions, or references over their approved lengths;
- markup, data URLs, file paths, or encoded binary content in text fields;
- duplicate or malformed stable keys;
- a local namespace in packaged data;
- a missing or incompatible dependency;
- unsupported schema or application versions;
- an invalid checksum or signature;
- duplicate sequences, invalid item types, invalid conditions, or unresolved
  role keys; or
- starter data marked editable or congregation-owned.

Recommended maximum lengths are 120 characters for labels, 80 for references,
and 250 for original planning notes and descriptions. Validation should also
flag suspiciously dense or sentence-like text for manual package review even
when it falls below a limit.

## 9. Hymnal relationship

An Order of Service package may declare one optional hymnal-package dependency.
Templates may therefore reference `No hymnal` or one installed hymnal. Hymn
lines store a suggested-use key such as `Hymn of Invocation`, not a hymn title,
lyric, or floating local database ID.

When a compatible hymnal is installed, permanent hymn identifiers may fill
weekly hymn selections through exact suggested-use matching. The template
itself does not embed hymn records. Removing or retiring a hymnal cannot rewrite
historical weekly hymn selections.

## 10. Required participant positions

A template may contain zero or more role requirements. Each requirement uses a
stable role key and a nonnegative required count. Starter packages may include
requirements, but the initial packaged starters need not define any.

Copying a starter copies its normal role requirements into the local template.
Applying a template makes those requirements visible for the service planner.
The planner may assign additional positions or people for one service without
changing the template.

## 11. Weekly snapshot

Applying a template creates or replaces `tblServiceBulletinOrder` and its lines
in one transaction. The snapshot stores the source template name and version as
passive provenance, but its continued use does not require the template or
package foreign key.

Every weekly line receives its own sequence, inclusion state, short label,
reference, selected value, condition metadata, and formatting metadata. Hymn
and reading selections belong to the weekly line. Saving normalizes sequences
to `1..n`.

Template deletion, package retirement, or package removal must not delete a
weekly snapshot. A weekly snapshot can be deleted only through the explicit
service-planning action for that service.

## 12. Installation and upgrade

Installation is transactional:

1. verify manifest schema, checksum, namespace, and compatible application;
2. validate the hard metadata-only boundary;
3. verify optional hymnal and role dependencies;
4. stage all templates, lines, and requirements;
5. compare stable keys with any installed version;
6. insert or update only records owned by that package;
7. retire package records omitted by an intentional upgrade policy;
8. record counts, warnings, checksum, version, and result; and
9. commit only after complete post-import validation.

An upgrade may correct starter metadata or add and retire starter elements. It
must never overwrite local templates, convert local records into starters, or
change weekly snapshots.

## 13. Retirement and removal

Retirement hides a package or starter from new selections while keeping it
available for references and audit. Removal is allowed only when package-owned
catalog records can be removed without orphaning active references. Otherwise
the package remains retired.

Removal never deletes local/custom templates or weekly service snapshots.
Local templates copied from a starter remain local after the package is gone.

## 14. User interface

The template catalog marks starters and custom templates distinctly. Users may:

- filter by installed hymnal or `No hymnal`;
- preview a starter outline;
- create a named custom copy from a starter;
- create a local template from scratch;
- edit and delete only local templates; and
- see package source and version without editing package ownership.

Every imported starter name begins with its package's catalog abbreviation and
one space. For example: `LSB Divine Service, Setting One`, `LSB Matins`, and
`LSB Vespers`. The same convention applies to every future hymnal or service-book
package; underscores are not used as the display separator.

Deleting a local template must explain that saved weekly Orders of Service are
preserved. The warning must not claim that weekly snapshots will be deleted.

## 15. Tests and completion criteria

Implementation is complete only when automated tests prove that:

- prohibited fields and content forms are rejected before database writes;
- stable keys, namespaces, checksums, versions, and dependencies validate;
- packages cannot edit records they do not own;
- starter records are protected;
- local templates can be created, edited, and deleted independently;
- template copy preserves lines and role requirements;
- applying a template creates a complete independent weekly snapshot;
- reapplying wholly replaces that snapshot and normalizes sequence;
- upgrades and removal do not change local templates or weekly services;
- optional hymnal dependencies and `No hymnal` both work;
- failures roll back the whole import; and
- generated output remains an outline and contains no prohibited content.

No package-schema migration or importer should be implemented until this
specification is approved.
