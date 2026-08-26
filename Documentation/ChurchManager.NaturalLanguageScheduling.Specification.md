# ChurchManager Natural-Language Scheduling Specification

**Status:** Implemented and visually accepted in ChurchDBTest

**Prepared:** August 15, 2026

**Scope:** Development ChurchManager and ChurchDBTest only

**Out of scope:** Production ChurchDB and the JSForm framework

## 1. Purpose

Replace the prayer and announcement schedule dialog's preset choices and monthly-Sunday checkboxes with a single, friendly schedule sentence.

Examples:

- `Every Sunday`
- `First and third Sundays of each month`
- `Last Sunday of each month`
- `First Sunday of each year`
- `Every year on October 1`
- `Every Christmas Eve`
- `Every New Year's Day`
- `First Sunday after the Fourth of July`
- `Once on December 24, 2026`

ChurchManager will interpret the sentence, show the user what it means, and store a standard recurrence rule. The stored rule—not the prose—is authoritative.

## 2. Current system

The database checkbox columns and `Continuous` fields were already removed by migrations 045 and 046. The current system stores private ChurchManager codes such as:

- `EVERY_SUNDAY`
- `MONTHLY_SUNDAYS:1,3`
- `ANNUAL_DATE:10-01`
- `ANNUAL_FIRST_SUNDAY`
- `ONE_TIME:2026-12-24`

The current schedule dialog still uses preset pages and five monthly-Sunday checkboxes. This project replaces both that dialog and those private rule codes.

## 3. Ownership boundary

This is ChurchManager domain behavior.

- ChurchManager owns the supported language, recurrence parsing, descriptions, service-week behavior, and database migration.
- JSForm requires no change.

## 4. Stored data

Both `tblPrayer` and `tblAnnouncement` will have:

- `ScheduleText varchar(255) NOT NULL`: canonical, friendly wording shown to the user.
- `ScheduleRule varchar(255) NOT NULL`: normalized RFC 5545 recurrence-set text used for evaluation.
- Existing `StartDate` and `EndDate`: optional inclusive limits on the schedule.

The application must never calculate inclusion by reparsing `ScheduleText`. It parses natural language only when a schedule is entered or changed.

Canonical examples:

| Friendly schedule | Stored rule |
|---|---|
| Every Sunday | `RRULE:FREQ=WEEKLY;BYDAY=SU` |
| First and third Sundays of each month | `RRULE:FREQ=MONTHLY;BYDAY=1SU,3SU` |
| Last Sunday of each month | `RRULE:FREQ=MONTHLY;BYDAY=-1SU` |
| First Sunday of each year | `RRULE:FREQ=YEARLY;BYMONTH=1;BYDAY=1SU` |
| Every year on October 1 | `RRULE:FREQ=YEARLY;BYMONTH=10;BYMONTHDAY=1` |
| Every Christmas Eve | `RRULE:FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=24` |
| Every New Year's Day | `RRULE:FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1` |
| First Sunday after the Fourth of July | `RRULE:FREQ=YEARLY;BYMONTH=7;BYDAY=SU;BYMONTHDAY=5,6,7,8,9,10,11` |
| Once on December 24, 2026 | `RDATE:20261224` |

`RDATE` is used for a one-time date because a one-time occurrence is not truly a repeating rule.

## 5. Supported language in version 1

The parser is deliberately controlled rather than a general English-language interpreter.

It will accept common variations of:

1. Every Sunday:
   - `Every Sunday`
   - `Each Sunday`
   - `Weekly on Sunday`
2. Ordinal Sundays of every month:
   - any combination of `first`, `second`, `third`, `fourth`, and `fifth`
   - `last Sunday of each month`
   - singular or plural `Sunday`
   - optional wording such as `of each month`, `of the month`, or `monthly`
3. Annual dates:
   - `Every year on October 1`
   - `Annually on Oct 1`
   - supported fixed-date holiday names:
     - `New Year's Day` (January 1)
     - `Christmas Eve` (December 24)
     - `Christmas Day` (December 25)
     - `New Year's Eve` (December 31)
   - accepted forms include `Every Christmas Eve`, `Each Christmas Day`, and `Annually on New Year's Day`
4. First Sunday of the year:
   - `First Sunday of each year`
   - `First Sunday of the year`
5. One-time dates:
   - `Once on December 24, 2026`
   - `On December 24, 2026 only`

Matching is case-insensitive and tolerates ordinary punctuation, extra spaces, and a small approved typo list such as `sinday` for `Sunday`. ChurchManager will store corrected canonical wording rather than the misspelled input.

`Each` and `Every` are interchangeable wherever either word introduces a repeating schedule.

Version 1 also accepts `First Sunday after <fixed month and day>` when the following seven dates remain in the same month. `After` is strict: if December 1 is itself Sunday, `First Sunday after December 1` means December 8. The wording `on or after` is not treated as equivalent.

For the common civil-holiday example, `Fourth of July`, `4th of July`, and `Independence Day` are equivalent. ChurchManager displays the canonical wording `First Sunday after the Fourth of July`.

Named holidays are accepted only when they always identify one fixed calendar date. Church-year and movable-feast expressions are expressly unsupported in version 1. Examples that must be rejected include:

- `First Sunday of Pentecost`
- `Second Sunday in Advent`
- `Sunday after Easter`
- `Ash Wednesday`
- `Palm Sunday`
- `Easter Day`

Those expressions require an authoritative liturgical-calendar engine and cannot safely be inferred from ordinary date parsing. ChurchManager will not silently convert them to an approximate date.

Version 1 will also reject ambiguous expressions such as `occasionally`, `when needed`, `most Sundays`, or `around Christmas`. It will explain that the schedule was not understood and leave the user's input available for correction.

## 6. Date parsing library

Use `python-dateutil` as the recurrence engine through `dateutil.rrule` and `rrulestr`.

ChurchManager will own the small grammar that recognizes recurring schedules. The `dateparser` package may be used only as a bounded helper for concrete dates such as `October 1` or `December 24, 2026`; it must not be treated as a recurrence parser.

For the initial implementation, the preferred approach is to parse English month names and the approved fixed-date holiday dictionary directly and avoid adding `dateparser` unless tests reveal a real benefit. This keeps installation smaller and the accepted language predictable. A general date parser must never cause an unsupported church-year phrase to be accepted.

## 7. User interface

The Prayer and Announcement editors will share one ChurchManager schedule control:

- Label: `Schedule`
- Editable text field containing the friendly sentence
- Example hint beneath it
- Read-only confirmation beginning `ChurchManager understands this as:`
- A short preview of the next three matching dates
- Existing optional `Starts` and `Ends` date controls

The confirmation and preview update when the field loses focus and before Save. A valid schedule can be saved without clicking a separate interpretation button.

If the schedule is invalid:

- Save is stopped.
- The schedule field remains unchanged and receives focus.
- The message identifies the unsupported portion when possible.
- Several supported examples are offered.

The raw recurrence rule is not shown on the ordinary screen. It may appear in support diagnostics.

## 8. Service-week behavior

The current Sunday-through-Saturday service-week rule remains unchanged.

If a schedule has any eligible occurrence during a service week, the prayer or announcement is valid for every worship service in that week. For example, `Every year on October 1` applies to all services in the Sunday-through-Saturday week containing October 1, including a Wednesday service.

`StartDate` and `EndDate` remain inclusive. An occurrence outside those limits does not activate the item.

## 9. Formatting rules back to natural language

ChurchManager will include a formatter for every recurrence shape it creates. This provides stable display wording without asking a general language model to reverse the rule.

Examples:

- `RRULE:FREQ=MONTHLY;BYDAY=1SU,3SU` becomes `First and third Sundays of each month`.
- `RDATE:20261224` becomes `Once on December 24, 2026`.

If an external tool inserts a valid recurrence outside ChurchManager's supported shapes, the editor will display `Custom recurrence rule` and require the user to replace it with a supported schedule before changing it. It will not silently reinterpret the rule.

## 10. Database migration

Migration 069 will be guarded and repeatable. It will:

1. Add `ScheduleText` to both tables.
2. Increase `ScheduleRule` to 255 characters.
3. Convert all current private rule codes to the standard rules in section 4.
4. Generate canonical `ScheduleText` for each converted row.
5. Update `rpt_sunday_prayer` and `rpt_sunday_announcement` to expose both fields.
6. Refuse to complete if any nonblank existing rule cannot be converted.

The migration will not modify migrations 045 or 046.

Before conversion, an equivalence check will evaluate every existing item across a multi-year date range using both the old and new engines. Any mismatch blocks the migration.

## 11. Application changes

1. Replace `ScheduleRuleDialog` with the shared natural-language schedule control.
2. Replace the custom evaluator in `sunday_content_rules.py` with:
   - controlled phrase parser
   - recurrence-set evaluator
   - canonical formatter
   - next-occurrence preview
3. Save both `ScheduleText` and `ScheduleRule` in `SundayContentRepository`.
4. Continue using `occurs_in_service_week` as the single weekly-inclusion entry point.
5. Update prayer and announcement lists and reports to display `ScheduleText`.
6. Log unsupported stored rules through the approved ChurchManager diagnostics system.

## 12. Validation and tests

Automated tests must cover:

- every supported phrase and accepted wording variation
- canonical rule and canonical display text generation
- parser/formatter round trips
- first through fifth and last Sundays
- months without a fifth Sunday
- leap years and February dates
- annual and one-time dates
- every approved fixed-date holiday name and wording variation
- rejection of church-year Sundays and movable feasts
- start and end boundaries
- Sunday-through-Saturday service-week inclusion
- invalid and ambiguous phrases
- typo tolerance without over-aggressive guessing
- next-occurrence preview
- old-to-new rule equivalence over multiple years
- prayer and announcement repository persistence
- report-view field contracts

Manual acceptance testing in ChurchDBTest will confirm:

1. A user can type each supported example and see the interpretation and next dates.
2. Invalid wording cannot be saved.
3. Existing prayer and announcement schedules behave exactly as before migration.
4. Weekly previews include the right items for Sunday and midweek services.
5. No monthly-Sunday checkboxes remain.

## 13. Acceptance criteria

The work is complete when:

- prayer and announcement scheduling uses one natural-language field
- ChurchManager stores a standard rule plus canonical friendly text
- existing schedules migrate without behavioral changes
- weekly service behavior remains correct
- invalid schedules fail clearly and safely
- all automated tests and ChurchDBTest acceptance checks pass
- no JSForm changes are required

## 14. Later possibilities, not part of version 1

- additional weekdays such as `Every Wednesday during Lent`
- exclusions such as `Every Sunday except Christmas Day`
- church-season-aware recurrence expressions
- a visual advanced recurrence editor
- localized schedule wording

These should be added only through explicit grammar and tests, not open-ended natural-language guessing.
