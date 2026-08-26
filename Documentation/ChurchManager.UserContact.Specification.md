# ChurchManager user contact information specification

**Status:** Approved

**Date:** August 14, 2026

**Approved by:** Rev. Jonathan C. Watt

**Target application:** Development ChurchManager

## 1. Purpose

Add an optional email address and phone number to each ChurchManager user
account. These values support administrative contact and future notification
workflows. They identify how to contact the person who operates ChurchManager;
they are not congregation membership records.

## 2. Ownership and separation

- Contact information belongs to `tblUser` because it describes an application
  account.
- It remains separate from `tblPerson`, `tblPersonContact`, participants,
  families, and directory records.
- No automatic link or synchronization with a member record will be created.
- A later explicit optional link may identify the corresponding person without
  changing ownership or synchronizing either record.
- A person may have a ChurchManager account without being a congregation member.
- Deleting, changing, or unlisting a member contact must not silently change an
  application user's contact information, or the reverse.

## 3. Database changes

Migration 063 will add:

```sql
Email varchar(254) NULL
Phone varchar(50) NULL
```

Both fields are optional and existing accounts receive `NULL`. Neither field is
unique because small congregations may legitimately share a church office email
address or telephone number.

The fields do not contain authentication secrets and must never be used to
identify the logged-in session. Username and user ID remain authoritative.

## 4. Validation and normalization

### Email

- Optional; blank input is stored as `NULL`.
- Trim leading and trailing whitespace.
- Maximum length is 254 characters.
- Require one `@`, a nonblank local part, and a domain containing no whitespace.
- Preserve the entered address for display; comparisons and duplicate warnings
  may be case-insensitive.
- Do not attempt network verification while saving a user.

### Phone

- Optional; blank input is stored as `NULL`.
- Trim leading and trailing whitespace and collapse accidental repeated spaces.
- Maximum length is 50 characters.
- Permit digits, spaces, parentheses, plus, hyphen, period, and common extension
  forms such as `ext. 12` or `x12`.
- Preserve readable formatting rather than storing digits only.
- Require at least four digits when a value is supplied.

Validation belongs to ChurchManager's user-administration service so it is
enforced even when the screen is bypassed.

## 5. Authorization

- Viewing or editing other users' contact information requires
  `security.users.manage` in the first release.
- User Administration already rechecks this permission at its operation
  boundary; menu visibility alone is insufficient.
- A later self-service contact screen may be considered separately. It is not
  included now.
- Contact information must not appear on the main menu or login screen.

## 6. User Administration changes

The user grid will include:

- Username
- Display name
- Email
- Phone
- Active
- Master
- Roles

The dialog may widen modestly but must remain fully visible on an ordinary
desktop screen.

**New User** will request username, display name, email, phone, temporary
password, and password confirmation. Email and phone remain optional.

Add **Edit Contact** for the selected user. It edits display name, email, and
phone in one compact dialog. Username is shown read-only because changing login
identity is a separate security operation.

Double-click continues to open role assignment unless later user testing
prefers a general user editor.

## 7. Service operations

`UserAdministrationService` will:

- include email and phone in `list_users`;
- accept optional email and phone in `create_user`;
- provide `update_contact(user_id, display_name, email, phone)`;
- validate and normalize all three values before database writes;
- lock or reread the selected user before updating;
- commit the user update and security audit event together;
- roll back both on failure.

The update must reject a missing user and a blank display name.

## 8. Auditing and error logging

- Creating a user continues to write `USER_CREATED`.
- Changing contact information writes `USER_CONTACT_UPDATED`.
- The audit record identifies the acting user and target user.
- Audit before/after values record only which fields changed, not the email
  address or phone number themselves.
- Email addresses and phone numbers must not be added to diagnostic error
  context or support packages.
- Validation errors are ordinary user messages, not unexpected-error logs.

## 9. Future email integration

The later email-system review may use an active user's email address only when
that workflow explicitly selects or identifies the user as a recipient.

- Merely storing an email address never subscribes the user to messages.
- Missing addresses must be shown before sending.
- Shared email addresses must be deduplicated for a single message.
- Delivery history must not copy credentials or unnecessary message content.
- Participant notifications continue to use participant/member contact sources;
  they must not substitute a similarly named ChurchManager user's address.

## 10. Testing requirements

Automated tests shall verify:

1. migration 063 adds nullable fields with the specified lengths;
2. existing users remain valid with both fields null;
3. new users can be created with or without contact information;
4. blank values normalize to null;
5. valid formatted phone numbers and ordinary email addresses are preserved;
6. malformed and overlength values are rejected before database access;
7. shared email addresses are permitted;
8. updating contact information commits atomically and audits the changed field
   names without storing their values;
9. unauthorized users cannot view or modify the administration screen;
10. contact values do not appear in diagnostic logs or support packages;
11. the updated dialog fits and its fields are fully visible;
12. existing security and ChurchManager suites continue to pass.

## 11. Acceptance criteria

The feature is complete when:

1. An administrator can create a user with optional email and phone values.
2. An administrator can edit a selected user's display name, email, and phone.
3. The user grid displays the saved values clearly.
4. Existing accounts work without contact information.
5. Contact data is not linked automatically to congregation member records.
6. Validation and permission checks occur in the service layer.
7. Audit and diagnostic records contain no contact values.
8. Automated tests pass and the user approves the updated screen.

## 13. Implemented identity extension

Migration 070 and the
[user-to-person link and welcome email specification](ChurchManager.UserPersonLink.Specification.md)
add an explicit optional Linked Person selector. This does not change the
approved contact-data boundary: user email and phone remain independent from
all congregation contact records.

The administration action is now labeled **Edit Details** because it edits the
display name, contact fields, and optional person link. The grid also displays
the linked person, and **Send Welcome** sends password-free account instructions.

## 12. Implementation sequence

1. Approve this specification.
2. Add guarded migration 063.
3. Extend the service model, validation, create, list, and update operations.
4. Update New User and User Administration dialogs.
5. Add focused security, validation, audit, and privacy tests.
6. Apply migration to ChurchDBTest.
7. Complete user acceptance before beginning the email-system review.
