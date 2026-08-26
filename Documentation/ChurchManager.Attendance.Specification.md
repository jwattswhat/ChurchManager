# ChurchManager Attendance Specification

## Purpose

Attendance records support congregational statistics, pastoral care, and Communion records without turning ordinary attendance reports into personal-history reports.

## Worship Service lifecycle

- Saving a new Worship Service creates exactly one linked Attendance Event.
- The event receives the service church, date and time, printable liturgical title, Holy Communion setting, and the `Worship Service` attendance type maintained in `tblChoices`.
- Saving changes to a service synchronizes its linked event while that event has no hand count and no individual attendance.
- Once attendance has been recorded, the event is a historical record and service edits do not silently rewrite it.
- Canceling an unsaved service leaves no Attendance Event.
- Deleting a service removes its empty generated event. Recorded attendance protects the service from deletion.

## Attendance editor

One combined editor replaces the separate event-maintenance and insert-only attendance-entry workflows.

The event area contains the church, optional Worship Service, date and time, description, attendance type, Communion offered, attendance hand count, Communion hand count, and notes. Service-derived identity fields are read-only; hand counts and event notes remain editable.

The person grid contains:

- Present
- Person
- Member or visitor
- Communion
- Note

The grid lists known congregation people together, supports searching, and loads existing attendance. Save treats the displayed model as the complete known-person record and transactionally inserts, updates, and removes individual rows. Communion requires both presence and an event at which Communion was offered.

The hand count is the authoritative total. Visitors and other attendees do not need Person records. The screen displays hand count, known-person attendance, and the unnamed difference. A difference is informational rather than blocking because congregations commonly record anonymous visitors. Creating a Person record remains optional when pastoral follow-up is desired; it is never required merely to count a visitor.

## Security and reports

- `attendance.record` permits event selection and attendance entry.
- `attendance.events.manage` permits creating and changing non-service events.
- Ordinary attendance reports contain event totals, not personal histories.
- Personally identified attendance and Communion history requires the pastoral-confidential report permission.
- Attendance Event Listing reports individual events.
- Weekly Attendance Summary aggregates event totals by week and attendance type.
