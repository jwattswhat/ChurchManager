# ChurchManager secure SMTP connection specification

**Status:** Approved

**Version:** 1.0

**Date:** August 16, 2026

**Approved by:** Rev. Jonathan C. Watt

**Target:** Development ChurchManager and JSForm

## 1. Purpose

Provide one secure, understandable email connection for all ChurchManager email
workflows. The first supported transport is standards-based SMTP, including
Gmail with an app password when permitted by the sender account. The design must
allow a future OAuth or provider-specific transport without changing ministry
workflows.

Email delivery remains optional. ChurchManager must work normally when email is
not configured.

## 2. Ownership boundary

### JSForm owns

- provider-neutral mail settings, messages, attachments, transports, and
  structured delivery results;
- SMTP connection, authentication, TLS, timeout, and safe exception handling;
- address and nonsecret configuration validation;
- fresh RFC message construction without reply/thread headers;
- reusable credential-store access by an opaque credential target name;
- fake transports and framework-level tests that never send real email.

### ChurchManager owns

- the protected Email Settings screen and menu permission;
- separate test and production setting identities;
- choosing sender identity and the credential target;
- explicit Test Configuration confirmation and destination;
- deciding which ministry or security workflow may send;
- authorization, safe audit events, and user-facing results;
- redaction from diagnostics and support packages.

The historical `clsSMTP` facade is not used by new ChurchManager workflows.

## 3. Configuration model

ChurchManager stores only nonsecret mail settings in its active database:

| Setting | Purpose |
| --- | --- |
| `Enabled` | Whether real delivery is available in this environment |
| `Provider` | Descriptive provider such as Gmail, Microsoft 365, or Other SMTP |
| `Server` | SMTP hostname |
| `Port` | SMTP TCP port |
| `Security` | `STARTTLS` or `SSL/TLS` |
| `UserName` | Provider login name; normally an email address |
| `SenderAddress` | Address placed in the From header |
| `SenderName` | Congregation or staff display name |
| `ReplyTo` | Optional reply-to address |
| `CredentialTarget` | Opaque name used to retrieve the secret securely |
| `TimeoutSeconds` | Bounded connection timeout, default 30 seconds |

No default Gmail server should make an unconfigured installation appear ready.
An incomplete configuration is disabled and reports the exact missing
nonsecret fields.

The password, app password, or token is stored in Windows Credential Manager,
never in `tblConfig`, `jsConfig`, source, JSON, logs, audit JSON, support
packages, or command-line arguments.

Credential targets must distinguish:

- the ChurchManager application;
- test versus production database/environment; and
- the configured sender account.

## 4. Connection security

- Normal ChurchManager delivery requires STARTTLS or implicit SSL/TLS.
- Plain unencrypted SMTP is prohibited.
- Certificate verification uses the operating system/Python trusted certificate
  store and may not be disabled through the screen.
- STARTTLS must be established before authentication.
- Network operations use the configured bounded timeout.
- Authentication secrets are held only as long as required to establish the
  connection and are never included in exception text.
- A future local development mail catcher requires a separate development-only
  override that cannot be enabled for production.

## 5. Email Settings screen

Add **Email Settings** to ChurchManager Settings. Opening or changing it requires
`application.config.manage` at the service boundary.

The screen contains:

- enabled status and provider;
- server, port, and security mode;
- username, sender address/name, and optional reply-to;
- credential status shown only as **Stored** or **Not stored**;
- **Store/Replace Credential** and **Remove Credential**;
- **Validate Settings**;
- **Send Test Email**; and
- last successful test time and safe result summary.

The secret is entered in a password control, confirmed when replacing it, sent
directly to the credential store, and then discarded. It is never read back for
display.

Changing sender, server, username, security mode, port, or credential target
clears the prior successful-test status.

## 6. Validation without sending

**Validate Settings** performs no network connection and sends no email. It
checks:

- all enabled required settings are present;
- port and timeout are in approved ranges;
- sender, username when email-shaped, and reply-to are valid;
- the selected TLS mode is approved;
- the credential target is well formed; and
- a credential exists when authentication is configured.

The result must explicitly say that validation did not verify provider login or
message delivery.

## 7. Test Configuration workflow

1. The administrator selects **Send Test Email**.
2. ChurchManager validates the saved nonsecret configuration and credential
   availability.
3. The administrator enters a destination address they control.
4. A confirmation displays the sender address, destination, provider/server,
   port, and TLS mode. It never displays the secret.
5. Only **Send Test** opens the connection and sends one plain-text test message.
6. The message identifies ChurchManager, the environment, sender, and test time;
   it contains no congregation or member data.
7. Success or failure is shown clearly. Provider details are reduced to a safe,
   actionable category.

Cancelling any step sends nothing. Saving settings, starting ChurchManager,
creating a user, or closing ChurchManager never triggers a test.

## 8. Gmail and provider compatibility

For Gmail SMTP, the initial documented configuration is:

- server `smtp.gmail.com`;
- port 587 with STARTTLS, or port 465 with SSL/TLS;
- the full sender email address as username; and
- a Google app password when the account and Google policy allow it.

ChurchManager must not request or store the user's ordinary Google password.
Google OAuth may replace app-password authentication later behind the same
JSForm mail-transport contract.

Other providers remain supported through explicit SMTP settings. ChurchManager
does not guess undocumented provider settings.

## 9. Delivery behavior

- Welcome messages and participant notifications use the same configured mail
  factory.
- Every send remains an explicit, confirmed workflow action.
- Recipient addresses are validated and deduplicated case-insensitively.
- Messages are delivered individually so recipients do not see one another.
- Each message receives a new message ID and no `In-Reply-To`, `References`, or
  prior provider thread identifier.
- Partial delivery returns a result per recipient. Successful recipients are not
  retried automatically.
- Disabled or invalid mail configuration prevents sending without affecting the
  underlying user, service, report, or participant records.

## 10. Auditing, diagnostics, and privacy

Safe audit events include:

- `MAIL_SETTINGS_UPDATED`;
- `MAIL_CREDENTIAL_STORED`;
- `MAIL_CREDENTIAL_REMOVED`;
- `MAIL_TEST_SUCCEEDED`; and
- `MAIL_TEST_FAILED`.

Events identify the acting user, environment, action, time, and safe outcome.
They do not include usernames, passwords, credential targets, recipient
addresses, message bodies, raw provider responses, or attachment content.

Central diagnostics may record a redacted error category and correlation ID.
Support packages must redact SMTP usernames, sender/recipient addresses,
credential targets, authentication material, and provider response text that
could expose account details.

## 11. Exposed-credential response

Any credential found in source or development artifacts is treated as exposed:

1. revoke or replace it at the provider;
2. remove it from the working tree;
3. assess whether repository history or backups require cleanup;
4. store the replacement only in Windows Credential Manager; and
5. verify the replacement through the explicit test workflow.

No automated cleanup may claim the provider credential was revoked; provider
revocation requires confirmation from the account owner.

## 12. Migration and compatibility

- Add any new nonsecret configuration records through a guarded numbered
  ChurchDB migration.
- Never migrate an existing plaintext SMTP password into another database
  field.
- An administrator may explicitly move the existing secret into Windows
  Credential Manager, after which the plaintext configuration value is cleared.
- Test and production values are handled independently.
- Existing notification and welcome-email services change only their mail
  factory; their recipient and authorization rules remain intact.

## 13. Automated testing

Tests must not contact a real provider. They cover:

1. complete and incomplete setting validation;
2. rejection of plain SMTP, invalid ports, addresses, and timeouts;
3. secure credential target separation for test and production;
4. missing, stored, replaced, and removed credential states;
5. permission enforcement on view, update, credential, and test operations;
6. explicit test confirmation and cancellation;
7. fake success, authentication failure, TLS failure, timeout, and partial
   delivery;
8. fresh message IDs and absent thread headers;
9. individual recipient delivery and deduplication;
10. safe audit and diagnostic redaction;
11. welcome and participant workflows using the same mail factory; and
12. absence of hard-coded or database-stored mail secrets in active source and
    configuration fixtures.

## 14. Manual acceptance

Manual acceptance occurs only in `ChurchDBTest` with a mailbox controlled by the
tester:

1. save nonsecret settings;
2. securely store the test credential;
3. validate without sending;
4. send and receive one explicit test message;
5. send a welcome message to the test mailbox;
6. send a fictional participant notification to the test mailbox;
7. confirm no unrelated send occurs;
8. inspect audits and diagnostics for redaction; and
9. remove or disable the test configuration if it is not intended for continued
   use.

Production mail configuration requires a separate deliberate setup and test.

## 15. Completion criteria

The SMTP connection work is complete when the credential is outside the
database and source tree, the protected settings and explicit test workflows
are operational, TLS and environment separation are enforced, all email
workflows use the shared factory, automated tests pass, and the product owner
approves a controlled test delivery.
