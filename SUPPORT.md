# Support

For a support request, include:

- ChurchManager and JSForm versions;
- the screen or report name;
- concise steps to reproduce;
- expected and actual behavior;
- whether the problem occurs in `ChurchDBTest`; and
- a redacted diagnostics package when available.

Use **Support Diagnostics** in ChurchManager to review and export technical
information. Remove personal, attendance, pastoral, financial, and credential
data before sharing. Never send a database password. Python tracebacks are
useful and are captured by the diagnostic system when possible.

Before reporting, restart after a database restore, confirm only one application
instance is running, apply pending test migrations when instructed, and run
`python run_churchmanager_tests.py`.
