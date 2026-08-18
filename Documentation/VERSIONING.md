# ChurchManager versioning

ChurchManager uses semantic versioning and has one authoritative version in
`churchmanager_version.py`. The current installation-readiness development
first beta baseline is `0.2.0-beta.1`.

- Patch versions identify compatible bug fixes.
- Minor versions identify completed compatible features.
- Major versions identify incompatible application or database changes.
- The `-dev` suffix remains until a supported release is prepared.

The main-window title, command description, diagnostic logs, Support and
Diagnostics screen, and support packages must all read this authoritative
value. Database migration numbers are independent of the application version.

ChurchManager and JSForm are versioned independently. A ChurchManager release
must be tested against the JSForm version it ships with.
