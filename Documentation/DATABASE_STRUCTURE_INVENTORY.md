# ChurchManager Database Structure Inventory

Last reviewed: 2026-08-14

This inventory tracks old JSForm-era database structures that remain in the
development ChurchManager system. In this document, **legacy** means obsolete
development-era structure or behavior. It does not refer to, depend upon, or
authorize changes to the separate Frozen ChurchManager application.

## Retired structures

| Structure | Present status | Recommendation |
|---|---|---|
| `tblOrderofService` | Removed by migration 053 after conversion to structured bulletin-order templates. | Retired. |
| `tblSchedule` | Removed by migration 053 after conversion to `tblWorshipSchedulePattern`. | Retired. |
| `tblCheckList` | Removed by migration 053 after replacement by normalized worship-preparation checklists. | Retired. |
| `tblAltReading` | Removed by migration 053; weekly readings are edited in the structured weekly Order of Service. | Retired. |
| `tblService.OrderofService` | Removed by migration 053 after replacement by structured weekly/template relationships. | Retired. |
| `tblService.CheckListComplete` | Still actively used as the user's overall approval that preparation is complete. | Keep. This field has a defined purpose in the current design. |
| `tblWorshipRole.LegacyRoleID` | Removed by migration 053 after role conversion was verified. | Retired. |
| `tblWorshipSchedulePattern.SourceLegacyScheduleID` | Removed by migration 053 after schedule conversion was verified. | Retired. |
| `tblServiceRole.Role` | Removed by migration 053; `WorshipRoleID` is now required. | Retired. |
| `tblParticipant.Roles` and `tblParticipant.Schedule` | Removed by migration 053 after migration 052 converted the remaining test participants. | Retired. |
| `tblBulletinOrderTemplate.SourceLegacyName` and `tblBulletinOrderLine.LegacyContent` | Removed by migration 053 after conversion was verified. | Retired. |
| Historical schema files under `SQL\` | Old database dumps and table exports; they are not the authoritative migration history. | Archive or remove them after confirming that the numbered migrations and documented installation process contain everything still required. |

## Older-named structures that remain current

These tables may predate the current redesign, but they still have an active,
defined purpose and should not be classified as obsolete merely because of
their age or naming:

| Structure | Current purpose |
|---|---|
| `tblParticipant` | Stores worship participants, including people who are not congregation members. |
| `tblChoices` | Maintains controlled categories and other shared choices used by current screens. |
| `tblPrayer` | Stores current prayer content and its normalized schedule/category information. |
| `tblAnnouncement` | Stores current announcement content and its normalized schedule/category information. |
| `tblHymnal` | Stores installed hymnals. |
| `tblHymn` | Stores hymns belonging to installed hymnals. |
| `tblHymnUsage` | Preserves hymn-selection and usage history. |

## Retirement procedure

An old structure is not removed merely because its replacement exists. Before
removal:

1. Search current application, report, form, and view definitions for readers and writers.
2. Inspect the live `ChurchDBTest` schema, row counts, foreign keys, and dependent views.
3. Compare converted records with the normalized replacement tables.
4. Replace remaining application and report references.
5. Add a guarded, numbered migration that removes the obsolete structure.
6. Update automated tests, installation resources, and this inventory.

## Verification status

Migrations 052 and 053 were applied to `ChurchDBTest` on 2026-08-14. The
preflight initially found four participant availability records and one role
record created after the original normalization. Migration 052 preserved those
records in the normalized relationship tables before migration 053 removed the
obsolete structures. A live information-schema check found no listed obsolete
tables or columns remaining. All 21 read-only database integration tests and
all 408 general automated tests passed afterward.
