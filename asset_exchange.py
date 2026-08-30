"""Privacy-safe CSV parsing and export helpers for current asset records."""

from __future__ import annotations

import csv
import io

from csv_safety import csv_safe_row


HEADERS = (
    "Asset Number", "Asset Name", "Category", "Description", "Quantity",
    "Manufacturer", "Model", "Serial Number", "Location", "Acquisition Method",
    "Acquisition Date", "Reference Value", "Condition", "Status",
    "Warranty Expires", "Next Maintenance", "Replacement Review", "Retired Date", "Note",
)


def read_csv(content):
    """Return normalized dictionaries from UTF-8 CSV bytes or text."""
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        raise ValueError("The CSV file has no header row.")
    names = {str(name).strip().casefold(): name for name in reader.fieldnames}
    required = ("Asset Number", "Asset Name", "Category")
    missing = [name for name in required if name.casefold() not in names]
    if missing:
        raise ValueError("Missing required CSV column(s): " + ", ".join(missing))
    rows = [
        {header: str(source.get(names.get(header.casefold(), ""), "") or "").strip()
         for header in HEADERS}
        for source in reader
    ]
    if not rows:
        raise ValueError("The CSV file contains no asset rows.")
    return rows


def write_csv(rows):
    """Return UTF-8 CSV text containing only approved register fields."""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=HEADERS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(csv_safe_row(row) for row in rows)
    return stream.getvalue()
