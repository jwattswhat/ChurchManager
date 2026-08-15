# ChurchManager Hymn Stanza Selection Specification

**Status:** Implementation-ready; awaiting approval

**Prepared:** August 15, 2026

**Scope:** Development ChurchManager and ChurchDBTest only

**Out of scope:** Frozen ChurchManager-Legacy, production ChurchDB, and the JSForm framework

## 1. Purpose

Allow the worship planner to record which stanzas of each selected hymn will be sung at a particular service. The selection must remain attached to that exact service hymn usage and appear consistently on the planning screen, weekly Order of Service, and worship-planning reports.

Examples of printed references:

- `LSB 656`
- `LSB 656, st. 3`
- `LSB 656, sts. 1–4`
- `LSB 581, sts. 1, 3, 11–12`

A blank stanza selection means that no stanza restriction was recorded; normally, the complete hymn is intended.

## 2. Ownership boundary

This is ChurchManager worship-domain behavior, not generic JSForm behavior.

- ChurchManager owns stanza parsing, hymn-reference formatting, persistence, and worship-planning rules.
- JSForm requires no change.
- ChurchManager-Legacy remains frozen and completely separate.

## 3. Source of truth

Add the stanza selection to `tblHymnUsage`, because it describes one hymn used in one service position.

It does not belong to:

- `tblHymn`, because the same hymn may use different stanzas at different services.
- `tblProperHymnSuggestion`, because a suggestion does not prescribe stanzas in this version.
- `tblServiceBulletinOrderLine.WeeklyValue`, because that field is the displayed hymn title, not the normalized source record.

The authoritative relationships remain:

- `tblHymnUsage.ServiceBulletinOrderLineID` identifies the weekly Order of Service line.
- `tblHymnUsage.HymnID` identifies the selected hymn.
- `tblHymnUsage.Stanzas` identifies the selected stanzas for that use.

## 4. Database change

Migration **067** will add:

```sql
ALTER TABLE tblHymnUsage
    ADD COLUMN Stanzas varchar(100) NULL;
```

The guarded migration must add the column only when absent and update the worship-planning report view without removing unrelated fields.

Stored values contain only the canonical stanza expression:

- `1`
- `1-4`
- `1,3,11-12`

Blank input is stored as `NULL`. Existing records remain unchanged and valid. No historical text will be parsed or backfilled.

## 5. Input and validation

The user may enter:

- one positive stanza number: `3`
- a comma-separated list: `1,3,5`
- an inclusive range: `1-4`
- a mixture: `1,3,11-12`
- spaces, which are removed during normalization
- an en dash, which is normalized to `-`
- pasted `st.` or `sts.` prefixes, which are removed

Reject:

- zero or negative numbers
- descending ranges such as `4-2`
- empty elements such as `1,,3`
- nonnumeric content
- open ranges such as `3-`
- duplicate expanded stanza numbers, such as `1-3,3`

The first version will not enforce a maximum stanza number because ChurchManager does not yet have authoritative stanza counts for every hymnal entry.

Invalid input must produce a plain-language message and make no database changes.

## 6. Shared ChurchManager functions

Add a small domain module, expected to be `hymn_stanzas.py`, with independently tested functions equivalent to:

```python
normalize_stanzas(text) -> str | None
format_stanza_notation(value) -> str
format_hymn_reference(hymnal_abbreviation, hymn_number, stanzas) -> str
```

Formatting rules:

- `NULL` -> no stanza suffix
- `3` -> `st. 3`
- `1-4` -> `sts. 1–4`
- `1,3,11-12` -> `sts. 1, 3, 11–12`

All ChurchManager screens and reports must use this shared formatter rather than reproduce the rules.

## 7. Planning-screen behavior

On **Plan Hymns and Readings**:

1. Add a **Stanzas** column between **Title** and **Suggested**.
2. Add an **Edit Stanzas...** button.
3. Enable the button only when the selected row is a hymn position with a selected hymn.
4. Show the hymn number and title in the editor for context.
5. Show an example such as `1,3,11-12`.
6. Validate and normalize on save.
7. Clearing the entry stores `NULL`.
8. Retain the existing double-click action for selecting or changing a hymn; stanza editing uses the clearly labeled button.

Screen columns remain separate:

- **Hymn:** hymn number
- **Title:** hymn title
- **Stanzas:** readable stanza expression

## 8. Weekly Order of Service synchronization

The normalized hymn usage and weekly line must remain synchronized:

- `WeeklyValue` stores the hymn title only.
- `ReferenceText` stores the formatted reference, such as `LSB 656, sts. 1–4`.
- `tblHymnUsage.Stanzas` stores `1-4`.

Saving a stanza edit updates `tblHymnUsage.Stanzas` and the matching weekly line's `ReferenceText` in one transaction. Failure rolls back both changes.

Direct free-form editing must not silently desynchronize a normalized hymn line. Hymn, title, reference, and stanza changes for `SERVICE_HYMN` lines must go through the hymn-planning workflow.

## 9. Changing, clearing, and applying hymns

- Selecting a different hymn clears the previous stanza selection.
- Clearing the hymn removes its `tblHymnUsage` record and therefore its stanza selection.
- Reapplying a Proper suggestion that resolves to the same hymn in the same line preserves the stanzas.
- Applying a different suggested hymn clears the stanzas.
- A newly applied suggestion starts with `Stanzas=NULL`.

Proper suggestions continue to match service positions by exact **Suggested Use**, including repeated positions such as `Distribution Hymn`, and are consumed in order.

## 10. Replacing the weekly template

Applying a different Order of Service template still wholly replaces the weekly order. Existing weekly line selections are rebuilt.

When ChurchManager reattaches an already selected hymn to a compatible new line with the same exact `UsedAs` position, it must carry that hymn's `Stanzas` with it. If the selection cannot be reattached, both the hymn selection and its stanza selection are discarded. Stanzas must never transfer to a different hymn.

## 11. Duplicate hymn rule

The existing duplicate-hymn warning remains unchanged:

- Duplicate detection is based on `HymnID` within the service.
- The same hymn is a duplicate even when different stanzas are selected.
- Every occurrence of the duplicate is flagged.
- The warning applies whether the duplicate came from suggestions or manual selection.

## 12. Reports and output

Migration 067 will extend `rpt_worship_planner_hymn` to expose at least:

- `HymnID`
- `HymnNumber`
- `Title`
- `Stanzas`
- `ReferenceText`
- the existing compatible `Hymn` display value

The worship-planning report dataset contract will be extended additively so custom report layouts may place the stanza or formatted reference separately. Because existing fields remain intact, its compatible version remains 4. The starter planning report will display the formatted hymn reference without combining it with the title.

Existing custom layouts that use the current `Hymn` field must remain loadable. Any contract-version upgrade must follow the existing report compatibility mechanism.

Hymn-usage history must preserve and expose the recorded stanza selection when that history is displayed or reported.

## 13. Copyright boundary

This feature stores only hymn-identification and stanza-selection metadata. It does not store hymn text, extract lyrics, produce licensing reports, or submit information to CCLI or ONE LICENSE.

## 14. Files expected to change

After approval, implementation is expected to include:

- `migrations/067_add_hymn_stanza_selections.sql`
- new `hymn_stanzas.py`
- `weekly_worship_plan_dialog.py`
- `bulletin_orders.py`
- worship-planning report view and dataset code
- worship-planning starter report if needed
- focused unit and database integration tests
- relevant user documentation

No JSForm or ChurchManager-Legacy file is expected to change.

## 15. Acceptance tests

The feature is complete when:

1. `1,3,11-12` saves canonically on the correct `tblHymnUsage` row.
2. One stanza formats with singular `st.`.
3. Multiple stanzas or ranges format with plural `sts.` and readable spacing/en dashes.
4. `WeeklyValue` remains the title and `ReferenceText` contains the formatted reference.
5. Blank input removes the stanza restriction.
6. Invalid input changes neither the usage row nor weekly line.
7. Changing or clearing a hymn leaves no stale stanza data.
8. Reapplying the same suggested hymn preserves stanzas.
9. Applying a different suggested hymn clears stanzas.
10. Replacing a template preserves stanzas only with a reattached matching hymn usage.
11. Duplicate hymns are flagged regardless of differing stanzas.
12. Planning reports expose and print stanza information correctly.
13. Existing rows with `Stanzas=NULL` continue to work.
14. Migration 067 applies successfully to ChurchDBTest.
15. Focused tests and the full automated test suite pass.
16. Manual GUI verification confirms selection, editing, clearing, suggestion application, template replacement, duplicate warnings, and report output.
17. No production or ChurchManager-Legacy resource is accessed or changed.

## 16. Deferred work

Deferred intentionally:

- default stanzas on Proper suggestions
- validation against hymnal stanza counts
- choir, soloist, congregation, or alternating-group assignments
- refrain-only and stanza/refrain patterns
- stanza-specific tunes or harmonizations
- lyric insertion into bulletins
- automatic copyright reporting
- inference from historical free-form notes

## 17. Approval boundary

Approval authorizes implementation and testing in development ChurchManager and ChurchDBTest only. Production deployment remains a separate reviewed action.
