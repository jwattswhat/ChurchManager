# ChurchManager Hymn Stanza Selection Specification

**Status:** Proposed for approval; not yet implemented  
**Prepared:** August 14, 2026  
**Scope:** Development ChurchManager and ChurchDBTest only until separately approved for production  
**Out of scope:** The separate Frozen ChurchManager application and its database

## 1. Objective

Allow a worship planner to record which stanzas of each selected hymn will be sung at a particular service, preserve that choice in service history, and display it consistently in the weekly worship plan, bulletin order, reports, and other worship-planning outputs.

Examples:

- `LSB 656`
- `LSB 656, sts. 1–4`
- `LSB 581, sts. 1, 3, 11–12`
- `LSB 442, st. 1` 

Leaving the stanza selection blank means the service uses the complete hymn or that no stanza restriction has been specified.

## 2. User outcome

For every hymn assigned to a service-order position, the planner can:

1. Select the hymn.
2. Optionally enter the stanzas to be sung.
3. See the stanza selection beside the hymn in the planning screen.
4. Have the formatted selection appear automatically in the weekly order and reports.
5. Edit or clear the stanza selection without reselecting the hymn.
6. Preserve the selection as part of that service's historical hymn usage.

## 3. Source-of-truth rule

The stanza selection belongs to `tblHymnUsage`, because it describes the use of a hymn in one particular service and order position.

It does not belong to:

- `tblHymn`, because the same hymn may use different stanzas at different services.
- `tblProperHymnSuggestion`, because a suggestion should not silently impose service-specific stanza choices in the first implementation.
- `tblServiceBulletinOrderLine.WeeklyValue`, because that is rendered display text rather than normalized worship-planning data.

`tblHymnUsage` is authoritative. `WeeklyValue` is regenerated from the selected hymn and stanza value.

## 4. Proposed data change

Add one nullable column to `tblHymnUsage`:

```sql
Stanzas varchar(100) NULL
```

The stored value is the normalized stanza expression only, without `st.`, `sts.`, the hymnal abbreviation, hymn number, or title.

Examples of stored values:

- `1`
- `1-4`
- `1,3,11-12`

Blank input is stored as `NULL`.

### Why a normalized string is appropriate initially

A fully relational row for every selected stanza would add complexity without a current requirement to search or report on individual stanza numbers. A normalized expression is sufficient for planning, display, export, and historical preservation.

If ChurchManager later stores hymn texts stanza by stanza, the expression can be parsed into individual selections without changing the user-facing syntax.

## 5. Accepted input

The editor accepts:

- A single positive number: `3`
- A comma-separated list: `1,3,5`
- An inclusive range: `1-4`
- Mixed lists and ranges: `1,3,11-12`
- User-entered spaces, which are removed during normalization
- An en dash in place of a hyphen, normalized to `-`
- Optional pasted prefixes `st.` or `sts.`, removed during normalization

The following are rejected:

- Zero or negative stanza numbers
- Descending ranges such as `4-2`
- Empty elements such as `1,,3`
- Non-numeric labels
- Open-ended ranges such as `3-`
- Duplicate stanza numbers after expansion

The application does not initially reject a stanza number merely because it exceeds a hymn's known stanza count. ChurchManager does not yet have complete, authoritative stanza-count metadata for every hymnal entry. When a reliable count exists in a future hymnal model, the editor may warn without corrupting historical or alternate-edition selections.

## 6. Canonical formatting

Display rules:

- No stanza restriction: `LSB 656 A Mighty Fortress Is Our God`
- One stanza: `LSB 656, st. 3 A Mighty Fortress Is Our God`
- More than one stanza or a range: `LSB 656, sts. 1–4 A Mighty Fortress Is Our God`

The user enters simple numeric syntax. ChurchManager supplies `st.` or `sts.` and converts stored hyphen ranges to en dashes for display.

The display formatter must be shared by:

- Weekly worship-plan screen
- `tblServiceBulletinOrderLine.WeeklyValue`
- Bulletin-order preview and generated order
- Worship-planner reports
- Hymn-usage history
- Any future export or calendar summary containing service hymns

## 7. Weekly worship-plan interface

On the **Plan Hymns and Readings** dialog:

1. Add a **Stanzas** column between **Title** and **Suggested**.
2. Add an **Edit Stanzas...** button.
3. Double-clicking the Stanzas cell or invoking the button opens a small editor for the selected hymn slot.
4. The editor shows the selected hymn number and title for context.
5. The editor accepts a stanza expression and displays a concise example such as `1,3,11-12`.
6. Saving validates and normalizes the expression.
7. Clearing the field sets `Stanzas` to `NULL`.
8. The command is disabled when the selected service slot has no hymn.

Selecting a different hymn for the same slot clears the prior stanza selection by default. This prevents stanza choices from one hymn from being applied accidentally to another hymn.

Clearing a hymn also clears its stanza selection because the associated `tblHymnUsage` row is deleted.

## 8. Applying Proper hymn suggestions

The existing **Apply Suggested Hymns** operation replaces service-slot hymn usage rows. In the first implementation:

- Applied suggestions have no stanza restriction.
- Existing stanza choices are cleared when the hymn in a slot changes.
- If an applied suggestion resolves to the same hymn already occupying that same slot, the current stanza choice should be retained.

The last rule prevents a harmless refresh of suggestions from erasing deliberate planning work.

## 9. Bulletin-order behavior

When a service hymn is selected or its stanzas are edited, ChurchManager regenerates the corresponding weekly line from normalized data.

The generated value includes:

- Hymnal abbreviation and hymn number as stored in the selected hymn entry
- Stanza notation when supplied
- Hymn title

The exact placement of the stanza notation must remain compatible with the bulletin's right-aligned hymn reference. If a bulletin template separates the label, title, and reference in the future, the stanza formatter should remain reusable rather than embedded in a template-specific string.

## 10. Reports and history

Add `Stanzas` to the worship-planner hymn report view and any general hymn-usage view used by ChurchManager.

Historical queries must be able to answer:

- Which hymn was used?
- At which service and position?
- Which stanzas were selected?

Existing rows remain valid with `Stanzas=NULL`, meaning no restriction was recorded.

The migration must not attempt to infer stanza selections from free-form historical service notes. For example, an old note saying `Hymn 581 verses 1, 3, 11, 12` is evidence that the feature is useful, but automatically associating such prose with the correct service-order slot would be unsafe.

## 11. Copyright and licensing

Stanza selection metadata does not itself reproduce copyrighted hymn text or music. It may, however, help determine what was printed, projected, or streamed.

This feature does not claim to perform CCLI or ONE LICENSE reporting. It should preserve enough accurate service-level usage information to support a later copyright-reporting feature.

## 12. Migration and compatibility

The implementation should use the next available guarded migration and:

1. Add the nullable `Stanzas` column only if absent.
2. Update relevant report views without dropping unrelated columns.
3. Leave all existing hymn-usage rows unchanged.
4. Avoid any production or Frozen-application connection.
5. Be exercised first against ChurchDBTest.

No existing service requires backfill because `NULL` is a valid historical value.

## 13. Proposed implementation components

After approval, implementation is expected to touch:

- A new guarded MariaDB migration
- `weekly_worship_plan_dialog.py`
- The shared hymn-display formatting path, likely factored from current repository code
- `bulletin_orders.py` where hymn weekly values are created or copied
- Worship-planner report views
- Unit tests for parsing, normalization, formatting, persistence, suggestion application, and UI presence
- Database integration tests against ChurchDBTest
- User documentation describing stanza syntax

## 14. Acceptance criteria

The feature is complete only when all of the following pass:

1. A planner can save `1,3,11-12` for a selected service hymn.
2. It is stored canonically as `1,3,11-12` on the correct `tblHymnUsage` row.
3. The planning screen displays `1, 3, 11–12` or another documented readable form.
4. The weekly order displays the hymn with `sts. 1, 3, 11–12`.
5. One selected stanza displays with singular `st.`.
6. Blank input removes the restriction.
7. Invalid expressions are rejected with a plain-language message and no partial database change.
8. Changing or clearing the hymn does not leave stale stanza data.
9. Reapplying the same suggested hymn preserves its stanza selection.
10. Applying a different suggested hymn clears the old stanza selection.
11. Reports include the stored stanza selection.
12. Existing hymn usage remains unchanged and readable.
13. LSB suggestion, bulletin-order, and hymn-history tests continue to pass.
14. ChurchDBTest migration and application tests pass.
15. No Frozen application file, runtime, configuration, or database is accessed or changed.

## 15. Deferred enhancements

The first implementation intentionally defers:

- Stanza defaults on Proper hymn suggestions
- Hymnal-entry stanza counts and validation against them
- Separate assignments for choir, congregation, soloist, or alternating groups
- Refrain-only and stanza/refrain performance patterns
- Different tunes or harmonizations by stanza
- Automatic lyric extraction or bulletin insertion
- Automatic CCLI or ONE LICENSE submission
- Recovery of stanza choices from historical free-form notes

These require the broader canonical hymn, text, tune, setting, and copyright model proposed for future multi-hymnal support.

## 16. Approval boundary

Approval of this specification authorizes implementation and testing in development ChurchManager and ChurchDBTest only. Production deployment would remain a separate reviewed action.
