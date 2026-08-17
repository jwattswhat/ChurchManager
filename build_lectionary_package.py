"""Build an installable lectionary package only from approved provenance."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path

from lectionary_packages import (
    LectionaryPackageError, LectionaryPackageValidator,
    canonical_lectionary_checksum,
)


PROVENANCE_FIELDS = frozenset({
    "package_code", "package_version", "approval_status", "reviewed_by",
    "reviewed_date", "source_owner", "redistribution_basis",
    "distribution_scope", "metadata_only_confirmed", "notes",
})


def validate_provenance(provenance, package):
    """Reject incomplete or mismatched authority records before packaging."""
    if not isinstance(provenance, dict):
        raise LectionaryPackageError("The provenance approval must be an object.")
    unknown = set(provenance) - PROVENANCE_FIELDS
    if unknown:
        raise LectionaryPackageError(f"Unknown provenance field: {sorted(unknown)[0]}.")
    required = (
        "package_code", "package_version", "reviewed_by", "reviewed_date",
        "source_owner", "redistribution_basis", "distribution_scope",
    )
    if str(provenance.get("approval_status") or "").upper() != "APPROVED":
        raise LectionaryPackageError("The source provenance is not approved for packaging.")
    for field in required:
        if not str(provenance.get(field) or "").strip():
            raise LectionaryPackageError(f"Provenance field {field} is required.")
    if provenance.get("metadata_only_confirmed") is not True:
        raise LectionaryPackageError("Metadata-only scope has not been confirmed.")
    if str(provenance["package_code"]).casefold() != str(package.get("package_code") or "").casefold():
        raise LectionaryPackageError("Provenance package code does not match the draft.")
    if str(provenance["package_version"]) != str(package.get("package_version") or ""):
        raise LectionaryPackageError("Provenance package version does not match the draft.")
    if str(provenance["distribution_scope"]).upper() not in {"REDISTRIBUTABLE", "LOCAL_ONLY"}:
        raise LectionaryPackageError("Distribution scope must be REDISTRIBUTABLE or LOCAL_ONLY.")
    try:
        date.fromisoformat(str(provenance["reviewed_date"]))
    except ValueError as error:
        raise LectionaryPackageError("Provenance review date must use YYYY-MM-DD.") from error
    return provenance


def build_package(draft, provenance):
    """Return a checksum-protected package after provenance and schema validation."""
    if not isinstance(draft, dict):
        raise LectionaryPackageError("The package draft must be an object.")
    package = dict(draft)
    package.pop("checksum", None)
    validate_provenance(provenance, package)
    package["checksum"] = canonical_lectionary_checksum(package)
    summary = LectionaryPackageValidator().validate(package, package["checksum"])
    return package, summary


def _read(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LectionaryPackageError(f"Unable to read valid UTF-8 JSON from {path}.") from error


def main():
    """Build one package from explicit draft, approval, and output paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", type=Path)
    parser.add_argument("provenance", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    package, summary = build_package(_read(args.draft), _read(args.provenance))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(
        f"built={args.output} package={summary.package_code} "
        f"version={summary.package_version} propers={summary.proper_count} "
        f"appointments={summary.appointment_count}"
    )


if __name__ == "__main__":
    main()
