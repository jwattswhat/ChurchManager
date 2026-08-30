# ChurchManager custom profile fields and controlled tags specification

**Status:** Approved  
**Version:** 1.0  
**Date:** August 22, 2026  
**Approved by:** Rev. Jonathan C. Watt  
**Target application:** ChurchManager  
**Application framework:** JSForm  
**Database:** MariaDB/MySQL

## 1. Purpose

This specification defines administrator-configurable fields and controlled
tags for ChurchManager person and family profiles. The feature lets a
congregation record local information without adding a database column or
hand-editing a JSON screen definition for every local need.

The feature is deliberately bounded. Custom profile data supplements the
ChurchManager domain model; it does not replace normalized relationships,
specialized subsystems, authorization, retention rules, or application
services.

The first release applies only to:

- `tblPerson` records; and
- `tblFamily` records.

Expanding the feature to another entity requires a specification revision,
explicit permissions, database constraints, user-interface support, reporting
rules, and tests. An administrator cannot enter an arbitrary table name or
entity type.

## 2. Design principles

1. **JSForm provides the mechanism.** JSForm renders dynamic controls, binds
   typed values, performs framework-level validation, applies control-level
   authorization, and exposes supported fields to screen and report designers.
2. **ChurchManager owns meaning and policy.** ChurchManager defines which
   entities may have custom fields, stores definitions and values, establishes
   privacy and export rules, authorizes operations, audits changes, and decides
   when a local field must become a normalized feature.
3. **Values remain typed.** Dates are stored and compared as dates, numbers as
   numbers, and Boolean values as Boolean values. Values are not flattened into
   an unvalidated JSON object or a single universal text column.
4. **Common values are controlled.** Choice fields and tags use managed option
   records so spelling, searching, reporting, retirement, and imports are
   predictable.
5. **Security fails closed.** A missing, unknown, malformed, or incompatible
   permission or privacy declaration prevents the affected field from being
   displayed, edited, exported, or reported.
6. **Local flexibility does not override domain integrity.** A custom field is
   rejected when its intended use belongs in an existing normalized
   ChurchManager relationship or protected subsystem.
7. **Definitions and data are durable.** Renaming, reordering, or retiring a
   definition does not silently discard recorded values.
8. **No executable customization.** Definitions contain data and validation
   settings only. They cannot contain Python, SQL, template expressions, file
   paths, shell commands, or arbitrary JSForm callbacks.

## 3. Ownership boundary

### 3.1 JSForm owns

JSForm provides application-neutral support for:

- a dynamic-field host or section in a JSON-defined screen;
- a supported control mapping for each field data type;
- typed conversion between controls and application-provided values;
- required, length, range, option-membership, and basic format validation;
- read-only, hidden, and protected control behavior;
- stable layout, tab order, labels, help text, and validation messages;
- change collection without writing directly to application tables;
- screen-designer placement of an approved dynamic-field section;
- report-designer discovery of application-approved dynamic fields; and
- testable contracts that do not mention ChurchManager table names or policy.

JSForm does not decide whether a ChurchManager user may define, view, edit,
search, report, export, import, retire, or delete a custom field. JSForm does
not interpret privacy classifications or write profile values directly to the
database.

### 3.2 ChurchManager owns

ChurchManager provides:

- definition, option, value, tag, and assignment tables;
- application services for every definition and value operation;
- allowed entity types and field data types;
- stable keys, uniqueness, lifecycle, and conversion rules;
- authorization and privacy policy;
- validation beyond JSForm's neutral control contract;
- atomic saving with the parent Person or Family record;
- searching, filtering, reporting, import, and export policy;
- audit attribution and safe audit content;
- backup, restore, installation, upgrade, and migration behavior; and
- promotion of widely used custom concepts into normalized features.

JSON screen definitions may declare where an application-provided custom-field
section appears. They must not become the authoritative store for custom field
definitions or values.

## 4. Supported field types

The initial field types are:

| Type | Stored value | Default JSForm presentation |
| --- | --- | --- |
| Short text | bounded Unicode text | single-line text control |
| Long text | bounded Unicode text | multi-line text control |
| Integer | signed integer | integer control |
| Decimal | fixed-precision decimal | decimal control |
| Date | calendar date without time | date picker |
| Yes/No | Boolean | checkbox |
| Single choice | one active or retired option reference | dropdown |
| Multiple choice | zero or more option references | checklist or multi-select control |

The initial release excludes calculated fields, formulas, scripts, rich text,
HTML, binary data, images, files, URLs with automatic actions, person-to-person
links, family-to-family links, external identifiers with synchronization
behavior, currency accounting behavior, and date-time or recurring schedule
behavior.

A future type requires an additive schema and contract revision. Unknown types
must be rejected rather than treated as text.

## 5. Field definitions

Each definition contains at least:

| Property | Rule |
| --- | --- |
| `ID` | Immutable database identifier. |
| `ChurchID` | Owning congregation or organization. Required and immutable after creation. |
| `EntityType` | Exactly `Person` or `Family` in version 1. |
| `FieldKey` | Stable, case-insensitively unique machine key within Church and entity type. |
| `Label` | User-facing label; editable without changing `FieldKey`. |
| `Description` | Optional concise help text. |
| `DataType` | One supported type from section 4. Immutable after values exist. |
| `Required` | Whether a value is required under the rules in section 8. |
| `Searchable` | Whether authorized users may use the field as a profile-search filter. |
| `SectionName` | Controlled presentation grouping. |
| `DisplayOrder` | Stable order within the section. |
| `DefaultValue` | Optional typed default for new records only. |
| `Validation` | Type-appropriate bounded settings; never executable code. |
| `PrivacyClass` | One controlled classification from section 10. |
| `ViewPermission` | Registered permission required to reveal the value. |
| `EditPermission` | Registered permission required to change the value. |
| `DirectoryPolicy` | Explicitly disallowed or permitted for an approved directory surface. |
| `ReportPolicy` | Explicitly disallowed or permitted for approved report datasets. |
| `ExportPolicy` | Explicitly disallowed or permitted for approved exports. |
| `Active` | Active definitions may be used for new edits. |
| Audit fields | Creator, creation time, last editor, and last edit time. |

`FieldKey` uses a conservative identifier format such as
`background_check_expires`. Reserved built-in names and permission-like names
are rejected. Labels are not used as database or import identifiers.

Defaults are applied only when a new Person or Family record is created and the
user is authorized to edit the field. Adding or changing a default never
backfills existing profiles.

## 6. Controlled choices

Single-choice and multiple-choice definitions own an ordered set of options.
Each option has an immutable ID and stable option key, an editable display
label, display order, and active flag.

Rules:

- option keys are unique within a field definition;
- inactive options remain readable on records that already use them;
- inactive options cannot be selected for a new value;
- an option referenced by a value cannot be physically deleted through the
  application;
- imports and integrations use the stable option key, not the display label;
- moving an option between definitions is prohibited; and
- changing a field away from a choice type after options or values exist is
  prohibited.

## 7. Controlled tags

Tags are a separate profile-classification feature, not free-form text fields.
A tag definition contains an ID, Church ID, stable key, label, description,
allowed entity type, display color or neutral visual category, privacy class,
view permission, assignment permission, report/export policy, display order,
active flag, and audit fields.

Person and Family tag assignments are stored in separate link tables with
foreign keys to the profile, tag definition, assigning user, and assignment
time. The same tag cannot be assigned to the same profile twice.

Inactive tags remain visible to authorized users on previously tagged records
but cannot be newly assigned. Tags are searchable only when the current user is
authorized to view them.

Free-form tag creation from the Person or Family screen is prohibited. Creating
or changing the controlled tag catalog is an administrative operation.

## 8. Required fields

A custom field marked required is required for creating or saving a profile
only when all of the following are true:

1. the definition is active;
2. it applies to the profile entity;
3. the current user is authorized to view and edit it; and
4. the field is present on the applicable supported editing workflow.

A hidden or unauthorized field must never make an otherwise authorized profile
save impossible. ChurchManager therefore rejects a configuration that marks a
field required for general profile completion while ordinary profile editors
lack edit permission.

Required custom fields are not retroactively populated. After an administrator
marks an existing field required, existing missing values are reported as data
quality exceptions and must be resolved through an explicit review workflow.

## 9. Data model

The implementation uses normalized definitions and typed values. Proposed
logical tables are:

- `tblCustomFieldDefinition`;
- `tblCustomFieldOption`;
- `tblPersonCustomFieldValue`;
- `tblFamilyCustomFieldValue`;
- `tblPersonCustomFieldOptionValue` for multiple-choice selections;
- `tblFamilyCustomFieldOptionValue` for multiple-choice selections;
- `tblProfileTagDefinition`;
- `tblPersonTag`; and
- `tblFamilyTag`.

Person and Family values use separate tables so MariaDB can enforce real
foreign keys and cascading deletion to the correct parent entity. A polymorphic
`EntityType` plus `EntityID` value table is not permitted in version 1.

Scalar value rows contain dedicated nullable columns for text, integer,
decimal, date, Boolean, and single-choice option values. Database checks and
the ChurchManager service layer enforce that exactly the column appropriate to
the definition's type is populated. Multiple-choice values use link tables and
do not encode lists as comma-separated text or JSON.

There is at most one scalar value row per profile and definition. Unique keys
enforce this rule. Every definition, option, value, and tag is scoped to the
same Church ID as its profile; cross-congregation references are rejected.

Database constraints provide foundational integrity. Cross-table data-type,
permission, privacy, and lifecycle rules are rechecked in the ChurchManager
service immediately before commit.

## 10. Privacy and authorization

Definitions and tags use a controlled privacy classification:

| Class | Intended treatment |
| --- | --- |
| Standard | Available to authorized profile users and approved ordinary reports. |
| Restricted | Requires an explicit field view or edit permission and is excluded from ordinary exports by default. |
| Directory-approved | Eligible for an approved directory only when its directory policy also permits it. |

`Directory-approved` is not a relaxation of authorization. Directory, report,
and export use requires all applicable permissions and policies.

The permission catalog includes at least:

- `profiles.custom_fields.define`;
- `profiles.custom_fields.view`;
- `profiles.custom_fields.edit`;
- `profiles.custom_fields.view_restricted`;
- `profiles.custom_fields.edit_restricted`;
- `profiles.tags.define`;
- `profiles.tags.view`; and
- `profiles.tags.assign`.

A definition may require a more specific registered permission, but an
administrator cannot invent an unregistered permission name. The effective
permission is the intersection of the general operation permission, the
definition-specific permission, the privacy classification, and the permission
for the parent Person or Family record.

Authorization is enforced in the ChurchManager service immediately before
reading or committing values. Hiding a JSForm control is not sufficient.

## 11. Prohibited uses

Custom fields and tags must not store or model:

- passwords, password hints, recovery codes, API keys, database credentials, or
  other secrets;
- accounting transactions, balances, contribution facts, bank information, or
  tax substantiation;
- pastoral-care narrative, counseling details, safeguarding allegations,
  medical records, or confidential case material;
- documents, attachments, images, page scans, or binary content;
- attendance events or attendance history;
- users, roles, permissions, or authorization decisions;
- family or person relationships that require referential integrity;
- full liturgical or musical content prohibited by the project boundary; or
- information already represented by an appropriate normalized ChurchManager
  field or relationship.

Examples of reasonable local fields include a bounded local directory caption,
a date on which a congregation-specific certification expires, or a controlled
choice describing a local ministry preference. Even these examples remain
subject to privacy review.

## 12. Screen behavior

### 12.1 Profile screens

The Person and Family screens contain a JSForm dynamic-field host. When a record
is opened, ChurchManager supplies an ordered, authorization-filtered set of
field descriptors and typed values. JSForm constructs controls from those
descriptors and returns validated proposed changes to ChurchManager.

The screen must:

- group fields by controlled section and display order;
- distinguish required fields clearly;
- show concise administrator-provided help text;
- show retired fields read-only when a stored value still exists;
- avoid revealing the label, value, choice list, validation rule, or existence
  of an unauthorized restricted field;
- preserve built-in profile values if dynamic-field loading fails; and
- prevent a partial custom-value save when the parent save fails.

Saving the parent profile and its custom values occurs in one transaction when
they are changed in the same workflow.

### 12.2 Definition administration

An authorized administration screen supports listing, creating, testing,
reordering, and retiring field and tag definitions. Before activation, it shows
a non-record preview of the JSForm control and summarizes privacy, permissions,
directory, report, and export behavior.

Double-clicking a definition, or choosing **Open Field**, displays its complete
record, including stable identity, lifecycle, version, validation settings,
usage policies, and choices. Draft definitions are fully editable. Once Active,
the stable key, entity type, data type, privacy class, and validation boundaries
are locked, while labels, help text, section, display order, required status,
and approved search/report/export policies remain editable. Retired definitions
are retained as read-only history.

The screen warns when a proposed custom field appears to duplicate a built-in
field or supported relationship. Activation requires an explicit confirmation
that the field contains no prohibited content category.

## 13. Searching and filtering

Only active definitions marked searchable are offered as filters. A retired
definition may be available in a separately identified historical-data search
when authorized.

Supported operations depend on type:

- text: equals, starts with, contains, is blank, is not blank;
- number and date: equals, before/less than, after/greater than, range, is blank;
- Yes/No: yes, no, is blank;
- single choice: selected option, any of selected options, is blank; and
- multiple choice and tags: has any, has all, has none.

Search services apply authorization before constructing queries. Unauthorized
definitions and tags do not appear in filter metadata, result columns, counts,
facets, or error messages.

Searchable fields receive appropriate indexes. Activation may refuse an
unbounded or operationally unsafe searchable definition rather than create an
expensive unrestricted query path.

## 14. Reports, directories, and exports

A field does not automatically appear in any report, directory, mail merge, or
export. Inclusion requires:

1. the definition's applicable policy to permit the surface;
2. the surface's approved dataset contract to expose the field;
3. the current user to hold all required permissions; and
4. the report or export to identify the custom field by stable key.

JSForm's report designer may list approved dynamic fields supplied by
ChurchManager. It does not query unrestricted custom-value tables or bypass the
ChurchManager report service.

Existing custom report layouts remain loadable when a field is renamed because
they use its stable key. If a definition is retired, an existing approved report
may show its historical value with a clear retired-field indicator. Physical
deletion must not silently repurpose a stable key.

Ordinary directory datasets exclude all custom fields by default. A field must
be `Directory-approved`, explicitly permitted by its directory policy, and
added to an approved directory dataset and layout before it can appear.

Exports include a metadata header or companion manifest that identifies field
keys, labels, types, and option keys. Restricted values are excluded unless an
explicit restricted export is both authorized and confirmed.

The first approved reporting surface is **Membership - Custom Profile
Listing** (`CMMB11`). Its safe database view exposes only definitions marked
`ReportAllowed`, keeps `FieldKey` in the dataset contract as the stable identity,
formats typed values for display, combines multiple-choice labels in their
defined order, and identifies retired definitions. Church and restricted-value
authorization are reapplied when the dataset is built. The starter layout uses
the human-readable field label; a customized layout may also use the stable key.

## 15. Imports

Imports match definitions and options by stable key. Unknown fields, invalid
types, inactive options, unauthorized fields, cross-Church references, and
prohibited values are reported during preview and rejected before commit.

Import is a two-step preview-and-commit operation. The preview reports creates,
changes, blanks, unchanged values, and errors without revealing restricted
existing values to an unauthorized user. Commit repeats authorization and
validation and writes an audit event.

An import cannot create definitions or options implicitly. Catalog changes are
separate administrative operations.

The implemented exchange is deliberately separate from ordinary membership
CSV export. **Export Values...** writes only Active definitions marked for
approved export and creates a companion JSON manifest containing stable field
keys, types, privacy classes, and stable choice keys. Restricted values require
the restricted-view permission plus a separate explicit confirmation. Identity
and custom-value cells use the shared CSV rule so spreadsheet formula prefixes
remain text.

**Import Values...** updates custom values for existing People or Families. It
matches the profile by its exact portable name fields and definitions by
`custom.<stable_key>` CSV headings. Every row is previewed as Ready or needing
attention; duplicate or missing profile matches, unknown or inactive fields,
invalid typed values, inactive choices, and unauthorized restricted fields
block the entire import. Commit rereads the source and saves all reviewed rows
in one transaction. It never creates profiles, definitions, or choices.

## 16. Lifecycle and conversion

Definitions move through these states:

1. Draft;
2. Active; and
3. Retired.

Draft definitions have no profile values and are visible only in authorized
administration. Active definitions may be edited within safe limits. Retired
definitions cannot receive new values but retain definitions, options, existing
values, report identity, and audit history.

Physical deletion is permitted only for an unused draft with no options,
values, report references, import mappings, or audit dependency.

Changing label, help text, display order, or appropriately tightening policy is
safe. Changing entity type, Church ownership, stable key, or data type after
activation is prohibited. A data-type change uses a new definition and an
explicit previewed conversion tool that records source definition, target
definition, per-record outcome, operator, and time. The old definition is
retired only after review.

When a custom concept becomes a supported ChurchManager feature, migration to a
normalized model follows the same preview, validation, audit, rollback, and
acceptance requirements. No runtime dual-write compatibility is added for the
separate Frozen application.

## 17. Audit behavior

ChurchManager records at least:

- definition and option creation, activation, edit, retirement, and deletion;
- tag definition and assignment changes;
- profile custom-value creation, change, and clearing;
- rejected unauthorized definition, value, report, export, and import actions;
- bulk import and conversion summaries; and
- restricted export confirmation and completion.

Audit events identify the application user, time, workstation or session,
entity type, entity ID, definition or tag ID, action, and outcome. Audit storage
does not copy passwords, secrets, prohibited content, long unrestricted text,
or unnecessary restricted values. For restricted fields, the audit may record
that a value changed and retain a protected hash or bounded safe summary rather
than the value itself.

Audit records are append-only through ChurchManager and follow the approved
user-security specification.

## 18. Backup, restore, installation, and upgrades

Definitions, options, values, tags, assignments, and their audit records are
congregation-owned data. They are included in normal backup and restore
coverage and are never overwritten by starter updates.

The feature is delivered through a guarded versioned migration and is tested
first against `ChurchDBTest`. Installation and restore validation checks:

- table and foreign-key presence;
- unique and check constraints;
- Church scoping;
- definition/value type consistency;
- option ownership;
- orphan values and assignments;
- permission catalog entries; and
- backup round-trip preservation.

The migration, baseline schema, baseline manifest, installer acceptance,
database inventory, public user guide, developer documentation, JSON-form
reference, and automated tests are updated together when implementation begins.

## 19. Performance and limits

The initial implementation uses conservative configurable limits, including:

- maximum active definitions per Church and entity type;
- maximum options per choice definition;
- maximum short- and long-text lengths;
- maximum tags per profile;
- bounded decimal precision and scale; and
- bounded search and export result sizes.

Exact limits are selected during implementation from measured ChurchDBTest
behavior and documented in the user guide. They are enforced in both the
ChurchManager service and database where practical.

Profile loading retrieves authorized definitions and values in bounded set
queries. It must not issue one database query per custom field.

## 20. Validation and error handling

Validation occurs at three layers:

1. JSForm validates the control-level type and declared neutral constraints.
2. ChurchManager validates ownership, authorization, definition lifecycle,
   privacy, option membership, prohibited use, and cross-field application
   rules.
3. MariaDB enforces foreign keys, uniqueness, nullability, check constraints,
   and supported referential actions.

Errors name the field label when the user is authorized to know it and explain
how to correct ordinary input. Security errors remain generic and do not reveal
hidden definitions or values. A failed value operation rolls back the complete
profile transaction and preserves the user's safe input for correction where
practical.

## 21. Acceptance criteria

The feature is accepted only when all of the following are demonstrated:

1. An authorized administrator can define each supported field type for a
   Person or Family and preview its JSForm control.
2. Creating a definition requires a valid stable key, registered permissions,
   privacy classification, and explicit directory/report/export policies.
3. Person and Family screens render authorized fields in the configured order
   without hand-editing the screen definition for each field.
4. Typed values round-trip without text coercion, locale corruption, decimal
   precision loss, or date-time drift.
5. Choice and tag values remain stable after label changes and remain readable
   after retirement.
6. Required-field behavior cannot block a user who is not authorized to edit
   the field.
7. Unauthorized users cannot infer a restricted definition or value through
   screens, search metadata, counts, reports, exports, imports, logs, errors, or
   report-designer discovery.
8. Service-layer permission tests prove that bypassing a hidden control does
   not bypass authorization.
9. Cross-Church definitions, values, options, and tags are rejected.
10. Database constraints prevent orphan values, duplicate scalar values,
    duplicate multiple-choice selections, and duplicate tag assignments.
11. Parent and custom-value edits commit atomically and roll back together.
12. Retiring a field preserves historical values and existing stable report
    references while preventing new values.
13. An unused draft may be deleted, while a used or audited definition cannot
    be physically deleted through the application.
14. Search operations return correct type-aware results and use bounded set
    queries.
15. Reports, directories, exports, and imports honor stable keys, permissions,
    privacy, and per-definition policies.
16. Audit tests verify attribution and prove that restricted or prohibited
    contents are not copied unnecessarily into audit records.
17. Backup and restore preserve definitions, options, values, tags,
    assignments, and stable identifiers.
18. Migration and baseline installation succeed only against the guarded
    development/test configuration and never access the separate Frozen
    application or its database.
19. JSForm contract tests prove that its dynamic-field support remains
    application-neutral.
20. JSON forms pass canonical schema and structure checks.
21. Person, Family, administration, search, and report-designer screens are
    rendered and visually inspected at supported window sizes before visual
    verification is claimed.
22. Relevant specifications, inventories, public guidance, docstrings, and
    tests agree on terminology and behavior.

## 22. Implementation sequence

1. Approve this specification and settle version 1 limits and terminology.
2. Define the application-neutral JSForm dynamic-field descriptor, value, and
   change-set contracts with framework tests.
3. Add guarded ChurchDBTest migrations, constraints, permission seeds, baseline
   updates, and integrity tests.
4. Implement ChurchManager definition, value, tag, search, report, import, and
   audit services.
5. Add the administration screen and Person and Family dynamic-field sections.
6. Add report-designer and screen-designer integration without exposing
   unrestricted table access.
7. Complete automated security, transaction, migration, backup, and performance
   testing.
8. Render and visually inspect all affected screens and representative reports.
9. Update the user guide, developer documentation, database inventory, form
   reference, and roadmap status in the same implementation commit.

## 23. Decisions requiring approval before implementation

The following remain explicit approval decisions:

1. whether the first release should include multiple-choice fields or defer
   them while retaining the schema design;
2. whether restricted fields need definition-specific permissions in version 1
   or only the controlled general restricted permissions;
3. the initial numerical limits described in section 19;
4. whether custom fields may ever be directory-approved in version 1; and
5. whether field-definition changes require a second administrator's approval
   or only permission plus audit.
