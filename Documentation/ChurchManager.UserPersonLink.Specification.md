# ChurchManager user-to-person link and welcome email specification

**Status:** Implemented in source; awaiting database migration and user acceptance

**Date:** August 16, 2026

**Target application:** Development ChurchManager

## 1. Purpose

ChurchManager may optionally associate an application user with one
congregation person. The relationship identifies the same human in two distinct
contexts without making membership a requirement for application access.

The same administration workflow may send a password-free welcome email after
an account is created or later on request.

## 2. Identity boundaries

- `tblUser` remains the authoritative login, authorization, and audit identity.
- `tblPerson` remains the congregation person and directory record.
- `tblParticipant` remains a separate worship-participant identity and may or
  may not link to a person.
- A user may remain unlinked because bookkeepers, auditors, volunteers, and
  support personnel are not necessarily congregation members.
- Linking never copies or synchronizes display name, email, phone, membership,
  family, participant, or directory data.

## 3. Database contract

Migration 070 adds nullable `tblUser.PersonID` with:

- a unique constraint so one person cannot represent more than one login;
- a foreign key to `tblPerson.ID`; and
- `ON DELETE SET NULL` so deleting a person never deletes or disables a user.

The guarded migration rejects preexisting duplicate or orphaned values before
adding its constraints.

## 4. User Administration

User Administration displays the linked person and provides an optional person
selector when creating or editing a user. Only people not already linked to a
different account are offered. The current link remains available while that
user is edited.

When a person is selected while creating a new user, Display name defaults to
that person's first name. The administrator may edit the proposed display name
before saving. Selecting or changing a link while editing an existing user does
not silently rename that established account.

Changing or removing a link is atomic with the user-detail update. The service
rechecks that the selected person still exists and is still available before
committing.

## 5. Welcome email

Welcome email is an explicit administrator action. It uses the shared
ChurchManager mail service and includes:

- the user's login name;
- instructions to open ChurchManager;
- notice that the temporary password must be changed at first login; and
- instructions to obtain the temporary password through a separate channel.

The temporary password is never placed in the email, audit event, error log, or
mail history. A delivery failure does not remove or disable the account and can
be retried with **Send Welcome**.

## 6. Auditing and privacy

- Contact changes continue to write `USER_CONTACT_UPDATED` with changed field
  names only.
- Link and unlink operations write `USER_PERSON_LINK_CHANGED` with only the
  linked/unlinked state, not the person ID or personal details.
- Welcome delivery writes `USER_WELCOME_EMAIL_SENT` or
  `USER_WELCOME_EMAIL_FAILED` without the email address, username, or password.

## 7. Acceptance criteria

1. Migration 070 applies successfully to `ChurchDBTest`.
2. Existing users remain valid and unlinked by default.
3. An administrator can create, change, and remove an optional person link.
4. A person already linked to another user cannot be selected or saved.
5. Removing a linked person record clears the link without changing the user.
6. Welcome email contains instructions and username but no password.
7. Failed welcome delivery leaves the account available and reports a useful
   retry message.
8. Automated security, migration, documentation, and application tests pass.
9. The User Administration screen is visually approved by the product owner.
