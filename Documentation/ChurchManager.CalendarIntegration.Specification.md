# ChurchManager external calendar integration specification

**Status:** Approved
**Version:** 1.1
**Date:** August 24, 2026
**Approved by:** Rev. Jonathan C. Watt
**Target application:** ChurchManager
**Primary external calendar:** Google Calendar
**Portable interchange:** iCalendar (`.ics`)

## 1. Purpose

ChurchManager will not maintain a competing calendar. It will maintain only
the dates needed by its own records and a small congregation-event listing,
then publish approved events to an external calendar. Google Calendar is the
primary expected destination, while standards-based iCalendar export keeps the
design provider-neutral.

## 2. First-release scope

Version 1 includes:

- a simple Church event record for congregation events not already represented
  by Worship Services, Group Meetings, or approved project milestones;
- natural-language recurrence, first event date, start/end time, all-day flag, location, safe description,
  owner, status, and publication flag;
- an agenda-style ChurchManager event list, not a month/week calendar UI;
- provider-neutral event descriptors from approved ChurchManager subsystems;
- `.ics` export for one event, a selected range, or an approved category;
- stable iCalendar UIDs so an updated export identifies the same event;
- explicit cancellation status;
- optional one-way Google Calendar publishing after secure OAuth setup;
- preview before publication;
- publication history, last result, and provider event identifier;
- permissions, auditing, backup, restore, and diagnostics; and
- safe handling of time zone and daylight-saving transitions.

Version 1 excludes:

- a full internal calendar, month/week grid, free/busy system, or calendar
  replacement;
- two-way synchronization or importing arbitrary external events;
- automatic conflict resolution or moving ChurchManager records;
- CalDAV server behavior;
- room, vehicle, or asset reservations;
- public registration, ticketing, payment, or attendance tracking beyond the
  owning ChurchManager subsystem;
- publishing restricted pastoral, Giving, audit, security, unlisted-contact,
  or private membership information; and
- background publication without an explicit configured policy.

## 3. Source-of-truth boundary

ChurchManager remains authoritative for:

- Worship Service date, time, location, and safe liturgical title;
- Group Meeting date, time, location, and approved public group name;
- simple Church Events;
- approved Project target dates and step due dates; and
- other dated records added through a future approved source adapter.

The external calendar is authoritative for ordinary calendar presentation,
personal reminders, invitations, colors, sharing, and provider-specific
features. Editing an exported event externally does not change ChurchManager.
Version 1 warns that later ChurchManager publication may replace provider-side
changes to fields owned by ChurchManager.

## 4. Simple Church events

### `tblChurchEvent`

| Field | Rule |
| --- | --- |
| `ID` | Positive primary key. |
| `ChurchID` | Required owning Church. |
| `EventKey` | Immutable Church-scoped stable key. |
| `Title` | Required safe public/administrative title. |
| `Description` | Optional bounded nonconfidential description. |
| `StartDateTime` / `EndDateTime` | Native local date-times for the first occurrence; end may not precede start. |
| `ScheduleText` | Required controlled natural language, such as `Every Tuesday`. |
| `ScheduleRule` | Canonical RFC 5545 rule derived from and displayed through `ScheduleText`. |
| `AllDay` | Uses dates rather than midnight-to-midnight guessing. |
| `TimeZoneName` | IANA/approved configured Church time zone. |
| `Location` | Optional bounded text. |
| `OwnerType` / `OwnerID` | Optional validated Person, Group, or User owner. |
| `Status` | Planned, Confirmed, Cancelled, or Completed. |
| `CalendarEligible` | Explicit publication eligibility. |
| audit fields | Creator/editor and timestamps. |

Standalone events use the same controlled natural-language scheduling engine
as other ChurchManager recurring content. `Each` and `Every` are equivalent;
the stored rule is deterministic rather than unrestricted prose. External
exports expand the rule into occurrences for the selected date range. Worship
and Group records retain their own source schedules and are not duplicated in
`tblChurchEvent`.

## 5. Provider-neutral event contract

Every source adapter returns a bounded descriptor containing:

- source type and immutable source ID;
- Church ID;
- stable UID;
- title, safe description, location;
- start/end or all-day dates;
- time zone;
- status and last-modified time;
- organizer/display owner when policy permits; and
- permission and publication-policy result.

The contract contains no SQL, callback, provider token, donor identity,
pastoral narrative, or unrestricted Person/Family data. Unsupported or
unauthorized sources fail closed.

## 6. iCalendar behavior

- UID format is stable and globally namespaced to ChurchManager, for example
  `worship-125@churchmanager.local-installation-id`.
- `DTSTAMP`, `DTSTART`, `DTEND`, `LAST-MODIFIED`, `STATUS`, and text escaping
  follow RFC 5545 requirements.
- Date-time exports include the configured time zone; all-day events use DATE
  values.
- Cancelled events export `STATUS:CANCELLED` when updating a previously
  published event.
- Line folding, Unicode, commas, semicolons, backslashes, and newlines are
  tested.
- Export writes a new file and never modifies the user's external calendar
  directly.

## 7. Google Calendar publishing

Google Calendar support is optional and one-way. Setup uses OAuth rather than
storing a Google password. Tokens use the existing protected credential
facility and never enter MariaDB, JSON configuration, logs, backups, or Git.

An administrator selects the destination calendar and runs **Test Connection**.
Before publishing, ChurchManager shows creates, updates, cancellations, skipped
records, and errors. Publication occurs only after confirmation unless the
administrator later enables an explicit bounded automatic policy.

Provider calls use the stable source UID and stored provider event ID. A failed
batch records per-event results and may be retried without creating duplicates.
Deleting an external event does not delete its ChurchManager source.

## 8. Publication state

### `tblCalendarPublication`

Stores Church ID, source type/ID, stable UID, provider, destination identifier,
provider event ID, last published source version/hash, last published time,
last result, and safe diagnostic code. Unique keys prevent duplicate active
bindings for the same source and destination.

Provider credentials are never stored in this table. Removing a binding does
not delete the source record and requires a clear choice about cancelling or
leaving the existing external event.

## 9. Privacy and security

- Publication requires `calendar.view` plus source-view permission;
  configuration and publishing use separate permissions.
- The source service returns only safe fields approved for calendar use.
- Pastoral follow-up and restricted notes are never calendar sources. A user
  may create a separate bland personal reminder directly in an external
  calendar.
- Giving, accounting audit, security events, contact details, birth dates,
  unlisted data, and confidential Group notes are prohibited.
- Person names are omitted unless the source policy explicitly permits a safe
  public role or owner display.
- Preview and audit never expose provider tokens.
- Test mode never publishes to Google Calendar. It may generate `.ics` files
  and use a fake provider for acceptance tests.

## 10. User interface

### Events

The main-menu **Events** screen is a compact upcoming/past list with Add, Edit,
Cancel, Complete, Export, and Close. Double-click edits. It is not a visual
calendar.

### Calendar publishing

The protected **Calendar Integration** screen contains:

- provider/destination status;
- date range and source filters;
- a preview grid with Create, Update, Cancel, Skip, and Error actions;
- Export `.ics`, Publish Selected, Test Connection, and Settings; and
- the most recent publication result.

## 11. Reports and exports

Starter outputs are:

- **Events - Upcoming Events**;
- **Events - Event Listing**; and
- `.ics` calendar export.

Ordinary PDF reports are optional conveniences; the external calendar remains
the normal calendar presentation.

## 12. Failure and recovery

Network or provider failure never rolls back or changes the ChurchManager
source record. Each failed publication remains retryable. Expired authorization
prompts an administrator to reconnect. Rate limits use bounded retries without
freezing the UI. Support logs contain safe error codes and correlation IDs, not
tokens or confidential event text.

Backup/restore preserves event records and publication metadata. Credentials
must be re-established when Windows credential protection cannot safely move to
the restored computer. Restore never republishes automatically.

## 13. Acceptance criteria

Acceptance proves:

1. Church events validate date, time, Church, status, and ownership;
2. Worship, Group, Event, and approved Project adapters produce the same neutral
   contract without duplicate database records;
3. stable UIDs survive edits and prevent duplicate publication;
4. `.ics` files correctly handle timed, all-day, updated, and cancelled events;
5. daylight-saving and time-zone cases round-trip correctly;
6. unauthorized and confidential records never appear in preview or output;
7. test mode cannot contact a live calendar provider;
8. one-way Google preview distinguishes create/update/cancel/skip/error;
9. retry does not duplicate events;
10. credential storage, logs, backup, and restore respect the security boundary;
11. the event list and publishing screen pass visual inspection; and
12. documentation clearly explains the one-way source-of-truth boundary.

## 14. Implementation sequence

1. Approve this specification and the version 1 one-way boundary.
2. Add simple Church Event schema, permissions, services, and list screen.
3. Define and test provider-neutral source adapters.
4. Implement and validate `.ics` export.
5. Add publication state and fake-provider acceptance tests.
6. Add optional Google OAuth settings and one-way publishing.
7. Integrate approved Worship, Group, and Project sources.
8. Add documentation, diagnostics, baseline changes, and fictional test data.
9. Complete automated and visual acceptance.

## 15. Approved version 1 decisions

The approved version 1 boundaries are:

1. standalone Events use controlled natural-language recurrence;
2. Google publishing follows `.ics` acceptance within version 1;
3. automatic publication remains disabled initially; and
4. ChurchManager never imports external-calendar edits in version 1.
