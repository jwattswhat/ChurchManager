# ChurchManager parochial school subsystem specification

**Status:** Proposed for review
**Version:** 0.1
**Date:** August 26, 2026
**Target application:** ChurchManager
**Application framework:** JSForm
**Database:** MariaDB/MySQL

## 1. Purpose

This specification defines an optional **ChurchManager School** subsystem for
small parochial elementary schools. It is intended to complement the church's
existing administration, accounting, giving, people, family, document, asset,
project, event, and reporting functions without forcing non-school
congregations to install or use school features.

The first release provides the practical administrative records a small school
needs most often:

- students, guardians, households, and emergency contacts;
- inquiries, applications, admission, enrollment, and withdrawal;
- school years, grade levels, classes, teachers, and rosters;
- daily attendance, tardiness, early dismissal, and absence reasons;
- authorized pickup, health alerts, immunization status, and required forms;
- tuition and school fees through a separate family account ledger;
- staff and volunteer safeguarding qualifications;
- school calendars, documents, assets, projects, and reports; and
- basic school advancement and donor relationships through the existing Giving
  subsystem.

The subsystem is designed first for one small school associated with one
congregation. It does not attempt to reproduce a large district SIS, learning
management system, or online classroom platform.

## 2. Product boundary

### 2.1 ChurchManager School is optional

School tables, permissions, menus, starter reports, and configuration are
installed only when the school subsystem is selected during installation or
enabled later by an authorized administrator. Disabling the subsystem hides
ordinary school work but never deletes school records.

### 2.2 ChurchManager remains the shared administrative foundation

The school subsystem reuses these ChurchManager capabilities:

- Church, Person, Family, contact, address, and document records;
- application users, roles, permissions, auditing, diagnostics, and backups;
- Groups for ordinary clubs, committees, and activity rosters where suitable;
- events and external calendar publication;
- assets, locations, maintenance, and projects;
- confidential Giving and fund accounting; and
- JSForm screens, search, reports, menus, and typed controls.

School-specific meaning is never forced into a general ChurchManager field.
Students, guardians, enrollments, classes, tuition accounts, academic records,
and safeguarding eligibility receive normalized school records.

### 2.3 Not a full SIS in the first release

Version 1 excludes:

- assignments, homework, lesson plans, online courses, and classroom content;
- a comprehensive gradebook, standards-based assessment, transcripts, and
  state reporting;
- a parent, student, or teacher web portal;
- online admissions, online tuition payment, and payment credentials;
- payroll, human-resources, substitute placement, and benefits;
- library circulation, lunch accounts, transportation, athletics, and child
  check-in;
- special-education case management, IEP or 504 document workflows;
- a nurse's clinical record or medication-administration system;
- disciplinary investigations or safeguarding-case records;
- multi-campus or diocesan administration; and
- automatic synchronization with an external SIS.

These may be considered later only after the first release is accepted and a
real school demonstrates the need.

## 3. Design principles

1. **One person, specialized roles.** A Person may be a church member, student,
   parent, teacher, donor, volunteer, or several of these without duplicate
   Person records.
2. **School identity is explicit.** School records belong to one School and one
   Church; they do not depend on a name or menu selection.
3. **Student history is preserved.** Enrollment, attendance, class placement,
   account activity, and record transfers are dated history, not overwritten
   current-state fields.
4. **Guardianship is not inferred.** Family membership does not automatically
   grant legal custody, pickup authority, record access, or financial
   responsibility.
5. **Tuition is not giving.** Tuition, registration fees, meals, activities,
   and other charges are school receivables. They never appear as charitable
   contributions merely because the school is church operated.
6. **Advancement is not tuition.** Donor gifts continue through confidential
   Giving, while school relationships and campaigns may extend that subsystem.
7. **Sensitive data receives least privilege.** Health, custody, financial,
   academic, and safeguarding information use separate operation-boundary
   permissions.
8. **Configurable church identity.** Congregational affiliation, religious
   instruction, chapel, and milestone fields are configurable and do not
   assume one denomination.
9. **External tools remain external.** ChurchManager exchanges approved data
   with calendars, payment providers, or future SIS products rather than
   storing their credentials or duplicating their full function.
10. **No hidden legal determination.** ChurchManager records facts and policy
    decisions; it does not determine custody rights, educational eligibility,
    tax treatment, medical fitness, or regulatory compliance.

## 4. Ownership boundary

### 4.1 JSForm owns

JSForm provides application-neutral support for:

- typed forms and controls;
- responsive master-detail layouts;
- date, time, phone, email, currency, and controlled-choice validation;
- search, filtering, lists, sorting, and double-click editing;
- application-provided authorization and audit hooks;
- protected and read-only fields;
- reviewed CSV import/export hosts;
- report layout, rendering, and customization from approved datasets; and
- consistent validation and error presentation.

### 4.2 ChurchManager owns

ChurchManager owns:

- school, student, guardian, enrollment, class, attendance, tuition, health,
  pickup, and safeguarding meaning;
- database schema, constraints, migrations, starter data, and retention rules;
- permissions, privacy, record disclosure, and same-School validation;
- admissions, enrollment, attendance, billing, and lifecycle transactions;
- accounting and Giving integration;
- approved search, report, export, and calendar datasets;
- privacy-safe auditing and diagnostics; and
- installation, backup, restore, test-data, and documentation behavior.

JSForm must not infer guardianship, custody, pickup rights, student status,
financial responsibility, teaching authority, or safeguarding eligibility.

## 5. School and configuration records

Each School contains:

| Field | Rule |
| --- | --- |
| `ID` | Immutable positive database identifier. |
| `ChurchID` | Owning Church; required. |
| `SchoolKey` | Stable unique key within the Church. |
| `Name` | Required public name. |
| `ShortName` | Optional concise display name. |
| `SchoolType` | Controlled type such as Preschool or Elementary. |
| `Status` | Draft, Active, Inactive, or Closed. |
| `AddressID` | Approved school address. |
| `Phone` and `Email` | Validated public contact values. |
| `PrincipalPersonID` | Optional linked Person. |
| `DefaultCalendarID` | Optional external-publication target. |
| `DefaultAccountingOrganizationID` | Required before billing handoff. |
| `Configuration` | Approved non-executable settings only. |
| Audit fields | Creator, creation time, editor, and edit time. |

One Church may own more than one School in the schema, but the first release
user interface supports one active School at a time. Multi-school operation is
not accepted merely because multiple rows are technically possible.

## 6. Student and guardian model

### 6.1 Student

A Student record links to exactly one Person and contains:

- School ID and immutable Student Number;
- admission, enrollment, expected graduation, withdrawal, and alumni status;
- current grade derived from active enrollment rather than copied text;
- preferred school name when different from the Person display name;
- previous school and transfer summary;
- ordinary administrative note; and
- audit fields.

A Person may have only one Student record per School. A withdrawn student is
retained and may later reenroll through a new enrollment term.

### 6.2 Guardian and school relationship

A Student-Adult relationship contains:

- Student ID and adult Person ID;
- controlled relationship label;
- legal guardian flag;
- educational-record access flag;
- school-communication flag;
- pickup authorization and effective dates;
- emergency-contact priority;
- financial-responsibility flag;
- lives-with-student flag;
- applicable restriction indicator; and
- audit fields.

The detailed text or documents supporting a custody or pickup restriction are
separately protected. Ordinary screens show only the minimum warning needed to
prevent unsafe disclosure or release.

Family membership may suggest possible adults during setup, but every school
relationship requires explicit review and confirmation.

### 6.3 Emergency contacts and pickup

- An emergency contact is a Person relationship, not a free-form name when an
  existing Person can be used.
- An authorized pickup list is effective-dated.
- Emergency priority is unique within a Student's active contacts.
- An expired or revoked pickup authorization remains historical.
- A restricted pickup person must never appear as authorized through another
  inferred Family relationship.

## 7. Admissions and enrollment

Admissions statuses are Inquiry, Application, Under Review, Accepted,
Wait-listed, Declined, Withdrawn, and Enrolled.

An application records the prospective Student, intended School Year and grade,
application date, status, checklist, decision, and bounded notes. Documents use
the protected ChurchManager document service and school-specific categories.

Enrollment is a separate accepted relationship containing:

- Student, School Year, grade level, and enrollment status;
- start and end dates;
- full-time or approved part-time indicator;
- parish or congregation affiliation classification;
- tuition classification and financial-responsibility account;
- withdrawal reason when ended; and
- audit fields.

Rules:

- a Student cannot have overlapping active enrollments in the same School;
- grade placement belongs to the enrollment term;
- accepting an application does not create a financial charge until enrollment
  is confirmed;
- withdrawal preserves attendance, class, billing, and report history; and
- reenrollment creates a new term rather than rewriting the old one.

## 8. School years, terms, grades, classes, and staff

The first release provides controlled records for:

- School Year;
- marking or reporting periods;
- grade levels;
- courses or subjects;
- class sections;
- rooms and meeting patterns;
- teacher and aide assignments; and
- student class enrollment.

A teacher or aide is an existing Person with an effective-dated staff
assignment. Employment and payroll remain outside scope.

Class rosters are derived from class enrollment. Groups may be used for clubs,
choirs, committees, and ordinary activities but do not replace academic class
enrollment.

## 9. Attendance

School attendance is distinct from worship and Group attendance.

The system supports:

- Present, Absent, Tardy, Excused, Early Dismissal, and Unknown;
- whole-day or half-day attendance in the first release;
- optional arrival and dismissal times;
- controlled absence reason;
- recording user and timestamp;
- reviewed correction history; and
- daily, student, class, and period reports.

Rules:

- one effective attendance result per Student and school day;
- attendance can be entered by class roster but resolves to the Student/day
  record;
- a non-instructional or closed day is not counted as an absence;
- corrections are audited;
- attendance alerts reveal only authorized student information; and
- ChurchManager does not automatically interpret attendance for truancy,
  funding, eligibility, or state reporting.

## 10. Health, forms, and student safety

Version 1 stores administrative status rather than clinical narratives:

- emergency health summary;
- allergy or critical-alert indicator and concise authorized instruction;
- physician and preferred facility contact when provided;
- immunization record status and verified date;
- required form definitions, received dates, expirations, and exceptions;
- medication-on-file indicator without medication administration logging; and
- protected supporting documents.

Detailed medical notes, diagnoses, counseling, medication administration, and
clinical treatment are outside scope. Screens and reports expose the minimum
necessary information for the user's authorized duty.

## 11. Safeguarding, staff, and volunteers

The subsystem reuses Persons and Groups but adds effective-dated qualification
records for staff and volunteers:

- role or assignment category;
- background-check status, review date, and expiration;
- safe-environment training status, date, and expiration;
- code-of-conduct acknowledgment;
- mandatory-reporting acknowledgment;
- credential or license summary where required;
- approved, restricted, expired, or pending eligibility; and
- authorized reviewer and audit fields.

ChurchManager stores status and controlled evidence references. It does not run
background checks, adjudicate allegations, or store investigative case files.
Expired or incomplete qualification produces a prominent warning and prevents
assignment where school policy marks the qualification mandatory.

## 12. Tuition, fees, and family accounts

Tuition is implemented as a school receivable subledger separate from Giving.

### 12.1 Account and charges

A School Account identifies one financially responsible Person or Family and
may cover multiple Students. It supports:

- tuition schedules and grade-based rates;
- registration, activity, material, and other controlled fee types;
- member, nonmember, sibling, staff, scholarship, and approved local discounts;
- parish or congregational subsidy;
- financial-aid awards;
- payment plans and due dates;
- charges, payments, credits, refunds, and adjustments;
- balances, aging, and statements; and
- privacy-safe summarized accounting handoff.

### 12.2 Financial rules

- Tuition and fee payments never create Giving contributions.
- A charitable gift cannot silently satisfy a particular family's tuition.
- Approved scholarships, aid, and congregation subsidies are recorded through
  controlled policy and accounting mappings.
- Posted account activity is corrected through linked adjustments, not edited
  or deleted.
- Payment-provider credentials and reusable payment tokens are not stored.
- The school receivable ledger and general ledger reconcile through summarized
  transactions without placing unnecessary Student identity in accounting.

## 13. Parochial-school configuration

Optional configuration may include:

- affiliated congregation and church-body label;
- congregation-member tuition classification;
- religious-instruction class or level;
- chapel participation and service schedule;
- configurable religious milestones such as Baptism or Confirmation;
- congregation subsidy policy; and
- church-body or diocesan report mappings.

No denomination-specific field is mandatory. Religious and sacramental data is
treated as sensitive and shown only to authorized users.

The subsystem stores administrative references and milestones. It does not
store copyrighted curriculum, textbook content, worship text, music, or lesson
content.

## 14. Donors and school advancement

The existing Giving subsystem remains the authoritative gift ledger. A School
may be an approved gift purpose or accounting dimension, subject to the same
directed-gift and congregation-control rules already established for Giving.

The first school release adds relationship metadata sufficient to identify:

- current and former parents;
- grandparents and other relatives;
- alumni and graduation year;
- staff, volunteers, businesses, and community supporters; and
- school-interest and communication preferences.

Optional advancement records may track campaigns, pledges, acknowledgments,
interactions, stewardship follow-up, matching gifts, and fundraising events in
a later phase. Donor identity and gift history remain restricted by Giving
permissions. Teachers and ordinary school users receive no donor access merely
because a donor is related to a Student.

## 15. Communication and calendar integration

Authorized users may prepare reviewed communications for:

- a School, grade, class, or activity;
- guardians authorized for school communication;
- staff or volunteers; and
- selected account or missing-document reminders.

Communication follows ChurchManager's preview, recipient resolution, unlisted
contact, TEST MODE, SMTP, audit, and explicit-send rules.

Calendar Integration publishes approved school events, closures, class events,
chapel, conferences, and activities to external calendars. ChurchManager does
not become a second full calendar platform or silently modify an external
calendar.

## 16. Permissions and privacy

Permissions are separated by operational duty. The initial catalog includes:

- `school.view` and `school.configure`;
- `school.students.view` and `school.students.edit`;
- `school.admissions.view` and `school.admissions.edit`;
- `school.enrollment.view` and `school.enrollment.edit`;
- `school.guardians.view` and `school.guardians.edit`;
- `school.pickup.view` and `school.pickup.edit`;
- `school.health.view` and `school.health.edit`;
- `school.classes.view` and `school.classes.edit`;
- `school.attendance.view` and `school.attendance.record`;
- `school.safeguarding.view` and `school.safeguarding.review`;
- `school.billing.view`, `school.billing.enter`, `school.billing.post`, and
  `school.billing.statements`;
- `school.reports.view` and `school.export`; and
- `school.communication.prepare` and `school.communication.send`.

Menu visibility is not authorization. Services, reports, searches, imports,
exports, and document access recheck permission and School scope.

Private and parochial elementary schools are not assumed to be outside every
privacy obligation merely because FERPA may not apply to a particular school.
ChurchManager applies least privilege, access auditing, protected backups,
purpose-limited exports, and disclosure review regardless of the school's
legal classification. Each installation remains responsible for determining
its federal, state, church-body, accreditation, and contractual requirements.

## 17. Proposed data model

The logical tables include:

- `tblSchool` and `tblSchoolConfiguration`;
- `tblSchoolYear`, `tblSchoolTerm`, and `tblSchoolGradeLevel`;
- `tblStudent` and `tblStudentAdultRelationship`;
- `tblSchoolApplication`, `tblSchoolApplicationRequirement`, and
  `tblSchoolApplicationRequirementStatus`;
- `tblStudentEnrollment`;
- `tblSchoolSubject`, `tblSchoolClass`, `tblSchoolClassStaff`, and
  `tblSchoolClassEnrollment`;
- `tblSchoolDay` and `tblStudentSchoolAttendance`;
- `tblStudentHealthSummary`, `tblStudentFormRequirement`, and
  `tblStudentFormStatus`;
- `tblSchoolStaffAssignment` and `tblSchoolSafeguardingQualification`;
- `tblSchoolAccount`, `tblSchoolCharge`, `tblSchoolPayment`,
  `tblSchoolAdjustment`, and `tblSchoolPaymentPlan`;
- `tblSchoolTuitionSchedule`, `tblSchoolDiscount`, and `tblSchoolAidAward`;
  and
- approved audit events in the existing ChurchManager audit system.

Database protections include positive identifiers, foreign keys, stable
School-scoped keys, date-order checks, status checks, same-School validation,
non-overlapping enrollment, unique attendance, immutable posted financial
activity, and indexes for current rosters, daily attendance, qualification
expiration, balances, and reports.

## 18. Screens

The first-release workspace includes:

1. **School Dashboard:** enrollment, today's attendance, missing forms,
   expiring qualifications, account exceptions, and upcoming events.
2. **Students:** searchable current and historical student list.
3. **Student Record:** identity, guardians, emergency/pickup, enrollment,
   classes, attendance, forms, health alerts, and account link.
4. **Admissions:** inquiry-to-enrollment workflow and requirement checklist.
5. **School Years and Classes:** years, terms, grades, classes, teachers, and
   rosters.
6. **Attendance:** efficient roster entry with immediate exception visibility.
7. **Staff and Volunteers:** assignments and safeguarding qualification status.
8. **Tuition and Accounts:** family accounts, charges, payments, plans,
   adjustments, and statements.
9. **School Reports:** approved report catalog with school-specific parameters.
10. **School Settings:** controlled configuration, choices, mappings, and
    installation status.

The ordinary ChurchManager main screen shows only frequent school actions when
the subsystem is enabled. Configuration and sensitive administration remain in
menus and role-appropriate workspaces.

## 19. Starter reports

The initial report inventory includes:

- School Student Directory;
- School Enrollment by Grade;
- School Class Roster;
- School Daily Attendance Sheet;
- School Attendance Summary;
- School Student Attendance History;
- School Emergency Contact and Authorized Pickup List;
- School Missing or Expiring Forms;
- School Safeguarding Qualification Status;
- School Tuition Account Statement;
- School Account Balance and Aging;
- School Enrollment and Tuition Reconciliation;
- School Family Mailing Labels; and
- School Advancement Constituents, without giving amounts unless the current
  user separately holds the required confidential Giving permission.

Reports containing health, custody, pickup, financial, or safeguarding data
are protected and unavailable to unrestricted report customization.

## 20. Import, export, backup, and retention

- Student, guardian, enrollment, class, attendance, and opening account data
  use reviewed preview-first imports with duplicate detection.
- Partial-row acceptance requires an explicit decision and produces a result
  report.
- Sensitive exports require permission, exact scope review, and destination
  confirmation.
- Portable school exchange packages include a manifest, schema version,
  checksums, and counts but no credentials.
- Whole-database backup and restore include school data and receive the same
  verification as ChurchManager data.
- Test-data reset creates only fictional students, guardians, staff, accounts,
  and attendance.
- Retention is controlled by school policy; the first release does not
  automatically delete student history.

## 21. Implementation phases

### Phase 1: administrative complement

- School configuration;
- Students, guardians, emergency contacts, and pickup authorization;
- admissions and enrollment;
- years, grades, classes, staff, and rosters;
- daily attendance;
- form, health-alert, and safeguarding status;
- school documents, events, assets, projects, and reports; and
- school relationship links for Giving.

### Phase 2: tuition and business office

- tuition schedules, fees, discounts, aid, and subsidies;
- family accounts, payment plans, charges, payments, and adjustments;
- statements, aging, and general-ledger reconciliation; and
- reviewed imports from external tuition/payment services.

### Phase 3: demonstrated extensions

Only after user acceptance and demonstrated need:

- basic grading and report cards;
- alumni, campaigns, pledges, and advancement follow-up;
- lunch, library, transportation, athletics, or extended care;
- external SIS exchange; or
- a safely designed parent/teacher portal with 2FA.

## 22. Acceptance criteria

The first release is ready for beta only when:

1. A Person can be a Student, guardian, staff member, volunteer, church member,
   and donor without duplicate Person records or leaked permissions.
2. Guardianship, educational-record access, emergency priority, pickup
   authorization, and financial responsibility are explicit and independently
   testable.
3. Enrollment history survives withdrawal and reenrollment.
4. Class rosters and daily attendance resolve correctly for an effective date.
5. Unauthorized users cannot discover protected health, custody, pickup,
   safeguarding, tuition, or donor information through any interface.
6. Expired mandatory safeguarding qualifications prevent assignment and appear
   in a protected exception report.
7. Tuition activity never creates a charitable contribution, and school gifts
   never silently pay one named family's charges.
8. School account handoff produces balanced privacy-safe accounting entries and
   reconciles to the school subledger.
9. Giving remains confidential and requires separate Giving permissions.
10. Communications include only authorized guardians and require preview and
    confirmation.
11. Imports detect duplicates and invalid relationships before changing data.
12. Backup and restore preserve every school relationship, history, financial
    link, permission, and audit record.
13. Error logs and support bundles contain no protected student narrative or
    financial detail.
14. Automated tests pass, and all school screens and reports receive actual
    Windows visual acceptance.

## 23. Decisions established by this specification

- ChurchManager School is an optional subsystem for small parochial schools.
- It complements ChurchManager but does not make the first release a complete
  SIS or learning-management platform.
- General Person and Family records are reused; school roles and legal
  relationships are explicit normalized records.
- School attendance is separate from worship and Group attendance.
- Tuition and fees are receivables, not charitable giving.
- Advancement uses the confidential Giving subsystem and separate permissions.
- Guardianship, pickup authority, educational access, and financial
  responsibility are never inferred from a Family record.
- The first release emphasizes administration, safety, attendance, tuition,
  and reporting before gradebooks or portals.
- Denominational and religious fields are optional and configurable.
- ChurchManager records administrative facts but does not make legal, medical,
  educational, or tax determinations.

## 24. Research basis

This proposal was informed by current official and open-source descriptions of
FACTS, openSIS, Frappe Education, RosarioSIS, LCMS school administration
guidance, Archdiocese of Milwaukee parish and school policy, National
Association of Independent Schools advancement practices, and United States
Department of Education student-privacy guidance.

The review consistently identified admissions, student/teacher records,
attendance, classes, grades, fees, parent communication, emergency records,
and reporting as core school functions. Parochial guidance additionally
emphasized immunization records, tuition collection, staffing ratios,
safe-environment qualifications, background checks, ethical standards, and
mandatory-reporting awareness. Independent-school advancement sources
confirmed that donor records, gift processing, campaigns, pledges,
acknowledgments, stewardship, and business-office reconciliation are distinct
from tuition administration.

Official references:

- [FACTS school management](https://factsmgt.com/public/)
- [openSIS features](https://opensis.com/features)
- [Frappe Education](https://github.com/frappe/education)
- [RosarioSIS](https://www.rosariosis.org/)
- [LCMS administration job descriptions](https://files.lcms.org/api/file/preview/084D1B3A-6A1F-447A-AED4-8A9E54110527)
- [Archdiocese of Milwaukee Parish and School Policy Manual](https://schools.archmil.org/CentersofExcellence/DOCsPDFs/Schools-Policy-Handbook/ParishandSchoolPolicyManual2023-24.pdf)
- [NAIS independent-school donor research](https://www.nais.org/resource-center/resources/research/nais-research-jobs-to-be-done-study-on-independent-schools-donors/)
- [U.S. Department of Education: FERPA applicability](https://studentprivacy.ed.gov/faq/which-educational-agencies-or-institutions-does-ferpa-apply)
