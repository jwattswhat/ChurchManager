# Source Construction Release Audit

Status: automated regression gate implemented August 22, 2026

`release_readiness_audit.py` rejects newly introduced `shell=True` execution
and newly introduced visibly interpolated `execute()` statements. The reviewed
baseline is maintained in `release-source-audit-baseline.json`.

The baseline entries are limited to structural construction: validated database
and account identifiers during isolated provisioning/cleanup, fixed internal
table and column lists, database-driver parameter markers, and fixed report
fragments. They do not approve interpolation of user-entered SQL values. All
ordinary values continue to use connector parameters, and external programs
must receive argument lists rather than command-shell strings.

Any baseline change requires inspection of the exact source line and this audit
must pass before commit. The baseline is evidence of a reviewed exception, not
a general permission to construct SQL dynamically.
