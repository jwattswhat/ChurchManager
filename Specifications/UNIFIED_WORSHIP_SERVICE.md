# Unified Worship Service Editor

## Purpose

The Worship Service editor is the single workspace for preparing and saving a
service. It replaces the separate service form, weekly-order editor, hymn plan,
and apply-selection steps.

## Layout

- Left panel (approximately two thirds): template selector and independently
  scrollable Order of Service grid.
- Right panel (approximately one third): independently scrollable service data.
- A fixed action bar applies to the complete service.

The internal sequence used to order database rows is not displayed. Users see
the service lines directly in their resulting order.

## Service data

The service panel retains Church, date and time, location, Proper, printable
liturgical date, Holy Communion, Psalm or Introit, sermon, bulletin, checklist,
Order of Service notes, and service notes.

Order of Service notes are supplied by the selected template and are read-only
on the Worship Service screen. Service notes remain independently editable.

Psalm or Introit and the final name/behavior of printable liturgical date remain
open design questions. Existing data is preserved until those decisions are
made.

## Working Order of Service

Selecting a template fills the working grid. Changing the template wholly
replaces the working grid after warning about unsaved work.

Selecting a Proper fills readings and suggested hymns:

- Match each Order of Service hymn line to Suggested Use by exact text.
- Walk Order of Service lines from top to bottom.
- Use the first unused matching suggestion.
- Allow the same hymn when separate suggestion records select it.
- Ignore suggestions left after all matching positions are filled.
- Leave positions blank when no exact match exists.

The user may edit the resulting weekly outline before saving.

## Save

Save writes the service record and the displayed weekly Order of Service as one
operation. The displayed weekly order becomes the authority for preview and
output. Actual hymn selections are recorded in hymn usage by weekly line.

## Validation

All occurrences of a duplicated hymn are flagged. Missing required hymns,
readings, and other required values are flagged. Additional validation rules may
be added as the workflow is tested.

## Template management

Reusable starter and custom templates remain separate from weekly services.
Applying a different template replaces the current working order. Deleting a
custom template removes weekly orders based on it, with an explicit warning.
