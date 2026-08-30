# ChurchManager Automated GUI Screen Testing Specification

Status: Implemented; manual visual acceptance completed August 30, 2026
Date: August 29, 2026
Framework owner: JSForm
Application integration owner: ChurchManager

Implementation status: reusable JSForm lifecycle, stable-control discovery,
geometry, capture, and PNG-comparison helpers are implemented. ChurchManager's
`gui-structural` suite covers Login, Participant Notifications, Project Plan,
and Asset Editor with fictional injected dependencies. The guarded database and
packaged profiles pass. Manual visual review of all four screens passed August
30, 2026 after the review runner was corrected so it cannot shrink a fitted
dialog. Automated desktop capture remains environment-incompatible, so no
reviewed screenshot baseline or automated visual comparison is claimed.

The visual candidate runner records PPI, display dimensions, platform, locale,
time zone, theme, and approval state in `.gui-test-artifacts`. On the August 29
desktop worker, the canonical 96-PPI profile was present but screen capture
returned uniform black images. A bounded Windows ImageGrab fallback was also
attempted and reported that screen capture is unavailable in this session. The
runner records either condition as `environment-incompatible`, removes unusable
images, and produces no candidate or baseline claim.

The explicit `gui-database` runner validates localhost, `ChurchDBTest`, and the
`ChurchManager/LocalTestAdmin` credential target before connecting. Its first
scenario enters a fictional project through Project Plan, saves through
`ProjectService`, reads the result back, and suppresses repository commits so
the enclosing transaction is rolled back. The August 29 run was skipped before
connection because that protected test credential was not installed.

The explicit `gui-packaged` runner accepts only the current development bundle,
always runs its packaged-resource proof, and uses the pinned test-only
`pywinauto 0.6.9` dependency for native automation. Its scenario logs in with
the protected LocalTestAdmin database credential, creates a temporary fictional
application login, verifies the authenticated main window, exits, and removes
the temporary login. Package proof, login, main-window identity, and clean exit
passed August 29. Projects and Scheduling activation remains pending because
the Projects dashboard entry was converted from mouse-only static text to a
keyboard-focusable native button. Source-level routing and interactive mouse
and keyboard checks pass. The unattended packaged profile now focuses that
button by its stable accessible name, presses Enter, detects the resulting wx
dialog through the native Win32 window tree, closes it, exits, and removes its
temporary fictional login. Manual visual acceptance passed August 30, 2026. No
Frozen application path is accepted.

Following that milestone, every visible main-dashboard action was converted to
the same native-button treatment for visual and keyboard consistency. The
columns and buttons were then reduced by about one-third, using **Contributors
and Envelopes** as the longest-label visual constraint. The compact dashboard
passed renewed human visual acceptance on August 30, 2026.
The rebuilt beta.2 bundle was then inspected for the embedded `52x40`,
32-button definition and passed unattended packaged login, accessible Projects
activation, child-window detection, cleanup, and exit against that exact build.

## 1. Purpose

Add repeatable automated testing for ChurchManager's wxPython screens so common
construction, interaction, layout, permission, and packaged-application
regressions are detected before release. Automated GUI evidence supplements the
existing logic and service tests and makes visual review more focused; it does
not replace human visual acceptance.

The first implementation covers login and three high-value ChurchManager
screens selected during implementation according to usage, data sensitivity,
and regression risk. The harness must support incremental coverage without
requiring every screen to be automated at once.

## 2. Goals

1. Detect screens that fail to construct, show, close, or release owned child
   windows correctly.
2. Verify essential controls, labels, initial values, enabled states, focus
   order, validation, and Save/Cancel behavior.
3. Detect visible clipping, overlap, unexpected movement, missing controls, and
   other stable layout changes through reviewed screenshot comparisons.
4. Exercise a small set of critical workflows against the packaged Windows
   application using stable control identities.
5. Produce useful failure evidence: scenario, screen, action, exception,
   screenshot, and visual difference image where applicable.
6. Preserve strict separation among unit tests, GUI integration tests, packaged
   smoke tests, and human visual acceptance in documentation and release claims.

## 3. Non-goals

- replacing service, repository, validation, security, or database tests with
  slower GUI tests;
- testing every permutation of every screen through the native interface;
- using production or congregation data;
- accessing or testing the separate Frozen ChurchManager application;
- asserting exact operating-system rendering across unrelated Windows versions,
  display scales, fonts, themes, or graphics drivers;
- treating a successful screenshot comparison as human visual acceptance;
- automating visual designers by relying on unstable pixel coordinates where a
  model-level or control-level test is available.

## 4. Ownership boundary

JSForm owns reusable framework-neutral test helpers for wx application lifetime,
event-loop draining, tracked-window cleanup, control discovery, synthetic wx
events, safe screenshot capture, geometry inspection, and deterministic test
diagnostics. JSForm tests those helpers with framework fixtures and does not
open a ChurchManager database.

ChurchManager owns application screen fixtures, guarded configuration,
fictional records, permission personas, screen-specific assertions, screenshot
baselines, packaged-application scenarios, roadmap status, and release evidence.
ChurchManager may use JSForm helpers but must not weaken the framework's normal
authorization or persistence boundaries for testing.

## 5. Test levels

### 5.1 Screen-construction tests

These are the default and fastest GUI tests. Each test creates the wx
application when needed, constructs one frame or dialog with controlled
dependencies, allows pending wx events to finish, verifies its contract, and
destroys all windows it owns.

Construction tests may verify:

- expected frame or dialog title and minimum usable size;
- required controls and unique stable names;
- user-facing labels, tooltips, choices, and default selections;
- visible, hidden, enabled, disabled, required, or read-only states;
- tab traversal and initial focus where the workflow depends on them;
- controls remaining within the client area and above minimum dimensions;
- absence of unintended modal prompts during construction and cleanup;
- cleanup of timers, child windows, and registered application resources.

Tests must prefer public screen contracts and stable control names over private
implementation details or source-text inspection.

### 5.2 Interaction tests

Interaction tests drive the in-process wx screen through control APIs, posted
events, or `wx.UIActionSimulator` where it is reliable. They cover representative
user behavior rather than every service-layer rule.

Required interaction categories are:

- text entry and choice selection;
- validation and understandable error presentation;
- Save applying the expected guarded change exactly once;
- Cancel and window close making no change;
- keyboard traversal and activation of the primary and cancel actions;
- permission-dependent visibility and denial at the action boundary;
- safe handling of an injected service or database failure.

Save assertions must verify the underlying result through an application
service, repository, or isolated test-database readback. A button click alone is
not evidence that persistence succeeded.

### 5.3 Visual-regression tests

Visual-regression tests render a populated, stable screen in a controlled
Windows display profile and compare the captured client area with a reviewed
baseline image. Each scenario uses deterministic fictional data, window size,
theme, fonts, locale, display scale, and animation state.

The comparison process must:

1. wait until the screen is laid out and the wx event queue is idle;
2. capture only the intended application window or client area;
3. mask explicitly approved volatile regions such as a generated timestamp;
4. compare dimensions before comparing pixels;
5. apply a documented small tolerance for rendering noise, not for structural
   changes;
6. save the actual image, expected image, and highlighted difference image when
   a comparison fails; and
7. return a failing test result until a reviewer either corrects the regression
   or deliberately approves a new baseline.

Baseline images are version-controlled test evidence. A baseline update must be
reviewed as a visible product change and must not be generated and accepted by
the same unattended test step.

### 5.4 Packaged-application smoke tests

A small Windows-only suite launches the current ChurchManager package and
drives representative workflows through native UI automation. It verifies the
installed or bundled entry point, not the separate Frozen application.

Packaged smoke tests must use accessibility or native-window properties and
stable control identifiers when available. A Windows UI Automation library such
as `pywinauto` is preferred for this layer; adding it requires a pinned,
test-only dependency and dependency review during implementation. Existing
PyAutoGUI support may be used for bounded screenshot capture or as a documented
last resort, but coordinate-only click sequences are not an accepted primary
strategy.

The initial packaged suite verifies:

- application launch and visible product identity;
- guarded test-account login;
- opening one selected high-value screen;
- one read-only or reversible interaction; and
- clean application exit without an unexpected dialog or orphaned process.

## 6. Stable control identity

Controls included in automated workflows must expose a unique, meaningful,
stable identity through their wx name or the strongest available native
automation property. Tests must not depend on creation order, translated label
text, or screen coordinates when a stable identity can be supplied.

Adding a stable control name is an interface improvement, not permission to
change the user-visible label. Duplicate identities within one window are a test
failure. JSForm-generated controls use their definition names where those names
are already unique and safe.

## 7. Harness lifecycle and isolation

The harness must provide one controlled wx application per compatible test
process and must leave no top-level windows behind after each test. It must:

- construct screens on the GUI thread;
- process pending events with a bounded timeout;
- detect and report unexpected modal dialogs;
- close or destroy owned windows in child-before-parent order;
- restore patched services, environment values, and application state;
- fail clearly on a hang instead of waiting indefinitely; and
- keep tests independent so their result does not depend on execution order.

GUI tests that cannot safely share a process are isolated in a subprocess. A
failure in one screen must not prevent the remaining screen results and evidence
from being reported.

## 8. Data, configuration, and security boundary

All GUI tests use fictional data and the guarded ChurchManager development/test
database configuration. Tests must never infer a database target from the
currently signed-in Windows user, a production configuration file, or a nearby
application installation.

Before any test capable of writing data, the existing test-target guard must
verify the configured server, database, and user. Destructive scenario setup is
limited to the approved disposable test database and uses the existing reset or
seed services where available.

Automated GUI testing must never read, launch, import from, synchronize with, or
modify `C:\Users\Pastor\Documents\ChurchManager-Legacy`, its runtime, JSForm
copy, forms, configuration, credentials, or production database. The Frozen
application is not a compatibility target and receives no test adapters,
migration path, or shared fixtures.

Screens involving confidential giving, pastoral, credential, or personal data
use synthetic values. Failure screenshots and logs must pass through the
existing diagnostic-redaction boundary and must not disclose secrets, hashes,
connection strings, protected notes, or unnecessary personal information.

## 9. Environment profiles

The test runner exposes explicit profiles so results cannot be overstated:

| Profile | Purpose | Expected availability |
|---|---|---|
| `gui-structural` | Construction, geometry, control-state, and interaction tests that do not need a live test database | Normal source test environment with wxPython |
| `gui-database` | Guarded interaction and persistence scenarios using fictional test data | Approved local test database only |
| `gui-visual` | Screenshot comparisons under the canonical display profile | Controlled interactive Windows worker |
| `gui-packaged` | Native automation against the current package | Explicit Windows package-acceptance run |

The canonical visual profile initially uses Windows at 100 percent display
scaling, the repository-approved application theme and fonts, a fixed locale and
time zone, and a documented screen work area. The implementation records the
actual profile in each result bundle and skips with a clear reason when the
required profile is unavailable. It must not silently compare incompatible
rendering environments.

## 10. Selection of initial screens

Login is mandatory because it establishes application identity and the guarded
test-account boundary. The other three initial screens are chosen and recorded
in the implementation plan using these factors:

1. frequency and importance of congregational use;
2. confidentiality or authorization risk;
3. persistence or workflow complexity;
4. history of layout or lifecycle regressions; and
5. representative coverage of JSForm-generated and application-owned UI.

At least one initial screen must exercise a guarded save, one must exercise a
permission-dependent state, and one must exercise a nontrivial resizable layout.

## 11. Result artifacts and reporting

Each failing GUI scenario reports the screen and scenario identity, test
profile, display metadata, last completed action, exception or assertion, and
paths to any screenshots or difference images. Machine-readable summary data
must distinguish passed, failed, skipped, timed out, and environment-incompatible
results.

Generated results go to an ignored test-artifact directory. Approved visual
baselines live in a documented version-controlled location. Reports and release
notes must use precise claims such as "structural GUI suite passed" or "visual
baselines compared under the canonical profile" rather than the broader phrase
"visually accepted" unless a person actually inspected the rendered screens.

## 12. Test-runner and release integration

The normal safe ChurchManager suite includes deterministic `gui-structural`
tests that can run in its supported wxPython environment. Database, visual, and
packaged profiles remain explicit because they require guarded resources or a
controlled interactive Windows session.

Release readiness records each profile separately. A skipped visual or packaged
profile does not fail unrelated source tests, but it remains an unmet release
gate whenever the release checklist requires that profile. Focused GUI success
must never be reported as completion of the full ChurchManager or JSForm suite.

## 13. Documentation and maintenance

Implementation must update, as applicable:

- the developer test guide and safe test runner usage;
- requirements for any pinned test-only automation or image-comparison tool;
- the screen inventory with stable automation identities;
- release-readiness and packaging acceptance documentation;
- JSForm documentation for reusable harness interfaces; and
- this specification and the roadmap when coverage or acceptance status
  changes.

New public test-harness interfaces require useful contract docstrings. Tests and
documentation change in the same commit as behavior. A visible screen change
must update its assertions and, after review, its baseline when appropriate.

## 14. Acceptance criteria

1. The reusable harness creates, exercises, and destroys screens without leaked
   top-level windows, timers, or unexpected modal dialogs.
2. Login and three approved high-value screens have construction tests covering
   essential controls, states, sizing, and cleanup.
3. The initial interaction set covers typing or selection, validation, Save,
   Cancel, keyboard behavior, permission denial, and one injected failure.
4. A guarded save is verified through service, repository, or isolated
   test-database readback, and Cancel produces no persisted change.
5. Visual scenarios compare successfully under the canonical display profile;
   an intentional layout change produces reviewable expected, actual, and
   difference images.
6. An unattended test cannot silently approve or overwrite a visual baseline.
7. The packaged smoke suite launches the current package, uses a guarded test
   account, opens an approved screen, completes a safe interaction, and exits
   cleanly using stable control identities.
8. Database-target guards reject production, unknown, and Frozen-application
   configurations before a write-capable test begins.
9. GUI artifacts and logs contain no credentials, protected notes, or real
   congregation data.
10. The safe ChurchManager suite and affected JSForm suite pass, with visual,
    database, and packaged profile results reported separately.
11. The developer documentation explains how to run each profile, review a
    visual difference, and deliberately approve a baseline change.
12. Human visual acceptance remains separately recorded for any release or
    feature that requires it.

## 15. Deferred work

- broad automation of every ChurchManager screen and every report parameter
  dialog;
- multi-monitor and multiple-display-scale comparison matrices;
- automated compatibility claims across every supported Windows release;
- performance benchmarking based on pixel timing or animation timing;
- unattended baseline approval;
- remote desktop, browser, or member-portal testing, which requires its own
  approved architecture and security specification; and
- any compatibility testing, migration support, or shared harness for the
  separate Frozen ChurchManager application.
