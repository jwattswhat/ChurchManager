# ChurchManager member web portal specification

**Status:** Proposed for review
**Version:** 0.1
**Date:** August 29, 2026
**Target application:** ChurchManager
**Application framework:** Separate web application using ChurchManager services
**Database:** MariaDB/MySQL through a protected service boundary

## 1. Purpose

This specification defines an optional **ChurchManager Member Portal** through
which an identified congregation member may securely view and act on a limited
selection of the member's own congregation information.

The portal is not ChurchManager's public product website and is not the
ChurchManager desktop application in a browser. It is a deliberately small,
separately deployable interface that provides approved member services without
exposing MariaDB, desktop forms, administrative routes, or the congregation's
general records to the public internet.

The initial portal may provide:

- secure account activation, sign-in, sign-out, and recovery;
- the member's own profile and household information;
- reviewed requests to correct contact and household information;
- an opt-in congregation directory;
- public, member-only, group, and personally relevant calendar information;
- the member's groups, registrations, volunteer availability, and assignments;
- the member's own giving history and contribution statements;
- safe requests for pastoral contact; and
- privacy, security, consent, and account-management controls.

## 2. Product and deployment boundary

### 2.1 Optional and separately deployed

The Member Portal is optional. ChurchManager remains usable without it. Portal
code, accounts, routes, services, permissions, and deployment configuration are
installed or enabled only through a separate reviewed process.

The portal is not added to the public static ChurchManager product website.
That website continues to contain no congregation database connection,
application login, member records, or support logs.

### 2.2 Private-network ChurchManager remains the authority

The congregation's ChurchManager database remains authoritative for people,
households, groups, assignments, events, giving, and approved changes. The
portal does not become a second member database or an independent system of
record.

The browser never connects directly to MariaDB. Internet-facing services never
reuse the unrestricted desktop database credential. Every request passes
through a narrow ChurchManager-owned service that authenticates the user,
checks permission and record relationship, validates input, limits returned
fields, and writes appropriate audit events.

The required trust path is:

```text
Member browser
    -> HTTPS portal
    -> authenticated ChurchManager portal service
    -> authorization and relationship checks
    -> least-privilege database access
    -> congregation database
```

MariaDB, database administration, Windows file sharing, and unrestricted
remote desktop services must never be exposed directly to the public internet.

### 2.3 Relationship to ChurchManager School

This specification is maintained beside the ChurchManager School specification
because a later school project may reuse the portal's identity, guardian,
household, consent, notification, and relationship-checking foundation.

The first Member Portal release is for adult congregation members. It does not
create a parent, student, or teacher portal; expose student records; implement
online admission; or provide tuition payment. Any school-facing portal requires
an approved revision to both this specification and the ChurchManager School
specification, including explicit custody, educational-record access, minor
privacy, and school-scope rules.

## 3. Design principles

1. **Own information by default.** A member sees only records explicitly linked
   to that user's verified identity and approved household relationships.
2. **Permission plus relationship.** A general permission never grants access
   to every record of that type. Services also prove that the requested record
   belongs to, is shared with, or has been assigned to the current user.
3. **Individual accounts.** Each adult uses an individual account. Shared
   household credentials are prohibited.
4. **Minimum necessary display.** Each route returns only fields needed for the
   member service being performed.
5. **Consent before directory publication.** Contact information is absent from
   the directory unless the person or authorized household adult has opted in
   to each approved category.
6. **Requests rather than silent master-data edits.** Profile and household
   corrections normally create reviewed change requests.
7. **No administrative desktop in a browser.** JSON forms, database tables,
   report designers, unrestricted searches, and arbitrary exports are not
   portal features.
8. **No secrets in notifications.** Email or text may announce an available
   item but does not include giving amounts, statements, passwords, private
   care information, or reusable sign-in credentials.
9. **Fail closed.** Missing configuration, an ambiguous identity link, an
   inactive relationship, or an unavailable authorization service denies the
   request without revealing protected data.
10. **Auditable without copying secrets.** Security-sensitive actions are
    attributable while passwords, tokens, full statements, and confidential
    narratives remain outside audit payloads.

## 4. Ownership boundary

### 4.1 The portal presentation layer owns

- responsive and accessible browser pages;
- secure session cookies and browser protections;
- member-oriented navigation and plain-language messages;
- input collection, client-independent server validation, and confirmation;
- generic error pages that do not disclose infrastructure or record existence;
  and
- safe links to approved ChurchManager-generated downloads.

### 4.2 ChurchManager owns

- the person, household, user, group, event, assignment, giving, and request
  records;
- identity links, roles, permissions, relationship policies, and auditing;
- approved portal datasets and field-level disclosure rules;
- change-request review and authoritative record updates;
- contribution-statement generation and authorization;
- deployment registration, account revocation, backup, and recovery; and
- privacy-safe diagnostics and support packages.

### 4.3 JSForm owns

JSForm may provide application-neutral validation, authorization hooks, and
shared service contracts when appropriate. It does not own portal identity,
household authority, directory consent, giving disclosure, pastoral routing,
or congregation-specific publication decisions.

## 5. Identity and account model

### 5.1 Portal user

A portal user is an individual ChurchManager application identity with a stable
User ID and an explicit link to one Person. A portal account cannot be activated
when the Person link is missing, ambiguous, inactive, or pending review.

The account record includes:

- stable User ID and linked Person ID;
- unique normalized username or verified email sign-in identifier;
- display name;
- active, locked, activation-pending, and recovery states;
- password hash and password-change state;
- optional multi-factor enrollment state;
- portal terms/privacy acceptance version and time;
- last successful login and security timestamps; and
- creation, activation, deactivation, and audit attribution.

The database service identity is never treated as the member's identity.

### 5.2 Account activation

The initial safe activation sequence is:

1. A prospective user requests access without receiving confirmation that a
   named person or email exists in ChurchManager.
2. An authorized church worker reviews the request and confirms the correct
   Person and household relationship.
3. ChurchManager creates or links the individual user account.
4. ChurchManager sends a single-use, short-lived activation link through an
   approved communication service.
5. The user establishes a password and, when required, a second factor.
6. ChurchManager records activation and invalidates the token.
7. The user signs in normally and sees only approved portal modules.

Activation and recovery tokens are random, single-use, stored only as protected
hashes, expire promptly, and are invalidated when replaced or the account is
disabled. Staff cannot view an existing password or activation token.

### 5.3 Authentication and sessions

- Passwords follow the ChurchManager User and Security Specification and use a
  maintained Argon2id implementation.
- Staff, financial-administration, or elevated portal functions require
  multi-factor authentication. Congregations may require it for every member.
- Repeated failures cause rate limiting and account protection without
  confirming whether an account exists.
- Authentication creates a server-side or cryptographically protected session
  with a short idle limit and an absolute expiration.
- Cookies are Secure, HttpOnly, and SameSite protected; authentication tokens
  are not stored in browser local storage.
- Password, email, permission, or security-setting changes revoke other active
  sessions when policy requires.
- Sensitive downloads may require recent authentication.

## 6. Authorization model

Every operation requires all applicable checks:

1. the portal deployment and module are enabled;
2. the account and linked Person are active;
3. the session is valid and meets any recent-authentication or multi-factor
   requirement;
4. the user has the named portal permission;
5. the requested record is owned by or explicitly shared with the linked
   Person or an authorized household relationship;
6. directory consent, group scope, time limits, and record status permit the
   disclosure; and
7. the returned dataset removes fields not approved for that route.

Representative permissions include:

- `portal.access`;
- `portal.profile.view_own` and `portal.profile.request_change`;
- `portal.household.view_own`;
- `portal.directory.view` and `portal.directory.manage_own_consent`;
- `portal.events.view_member` and `portal.registrations.manage_own`;
- `portal.groups.view_own`;
- `portal.assignments.view_own` and `portal.availability.manage_own`;
- `portal.giving.view_own` and `portal.statements.download_own`;
- `portal.pastoral_contact.request`; and
- separate staff permissions for reviewing requests and administering portal
  accounts.

An `own` permission never authorizes an unrestricted table query. Database and
service tests must prove cross-person, cross-household, cross-contributor, and
cross-group access is denied even when IDs or URLs are altered manually.

## 7. Member home page

After sign-in, the home page may display:

- the member's preferred display name;
- the next approved public or member event;
- personally relevant group events and volunteer assignments;
- new congregation announcements approved for portal display;
- outstanding profile-change or registration requests;
- availability of a new contribution statement without displaying its amount;
- shortcuts to enabled member services; and
- privacy, help, and sign-out actions.

The home page does not expose confidential pastoral, attendance, giving, or
household detail in page titles, notification previews, analytics, or URLs.

## 8. Profile and household information

### 8.1 Viewable information

An adult member may view an approved subset of the member's own Person record
and household information, including:

- preferred and formal names;
- mailing and physical address when maintained;
- phone numbers and email addresses;
- communication preferences;
- household members and approved relationship labels;
- directory-sharing choices; and
- the date on which the displayed information was last reviewed.

Internal notes, pastoral information, unapproved relationship details, giving
identifiers, security fields, audit metadata, and deleted or merged-record
history are never included in the member profile dataset.

### 8.2 Change requests

The first release does not silently edit authoritative Person or Family records.
A member submits a proposed change containing the field, current display value,
requested value, optional short explanation, and request timestamp.

An authorized worker may approve, revise with the member's knowledge, reject,
or mark the request duplicate. Approval applies the change through a
ChurchManager service and links the authoritative audit event to the request.
The member can see the request status but not internal review notes.

Changes affecting identity, household membership, marital or family
relationships, minors, directory authority, contributor ownership, or user
security always require staff review.

## 9. Member directory

The directory is disabled until the congregation approves its policy and
collects consent. It is available only to authenticated users with directory
permission.

Each eligible person or household can separately opt in to approved fields:

- photograph;
- household or individual display name;
- mailing address;
- phone number;
- email address;
- household relationships; and
- birthday month and day without year, if congregational policy permits.

Rules:

- absence of consent means absence from the relevant directory result;
- an unlisted or restricted-contact setting overrides ordinary consent;
- consent records the policy version, fields, actor, source, and time;
- consent can be withdrawn and takes effect promptly;
- minors require an approved adult authority and a separate policy;
- search is rate limited and returns bounded results;
- bulk download, scraping-oriented endpoints, and full-directory export are
  prohibited in the first release; and
- contact information is never included in page metadata, public search, or
  unauthenticated error messages.

## 10. Calendar, announcements, and registrations

Portal events are approved projections of ChurchManager event records. Each
event has a disclosure level such as Public, Signed-in Members, Selected Group,
Assigned Participants, or Staff Only.

The portal may show title, approved description, date and time, public location,
registration status, and a safe contact route. Internal preparation notes,
pastoral appointments, safeguarding details, private homes, participant lists,
and staff-only attachments are excluded unless a narrower approved service
explicitly requires them.

Members may register themselves or approved household members, state attendance
count, answer bounded registration questions, volunteer for listed duties, or
cancel within policy. Registration never grants broader group or record access.

## 11. Groups, volunteer availability, and assignments

A member may see groups in which the linked Person has an active membership and
only the fields approved for member display. A group leader receives no broader
membership access merely because the leader can manage one group.

The portal may allow a member to:

- view the member's active groups and approved meeting information;
- view the member's own current and future assignments;
- accept, decline, or request help with an assignment;
- submit date-specific unavailable periods;
- state approved service preferences; and
- receive confirmation and reminders.

Responses and availability use the Volunteer Availability specification.
Changes that affect an approved schedule create a response or coordinator task;
they do not silently rewrite the schedule.

## 12. Giving history and statements

Giving access is optional and disabled until contributor-link verification,
statement authorization, and recovery procedures pass acceptance testing.

An authorized member may see only contribution information linked to the
member's verified contributor identity or an explicitly authorized household
giving relationship. Available information may include:

- contribution date;
- fund or approved purpose;
- amount;
- noncash indicator and approved description;
- year-to-date summary; and
- finalized contribution statements available for secure download.

The portal never permits a member to edit, delete, post, reverse, or reassign a
contribution. A suspected error creates a confidential inquiry for authorized
giving staff.

The portal does not expose another contributor's gifts, deposit composition,
envelope-administration notes, bank details, payment credentials, accounting
entries, internal adjustments, or unrestricted financial reports.

Statements are generated by ChurchManager, authorized at request time, delivered
over HTTPS, protected from predictable URLs, and omitted from ordinary caches.
Notification messages state only that a statement is available.

Online giving and payment processing are outside the first release. A future
provider integration must use provider-hosted payment handling and a separately
approved specification; ChurchManager must not store reusable card or bank
credentials.

## 13. Attendance boundary

The first release does not display worship, group, class, or school attendance
history to members. Attendance can reveal sensitive pastoral and household
patterns, and household authority does not automatically establish that such
history should be disclosed.

Adding member-visible attendance requires a specification revision defining the
pastoral purpose, permitted records, household and minor authority, correction
process, retention, and disclosure risks.

## 14. Pastoral-contact requests

The portal may provide a small request form with:

- request category such as call, visit, or private conversation;
- preferred safe contact method and time;
- an optional short routing message;
- urgent-help guidance defined by the congregation; and
- confirmation that the request was received.

The portal is not an emergency service, counseling platform, clinical record,
or confidential pastoral-note editor. It does not display pastoral-care history
or restricted notes. Submitted text is treated as sensitive, visible only to
authorized recipients, retained according to policy, and excluded from routine
email bodies and diagnostic logs.

## 15. Notifications

Members may choose approved email or text notifications for events, assignments,
registrations, profile requests, security activity, and statement availability.

Notifications contain the minimum necessary information and direct the member
back to the authenticated portal. They do not contain contribution amounts,
attached statements, directory exports, household-sensitive changes, pastoral
narratives, passwords, activation secrets beyond the required single-use link,
or confidential documents.

Every notification records template, purpose, recipient resolution, send result,
and safe attribution without copying confidential content into general logs.

## 16. Security and privacy requirements

The portal requires a documented deployment threat model and security review
before any real congregation data is reachable from the internet. At minimum:

- TLS is required for every nonlocal request, with secure redirect and strict
  transport policy after deployment validation;
- internet-facing hosts and credentials are separate from development and
  desktop administration;
- the service database account has only the operations required by approved
  portal services;
- server-side authorization is repeated for every view, change, download, and
  action;
- state-changing requests use anti-forgery protection and strict origin checks;
- output encoding, parameterized queries, upload prohibition or strict file
  controls, and safe error handling are mandatory;
- login, activation, recovery, directory search, and download routes are rate
  limited;
- sensitive pages and downloads use restrictive cache controls;
- security headers restrict framing, content sources, referrers, and MIME
  interpretation;
- production contains no demonstration users, default passwords, database
  dumps, source maps with secrets, or verbose debug output;
- dependencies and host systems receive maintained security updates;
- backup, restoration, key rotation, incident response, and account offboarding
  are rehearsed; and
- a privacy notice explains data sources, uses, visibility, retention, member
  choices, and contact procedures.

The portal must not add analytics, advertising, tracking pixels, social-media
widgets, or third-party scripts that receive member activity or congregation
data without a separately approved privacy review.

## 17. Audit and operational review

Audit events include:

- successful and failed authentication and account recovery;
- account activation, disablement, lockout, and security-setting changes;
- directory consent changes;
- profile and household change requests and decisions;
- event registration and volunteer response changes;
- giving-history access and statement download;
- pastoral-contact request routing;
- staff impersonation, if ever introduced; and
- authorization denials for sensitive or anomalous requests.

Audit events identify the user, session, operation, entity type and safe ID,
result, time, and appropriate request context. They do not contain passwords,
tokens, statement contents, full giving details, full directory results,
pastoral narratives, or unnecessary personal data.

Congregations establish review and retention procedures before launch. Audit
records are append-only through ordinary ChurchManager and portal interfaces.

## 18. Accessibility and member experience

The portal supports current WCAG-oriented practices, including:

- semantic landmarks, headings, labels, and error associations;
- complete keyboard operation and visible focus;
- sufficient contrast and status cues that do not rely only on color;
- responsive layouts and comfortable touch targets;
- clear session-expiration and reauthentication messages;
- accessible tables and downloadable statements;
- plain language suitable for members without technical knowledge; and
- no requirement for a mobile application.

Security messages remain useful without confirming account or record existence.

## 19. Proposed data model

The portal reuses `tblUser`, `tblPerson`, the approved user-to-person link,
roles, permissions, security audit events, and authoritative ChurchManager
domain tables. Portal-specific logical records include:

- `tblPortalDeployment` for approved host, status, policy versions, and module
  configuration;
- `tblPortalAccountState` for activation and portal-specific security state;
- `tblPortalActivationToken` and `tblPortalRecoveryToken` using protected token
  hashes and expiration;
- `tblPortalSession` or an equivalent protected session store;
- `tblPortalDirectoryConsent` for field-specific, versioned consent;
- `tblPortalProfileChangeRequest` and request-field details;
- `tblPortalRegistration` for portal-originated event participation where the
  existing event model does not already provide it;
- `tblPortalPastoralContactRequest` containing minimum necessary routing data;
  and
- approved portal events in the existing append-only audit system.

Tables use positive identifiers, foreign keys, effective dates, state checks,
unique active-link constraints, expiry indexes, and deletion restrictions.
Tokens and sessions are deactivated or expired, never exposed through ordinary
forms or reports.

## 20. Service interface requirements

The portal consumes purpose-specific operations rather than generic table APIs.
Representative operations are:

- get the current member's home summary;
- get the current member's approved profile and household view;
- submit and view the current member's change requests;
- search the consent-filtered member directory;
- list events visible to the current member;
- manage the current member's registrations and availability;
- list the current member's assignments and groups;
- list the current member's authorized giving summary;
- download one currently authorized finalized statement; and
- submit a pastoral-contact request.

Services use server-derived User and Person IDs. A browser-supplied Person,
Household, Contributor, or User ID is never accepted as proof of ownership.
Responses use explicit allow-listed fields and bounded pagination.

## 21. Explicit exclusions from version 1

Version 1 excludes:

- a browser version of ChurchManager administrative forms;
- public or anonymous member-directory access;
- shared household accounts;
- direct editing of authoritative Person, Family, giving, or accounting data;
- member-visible attendance history;
- online giving, tuition payments, or stored payment credentials;
- school parent, student, teacher, admission, tuition, grade, health, custody,
  pickup, or attendance access;
- confidential pastoral notes or pastoral-care history;
- arbitrary report execution or database export;
- member uploads and general document sharing;
- chat, social feeds, discussion boards, or public comments;
- third-party advertising, behavior analytics, or tracking;
- full liturgical or musical content prohibited by the ChurchManager worship
  content boundary; and
- direct public access to MariaDB, Windows shares, backups, logs, or desktop
  remote-control services.

## 22. Testing and acceptance

Automated testing includes:

- activation, expiration, single use, recovery, lockout, and session revocation;
- password hashing and multi-factor enforcement where configured;
- permission and relationship checks for every service;
- attempted cross-person, cross-household, cross-contributor, cross-group, and
  changed-ID access;
- directory opt-in, withdrawal, unlisted override, minor exclusion, and search
  limits;
- profile-request lifecycle and authoritative-update attribution;
- event visibility and registration scope;
- assignment and availability ownership;
- giving and statement authorization, cache controls, and predictable-URL
  resistance;
- pastoral-request privacy and safe notification content;
- anti-forgery, injection, output encoding, rate limiting, and generic errors;
- audit creation and secret/confidential-content exclusion;
- database least privilege and test/production isolation; and
- regression tests for affected desktop ChurchManager functions.

Acceptance also requires:

1. a reviewed threat model and deployment diagram;
2. an approved privacy, directory-consent, account-recovery, retention,
   incident-response, and offboarding policy;
3. testing only with fictional data until security acceptance is complete;
4. independent security review of the internet-facing application;
5. representative desktop and mobile browser testing, including keyboard and
   accessibility review;
6. backup and restoration rehearsal;
7. proof that MariaDB and desktop administration are not publicly reachable;
8. a pilot using a bounded set of non-sensitive modules before Giving is
   enabled; and
9. explicit product-owner approval before production deployment.

No claim of visual, security, or production acceptance may be made from unit
tests alone.

## 23. Recommended implementation sequence

1. Approve this specification and settle the decisions in Section 24.
2. Prepare the portal threat model, privacy policy, and deployment design.
3. Define purpose-specific service contracts and relationship-test helpers.
4. Implement deployment registration, activation, authentication, sessions,
   recovery, revocation, and audit behavior using fictional data.
5. Implement the home page and own-profile view.
6. Implement reviewed profile-change requests.
7. Implement directory consent and bounded directory search.
8. Implement approved events, registrations, groups, assignments, and volunteer
   availability.
9. Complete a nonfinancial pilot and security review.
10. Implement verified contributor relationships and own-giving views.
11. Add secure finalized-statement download only after separate financial
    acceptance.
12. Implement pastoral-contact routing.
13. Complete accessibility, recovery, incident, deployment, and full regression
    acceptance before production release.

## 24. Decisions required before implementation

1. Where the portal service will run and who will maintain its operating system,
   certificates, domain, backups, updates, and monitoring.
2. Whether every member must use multi-factor authentication or only accounts
   with financial or elevated access.
3. Which profile fields members may view and which low-risk fields, if any, may
   be updated without staff review.
4. Who may authorize household relationships and act for minors or dependent
   adults.
5. Which directory fields are offered, whether photographs are included, and
   the exact consent and renewal policy.
6. Which events and announcements may be Public, Member, Group, or Assigned
   Participant information.
7. Whether Giving is included in the first production release or enabled only
   after a nonfinancial pilot.
8. Whether giving access is individual or household-based and how contributor
   relationships are verified and revoked.
9. Which pastoral-contact categories and recipients are permitted and what
   urgent-help wording is displayed.
10. Session idle and absolute timeouts, recent-authentication rules, token
    lifetimes, and account-recovery verification.
11. Audit, consent, request, session, and notification retention periods.
12. Support, incident-response, breach-notification, and portal shutdown
    authority.

## 25. Decisions established by this specification

- The portal is optional and separately deployed from both desktop
  ChurchManager and the static public product website.
- The browser never connects directly to MariaDB.
- Purpose-specific ChurchManager services enforce both permission and record
  relationship at every operation boundary.
- Each adult uses an individual account linked to one verified Person.
- Profile corrections normally use reviewed requests.
- The member directory is authenticated, consent-based, bounded, and not
  bulk-exportable in version 1.
- Giving access, when enabled, is limited to verified own or explicitly
  authorized household contributor relationships.
- Attendance history, school portals, payments, administrative forms, and
  confidential pastoral records are outside version 1.
- The portal stores planning references and member services only; it does not
  add prohibited full liturgical or musical content.
- No production launch occurs without threat modeling, security review,
  operational policies, fictional-data testing, and explicit approval.
