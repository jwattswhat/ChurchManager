# ChurchManager SMTP connection review

**Status:** Reviewed; remediation is an immediate roadmap item

**Date:** August 16, 2026

## 1. Current connection path

ChurchManager participant notifications and user welcome messages call
`configured_mail_service()` in `participant_notifications.py`. That adapter reads
the `SMTP` configuration family and constructs the provider-neutral JSForm
`MailSettings`, `SMTPTransport`, and `MailService` objects.

JSForm currently supports SMTP over implicit TLS or STARTTLS, validates the
sender and reply-to addresses, sends each recipient separately, creates a fresh
message ID, and converts provider/network failures into a credential-free
delivery message.

Automated tests use fake delivery and do not send real email.

## 2. Gaps found

1. The SMTP password is still read from ordinary `tblConfig`/`jsConfig` data.
   It should instead be retrieved from Windows Credential Manager or a future
   provider token store.
2. There is no protected ChurchManager mail-settings screen.
3. The approved **Test Configuration** workflow has not been implemented.
4. The current adapter supplies Gmail-oriented defaults even when no provider
   has been deliberately configured. Missing configuration should fail clearly
   rather than implying that Gmail is ready.
5. JSForm permits unencrypted plain SMTP. ChurchManager should require TLS,
   except for an explicitly authorized local development mail catcher.
6. The historical JSForm `clsSMTP` facade and old scheduling email code remain
   available and should be proven unused by ChurchManager before retirement.
7. A development test file in the JSForm tree contains what appears to be a
   hard-coded mail credential. That credential must be treated as exposed,
   revoked at the provider, and removed from source and history.
8. Mail configuration and delivery diagnostics need explicit redaction tests
   for usernames, passwords, recipient addresses, and provider responses.

## 3. Recommended design

- Keep nonsecret settings in application configuration: provider name, server,
  port, TLS mode, sender address, sender name, reply-to, and credential key.
- Store the authentication secret in Windows Credential Manager under separate
  test and production targets.
- Add a protected **Email Settings** screen requiring
  `application.config.manage`.
- Add **Test Configuration**. The administrator enters a destination, reviews
  the exact sender and security mode, confirms the explicit test send, and sees
  a safe result.
- Provide a **Validate Without Sending** action for field and credential-store
  checks. It must not claim that provider authentication or delivery works.
- Require STARTTLS or implicit TLS in normal ChurchManager use.
- Make test and production mail credentials and sender identities independent.
- Keep actual sending explicit; startup, account creation, saving, and closing
  ChurchManager must never silently send email.
- Retain SMTP as the initial transport while leaving the JSForm interface open
  to OAuth/provider transports later.

## 4. Acceptance criteria

1. No mail secret is stored in source, JSON, database configuration, logs,
   support packages, or command-line arguments.
2. Any exposed development credential has been revoked and removed.
3. An authorized administrator can maintain nonsecret mail settings and store or
   replace the secret securely.
4. Missing configuration gives a precise, nonsecret explanation.
5. Test Configuration sends only after explicit confirmation to a user-entered
   test address.
6. Test and production configurations cannot be confused.
7. Welcome and participant messages use the same reviewed mail factory.
8. Fake-transport, redaction, permission, TLS, and configuration tests pass.
9. Manual acceptance is performed only with a mailbox controlled by the tester.
