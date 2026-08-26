# LimeReports retirement

Status: implemented in source; migration `065_retire_limereports_runtime.sql`
must be applied to each ChurchManager database.

## Decision

ChurchManager no longer uses the external LimeReports executable. Supported
catalog reports are rendered by JSForm's visual report system from JSON
definitions in `visual_reports/definitions` and approved report datasets.
JSForm may retain generic LimeReports compatibility for other applications, but
ChurchManager does not call it.

## Inventory result

| Classification | Codes | Disposition |
| --- | --- | --- |
| Supported visual reports | `CMGN01`, `CMAT01`-`CMAT05`, `CMGN02`, `CMWS03`-`CMWS06`, `CMPC03`, `CMMB01`, `CMMB02`-`CMMB04`, `CMMB05`-`CMMB06`, `CMPC04`, `CMMB07`, `CMMB08`, `CMPC05`, `CMGN03`, `CMWS01`, `CMWS02` | JSON starter exists and the JSForm PDF renderer is used. |
| Consolidated old layouts | `CMAD01`, `CMPH01` | Their useful output is covered by supported visual reports. |
| Disabled report | `CMSM01` | Remains retired. |
| Former batch launcher | `CMBATCH00` | Retired; users run authorized reports individually. |
| Obsolete catalog codes | `CMFD01`, `CMCL01`, `CMDN01`, `CMDN02`, `CFCA01`, `CFCR01`, `CFGR01` | Disabled by migration 065. |

The 30 `.lrxml`/`.lrsml` files were removed after confirming that every
supported code has a JSON definition. The LimeReports diagnostic and conversion
utilities were also removed.

The obsolete `CMEN01` enhancement report and its database-backed enhancement
tracker were retired separately by migration 066.

## Runtime safeguards

- `ChurchManagerReportService` accepts only codes in `OFFICIAL_CODES`.
- An authorized but unregistered code fails closed instead of falling back to
  an external executable.
- Report data continues to come from approved providers and report-safe views.
- Starter definitions remain recoverable and user customizations remain
  separate.
- Migration 065 disables known obsolete catalog rows and removes obsolete
  LimeReports path configuration.

## Acceptance checks

Status: completed through the maintained report catalog and repeated user visual
acceptance during development. Continue to sample these families in beta
regression testing; do not reintroduce LimeReports.

1. Apply migration 065 to `ChurchDBTest` with ChurchManager closed.
2. Open the Reports screen and confirm no retired code is listed.
3. Run at least one report from each permission family: general, attendance,
   membership, worship, ministry, and pastoral.
4. Confirm Prayer Requests (`CMPC05`) runs through the ordinary report screen.
5. Confirm a customized report still opens and a missing customization falls
   back to its JSON starter.
6. Inspect representative PDFs for privacy, clipping, wrapping, pagination, and
   totals.
7. Confirm ChurchManager starts and runs without a LimeReports installation or
   `Location/LimeReport` configuration value.

## Historical material

Git history preserves the retired templates and integration for research. They
must not be restored to the active runtime. If a missing report is discovered,
build it with the JSForm visual report contract rather than reintroducing the
external engine.
