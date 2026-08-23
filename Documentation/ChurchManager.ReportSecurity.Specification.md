# ChurchManager Report Security Specification

Status: Proposed for approval  
Scope: LimeReport and other ChurchManager reports; accounting report data is deferred

## 1. Objective

ChurchManager reports must enforce the signed-in user's permissions before a
report is listed or launched. LimeReport must read only approved SQL reporting
views through restricted database accounts. Report templates must not contain
permanent database credentials or query ChurchManager base tables directly.

## 2. Security boundaries

Report security uses four independent controls:

1. ChurchManager authorizes the signed-in user.
2. The report catalog assigns one required permission to each report.
3. A restricted MariaDB report account can select only approved reporting views.
4. Every attempted report run is written to the ChurchManager security audit log.

Hiding a menu item or filtering a combo box is not authorization. The report
service must repeat the permission check immediately before launching LimeReport.

## 3. Initial non-accounting permissions

| Permission | Intended information |
|---|---|
| `reports.general.run` | Assets, document lists, report catalog, and other low-sensitivity administration reports |
| `reports.attendance.run` | Attendance totals and attendance-event summaries without personal contact data |
| `reports.membership.run` | Membership lists and aggregate membership reports |
| `reports.membership.contact` | Directories, addresses, telephone numbers, and email addresses |
| `reports.worship.run` | Services, hymns, readings, schedules, and worship planning |
| `reports.pastoral.confidential` | Visits, personal attendance histories, prayer/pastoral material, or similarly sensitive reports |

`reports.run` remains only as the permission to open the report screen during
transition. It never authorizes a selected report by itself.

Accounting reports will later use the existing `accounting.reports.run` plus
more specific permissions where donor, payroll, bank, or audit details require
separation.

## 4. Initial role policy

| Role | Default report permissions |
|---|---|
| Master Administrator | All non-accounting report permissions |
| Pastor/Staff | General, attendance, membership, contact, worship, ministry, and pastoral confidential |
| Volunteer | Worship only |
| Auditor | General and attendance; accounting permissions remain governed separately |

Assignments are defaults and may be changed by an authorized administrator.
Master-administrator status does not replace explicit accounting-report policy.

## 5. Report catalog contract

`tblReports` will receive a non-null `RequiredPermissionID` foreign key. Every available
report must name exactly one installed permission. A report with a missing,
unknown, or malformed permission fails closed and is neither listed nor run.

The report picker will query only reports allowed for the current session. The
service will load the selected report record again and re-check its permission
before collecting parameters or starting any external process.

## 6. SQL reporting-view contract

Reporting views use the `rpt_` prefix and are installed through a guarded,
versioned migration. Views expose only fields required by registered reports.

Initial view families:

- `rpt_church_identity`
- `rpt_asset`
- `rpt_document`
- `rpt_attendance_event` and `rpt_attendance_person`
- `rpt_membership_person` and `rpt_membership_summary`
- `rpt_directory_family`, `rpt_directory_person`, and approved contact/address views
- `rpt_service`, `rpt_hymn_usage`, `rpt_reading`, and `rpt_service_role`
- `rpt_pastoral_visit` and other confidential pastoral views
- `rpt_sermon`, `rpt_pastor_report`, and `rpt_report_catalog`

Privacy rules belong in the views. Directory views must exclude records marked
unlisted. Ordinary membership views must not expose addresses, phone numbers,
email addresses, pictures, or notes unless their report category requires them.
Security credentials, password hashes, lockout state, audit internals, and
accounting data are never exposed by non-accounting views.

Views will use a controlled MariaDB definer account and `SQL SECURITY DEFINER`
so report accounts need no privilege on underlying tables. Migration validation
must verify the definer and security mode and detect invalid views.

## 7. Database report accounts

Production and testing use separate report accounts and Windows Credential
Manager targets. The accounts receive:

- permission to connect only from their intended host;
- `SELECT` only on explicitly approved reporting views;
- no direct privilege on base tables;
- no write, DDL, file, routine-creation, grant, or administrative privilege.

Non-accounting and accounting reporting accounts are separate. Compromise of a
general-report template must not expose accounting views.

## 8. LimeReport credential handling

Permanent `.lrxml` and `.lrsml` files must contain no usable username, password,
server address, or retained-credential setting. Before launch, ChurchManager
creates a unique temporary report copy using the correct restricted credential.

The temporary file:

- is accessible only to the current Windows user;
- is never placed in the repository;
- never exposes its password through command-line arguments or logs;
- is deleted immediately after LimeReport exits;
- is removed by startup cleanup if a prior crash left it behind.

Production/test mode is revalidated before staging. A production database is
refused in test mode and a test database is refused in production mode.

## 9. Audit requirements

Each report attempt records:

- signed-in ChurchManager user and session;
- report code and required permission;
- sanitized parameters;
- workstation and time;
- allowed, denied, succeeded, or failed status.

Passwords, database credentials, report contents, and sensitive parameter values
must not be written to the audit record.

## 10. Migration sequence

1. Inventory each registered non-accounting report and assign its category.
2. Add permissions, role defaults, and `tblReports.RequiredPermission`.
3. Install and validate the non-accounting reporting views.
4. Rewrite templates to query only approved views.
5. Create separate local-test report accounts and grants.
6. Implement fail-closed picker filtering and launch-time authorization.
7. Implement secure runtime template staging and cleanup.
8. Remove embedded credentials from permanent templates.
9. Run automated, database-integration, permission-matrix, and visual report tests.
10. Repeat account creation and credential rotation for production only after test acceptance.

## 11. Required tests

- Every available report has one valid required permission.
- Every permanent template contains no stored credential or server address.
- Every template query references only approved `rpt_` views.
- The report accounts cannot select any base table or perform writes.
- Unlisted directory contacts cannot be returned through reporting views.
- Each fictional test user sees only its permitted reports.
- Direct invocation cannot bypass the picker filter.
- Allowed, denied, successful, and failed runs create correct audit events.
- Test mode cannot contact the production database or production report account.
- All existing reports remain structurally valid and pass visual review after conversion.

## 12. Deferred accounting extension

Accounting views and report-account grants will be designed after the
non-accounting model is proven. Donor identities, bank information, payroll,
attachments, audit evidence, and ordinary financial statements may require
different permissions and separate views.
