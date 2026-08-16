# ChurchManager User and Security Specification

**Status:** Approved  
**Version:** 1.0  
**Date:** August 10, 2026  
**Approved by:** Rev. Jonathan C. Watt  
**Target application:** ChurchManager  
**Application framework:** JSForm  
**Database:** MariaDB/MySQL

## 1. Purpose

This document specifies authentication, authorization, user administration,
JSON-form security, and audit attribution for ChurchManager. It establishes the
security foundation required before the proposed fund-accounting module becomes
operational.

The user system identifies the person operating ChurchManager. It is separate
from the MariaDB service credential that ChurchManager uses to connect to the
database.

## 2. Security principles

1. Every person uses an individual ChurchManager account. Shared application
   accounts are prohibited for ordinary use.
2. Passwords are stored only as modern salted password hashes. Plaintext and
   reversibly encrypted passwords are prohibited.
3. Access is denied unless it has been granted through an active role or a
   controlled master-administrator rule.
4. Permission checks occur at the operation boundary, not only in the visible
   interface. Hiding a menu item or button is not sufficient authorization.
5. Financial posting, reversal, period control, user administration, backups,
   and other sensitive operations are performed through application services
   that recheck authorization immediately before committing.
6. Security and financial audit records are append-only through ChurchManager.
7. Posted accounting records are immutable. Corrections use controlled reversal
   and replacement transactions.
8. Test and production users, roles, credentials, and audit records remain in
   their respective databases.
9. The system uses least privilege: users receive only the access needed for
   their assigned work.
10. Authentication failures and authorization denials must not disclose
    passwords, hashes, database credentials, or confidential record contents.

## 3. Identity and login

### 3.1 Application user versus database user

ChurchManager continues to connect to MariaDB with its protected service
credential obtained through Windows Credential Manager. A ChurchManager user is
an application identity stored in ChurchDB and used for authorization and audit
attribution.

The MariaDB username is never treated as the identity of the person using the
application.

### 3.2 Login sequence

ChurchManager will:

1. Start wxPython and connect to the configured ChurchDB and JSForm databases.
2. Display the ChurchManager login dialog before constructing or showing the
   main menu.
3. Authenticate an active user against the stored password hash.
4. Load the user's active roles and effective permissions.
5. create an application session containing the stable user ID, username,
   display name, role IDs, permission names, login time, and workstation name;
6. write a successful-login audit event; and
7. display the permission-filtered main menu.

Failed login attempts produce a generic message and an audit event. The message
must not reveal whether the username or password was incorrect.

### 3.3 Password policy

- Passwords are hashed with Argon2id using a maintained Python library.
- A newly created or administratively reset password is temporary and must be
  changed at the next login.
- A password must contain at least 12 characters. Passphrases are encouraged;
  arbitrary composition rules are not required.
- Passwords are never placed in JSON forms, logs, command-line arguments,
  configuration files, audit before/after data, or database backups in
  plaintext.
- Five consecutive failed attempts lock the account for 15 minutes. Successful
  authentication clears the failure count.
- An administrator may disable an account or require a password change, but may
  not view an existing password.

### 3.4 Session behavior

The authenticated session lasts until ChurchManager closes or the user chooses
Log Out. A future release may add configurable inactivity locking. Sensitive
operations may request password confirmation if congregational policy requires
it.

### 3.5 Future remote access boundary

The initial ChurchManager deployment is private-network software. If remote
desktop users are later supported, they must reach the congregation's private
network through a safely configured encrypted VPN suitable for the local
environment. ChurchManager does not endorse a particular VPN provider or
product.

MariaDB, database administration, Windows file sharing, and unrestricted remote
desktop services must not be exposed directly to the public internet. Remote
access design must include least-privilege and individually revocable VPN
accounts, maintained endpoint devices, access-offboarding procedures, audit
review, and a recovery plan.

The VPN is only a network boundary. It does not replace individual
ChurchManager authentication, permissions, database least privilege, auditing,
session controls, or two-factor authentication required by a future remote,
browser, or member-access project.

## 4. Master administrator

### 4.1 Initial master account

Installation creates one master-administrator user. For the initial deployment,
this account is assigned to Pastor Jonathan Watt unless the deployment owner
directs otherwise. Installation uses a temporary password that must be changed
at first login.

The master administrator:

- has every defined ChurchManager permission;
- manages users, roles, and permission assignments;
- can inspect security and accounting audit history;
- can perform controlled account recovery; and
- can access newly introduced forms long enough to assign their permissions.

The master account is an ordinary identifiable ChurchDB user record with a
protected master flag. It is not a hidden username, hard-coded password, or
backdoor.

### 4.2 Master-account protections

- ChurchManager may not delete the last active master account.
- ChurchManager may not disable the last active master account.
- ChurchManager may not remove master status from the last active master
  account.
- A master administrator may not erase or edit audit history.
- Changes to master status require password confirmation and a recorded reason.
- The application should support at least two master administrators after
  initial setup so recovery does not depend permanently on one person.

### 4.3 Recovery

There is no universal recovery password. A local recovery command may reset a
master password only when run by an authorized Windows account on an approved
ChurchManager computer. Recovery creates an audit event and forces a password
change at the next login.

## 5. Roles

ChurchManager supports multiple roles per user. The initial general roles are:

| Role | Purpose |
| --- | --- |
| Master Administrator | Complete access, user administration, recovery, configuration, and emergency authority. |
| Pastor/Staff | Congregational, worship, attendance, pastoral, scheduling, and ordinary reporting work as assigned. |
| Volunteer | Access only to specifically assigned operational tasks. |

The initial accounting roles are defined by the fund-accounting specification:

| Role | Purpose |
| --- | --- |
| Accounting Viewer | View permitted posted transactions and reports. |
| Accounting Entry Clerk | Create and edit permitted drafts; cannot post. |
| Treasurer | Create, review, post, reconcile, and run accounting reports. |
| Accounting Approver | Approve transactions under the configured policy without altering approved lines. |
| Accounting Administrator | Maintain accounting configuration and perform controlled period operations. |
| Auditor | Read-only access to accounting records and accounting audit history. |

Roles provide defaults; permissions remain the authoritative access decision.
A user may hold more than one role.

## 6. Permissions

### 6.1 Naming

Permission names are stable lowercase identifiers in the form
`area.resource.action`. Form filenames, control labels, and menu text may change
without changing permission names.

Initial security permissions include:

- `security.users.view`
- `security.users.manage`
- `security.roles.view`
- `security.roles.manage`
- `security.audit.view`
- `application.config.manage`
- `application.backup.run`

Initial accounting permissions include:

- `accounting.transactions.view`
- `accounting.transactions.create`
- `accounting.transactions.edit_own_draft`
- `accounting.transactions.edit_any_draft`
- `accounting.transactions.delete_draft`
- `accounting.transactions.mark_ready`
- `accounting.transactions.approve`
- `accounting.transactions.post`
- `accounting.transactions.reverse`
- `accounting.reports.run`
- `accounting.reconciliation.manage`
- `accounting.master_data.manage`
- `accounting.periods.override`
- `accounting.audit.view`

Additional membership, worship, attendance, pastoral, scheduling, report, and
administrative permissions will be cataloged during implementation. Sensitive
pastoral information must have a distinct permission rather than inheriting
general membership access.

### 6.2 Enforcement points

Permissions are checked when:

- displaying and dispatching main-menu actions;
- creating or opening a form;
- loading protected records or fields;
- creating, saving, or deleting a record;
- invoking a custom form action;
- running or opening a protected report;
- exporting data;
- initiating a backup;
- changing users, roles, permissions, or application configuration; and
- invoking accounting posting, reversal, reconciliation, close, reopen, or
  approval services.

Database queries and application services must prevent unauthorized access even
if a user bypasses a menu or directly invokes a form route.

## 7. JSON-form security contract

### 7.1 Form declaration

The JSForm schema will support an optional `security` object in a form's `FORM`
definition. A typical declaration is:

```json
"security": {
    "open": "accounting.transactions.view",
    "create": "accounting.transactions.create",
    "update": "accounting.transactions.edit_any_draft",
    "delete": "accounting.transactions.delete_draft"
}
```

Supported form-level keys are:

- `open`
- `create`
- `update`
- `delete`
- `report`

A value is a registered permission name. The implementation may later support
a list when an operation legitimately requires more than one permission.

### 7.2 Control and field declarations

A control may optionally declare:

```json
"security": {
    "view": "pastoral.notes.view",
    "edit": "pastoral.notes.edit",
    "invoke": "accounting.transactions.post"
}
```

- `view` governs whether the control and its value may be displayed.
- `edit` governs whether a data-bound control may be changed.
- `invoke` governs a button, link, report, or custom action.

A hidden field must also be excluded from unauthorized queries, exports, logs,
and reports. Merely hiding its wxPython control is insufficient.

### 7.3 Form-change rules

When a `.json` form changes:

- moving controls, changing layout, or changing labels has no permission effect;
- adding an ordinary data field inherits the form's operation permissions;
- adding a sensitive field requires explicit `view` and `edit` permissions;
- adding a button, link, report, or custom action requires an appropriate
  `invoke` permission when the action is protected;
- renaming a form does not change access when stable permission names are
  retained;
- renaming or removing a permission requires an explicit permission migration;
- a new financial or security-administration form must declare security
  explicitly; and
- a malformed or unknown permission declaration fails form validation.

Existing nonfinancial forms may be migrated incrementally using a controlled
permission registry. Until a legacy form has an explicit declaration, its route
uses the registry rather than an implicit allow rule.

### 7.4 Fail-closed behavior

- Financial and security-administration forms without valid declarations do not
  open for ordinary users.
- A missing permission never grants access.
- The master administrator may open a newly recognized, structurally valid form
  for configuration, but malformed forms still fail validation for everyone.
- Custom service actions always check their own permission even when the form
  declaration permits opening the screen.

### 7.5 Validation and deployment

Before a changed form is accepted:

1. Validate it against the canonical JSForm schema.
2. Verify that every declared permission exists in the permission catalog or in
   an accompanying migration.
3. Verify that sensitive controls and actions declare the required permissions.
4. Run representative role tests.
5. Review the permission changes before deploying the form to production.

The source repository and version-control history record changes to JSON form
definitions. Runtime user audit records track use of the forms, not source-code
layout edits.

## 8. Data model

The reusable ChurchManager security tables are:

| Table | Purpose | Essential fields |
| --- | --- | --- |
| `tblUser` | Application identity | `ID`, optional unique `PersonID`, `Username`, `DisplayName`, `Email`, `Phone`, `PasswordHash`, `Active`, `MasterAdministrator`, `MustChangePassword`, `FailedLoginCount`, `LockedUntil`, `LastLoginAt`, timestamps |
| `tblRole` | Named permission grouping | `ID`, `Name`, `Description`, `SystemRole`, `Active` |
| `tblPermission` | Stable permission catalog | `ID`, `Name`, `Description`, `Sensitive`, `Active` |
| `tblUserRole` | User-to-role assignment | `ID`, `UserID`, `RoleID`, effective dates, assignment audit fields |
| `tblRolePermission` | Role-to-permission assignment | `ID`, `RoleID`, `PermissionID`, assignment audit fields |
| `tblSecurityAuditEvent` | Append-only security and access history | `ID`, `UserID`, `SessionID`, `Action`, `EntityType`, `EntityID`, `FormName`, `BeforeJSON`, `AfterJSON`, `Reason`, `Workstation`, `OccurredAt` |

Usernames and permission names are unique without regard to letter case. User,
role, and permission records referenced by audit history are deactivated rather
than deleted.

Accounting may use `tblSecurityAuditEvent` for common identity/security events
and retain `tblAccountingAuditEvent` for detailed ledger events. Both reference
the same stable `tblUser.ID`.

`tblUser.PersonID` may explicitly identify the corresponding congregation
person, but remains nullable because an authorized ChurchManager user need not
be a congregation member. The link does not synchronize user contact data with
person, family, participant, or directory records. Deleting a linked person
sets the user link to null and never removes the application account.

## 9. Audit requirements

The audit system records at least:

- successful and failed login;
- logout and administrative session termination;
- account creation, disablement, reactivation, lockout, and password reset;
- role and permission assignment changes;
- master-administrator changes;
- authorization denials for sensitive actions;
- protected record creation, update, deletion, posting, reversal, and export;
- reports containing financial, contributor, pastoral, or other confidential
  information;
- configuration changes and backups; and
- local master-account recovery.

Record-change audit events identify the user, timestamp, form, table or entity,
record ID, operation, and changed fields. Before/after values are included only
when useful and safe. Password hashes, secrets, tokens, entire confidential
documents, and unnecessary sensitive contents are never copied into audit data.

Ordinary forms cannot update or delete audit events. Retention and archival are
administrative processes governed by an approved retention policy.

## 10. User-administration interface

ChurchManager will provide:

- a login dialog;
- Change Password;
- Log Out;
- a user list and user editor;
- role and permission editors;
- password reset and account unlock actions;
- a read-only security audit inquiry; and
- a display of the current authenticated user in the main window.

Password entry and reset are custom security actions. They are not ordinary
JSForm record saves and never load an existing password hash into a form
control.

## 11. JSForm and ChurchManager responsibilities

JSForm will provide reusable mechanisms to:

- accept an authorization policy/session when constructing a form;
- interpret validated form and control security declarations;
- apply read-only and hidden-control behavior;
- call authorization checks immediately before ordinary create, update, and
  delete operations; and
- expose save/delete audit hooks after a successful database commit.

ChurchManager will:

- authenticate users and own the application session;
- define the permission catalog and role assignments;
- filter menu routes;
- supply the authorization policy to its form factory;
- enforce permissions in custom application and accounting services;
- write security audit events; and
- provide user-administration and recovery workflows.

The security mechanism must default to a no-op policy only for other legacy
JSForm applications that have not opted into authentication. ChurchManager
must always supply its security policy after this feature is enabled.

## 12. Testing requirements

Testing must include:

- password hashing and verification without logging secrets;
- successful login, failure, lockout, reset, first-login password change, and
  disabled-account behavior;
- prevention of losing the last active master administrator;
- role aggregation and denied-by-default behavior;
- menu, form-open, field, save, delete, report, backup, and custom-action checks;
- validation of JSON security declarations;
- rejection of undeclared financial/security forms;
- master access to a valid new form and rejection of malformed forms;
- audit attribution and append-only protection;
- accounting creator/approver separation and posted-record immutability;
- test/production database isolation; and
- regression tests demonstrating that authorized existing ChurchManager forms
  continue to load, navigate, save, and close correctly.

All schema and behavioral tests are first run against `ChurchDBTest` and
`JSFormTest`. Production migration requires a verified backup and successful
test-environment acceptance.

## 13. Implementation sequence

1. Approve this specification and resolve the decisions in Section 14.
2. Add the password-hashing dependency and isolated authentication tests.
3. Create test-database migrations for users, roles, permissions, assignments,
   and security audit events.
4. Bootstrap the first master administrator in the test database.
5. Add the application session, login dialog, logout, and password-change flow.
6. Add ChurchManager menu and form-factory authorization.
7. Add the JSForm security declaration schema and operation hooks.
8. Catalog existing ChurchManager routes, forms, reports, and custom actions and
   assign their initial permissions.
9. Add user, role, permission, and audit-administration screens.
10. Integrate the accounting services with the shared user identity and
    permission system.
11. Complete security, regression, and recovery testing.
12. Back up production, apply the reviewed migration, bootstrap production
    administrators, and verify access before enabling financial features.

## 14. Decisions required before implementation

The following decisions remain open for approval:

1. Whether a second master administrator is required before financial features
   can be enabled.
2. Which Pastor/Staff functions should be included by default.
3. Whether ordinary membership notes and confidential pastoral notes will be
   separate fields or records.
4. Whether inactivity locking is required in the first release and, if so, the
   timeout.
5. Whether password confirmation is required before posting, changing roles,
   changing master status, or running a backup.
6. Whether every accounting transaction requires a different approver or only
   transactions above a configured threshold.
7. Which roles may view payee detail, contributor detail if later implemented,
   bank information, and complete accounting audit history.
8. The security and accounting audit-retention policy.
9. Which Windows accounts and computers may run the master recovery command.

These choices affect policy and release scope but do not change the core
requirements for individual accounts, stable permissions, explicit JSON-form
security, operation-level enforcement, and auditable financial actions.
