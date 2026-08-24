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
7. Pastoral Care
8. Reports and layout customization
9. Fund accounting
10. Users, email, backup, and recovery
11. Getting help

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

This group contains church information, people, families, attendance, documents,
and the journal.

Data Management provides a guarded duplicate review. Matching names, contact
information, or mailing addresses are possible duplicates, not an automatic merge.
Select a pair and choose **Not Duplicates** to record that both records are valid,
or **Review Later** to remove the pair from the active queue. These decisions do
not delete, merge, or alter either membership record. Select **Include matches
marked Review Later** whenever those deferred pairs should be reconsidered.

Select **Review Merge Impact** to see how many attendance, contact, family,
giving, user, participant, group, pastoral-care, and other linked records belong
to each side. This preflight is generated from the current database relationships
and makes no changes.

Select **Merge Records** only after reviewing that impact. Choose which record
to keep, enter the reason, and confirm the operation. ChurchManager moves all
linked history and removes the duplicate in one transaction. If the records own
conflicting unique history, the whole merge is rolled back and neither record is
changed. The merge reason and record identities remain in protected history.

The beta test dataset includes two fictional records named **Pat Duplicate** so
this review can be exercised without weakening the normal import protections.

**Create Portable Archive** produces a ZIP containing privacy-safe People and
Families CSV files and a versioned checksum manifest. ChurchManager verifies the
archive before reporting success. This is not a database backup: unlisted contact
information, passwords, giving, accounting, audit internals, and pastoral-care
information are excluded.
instructions. Review the underlying records before making any correction.

Select **Preview Membership CSV** to inspect a People or Families CSV file. The
first row must contain column names. Review every suggested mapping, map the
required fields marked with an asterisk, and then select **Preview Mapped Rows**.
Preview does not create or update records. Rows marked **Ready** may be imported;
duplicate or invalid rows appear in red as **Excluded** and remain unchanged.
**Import Reviewed Rows** creates only the Ready records in one transaction; any
failure rolls back the whole import. It never merges or replaces existing
records. ChurchManager records the church, user,
file name and checksum, counts, and time, but does not retain the source rows.
Safe sample files are available in `TestData` for both People and Families.

Select **Export Membership CSV** to create an authorized People or Families
directory extract. Choose the church and destination file, then confirm the
export. ChurchManager always excludes unlisted addresses, email addresses, and
telephone numbers. The export contains no passwords, giving identity,
accounting detail, pastoral records, or internal audit content. Export history
stores attribution, counts, file name, and checksum rather than a copy of the
exported rows.

### Member Giving

This confidential group contains contributors and envelopes, approved giving
purposes, contribution batches, and protected Giving reports. Its separate
placement does not replace permission checks; users see and invoke only the
operations their Giving roles permit.

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

For a contributor linked to a person or family, **Refresh from Directory...**
shows each stored contact field beside the current directory value. Nothing is
changed until the preview is confirmed. **Merge Duplicate...** keeps the
currently selected contributor, moves the duplicate's Giving, envelope, and
statement history, and deactivates the duplicate. ChurchManager blocks a merge
when overlapping envelope or statement history must be resolved first, and it
requires a permanent audit reason.

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
total. Open the batch and add each contribution.

For donated property, choose **Non Cash** as the method. Describe the property
and then assign its approved giving purpose with a zero-dollar allocation. You
may record an optional **Donor-provided estimate (unverified)** for internal
reference. ChurchManager does not verify that estimate, use it in accounting,
or print it as the congregation's valuation on a contribution statement. A
batch containing only non-cash gifts completes
inside Giving after review and does not create a zero-dollar accounting
transaction. Mixed batches send only their monetary amounts to accounting.

Choose **Import CSV** to map the columns in an electronic-giving or spreadsheet
export. The preview reads the file without changing the database and marks
unknown envelopes, contributors, purposes, conflicting identities, and possible
duplicates in red. Import is not available until every row is resolved. After
all rows are Ready, select the accounting organization, receiving bank account,
deposit date, and batch description, then choose **Import Ready Rows to Draft
Batch**. ChurchManager creates a new Draft batch; it does not post the gifts.
The exact source CSV is retained in protected ChurchManager storage with its
file hash and mapping, and the same file cannot be imported twice.
The development test dataset includes `GivingImport.Valid.Sample.csv` and
`GivingImport.Issues.Sample.csv` in the `TestData` folder for exercising both
successful and flagged previews. Resetting the Giving test dataset also removes
test import-evidence rows and their protected test copies after the replacement
dataset commits successfully.

A Draft cannot be marked Ready unless its deposit date belongs to exactly one
open fiscal period for its accounting organization. If an unsent Ready batch
needs correction, select it in Contribution Batches and choose **Return Ready
to Draft**. Use **Edit Batch Details** to correct its deposit date; the screen
shows the accounting organization's currently open fiscal-period range. Batches
already sent to Accounting cannot be returned this way.

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
check/reference value. A monetary or mixed batch changes to **Ready** only when
every check passes. A non-cash-only batch changes directly to **Posted** because
it has no bank deposit or accounting handoff.

While a batch remains Draft, double-click a contribution—or select **Edit
Contribution**—to correct its contributor, envelope, amount, method, statement
treatment, note, or purpose allocations. **Delete Contribution** requires
confirmation. Both operations immediately recalculate the batch total and add
a privacy-safe audit event. Ready and posted gifts cannot be edited or deleted.

To correct a posted batch, select it in **Contribution Batches** and choose
**Correct Posted Batch**. Enter an open-period correction date and a required
reason. ChurchManager creates a Ready accounting reversal and an editable Draft
copy of the original gifts. Approve and post the reversal through normal
Accounting Posting before reviewing and sending the replacement batch. The
original batch remains in the audit history with Void status.
Once a Ready batch has created its summarized accounting transaction, the batch
list displays **Sent to Accounting** until that transaction is posted.

For a returned check, select its Posted batch and choose **Returned Check...**.
Select the check, enter the bank return date and an audit reason, and confirm the
correction. ChurchManager creates the full summarized accounting reversal and a
Draft replacement batch that omits only the returned check. Post the reversal
before reviewing and sending the replacement batch. The original gift remains
unchanged in the protected audit history, and donor identity never enters the
accounting reversal.

### Giving reports

Open **Giving Reports** for operational review. **Batch Control Summary** shows
batch dates, statuses, controls, entered totals, differences, and accounting
transaction links without displaying donor identity. Users with confidential
history permission also receive **Contributor History**, which shows one
contributor's Ready and Posted allocations for the selected dates. Draft gifts
are deliberately excluded from contributor history. The **Refresh** buttons
update the on-screen review and display the completion time beneath the grid;
they do not create a PDF. **Preview PDF** on the Batch Control Summary creates
the protected donor-free `GIVE-BATCH` report for the selected dates. Contributor
statements are available only to users with the statement-generation permission.

The **Operational Reports** tab provides protected printable batch detail,
contributor history, statement exceptions, and envelope exceptions. It also
provides donor-free **Giving by Fund and Period** and **Accounting Posting
Reconciliation** reports. Select the dates, choose the report, select a
contributor only when printable Contributor History requires one, and choose
**Preview Selected Report**.
On **Contribution Statements**, select either **Quarterly**, **Calendar Year**,
or **Custom Date Range**, then select one contributor or **All eligible
contributors** and choose **Preview Statement(s)**.
The preview includes only Posted gifts and only allocations marked statement
eligible. Previewing does not record that a statement was issued or delivered.
Choose **Issue and Record Statement(s)** only when the PDF is being treated as
an official statement. ChurchManager records its covered period, generation
time, revision, filename, and SHA-256 identifier. This does not claim the
statement was printed, mailed, emailed, or received. **Statement Issuance
History** identifies prior issues and reissues.

Statements list non-cash gifts by their stored description with a blank Amount
cell. They are not included in **Eligible monetary contributions**. Any
donor-provided estimate remains internal, unverified information and is not
printed as the congregation's valuation.

Users with confidential Giving-report permission also receive **Memorial / Honor
Gifts**. Select the covered dates and choose **Preview Memorial / Honor List**
to create a protected acknowledgment-work PDF containing Posted gifts only.
The donor name appears only when donor disclosure was explicitly authorized;
otherwise it says **Not disclosed**. The amount appears only when amount
disclosure was separately authorized. These two permissions are never inferred
from one another.

Use **Acknowledgment / Tribute...** while entering a contribution to record a
special donor instruction. Select **Needs review** until the congregation has
decided how it will respond. A completed disposition requires a resolution note;
ChurchManager records the resolving user and time automatically. **Returned to
donor** retains the review record but excludes the amount from the deposit,
ledger handoff, and contribution statement. **Accepted under congregation
control** documents that the congregation retains control and discretion over
an approved purpose. ChurchManager documents the action; it does not decide tax
deductibility. Use **Giving Reports > Directed Gift Review** for the confidential
review and disposition list.

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

## 7. Pastoral Care

Pastoral Care is a protected ministry work list for follow-ups, completed care
actions, and future reminders. It is not a counseling transcript, medical
record, safeguarding case file, or place to record everything a caregiver
knows.

### Follow-ups and actions

Open **Pastoral Care** from the main menu. **Assigned to Me** shows your open
work; authorized users may select **All Open**. Create a follow-up with the
correct church, person or family when applicable, category, assignee, priority,
opened date, and optional due date. Keep the safe summary brief and
minimum-necessary.

Double-click a follow-up to review its safe history, record a completed action,
set the next follow-up, assign it, or change its status. Regular shut-in and
homebound visits may use the natural-language scheduling pattern provided by
the screen.

Attendance and Prayer Requests can deliberately create a Pastoral Care
follow-up. ChurchManager does not copy an attendance-event note or the wording
of a prayer request into the follow-up. Review the new record and add only the
safe operational detail that is actually needed.

### Pastoral Care reports and confidentiality

**Pastoral Care - Work List** contains authorized operational fields. **Pastoral
Care - Activity Summary** contains aggregate counts. Neither report includes
restricted notes or confidential narrative. Report access is protected by
Pastoral Care permissions.

Authorized users may select **Restricted Notes...** from a follow-up history.
The list shows dates and updater information only; note text stays closed until
one note is explicitly opened. Creating or changing a note also requires the
restricted-note edit permission and verified recovery protection. Use the
minimum necessary wording. Restricted notes never appear in reports, exports,
diagnostics, or search. Do not place confidential narrative in an ordinary
summary, action, report, document, prayer request, or other unprotected field.

ChurchManager is a reminder and recordkeeping aid, not an emergency-response or
mandated-reporting system. Follow the congregation's safeguarding procedures
and applicable law whenever immediate action or a report to civil authorities
may be required.

## 8. Reports and layout customization

Select a report, supply its enabled parameters, and choose **Run Report**.
ChurchManager creates a PDF using a protected report dataset. A customized
layout is shown in blue; when no customization exists, ChurchManager uses the
starter layout.

Authorized users may open the Report Designer, create a customization from a
starter, move and resize controls, preview the PDF, validate the definition,
and restore the starter. Report definitions control presentation only; they do
not bypass report permissions or expose unapproved database fields.

## 9. Fund accounting

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

## 10. Users, email, backup, and recovery

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
changed. An optional automatic backup can run when ChurchManager exits. Keep
the permanent backup folder outside MariaDB's data folder; preferably use a
separate physical device or independently protected network location so one
disk failure does not destroy both the database and its backups.

### Pastoral Care recovery protection

Before restricted pastoral notes can ever be enabled, a Master Administrator
must configure a separate Pastoral Care recovery password in **Database
Backup**. ChurchManager does not store that password and cannot recover it.

An authorized Master Administrator may use **Rotate Encryption Key** from that
same protected section. Rotation requires the recovery password and creates
separate, clearly labeled before-and-after backups. Do not interrupt
ChurchManager or MariaDB while it is running. Keep both backups and their
matching sidecars according to the congregation's protected retention policy.

A complete backup of encrypted pastoral notes consists of two matched files:
the SQL backup, which contains ciphertext only, and its protected pastoral
recovery sidecar. Preserve both files together in protected storage. The SQL
file alone cannot make restricted notes readable on a replacement computer.
Restore must reject a missing, altered, mismatched, or incorrectly protected
sidecar without silently clearing a note.

### Restore

Restore replaces the active database with the selected backup. Read every
warning, verify the database name shown, and allow the operation to finish.
ChurchManager must restart after a successful restore because its previous
database connections were closed.

## 11. Getting help

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
