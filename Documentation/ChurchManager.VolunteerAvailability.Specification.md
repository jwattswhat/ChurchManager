# ChurchManager Volunteer Availability and Responses Specification

Status: Approved roadmap implementation

## Purpose

Extend the existing worship-participant scheduler so a small congregation can
record when a volunteer cannot serve, request service, record the volunteer's
response, and see conflicts without replacing the planner's judgment.

## Boundaries

- Existing recurring service patterns remain the volunteer's usual
  availability.
- Date-specific unavailable periods override those patterns.
- ChurchManager stores worship services and their assignments, but it does not
  maintain a separate general calendar. A later integration may export service
  assignments to an external calendar.
- Version 1 records responses entered by an authorized planner. Email response
  links, a member portal, and two-way calendar synchronization are deferred.
- Suggestions are previews. They never replace or remove assignments silently.

## Data

### Availability exception

Each exception contains a participant, inclusive start and end dates, an
optional worship role, a short reason, active status, and audit timestamps. A
blank role means the volunteer is unavailable for every role during the period.

### Assignment response

The existing service assignment status is retained and normalized as:

- `PENDING` - service has been requested but no response is recorded;
- `CONFIRMED` - volunteer accepted;
- `DECLINED` - volunteer declined and the required position remains open;
- `ASSIGNED` - planner made a direct assignment without a separate request;
- `SUGGESTED` - ChurchManager preview was accepted by the planner but has not
  yet been treated as a request.

Assignments also retain the response date, response source, and optional note.

## Rules

1. Suggestions exclude volunteers with an active exception covering the
   service date for either every role or the suggested role.
2. A saved assignment that conflicts with an exception remains visible. It is
   marked as a conflict and must be resolved manually.
3. Declined assignments never fill required positions.
4. A participant may have overlapping exceptions; all applicable exceptions
   are honored.
5. Ending or deactivating an exception does not change historical assignments.
6. Last-served information is shown to help the planner distribute service
   fairly, but it never imposes an automatic rotation.

## Screens

- **Worship Participants** adds an **Availability...** action for the selected
  participant.
- **Volunteer Availability** lists current and future unavailable periods and
  permits add, edit, and deactivate.
- **Service Participants** shows response status, last served, and an explicit
  conflict warning. Its assignment editor records the response source and date.

## Security and audit

The existing `worship.manage` permission governs availability and response
maintenance. Changes are operational scheduling data and use the established
ChurchManager audit/error-support boundaries. Reasons must remain brief and
must not contain pastoral or medical detail.

## Acceptance

1. An unavailable volunteer is omitted from suggestions.
2. An existing assignment becomes visibly conflicted if an applicable
   exception is entered later.
3. Pending, confirmed, declined, assigned, and suggested states can be saved.
4. A declined assignment leaves its required slot open.
5. Last-served information is accurate and does not count declined service.
6. No availability action sends email or writes to an external calendar.
