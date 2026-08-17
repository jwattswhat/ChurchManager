# ChurchManager Lectionary Package Authoring

## Boundary

An installable lectionary package is a citation and scheduling metadata catalog.
It is not a publication archive. It must not contain Scripture text, psalm text,
prayers, collects, liturgical wording, rubrics copied at meaningful length,
lyrics, music, notation, artwork, media, or publisher page images.

Package creation requires two separate UTF-8 JSON inputs:

1. A package draft matching the schema enforced by `lectionary_packages.py`.
2. A provenance approval record matching the template below.

The builder validates provenance, removes any draft checksum, calculates a new
checksum over canonical package data, and runs the same fail-closed validator
used by ChurchManager. It writes nothing if either input fails.

The approved `distribution_scope` is copied into the finished package before
its checksum is calculated. It therefore travels with the package, is visible
in the package manager, and cannot be changed without invalidating the file.
The builder rejects a draft that claims a different scope from its approval.

## Provenance approval template

```json
{
  "package_code": "publisher-catalog-key",
  "package_version": "1.0.0",
  "approval_status": "PENDING",
  "reviewed_by": "",
  "reviewed_date": "YYYY-MM-DD",
  "source_owner": "",
  "redistribution_basis": "",
  "distribution_scope": "LOCAL_ONLY",
  "metadata_only_confirmed": false,
  "notes": ""
}
```

`approval_status` must be changed to `APPROVED` by an identified reviewer.
`distribution_scope` is either `REDISTRIBUTABLE` or `LOCAL_ONLY`. `LOCAL_ONLY`
does not authorize adding the resulting package to the public ChurchManager
repository. It merely records that a congregation has separately established a
lawful local basis for using its own citation metadata.
An omitted or unrecognized scope is rejected; it is never inferred from the
package title, filename, source, or installation location.

Installed packages are retired rather than destructively deleted. ChurchManager
requires the church default to be changed first, deactivates only records owned
by that package, and preserves service-owned reading snapshots and local data.

The approval must identify the actual source owner and a concrete redistribution
or local-use basis. Owning a printed book is not, by itself, a redistribution
authorization. ChurchManager does not determine or enforce licensing; the
record prevents an undocumented assumption from becoming a distributable file.

## Build command

```powershell
.\.runtime-venv\Scripts\python.exe build_lectionary_package.py `
  package-draft.json provenance-approval.json package.json
```

The resulting JSON can then be reviewed and installed through **Lectionary
Packages**. Draft and provenance working files should not contain credentials,
account numbers, full copyrighted material, or private correspondence.
