"""Prepare and build the metadata-only LSB hymnal package."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

from hymnal_packages import HymnalPackageError, HymnalPackageValidator, canonical_hymnal_checksum
from hymn_titles import title_case


ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "data" / "lsb_printed_hymn_tunes.csv"
REVIEW = ROOT / "data" / "lsb_printed_hymn_review.csv"
OUTPUT = ROOT / "packages" / "hymnal" / "lsb-1.0.0.json"
REVIEW_FIELDS = (
    "HymnNumber", "Title", "Tune", "PrintedStanzaCount", "VerificationStatus",
    "VerificationSource", "VerifiedBy", "VerifiedDate", "ReviewNote",
)


def catalog_rows(path=CATALOG):
    """Read and validate the fixed 331-966 printed LSB catalog."""
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    numbers = [int(row["HymnNumber"]) for row in rows]
    if numbers != list(range(331, 967)):
        raise HymnalPackageError("The LSB source must contain every printed hymn from 331 through 966 once.")
    for row in rows:
        row["Title"] = title_case(row["Title"])
        row["Tune"] = str(row.get("Tune") or "").strip()
        if not row["Title"]:
            raise HymnalPackageError("Every LSB source row must have a title.")
    return rows


def initialize_review(catalog_path=CATALOG, review_path=REVIEW):
    """Create or safely refresh the human stanza-count review ledger."""
    rows = catalog_rows(catalog_path)
    existing = {}
    review_path = Path(review_path)
    if review_path.exists():
        with review_path.open(newline="", encoding="utf-8-sig") as stream:
            existing = {int(row["HymnNumber"]): row for row in csv.DictReader(stream)}
    with review_path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        for source in rows:
            number = int(source["HymnNumber"])
            old = existing.get(number, {})
            unchanged = (
                old.get("Title") == source["Title"] and old.get("Tune", "") == source["Tune"]
            )
            writer.writerow({
                "HymnNumber": number,
                "Title": source["Title"],
                "Tune": source["Tune"],
                "PrintedStanzaCount": old.get("PrintedStanzaCount", "") if unchanged else "",
                "VerificationStatus": old.get("VerificationStatus", "PENDING") if unchanged else "PENDING",
                "VerificationSource": old.get("VerificationSource", "") if unchanged else "",
                "VerifiedBy": old.get("VerifiedBy", "") if unchanged else "",
                "VerifiedDate": old.get("VerifiedDate", "") if unchanged else "",
                "ReviewNote": old.get("ReviewNote", "") if unchanged else "",
            })
    return len(rows)


def reviewed_rows(catalog_path=CATALOG, review_path=REVIEW):
    """Return catalog rows only when every stanza count has review evidence."""
    source = catalog_rows(catalog_path)
    review_path = Path(review_path)
    if not review_path.exists():
        raise HymnalPackageError("Initialize and complete the LSB review ledger first.")
    with review_path.open(newline="", encoding="utf-8-sig") as stream:
        review = list(csv.DictReader(stream))
    if len(review) != len(source):
        raise HymnalPackageError("The LSB review ledger does not match the catalog row count.")
    result = []
    pending = []
    for expected, row in zip(source, review):
        number = int(expected["HymnNumber"])
        if int(row.get("HymnNumber") or 0) != number or row.get("Title") != expected["Title"] or row.get("Tune", "") != expected["Tune"]:
            raise HymnalPackageError(f"The review identity does not match LSB {number}.")
        if str(row.get("VerificationStatus") or "").strip().upper() != "VERIFIED":
            pending.append(number)
            continue
        try:
            count = int(row["PrintedStanzaCount"])
        except (TypeError, ValueError) as error:
            raise HymnalPackageError(f"LSB {number} has no valid verified stanza count.") from error
        if not 1 <= count <= 99:
            raise HymnalPackageError(f"LSB {number} must have a printed stanza count from 1 through 99.")
        if not str(row.get("VerificationSource") or "").strip() or not str(row.get("VerifiedBy") or "").strip():
            raise HymnalPackageError(f"LSB {number} is missing verification evidence.")
        try:
            date.fromisoformat(str(row.get("VerifiedDate") or ""))
        except ValueError as error:
            raise HymnalPackageError(f"LSB {number} needs an ISO verification date.") from error
        result.append((expected, row, count))
    if pending:
        preview = ", ".join(str(number) for number in pending[:10])
        suffix = "..." if len(pending) > 10 else ""
        raise HymnalPackageError(f"{len(pending)} LSB stanza counts remain unverified ({preview}{suffix}).")
    return result


def build_package(catalog_path=CATALOG, review_path=REVIEW):
    """Build the final package only from a completely verified review ledger."""
    entries = []
    for source, review, count in reviewed_rows(catalog_path, review_path):
        number = int(source["HymnNumber"])
        entries.append({
            "hymn_id": 10000 + number,
            "entry_slot": number,
            "printed_reference": f"LSB {number}",
            "title": source["Title"],
            "printed_stanza_count": count,
            "is_active": True,
            "tune": source["Tune"],
            "text_copyright_status": "UNKNOWN",
            "tune_copyright_status": "UNKNOWN",
            "setting_copyright_status": "UNKNOWN",
            "source_note": (
                f"Stanza count verified from {review['VerificationSource']} by "
                f"{review['VerifiedBy']} on {review['VerifiedDate']}."
            ),
        })
    package = {
        "package_code": "lsb",
        "package_version": "1.0.0",
        "schema_version": 1,
        "checksum": "",
        "hymnal_id": 2,
        "hymn_id_start": 10001,
        "hymn_id_end": 14999,
        "abbreviation": "LSB",
        "title": "Lutheran Service Book",
        "edition": "Pew Edition",
        "publisher": "Concordia Publishing House",
        "publication_year": 2006,
        "isbn": "978-0-7586-1217-5",
        "source_name": "Congregation-owned Lutheran Service Book and reviewed catalog metadata",
        "source_reference": "Printed LSB hymns 331-966; see the repository review ledger",
        "distribution_notice": "Metadata and outline support only; no lyrics, music, or published service text.",
        "entries": entries,
    }
    package["checksum"] = canonical_hymnal_checksum(package)
    HymnalPackageValidator().validate(package, package["checksum"])
    return package


def main(argv=None):
    """Initialize the review ledger or write the verified LSB package."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initialize-review", action="store_true")
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--review", type=Path, default=REVIEW)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    if args.initialize_review:
        print(f"review_rows={initialize_review(args.catalog, args.review)}")
        print(f"review={args.review}")
        return 0
    try:
        package = build_package(args.catalog, args.review)
    except HymnalPackageError as error:
        parser.exit(1, f"LSB package not written: {error}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"entries={len(package['entries'])}")
    print(f"wrote={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
