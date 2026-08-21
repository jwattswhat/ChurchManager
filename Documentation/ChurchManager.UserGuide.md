# ChurchManager User Guide

**Version 0.3.0-dev**

**For congregations using ChurchManager**

ChurchManager brings worship planning, people and family records, attendance,
reports, communications, and fund accounting into one congregation-owned
application. This guide explains the ordinary tasks a user performs. Technical
installation and development procedures are maintained separately.

\pagebreak

## Contents

1. Getting started
2. The main menu
3. People and congregation records
4. Worship planning
5. Attendance
6. Prayers, announcements, and participant notices
7. Reports and layout customization
8. Fund accounting
9. Users, email, backup, and recovery
10. Getting help

## 1. Getting started

### Installing ChurchManager

The ChurchManager Setup wizard checks the computer first, then collects the
local database connection, congregation name, first Master Administrator, and
optional catalog choices. Its review page never displays a password. The
temporary Master Administrator password must be changed at first login.

During development the wizard opens in **preview mode**, which validates the
complete plan without creating a database or changing saved credentials.

### Sign in

Start ChurchManager from its Windows shortcut. Enter the user name and password
provided by the congregation administrator. A temporary password must be
changed when requested. Each person should use an individual account; accounts
must not be shared.

The login window identifies ChurchManager, the local congregation, the installed
version, and the open-source license. Confirm the congregation name before
signing in, especially when working with a test or support installation.

The title bar clearly identifies a test database. Work entered in TEST MODE is
not production congregation data.

### Moving around

The main menu is organized by task. Select a blue item to open it. Close a task
window to return to the main menu. Lists generally support double-clicking a row
to open or edit the selected item. Buttons that are unavailable are disabled
until the required selection is made.

### Saving work

Use the screen's Save, Update, or Save Service control before closing. If a
screen reports unsaved changes, choose whether to save or discard them. Red
rows or red text identify information that still needs attention.

## 2. The main menu

### Service Planning

- **Worship Services** creates and completes a service plan and its weekly
  Order of Service.
- **Weekly Bulletin Order** reviews the outline prepared for a particular
  service.
- **Service Participants** assigns people to the positions required for a
  service.
- **Notify Participants** prepares participant messages.
- **Weekly Prayers** and **Weekly Announcements** show material scheduled for
  the selected week.
- **Prepare Bulletin Order** produces an outline suitable for copying into a
  bulletin document.

### Worship Resources

This group maintains sermons, local lectionaries, bulletin-order templates,
prayers, announcements, hymnals, hymns, participants, positions, scheduling
patterns, and preparation checklists. Installed package records are protected;
make congregation-owned records or customized templates when changes are
needed.

### People and Congregation

This group contains church information, people, families, attendance, projects,
tasks, documents, the journal, and confidential contributor and envelope
maintenance for authorized giving users.

### Reports and Design

Use **Reports** to run approved reports. Authorized users may use **Report
Designer** and **Screen Designer** to create congregation-specific layouts.
Starter layouts remain available for recovery.

### ChurchManager Settings

Authorized administrators maintain configuration, choices, users, email,
catalog packages, backups, and support diagnostics here.

## 3. People and congregation records

### Church information

Enter the congregation's name, address, contact information, report logo,
primary hymnal, and default lectionary. The selected hymnal and lectionary guide
the choices offered in worship planning.

### People

Create one person record for each member or other person the congregation needs
to track. A person may have a photograph and may be linked to a family.
Telephone numbers are stored as digits and formatted for display. Respect every
unlisted-contact setting; unlisted contact information is excluded from public
directory output.

### Families

Family records group people for directories and household communication. A
family may have its own photograph and address information. Confirm family
membership before generating a directory.

### Users are separate from people

A ChurchManager user may optionally be linked to a person record, but the two
records serve different purposes. Not every member needs a user account, and a
user does not have to be a congregation member.

### Contributors and envelopes

A giving contributor may be linked to one person, linked to one family, or
maintained as an outside contributor. Statement identity and contact fields do
not silently synchronize with the membership directory.

Numeric envelope numbers are normalized, so `001`, `01`, and `1` are the same
number. Each assignment has a starting date and may have an ending date.
ChurchManager prevents the same number from being assigned to different
contributors during overlapping dates. Double-click an envelope-history row to
edit it.

### Approved giving purposes

Before entering contribution batches, a giving administrator records each
congregation-approved purpose, its approval date and authority, effective
dates, statement treatment, and accounting organization, fund, and revenue
account. The required control-and-discretion confirmation documents that the
congregation—not an individual donor—controls use of the gift.

### Contribution batches

Open **Contribution Batches** to begin a confidential draft for a Sunday
offering, special collection, or other deposit. Enter the batch date,
description, accounting organization, and—when known—the expected control
total. Open the batch and add each monetary contribution.

Choose a contributor directly or enter an envelope number and leave the
contributor at **Anonymous / resolve from envelope**. ChurchManager resolves
the envelope assignment that was effective on the gift's received date. A gift
may be divided among several approved purposes, but the allocations must equal
the gift amount exactly. The batch header refreshes its entered total and any
remaining difference after every saved gift.

Users with **Review contribution batches** permission can select **Review / Mark
Ready**. ChurchManager first lists anything that still needs attention,
including an unresolved envelope, control-total difference, incomplete split,
expired purpose or accounting destination, donor-direction review, or duplicate
check/reference value. A batch changes to **Ready** only when every check passes.

While a batch remains Draft, double-click a contribution—or select **Edit
Contribution**—to correct its contributor, envelope, amount, method, statement
treatment, note, or purpose allocations. **Delete Contribution** requires
confirmation. Both operations immediately recalculate the batch total and add
a privacy-safe audit event. Ready and posted gifts cannot be edited or deleted.

## 4. Worship planning

### Create a worship service

1. Open **Worship Services** and create a new service.
2. Enter the service date, time, location, and congregation.
3. Select an Order of Service template.
4. Select a Proper when one applies. The Proper supplies the printable
   liturgical title, color, reading citations, and hymn suggestions.
5. Review the service outline on the left and the service details on the right.
6. Fill every required hymn or reading line and resolve red warnings.
7. Assign participants and review the Preparation Checklist.
8. Save the service.

Creating a worship service also creates its attendance event. The saved weekly
Order of Service is a service snapshot; later changes to the source template do
not rewrite the saved service.

### Order of Service templates

Templates store outline metadata only. They do not contain complete liturgical
texts, prayers, psalms, lyrics, music, or publisher artwork. Create an editable
custom template from a starter or create one from scratch. Required participant
positions may be attached to a template and carried into a new service.

### Hymns

Select a hymn line before using **Select Hymn**. The hymn picker searches and
sorts the congregation's installed hymnal entries. A selected hymn displays its
title as the weekly value and its hymnal number as the reference. Select stanzas
when needed. Duplicate hymn selections are always flagged, including duplicates
chosen manually.

For Lutheran Service Book references, pages in the service section use the
form `LSB p. 151`; printed hymns use the form `LSB 331`. Psalms are citations,
not LSB page references.

### Readings, colors, and titles

ChurchManager stores biblical citations, not Scripture text. A service planner
may override a reading in the weekly outline. The printable liturgical title
comes from the Proper. A service-specific color override updates the color block
on the planning screen and planning report.

### Preparation checklist

The checklist is a planning reminder, not a hard closing system. Items may be
Done, Not Done, or Not Needed. One-time tasks may be added to a service. The
summary reports checklist progress, required participant coverage, and hymn
completion. Marking the whole checklist complete records the planner's judgment
even when an exception is intentional.

## 5. Attendance

Open **Attendance** and choose an event. Worship services normally create their
attendance events automatically. Members appear first, followed by visitors.
Visitors may be counted without creating person records. Record communion only
when it was offered and the information is appropriate to maintain.

Available reports include event listings, weekly attendance, year-to-date
totals, individual history, member follow-up, and a pastor's comparison report.
The follow-up report can flag members after a chosen number of consecutive
missed weeks.

## 6. Prayers, announcements, and participant notices

Prayers and announcements use categories maintained in Choices. Their natural
language schedules may describe patterns such as `Every Sunday`, `First and
Third Sunday of the month`, or an approved fixed annual date. Scheduling is
week-based so material may apply to Sunday, Wednesday, or another service in
the same ministry week. Unsupported or ambiguous expressions are rejected.

Use the weekly preview before preparing bulletin material. Participant notices
use the congregation's configured email service. TEST MODE never sends external
email.

## 7. Reports and layout customization

Select a report, supply its enabled parameters, and choose **Run Report**.
ChurchManager creates a PDF using a protected report dataset. A customized
layout is shown in blue; when no customization exists, ChurchManager uses the
starter layout.

Authorized users may open the Report Designer, create a customization from a
starter, move and resize controls, preview the PDF, validate the definition,
and restore the starter. Report definitions control presentation only; they do
not bypass report permissions or expose unapproved database fields.

## 8. Fund accounting

### Initial setup

Complete Accounting Setup, the chart of accounts, funds and restrictions,
functional classifications, fiscal years and periods, bank accounts, and
payees before entering live transactions.

### Daily work

1. Create a balanced draft in **Transaction Entry**.
2. Review it and mark it ready.
3. Approve it under the congregation's approval policy.
4. Post it. Posting makes the accounting entry permanent.
5. Use a reversing transaction to correct a posted entry.

Small congregations may enable the audited solo-approval policy. When used, the
override and its reason remain in the audit history.

### Bank work and reconciliation

Bank File Import previews and stages a bank CSV; it does not post transactions.
Match imported lines carefully, complete the reconciliation, and review the
reconciliation report before closing the period.

### Budgets and period end

Budgets may use general accounts alone or include detailed line items. Review
Budget to Actual and the Close Checklist before period or year-end processing.
Year-End Close is controlled and auditable; make a verified backup first.

## 9. Users, email, backup, and recovery

### Users and roles

Administrators create individual accounts and assign only the permissions each
user needs. A new account may be linked to a person and may receive a temporary
password notice after outgoing email has been configured. Disable accounts that
should no longer sign in instead of reusing them.

### Email

Configure the congregation's SMTP provider under **Email Settings** and test the
connection. Credentials are protected locally and are not written into reports,
logs, or database backups. TEST MODE suppresses delivery.

### Backup

Use **Database Backup** regularly and before migrations, restore operations,
year-end close, or major catalog changes. The default backup folder may be
changed. An optional automatic backup can run when ChurchManager exits.

### Restore

Restore replaces the active database with the selected backup. Read every
warning, verify the database name shown, and allow the operation to finish.
ChurchManager must restart after a successful restore because its previous
database connections were closed.

## 10. Getting help

Select **Help - User Guide** on the main menu to open this document. If an
unexpected error occurs, note what you were doing and open **Support and
Diagnostics**. Create the privacy-safe support package and give that package to
the person supporting ChurchManager. Do not send database passwords.

The application version appears in the ChurchManager title bar. Include that
version when requesting help.

---

ChurchManager is open-source congregation software. This guide describes the
0.3.0-dev development line and will be revised as beta testing identifies
additional instructions or screenshots that are needed.
