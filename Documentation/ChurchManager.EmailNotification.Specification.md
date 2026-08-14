# ChurchManager email and participant-notification specification

**Status:** Approved

**Date:** August 14, 2026

**Approved by:** Rev. Jonathan C. Watt

**Target:** Development ChurchManager and JSForm

## 1. Purpose

Replace the legacy immediate-send participant notification with a reviewable,
secure workflow that generates and attaches the current Worship Planning report
for the selected service.

Email remains an explicit user action. ChurchManager never sends a participant
message merely because a service, assignment, report, or user account changes.

## 2. Ownership boundary

JSForm owns reusable mail infrastructure:

- mail-server configuration and validation;
- a provider-neutral message and attachment interface;
- recipient-address normalization;
- duplicate-address removal;
- structured per-recipient delivery results;
- safe exceptions that never expose credentials.

ChurchManager owns ministry and security decisions:

- selecting a worship service;
- determining eligible assigned participants;
- resolving participant contact addresses;
- generating the Worship Planning report;
- composing the default subject and message;
- presenting the complete review screen;
- requiring final confirmation;
- authorization and communication history.

ChurchManager user-account email addresses are not substituted for participant
addresses. Participant/member contact records remain the authoritative source
for this workflow.

## 3. Existing behavior to retire

The current `fnSchedule.notifyviaeMail` workflow:

- assumes `Reports/CMWP01.pdf` is already current;
- sends without a recipient and message review;
- does not show participants with missing email addresses;
- provides no useful delivery summary;
- couples ChurchManager directly to the historical `clsSMTP` implementation.

The menu item may remain named **Notify Participants**, but it will open the new
review screen rather than the old JSON form.

## 4. Notification workflow

1. The user selects a service.
2. ChurchManager loads active, non-declined assigned participants.
3. The screen lists each participant, assignment position, address, and status.
4. Missing and invalid addresses are visibly flagged and excluded from sending.
5. Repeated addresses are combined into one recipient entry and visibly noted.
6. ChurchManager generates a fresh `CMWP01` PDF from the selected service.
7. The screen displays the subject, editable message, and exact attachment.
8. The user previews the PDF if desired.
9. **Send** opens a final confirmation containing the recipient count and
   attachment name.
10. Only after confirmation does the mail service attempt delivery.
11. The result screen reports succeeded and failed recipients without exposing
    credentials.

No eligible recipient means Send is disabled.

## 5. Recipient rules

- Include active participants assigned to the selected service.
- Exclude declined assignments.
- Include confirmed, assigned, and suggested assignments when they represent a
  saved service assignment.
- A participant serving in multiple positions receives one message.
- Shared addresses receive one message.
- Address comparisons are case-insensitive and ignore surrounding whitespace.
- Blank or invalid addresses remain visible in the review as **Missing email**
  or **Invalid email**.
- Recipient addresses use blind-copy or individual delivery so participants do
  not receive one another's addresses.

## 6. Report generation

The attachment must be generated from the selected service immediately before
the review is finalized. It uses the authorized visual-report definition:

1. saved customized `CMWP01` layout, when present;
2. otherwise the protected starter layout.

The generated report must not depend on a prior report-menu run. A generation
failure stops the workflow before sending.

## 7. Message defaults

Default subject:

`Worship Planning - <full service date and time> - <church name>`

Example:

`Worship Planning - Sunday, August 16, 2026 at 9:00 AM - Reformation Lutheran Church`

The full service date and time are required so each service notification begins
a distinct Gmail conversation instead of being attached to an older weekly
planning thread.

Default message:

`You are scheduled to serve in worship. Please review the attached Worship Planning report for details.`

The user may edit the subject and message for this send. Initial implementation
uses plain text. Rich HTML and reusable message templates are later enhancements.

### New-conversation requirement

Every notification send is a newly composed message, not a reply or continuation.
The mail transport must:

- create a fresh RFC message ID;
- omit `In-Reply-To` and `References` headers;
- omit any provider-specific prior thread or conversation ID;
- retain the service-specific full date and time in the subject.

A deliberate resend for the same service may retain the same subject and can be
grouped with the prior attempt. Notifications for different services must have
different subjects.

## 8. Configuration

Mail credentials must not be stored in source, JSON screen definitions, logs,
or support packages. The mail layer shall distinguish:

- sender display name and sender address;
- server/provider settings;
- authentication secret;
- connection security and port;
- optional reply-to address.

The screen must offer **Test Configuration** using a user-entered destination.
Testing is an explicit send and requires confirmation.

The first implementation may preserve compatible existing configuration while
placing access behind the new JSForm interface. Provider-specific OAuth can be
added later without changing ChurchManager's notification service.

## 9. Authorization

- Opening and sending participant notifications requires `worship.manage`.
- Generating the attachment also requires `reports.worship.run`.
- Mail-configuration maintenance requires an administrative configuration
  permission and is not exposed to ordinary planners.
- Authorization is enforced in services, not only by hiding menu controls.

## 10. Communication history

Record one safe history event per send attempt containing:

- service ID;
- acting user ID;
- UTC timestamp;
- subject or a bounded subject summary;
- attachment report code and generated filename;
- recipient count;
- succeeded count;
- failed count;
- overall status.

Do not store SMTP credentials, full message bodies, attachment contents, or a
duplicated list of recipient addresses in audit JSON. Detailed failures belong
in privacy-safe local diagnostics with addresses redacted.

## 11. Failure handling

- Report-generation failure: nothing is sent.
- Configuration failure: nothing is sent and the user receives a specific
  configuration message.
- Partial delivery: successful deliveries are not repeated automatically; the
  results identify failed recipients for a deliberate retry.
- Unexpected Python or provider errors use the centralized error reporter.
- Closing or cancelling the review performs no send.

## 12. Testing

Automated tests must use fakes and perform no real email delivery. Tests cover:

- participant eligibility and declined-assignment exclusion;
- missing and invalid address visibility;
- case-insensitive deduplication;
- multiple roles for one participant;
- fresh report generation before send;
- starter/custom report resolution;
- explicit confirmation and cancel behavior;
- BCC or individual-recipient privacy;
- distinct service subjects and absence of reply/thread headers;
- complete and partial delivery summaries;
- authorization at the service boundary;
- audit content and diagnostic redaction;
- configuration validation without credential disclosure.

Manual acceptance uses fictional recipients and a test mailbox only.

## 13. Delivery stages

1. Add the reusable JSForm mail service and fake-transport tests.
2. Add the ChurchManager recipient and notification service.
3. Add fresh Worship Planning PDF generation without opening it automatically.
4. Replace the old Notify Participants form with the review screen.
5. Add protected configuration maintenance and test-send support.
6. Add safe communication history.
7. Complete test-mode acceptance before any production configuration is used.

## 14. Acceptance criteria

The feature is complete when a permitted user can select a service, see every
eligible or address-deficient assigned participant, generate the current
Worship Planning report, review the message and attachment, explicitly confirm
the send, and receive a clear delivery summary, with no stale-report path,
duplicate exposure, automatic sending, or credential leakage.
