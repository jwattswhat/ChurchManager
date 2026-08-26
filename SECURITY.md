# Security policy

## Supported versions

ChurchManager is currently pre-release. Security fixes are made on the active
development branch; the separately installed frozen legacy program is not
covered by this repository's support policy.

## Reporting a vulnerability

Do not disclose credentials, member records, attendance, pastoral information,
financial data, database dumps, or exploit details in a public issue. Contact
the maintainer privately with the affected version, safe reproduction steps,
impact, and suggested mitigation. Use fictional data and redact support files.

## Operational security

- Use a least-privilege MariaDB account; do not run the application as database
  root.
- Store secrets in Windows Credential Manager, not source or command lines.
- Treat backup files, reports, logs, attachments, and support packages as
  confidential.
- Use roles and permissions for application actions and preserve the audit log.
- Run development only against `ChurchDBTest`.
- Review unlisted contact flags and report-safe views before distributing output.
- Restore operations replace data and require an explicit, informed user action.

Security in the interface is not sufficient by itself. Services must enforce
authorization and database accounts must be limited to the access they require.
