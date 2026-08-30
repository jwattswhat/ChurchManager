# ChurchManager Data Management Specification

Status: Approved roadmap implementation

## Purpose

Data Management provides a single, guarded place to review duplicate people and
families, import congregation-owned data, export authorized data, and create a
portable archive. It does not bypass ChurchManager forms, privacy rules, or
authorization.

## Safety rules

- Import preview never writes to the database.
- Every import uses explicit column mapping and validates every row.
- Likely duplicates are reviewed; ChurchManager never silently merges records.
- A committed import is one transaction and records accepted and rejected rows.
- Exports use approved fields and exclude unlisted contact information unless an
  explicit sensitive-contact permission authorizes it.
- Passwords, password hashes, audit internals, confidential giving identity,
  accounting detail, and encrypted pastoral narratives are never included in a
  general membership export.
- Portable archives identify their format and ChurchManager version and are
  validated before restoration or import.
- A duplicate merge requires an explicit survivor, a reason, and final
  confirmation. All foreign-key relationships move in one transaction; any
  uniqueness conflict rolls back the entire merge. A safe provenance record
  remains after the duplicate is removed.

## Delivery phases

1. **Duplicate review.** Detect exact normalized email and telephone matches,
   exact normalized person names, and exact normalized family names and mailing
   addresses. Results are advisory and link the two record identifiers.
2. **CSV preview.** Choose a people/family CSV, map its columns, validate values,
   and display accepted and rejected rows without database changes.
3. **Reviewed import.** Clearly mark valid rows Ready and duplicate or invalid
   rows Excluded. Require confirmation, import the Ready rows atomically, retain
   rejected-row reasons, and audit the outcome without storing unnecessary source
   content.
4. **Privacy-safe export.** Export approved people/family datasets, enforce
   unlisted contact rules, neutralize spreadsheet-formula cells through the
   shared CSV rule, and record who exported what and when. Portable
   archive CSV payloads use the same protection.
5. **Resolution and portability.** Provide deliberate duplicate merge/archive
   actions and a documented portable archive distinct from ordinary reports and
   database backup.

## Duplicate rules

Normalization is conservative: surrounding whitespace and presentation
punctuation are ignored for comparison, but partial names and approximate
spellings are not automatically treated as duplicates. Every result states its
reason and both database record IDs. Duplicate review changes no records.
