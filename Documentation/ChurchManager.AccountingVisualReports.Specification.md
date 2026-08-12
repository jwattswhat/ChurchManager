# ChurchManager Accounting Visual Reports Specification

Status: Proposed for approval  
Date: August 12, 2026  
Scope: Printed and PDF accounting reports in the new JSForm visual reporting system

## 1. Objective

Replace the accounting module's screen-only and one-off printable outputs with secure, consistent, user-adjustable visual reports. Existing accounting services remain authoritative for calculations and validation. Report definitions control presentation only; they must not contain SQL, credentials, formulas that alter accounting meaning, or permission rules.

The integration must preserve the small-congregation workflow: one authorized accounting user may run ordinary reports, while higher-risk close, audit, reversal, and approval information remains separately protected.

## 2. Architectural boundary

### JSForm owns

- Report-definition schema, loading, validation, saving, version recovery, and starter restoration.
- Visual canvas, bands, tables, repeaters, groups, totals, alignment, distribution, page setup, and preview.
- Generic PDF pagination, repeating headings, page numbers, run metadata, empty-result output, native date/time/currency formatting, and print-safe layout.
- Generic protected-control support described in section 7.
- Generic matrix/cross-tab support described in section 7.
- Dataset contracts that allow only explicitly approved collections and fields.

### ChurchManager owns

- Accounting permissions and authorization checks.
- Selection dialogs and valid parameters.
- Accounting calculations, signs, classifications, balancing checks, and close-readiness rules.
- Secure dataset providers that adapt existing service results into approved report contracts.
- Official accounting starter definitions, titles, terminology, standard headers, and required footnotes.
- The distinction between ordinary financial reports, transaction support, audit records, and close-control documents.

## 3. Security model

All accounting report data is sensitive. Every dataset provider must recheck authorization before reading the database or invoking a service.

| Report class | Required permission |
|---|---|
| Formal statements, ledgers, budgets, fund reports, reconciliations, and close checklist | `accounting.reports.run` |
| Posted transaction register and journal-entry report | `accounting.transactions.view` |
| Accounting audit history | `accounting.audit.view` |
| Year-end close preview and close/reopen proof | `accounting.periods.override` |
| Customize accounting report layouts | New `accounting.reports.design` permission |

The ordinary `reports.design` permission does not grant access to accounting layouts or data. The new accounting-design permission is sensitive and initially belongs only to the Master Administrator. A user must hold both the report's run/view permission and `accounting.reports.design` to preview that accounting report in the designer.

Templates contain no SQL. Dataset providers use the existing parameterized accounting services or dedicated read-only service methods. Permanent report files contain no database host, username, password, or connection metadata.

## 4. Official accounting report inventory

### 4.1 Formal financial statements

| Code | Report | Parameters | Required structure |
|---|---|---|---|
| ACCT-TB | Trial Balance | Organization; as-of date | Account code/name/type/normal balance; debit and credit activity; debit and credit balances; locked balance totals and difference |
| ACCT-FP | Statement of Financial Position | Organization; as-of date | Assets, liabilities, net assets without donor restrictions, net assets with donor restrictions, current activity; locked accounting equation and difference |
| ACCT-ACT | Statement of Activities | Organization; from/through dates | Revenue, expenses, transfers, and change in net assets; columns for without restrictions, with restrictions, and total |
| ACCT-FUNC | Statement of Functional Expenses | Organization; from/through dates | Natural expense accounts by ministry function, dynamically generated function columns, row totals, column totals, grand total |
| ACCT-FUND | Fund Activity and Balances | Organization; from/through dates | Beginning balance, revenue, expense, transfers/releases, other activity, ending balance by fund and restriction class; locked totals |
| ACCT-BVA | Budget to Actual | Adopted budget; through period | General-account summary plus optional detailed budget lines; period and year-to-date budget, actual, variance, and percentage |

### 4.2 Detailed and supporting reports

| Code | Report | Parameters | Required structure |
|---|---|---|---|
| ACCT-GL | General Ledger | Organization; account; optional fund; from/through dates | Opening balance; transaction date/number/type/description/reference/fund/line description; debit, credit, running normal balance; ending balance |
| ACCT-REG | Posted Transaction Register | Organization; optional dates/type/status | Posted and reversed transactions only; number, date, type, status, description, reference, total; optional line detail |
| ACCT-JE | Journal Entry | Posted/reversed transaction | Transaction metadata, creator/reviewer/poster attribution, reversal links, balanced lines, totals, and attachment names plus hashes |
| ACCT-REC | Bank Reconciliation Report | Completed reconciliation | Beginning balance plus cleared activity equals statement ending balance; difference; cleared items; outstanding items; preparer and completion timestamp |
| ACCT-BUD | Adopted Budget | Adopted budget; optional through period | Account-only or detailed form matching the budget's adopted mode; period values and fiscal-year totals |

### 4.3 Control, audit, and close reports

| Code | Report | Parameters | Required structure |
|---|---|---|---|
| ACCT-CLOSE | Fiscal Period Close Checklist | Organization; fiscal period | Every readiness check, clear/blocked status and explanation; period status; run timestamp; explicit READY/NOT READY conclusion |
| ACCT-YE | Year-End Close Preview/Proof | Organization; fiscal year | Revenue, expense, transfers, change by fund, destination net-asset account, blockers, readiness; after close, closing transaction and audit attribution |
| ACCT-AUDIT | Accounting Audit History | Organization; optional user/action/date range | Timestamp, actor, action, entity, reason, before/after details; clearly marked confidential audit record |

The bank-import review, budget editor, transaction entry, approval, posting, and reversal dialogs remain operational screens rather than printed reports. They may link to the appropriate proof or journal-entry report after completion.

## 5. Standard accounting report appearance

Every official starter includes:

- Church logo and church name.
- Accounting organization legal name when it differs from the church name.
- Formal report title and stable report code.
- Clearly printed parameter period, as-of date, account, fund, budget, or reconciliation selection.
- Run date/time and signed-in user's display name.
- Page number and repeated column headings.
- Right-aligned money with commas, two decimals, and aligned decimal points.
- Parentheses for negative amounts on formal financial statements; no ambiguous trailing minus sign.
- Explicit zero or blank policy selected per report and applied consistently.
- Footer identifying ChurchManager and stating whether the report is draft, preview, completed proof, or official posted-ledger output.
- A clear empty-result sentence rather than a blank page.

Formal statements default to portrait unless the column count requires landscape. Detailed ledgers, functional expenses, transaction registers, and reconciliation details default to landscape.

## 6. Accounting invariants that layouts cannot change

The following are computed by ChurchManager and exposed as final approved fields. A report definition cannot recalculate or override them:

- Normal-balance sign conversion.
- Debit and credit totals.
- Trial-balance difference.
- Assets minus liabilities and net assets.
- Revenue, expense, transfer, and change-in-net-assets classifications.
- Donor-restriction classifications.
- Beginning, activity, and ending fund balances.
- Budget actuals, variances, and percentages.
- General-ledger opening and running balances.
- Reconciliation cleared totals, outstanding totals, and difference.
- Close-readiness and year-end blocker results.
- Transaction status, attribution, approval, posting, reversal, and attachment hashes.

Required totals, conclusions, accounting-period labels, audit attribution, and confidentiality labels are protected controls. Users may reposition or style them within safe bounds, but may not delete them, hide them, change their binding, or replace their official wording.

## 7. Required JSForm additions

The current report writer already supplies tables, repeaters, grouping, aggregates, page metadata, editable columns, and empty-result messages. Accounting integration requires these additional generic capabilities:

1. **Protected controls and bands**
   - Definition properties identify required controls/bands.
   - The designer allows safe position, size, font, color, and alignment changes.
   - Delete, hide, rebind, or move to an invalid band is refused with a plain-language explanation.

2. **Matrix/cross-tab control**
   - Row fields, dynamic column collection, value field, row total, column totals, and grand total.
   - Required for functional expenses and useful for period-by-period adopted budgets.
   - Dynamic columns paginate horizontally or select landscape/legal page setup predictably.

3. **Computed result fields, not designer expressions**
   - Dataset providers supply calculated values.
   - The designer formats approved fields but does not accept arbitrary formulas or SQL expressions.

4. **Conditional presentation from approved boolean/status fields**
   - Examples: show READY or NOT READY styling; show a blocker section only when blockers exist.
   - Conditions are declarative equality/empty checks against approved fields only.

5. **Section continuation and keep-together rules**
   - Repeat group headings after page breaks.
   - Keep totals with the last detail row where possible.
   - Allow controlled page breaks between major financial-statement sections.

6. **Report-level classification metadata**
   - Draft, preview, official, confidential, and completed-proof labels.
   - Classification appears in preview, export, and printed footer.

7. **Render-time context fields**
   - Signed-in user display name in addition to run date/time, page, title, and code.

8. **Locked starter validation**
   - ChurchManager supplies a manifest of required controls and bindings.
   - Save and preview fail if a customized definition violates the manifest.

## 8. Dataset contract strategy

Each report receives a versioned ChurchManager dataset contract. Contracts expose presentation-ready values and never expose credentials, password hashes, security tables, unposted transactions unless the specific control report requires them, or unrelated organizations.

Common collections:

- `church`: logo and display identity.
- `organization`: legal name and accounting basis/policy labels.
- `parameters`: printable user selections and reporting period.
- `report_context`: run timestamp, user, classification, and official/preview status.
- Report-specific summary/detail collections.

Providers call existing services wherever possible. Service calculations move out of wx dialogs where they are currently duplicated. The screen and PDF must consume the same result object so totals cannot disagree.

## 9. Customization policy

Users with accounting-design permission may:

- Move and resize permitted controls.
- Adjust fonts, colors, borders, spacing, and page orientation.
- Change optional explanatory labels.
- Reorder approved detail columns.
- Hide explicitly optional columns.
- Add approved fields from the report's dataset contract.

They may not:

- Add SQL or arbitrary expressions.
- Bind to fields outside the contract.
- remove or hide protected totals, period labels, report classification, or audit attribution.
- Alter accounting signs, formulas, classifications, or readiness conclusions.
- Combine data from unauthorized organizations.
- Save a customization that does not validate against the official starter manifest.

Starter restoration remains available. User customizations remain under `%LOCALAPPDATA%\ChurchManager\ReportDefinitions`; official starters remain versioned with ChurchManager.

## 10. Implementation sequence

### Phase 1 - Framework safety

- Add protected controls/bands, conditional presentation, report classification, run-user context, matrix/cross-tab, continuation rules, and manifest validation to JSForm.
- Add focused schema, model, renderer, designer, and security tests.

### Phase 2 - Shared accounting report infrastructure

- Add `accounting.reports.design` permission and Master Administrator grant.
- Add common accounting identity/context contracts and header/footer starter components.
- Add a ChurchManager accounting visual-report launcher that rechecks permission and opens the PDF.
- Preserve current read-only report dialogs as parameter and on-screen review screens during migration.

### Phase 3 - Core financial statements

- ACCT-TB, ACCT-FP, ACCT-ACT, ACCT-FUND.
- Verify every printed total against the existing service result and accounting equation.

### Phase 4 - Complex statements and budgets

- ACCT-FUNC, ACCT-BVA, ACCT-BUD.
- Exercise matrix output, dynamic functions, account-only budgets, and detailed budgets.

### Phase 5 - Detailed support

- ACCT-GL, ACCT-REG, ACCT-JE, ACCT-REC.
- Replace the journal-entry HTML export only after PDF output is verified equivalent or better.

### Phase 6 - Controls and audit

- ACCT-CLOSE, ACCT-YE, ACCT-AUDIT.
- Keep close/reopen actions in their operational dialogs; reports are immutable previews/proofs, never action surfaces.

## 11. Testing and acceptance

Every report must pass:

- Permission-denied test before any database read.
- Organization-scope and parameterization tests.
- Posted/reversed-only tests where applicable.
- Native date/time/decimal preservation tests.
- Exact total and balancing assertions against existing service results.
- Empty-data rendering.
- Multi-page repeated headings and page numbering.
- Long description, long account name, many funds/functions, and landscape overflow cases.
- Protected-control tampering tests.
- Save, close, reopen, restore starter, preview, and export tests.
- Visual PDF review at representative and edge-case data volumes.

User acceptance proceeds in waves. One representative report in each phase is approved visually before the remaining reports in that phase adopt its layout pattern.

## 12. Decisions requested

Approval of this specification authorizes Phase 1 implementation only. Later phases may proceed automatically after their tests and representative proof are approved, following the established development workflow.

Specific proposed decisions:

1. Create the sensitive `accounting.reports.design` permission and grant it initially only to Master Administrator.
2. Treat required accounting totals and official labels as protected but visually movable/styleable.
3. Keep all accounting calculations in ChurchManager services; do not add free-form formulas to the designer.
4. Add a generic matrix/cross-tab control to JSForm.
5. Include the adopted budget, transaction register, accounting audit history, and year-end proof in the official inventory even though some currently lack printable output.
6. Retain the existing dialogs as parameter/review screens while visual PDFs are introduced incrementally.
