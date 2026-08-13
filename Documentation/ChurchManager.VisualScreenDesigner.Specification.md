# ChurchManager Visual Screen Designer Specification

Status: Approved for implementation by Rev. Jonathan C. Watt  
Date: August 12, 2026  
Framework owner: JSForm  
Application integration owner: ChurchManager

## 1. Purpose

Provide a visual editor for JSForm screen definitions so authorized users can
arrange and configure screens without hand-editing JSON. The designer uses the
same named-root JSON format as existing JSForm screens and shares the mature
interaction conventions of the JSForm report designer.

The independent legacy program and production databases are outside this
project and must not be opened or modified by the designer or its tests.

## 2. Ownership boundary

JSForm owns the generic screen-definition model, catalog, canvas, property
editor, undo/redo, clipboard operations, alignment and distribution, form-size
editing, validation, safe persistence, starter restoration, preview interface,
and automated framework tests.

ChurchManager owns the approved form directory, protected-form policy,
authorization and audit boundaries, main-menu integration, application-specific
preview construction, and ChurchManager tests and migrations.

## 3. Security

- Opening the ChurchManager designer requires `screens.design`.
- The permission is sensitive and initially belongs only to Master
  Administrator.
- Menu visibility is not authorization; the launch service rechecks permission.
- The catalog is confined to approved `.json` files beneath configured form
  roots. Path traversal and arbitrary file browsing are rejected.
- Passwords, credentials, stored hashes, and live record values are never
  written into a screen definition.
- Table/query metadata and control security declarations are displayed to the
  designer, but the first release does not provide free-form SQL editing.
- Saving validates the complete definition against JSForm's canonical schema.
- Shipped starters are never overwritten. ChurchManager customizations are
  stored separately under the current user's local application-data directory.
- Open, save, save-as, restore, validate, and preview operations are auditable
  through ChurchManager's existing application audit boundary.

## 4. Functional scope

The first release includes the report designer's applicable features:

- catalog, open, save, save as, previous-version recovery, and restore starter;
- menu bar plus a compact two-row toolbar;
- zoom, fit form, grid display, and snap to grid;
- selection by canvas or control list and visible selection highlighting;
- drag move, corner resize, keyboard move, and Shift+keyboard resize;
- add, duplicate, copy, paste, Delete-key deletion, and stable unique names;
- undo and redo with grouped transactions;
- align left/right/top/bottom and distribute across/down;
- form position and size editing;
- control position, size, label, type, tooltip, visibility, read-only, required,
  font, colors, alignment, layout, and security-property editing where supported;
- validation for root naming, schema compatibility, duplicate names, invalid
  geometry, controls outside the form, and overlapping controls;
- preview through a caller-supplied safe preview handler;
- no JSON changes merely from opening and closing the designer.

## 5. Definition and coordinate rules

The filename `frmExample.json` contains exactly one root named
`frmExampleFORM`, with `FORM` and `CONTROLS` children. Existing `posch` and
`sizech` values remain the authoritative logical coordinates. The designer does
not silently convert a legacy layout to responsive layout or rewrite unrelated
properties.

All unknown but schema-valid properties are preserved round-trip. A property is
removed only by an explicit user action.

## 6. Preview

JSForm exposes a preview callback rather than opening a database itself.
ChurchManager previews only approved test-safe forms and may substitute empty or
fictional values. Preview never saves data. Forms whose construction would
execute unsafe application behavior are validation-only until a developer adds
an approved preview adapter.

## 7. Persistence and recovery

Saves use UTF-8 JSON, a temporary file, atomic replacement, and a `.previous`
copy of the last good definition. Definitions are schema-validated before the
replacement. Restore Starter replaces only the user's customization after
confirmation. Export/Save As cannot grant additional permissions.

## 8. ChurchManager integration

The main window adds **Screen Designer** beside **Report Designer**. The menu
entry requires `screens.design`; the dispatcher and designer service recheck it.
Migration 021 creates the sensitive permission and assigns it only to Master
Administrator. Regular users do not see or invoke the designer.

## 9. Acceptance criteria

1. An authorized master administrator can open the ChurchManager screen catalog.
2. A regular user is denied even when calling the launcher directly.
3. A screen can be moved, resized, edited, saved, closed, and reopened without
   drift or loss of unknown properties.
4. Copy/paste, duplicate, Delete, undo/redo, align, distribute, snap, fit, and
   form-size changes work as in the report designer.
5. Invalid definitions fail before replacing the last good file.
6. Restore Starter and restore previous recover a working definition.
7. Production and legacy paths and databases are never accessed by automated
   tests.
8. JSForm and ChurchManager automated suites pass.

## 10. Deferred work

- visual creation of arbitrary SQL, Python handlers, or permission names;
- live data editing inside preview;
- a full responsive-grid authoring mode;
- subform relationship authoring and database schema design;
- multi-user synchronization or server-hosted layouts;
- conversion of every legacy form to a user-customized layout.
