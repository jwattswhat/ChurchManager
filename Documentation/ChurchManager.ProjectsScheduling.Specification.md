# ChurchManager projects and scheduling specification

**Status:** Approved
**Version:** 1.0
**Date:** August 24, 2026
**Approved by:** Rev. Jonathan C. Watt
**Target application:** ChurchManager
**Application framework:** JSForm
**Database:** MariaDB/MySQL

## 1. Purpose

ChurchManager will provide a small-congregation project planner for bounded
congregational work such as a fellowship event, building improvement, annual
meeting preparation, stewardship campaign, or community-service effort. It
will answer:

1. What are we trying to accomplish?
2. Who owns the work?
3. What must happen, and by when?
4. What is blocked or overdue?
5. What was completed?

This is a new normalized subsystem. It does not restore the retired generic
Projects and Tasks tables or their behavior.

## 2. First-release scope

Version 1 includes:

- projects belonging to one Church;
- a project owner who may be a Person, Group, or application User;
- controlled status and priority;
- optional planned start, target completion, and actual completion dates;
- ordered project steps with an assignee, due date, status, and short note;
- multiple assignees only when represented by a Group;
- simple dependencies between steps in the same project;
- project activity history and bounded nonconfidential notes;
- links to existing ChurchManager Documents;
- list, detail, due-soon, overdue, and completed-project screens and reports;
- explicit calendar-publication eligibility for dated projects and steps;
- permissions, auditing, backup, restore, import, and export; and
- test data covering active, blocked, overdue, and completed work.

Version 1 excludes:

- time sheets, payroll, billing, budgets, purchase orders, or accounting;
- Kanban boards, Gantt charts, critical-path calculations, or resource leveling;
- chat, file storage, document editing, or version control;
- recurring household chores or personal to-do lists;
- automatic reassignment or schedule optimization;
- confidential pastoral-care, donor, safeguarding, medical, or personnel data;
- arbitrary scripts, formulas, SQL, or workflow automation; and
- a second calendar system.

## 3. Design principles

1. **Projects are outcomes, not inboxes.** Every project has a clear name,
   owner, status, and intended result.
2. **Steps remain understandable.** A project step is a concrete piece of work,
   not a general-purpose application task.
3. **One accountable owner.** A project and each step have at most one direct
   owner; a Group represents shared responsibility.
4. **Dates are optional but truthful.** Blank means unscheduled. ChurchManager
   never invents dates or silently moves overdue work.
5. **History is preserved.** Completion, cancellation, reassignment, and date
   changes are audited; completed projects are archived rather than deleted.
6. **External calendars remain external.** Eligible dates are published through
   the Calendar Integration service defined separately.
7. **No confidential narrative.** The subsystem contains ordinary operational
   information only.

## 4. Data model

### 4.1 `tblMinistryProject`

| Field | Rule |
| --- | --- |
| `ID` | Positive primary key. |
| `ChurchID` | Required owning Church. |
| `ProjectNumber` | Stable Church-scoped number such as `PRJ-0001`. |
| `Name` | Required bounded title. |
| `Purpose` | Optional bounded description of the intended result. |
| `OwnerType` / `OwnerID` | Valid Person, Group, or User owner resolved by the service. |
| `Status` | Planned, Active, On Hold, Completed, or Cancelled. |
| `Priority` | Low, Normal, High, or Urgent. |
| `PlannedStartDate` | Optional date. |
| `TargetDate` | Optional date not before the planned start. |
| `CompletedDate` | Required only for Completed status. |
| `CalendarEligible` | Whether its dated milestone may be published. |
| `Note` | Bounded operational note. |
| audit fields | Creator/editor and timestamps. |

`ProjectNumber` is immutable and unique within a Church. A polymorphic owner is
accepted only through a service that validates the selected record and Church;
raw arbitrary type names are prohibited.

### 4.2 `tblMinistryProjectStep`

| Field | Rule |
| --- | --- |
| `ID` | Positive primary key. |
| `ProjectID` | Required parent project with cascading deletion only for unused drafts. |
| `Sequence` | Positive display order unique within the project. |
| `Title` | Required action-oriented title. |
| `AssigneeType` / `AssigneeID` | Optional Person, Group, or User assignment. |
| `Status` | Not Started, In Progress, Blocked, Complete, or Not Needed. |
| `DueDate` | Optional date. |
| `CompletedDate` | Set when completed and cleared only by an explicit reopen. |
| `CalendarEligible` | Whether the due date may be published. |
| `Note` | Bounded operational note. |
| audit fields | Creator/editor and timestamps. |

### 4.3 `tblMinistryProjectStepDependency`

Stores same-project predecessor relationships. Self-reference, duplicates,
cross-project dependencies, and dependency cycles are rejected.

### 4.4 `tblMinistryProjectDocument`

Links a project or step to an existing Document. The service validates Church
ownership and authorization; the project subsystem does not duplicate files.

### 4.5 Project activity

Material changes use the common security audit facility. A separate narrative
history table is unnecessary in version 1 unless acceptance testing proves the
audit view cannot provide an understandable timeline.

## 5. Business rules

- Only Active projects accept new steps.
- A Completed project may contain Not Needed steps but no incomplete required
  steps unless the user explicitly confirms completion and supplies a reason.
- A Cancelled project preserves steps, documents, assignments, and history.
- Deleting a project is allowed only for an unused draft with no steps,
  documents, calendar publication, or audit dependency.
- A blocked step requires a short reason.
- A step cannot be Complete with a future completion date.
- Changing an assignee or due date never sends a message automatically.
- Calendar publication is opt-in and contains only safe operational text.

## 6. Screens

### Project list

The main-menu entry **Projects and Scheduling** opens a compact list with
Church, status, owner, priority, target date, and overdue indicator. Default
view shows Planned, Active, and On Hold projects. Double-click opens the detail.

### Project detail

The header contains name, purpose, owner, status, priority, and dates. The main
area is an ordered step grid. Buttons support Add, Edit, Complete/Reopen, Move
Up, Move Down, Documents, and Close. Double-click edits a step. Red indicates
overdue or blocked work; it is never the only indicator.

### Due-work view

An optional compact view shows the current user's or selected Group's overdue
and upcoming assignments without becoming a personal task manager.

## 7. Reports

Starter reports are:

- **Projects - Active Summary**;
- **Projects - Due and Overdue Work**;
- **Projects - Project Plan**; and
- **Projects - Completed History**.

Reports use approved views, stable report codes, Church scoping, and the visual
report system. They exclude private profile data and confidential narratives.

## 8. Authorization and audit

Permissions separate viewing, editing, assigning, completing, administering,
reporting, and calendar publishing. Users see only projects belonging to a
Church they may access. Material create, edit, status, assignment, dependency,
document-link, completion, reopen, calendar-publication, and deletion attempts
are audited without copying long notes unnecessarily.

## 9. Calendar integration

The project service exposes approved dated milestones and step due dates to the
Calendar Integration service. It does not call Google Calendar, create `.ics`
files, store provider tokens, or maintain synchronization state itself.

## 10. Installation, test data, and acceptance

Implementation requires a guarded migration, permissions, approved views,
baseline regeneration, backup/restore coverage, user documentation, and a
fictional test set. Acceptance proves:

1. project and step lifecycle rules;
2. Person, Group, and User ownership validation;
3. ordering, dependencies, and cycle rejection;
4. overdue and blocked indicators;
5. guarded completion, cancellation, reopening, and deletion;
6. Church and permission isolation;
7. approved reports and exports;
8. calendar eligibility without direct provider access;
9. backup/restore preservation; and
10. visual inspection at supported window sizes.

## 11. Implementation sequence

1. Approve this specification and terminology.
2. Add normalized schema, permissions, views, and service tests.
3. Implement project and step services.
4. Add list, detail, due-work, and document-link screens.
5. Add reports and Calendar Integration provider contract.
6. Add fictional acceptance data and backup/restore verification.
7. Update documentation, inventories, and baseline artifacts.
8. Complete automated and visual acceptance.
