# ChurchManager Visual Report Designer Specification

Status: Approved
Project type: Separate side project
First milestone: Member Directory proof of concept

## 1. Purpose

ChurchManager needs reports that authorized users can customize visually without
writing Python or SQL. The report system must remain dependable as MariaDB,
Python, and Windows are updated, and it must not depend on a report designer
that connects directly to the ChurchManager database.

The project will provide a ChurchManager Visual Report Designer with reusable
framework components in JSForm. ChurchManager supplies approved report data;
the designer controls presentation; a ChurchManager-owned renderer produces the
final PDF.

This project is independent of the legacy program and must not change or depend
on the legacy ChurchManager installation.

## 2. Design principles

1. Users design reports visually, without SQL or programming.
2. ChurchManager authorizes every report and supplies only approved data.
3. Report definitions contain layout and formatting, never credentials.
4. Saved definitions are readable, versioned JSON rather than opaque binaries.
5. Reports use shared header, footer, typography, and formatting standards.
6. The preview and final PDF use the same layout engine.
7. The first release favors a small dependable feature set over a complete
   general-purpose reporting language.
8. LimeReport templates remain reference designs during conversion but are not
   the runtime dependency of the new system.

## 3. Ownership boundary

### JSForm owns

- the generic report-definition JSON schema;
- the designer canvas and selection model;
- drag, move, resize, align, distribute, copy, paste, and delete operations;
- page, band, text, image, line, rectangle, and table components;
- the property editor;
- generic field binding to a supplied dataset contract;
- formatting rules for text, numbers, currency, dates, times, and booleans;
- grouping, sorting, totals, page breaks, and pagination primitives;
- definition loading, validation, version upgrades, and save-as behavior;
- preview rendering and PDF-renderer interfaces;
- generic automated tests for layout and definition compatibility.

### ChurchManager owns

- the report catalog and report permissions;
- approved report datasets and their fields;
- privacy filtering, including unlisted contact information;
- organization and church selection rules;
- church identity, branding, and logo data;
- report-specific parameters and validation;
- sanitized report-run auditing;
- the location and naming of ChurchManager report definitions and output;
- ChurchManager-specific starter templates and visual acceptance tests.

## 4. Security model

The designer cannot contain or execute SQL. A report definition identifies an
approved dataset by a stable name such as `membership.directory`. ChurchManager
resolves that name after checking the signed-in user's permission.

Each dataset contract declares:

- its stable name and version;
- its required ChurchManager permission;
- available fields and user-facing labels;
- data types and permitted formatting;
- allowed parameters, filters, groupings, and sorts;
- whether each field is ordinary, contact-sensitive, pastoral-confidential, or
  financial-sensitive;
- parent-child relationships between result collections.

Unknown datasets, fields, parameters, functions, or definition versions fail
closed. Definitions cannot reference passwords, user-security tables, arbitrary
files, operating-system commands, Python expressions, or database connections.

The existing `rpt_` views may remain the internal source for ChurchManager's
dataset providers, but report definitions never query those views directly.

## 5. User editing levels

### Basic editor

May change titles, text, fonts, colors, borders, spacing, logo placement, column
widths, visibility, and page orientation.

### Report designer

May also add approved fields, tables, groups, sorting, totals, conditional
visibility, page breaks, and report parameters.

### Developer

Creates or changes dataset contracts, providers, permissions, calculated fields,
and schema migrations. These operations are not exposed in the visual designer.

ChurchManager permissions determine which editing level is available. Running a
report and editing its design are separate permissions.

## 6. Report-definition format

Definitions use UTF-8 JSON with a required schema version and follow the same
named-root convention as JSForm screens. A report has one `<name>REPORT` root,
a `REPORT` settings section, and a keyed `CONTROLS` section. Familiar JSForm
properties such as `type`, `field`, `position`, `size`, font, color, and
alignment are reused. Report-specific behavior is added through properties such
as `band`, `collection`, `format`, grouping, and repetition.

A definition contains:

- report identifier, title, and dataset contract name/version;
- page size, orientation, margins, and units;
- theme and shared component references;
- report header and footer;
- page header and footer;
- detail and group bands;
- elements with stable IDs, bounds, styles, bindings, and formatting;
- allowed sort, group, filter, and aggregate declarations;
- parameter presentation settings;
- created/modified metadata that contains no credentials or sensitive data.

Definitions do not contain report results. Saving a design never saves member,
pastoral, donor, payroll, or accounting records into the JSON file.

Definitions receive a deterministic validation error when a dataset revision
removes or changes a field. Automatic upgrades may add safe defaults, but must
never silently substitute a different field.

## 7. Initial visual components

The proof of concept supports:

- fixed text;
- bound text;
- church logo or other approved image fields;
- horizontal and vertical lines;
- rectangles with border and fill;
- a repeating detail table;
- report and page headers/footers;
- family grouping;
- page number, page count, generation date/time, and report title;
- alignment, padding, font, color, border, and visibility properties;
- standard formatters for names, addresses, phone numbers, dates, and times.

Free-form scripting, arbitrary formulas, charts, crosstabs, nested subreports,
HTML, rich text, barcodes, and user-supplied plugins are deferred.

## 8. Designer interaction

The initial designer window contains:

- a page canvas with printable margins and a zoom control;
- a component palette;
- a dataset-field palette showing only approved fields;
- a property panel for the current selection;
- undo and redo;
- grid and snap controls;
- alignment and distribution commands;
- preview, validate, save, save as, and restore-starter-layout commands.

Keyboard movement and resizing must be supported. The designer must warn about
elements outside printable bounds, overlaps likely to obscure content, missing
bindings, inaccessible contrast, and detail rows too wide for the page.

Double-clicking a visual element opens its most relevant editor. The saved file
must not change merely from opening and closing the designer.

## 9. Rendering model

The renderer receives two separate inputs:

1. a validated report definition;
2. an in-memory dataset produced by ChurchManager for the current authorized
   report run.

It lays out bands deterministically, repeats detail rows, applies grouping and
page breaks, and produces a PDF. Preview uses the same measurements and
pagination as the final PDF.

The first renderer may use a stable Python PDF library internally, but that
library is an implementation detail. ChurchManager report definitions must not
depend on library-specific Python code.

## 10. Member Directory proof of concept

The first dataset contract is `membership.directory.v1` and requires
`reports.membership.contact`.

It supplies:

- church name, address, city, state, ZIP, phone, email, pastor, and logo;
- directory families;
- listed family addresses and contacts;
- people belonging to each directory family;
- listed personal addresses and contacts where the design permits them.

The provider excludes unlisted information before data reaches the designer or
renderer. The starter design follows the existing Member Directory report's
intent while using Reformation Lutheran Church test branding.

The proof of concept is accepted only when a user can:

1. open the starter design;
2. move and resize the church header and family elements;
3. change typography and column widths;
4. save the design as JSON;
5. close and reopen it without layout drift;
6. preview multiple fictional families across multiple pages;
7. generate a visually matching PDF;
8. verify that unlisted data is absent;
9. restore the starter layout;
10. run the report only with the required permission.

## 11. Definition storage and recovery

ChurchManager ships read-only starter definitions in the application. User
customizations are saved separately under the current Windows user's application
data, not over the shipped starter file.

Save uses a temporary file followed by an atomic replacement. The previous good
version is retained for recovery. Invalid or newer unsupported definitions do
not overwrite the last good definition.

Import and export of report definitions may be added after the proof of concept.
Imported definitions are schema-validated and cannot add dataset privileges.

## 12. Testing requirements

- JSON schema accepts valid definitions and rejects unknown or unsafe content.
- Permission checks occur before dataset creation, preview, design, and export.
- Unlisted contact data never enters the directory dataset.
- The same definition and dataset produce deterministic pagination.
- Save/reopen preserves all supported properties exactly.
- Unsupported dataset or field versions fail with useful messages.
- Long names, empty fields, large families, and page-boundary cases render safely.
- Fonts, images, headers, footers, and page numbers render correctly.
- Structural PDF checks and rendered-page visual review are reported separately.
- The legacy program and production database are never used by automated tests.

## 13. Development sequence

1. Approve this specification and freeze the proof-of-concept scope.
2. Define the JSForm report JSON schema and immutable in-memory model.
3. Implement the ChurchManager `membership.directory.v1` dataset provider.
4. Implement a non-editing renderer and reproduce the directory as a PDF.
5. Add definition load/save and starter-layout recovery.
6. Add the minimal canvas, selection, movement, and resizing tools.
7. Add field and property palettes plus formatting controls.
8. Add preview using the same renderer.
9. Complete permission, privacy, compatibility, and visual tests.
10. Review the proof of concept before selecting the next report or adding
    advanced features.

## 14. Deferred decisions

- advanced formulas and expression language;
- charts, crosstabs, labels, and subreports;
- report-definition sharing between congregations;
- accounting, donor, payroll, and banking datasets;
- email distribution and scheduled report generation;
- migration tooling for LimeReport definitions;
- whether a future standalone designer application is useful outside
  ChurchManager.

## 15. Project boundary

This is a side project. Until its proof of concept is accepted, it does not
replace the existing ChurchManager development sequence, and it does not require
changes to production or the independent legacy program.
