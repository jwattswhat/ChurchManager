"""Export the current ChurchDBTest lectionary as read-only reconciliation data."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime, time
from pathlib import Path

from import_lsb_from_production import connect, rows_as_dicts


ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "churchmanager.json"
OUTPUT = ROOT / "ConversionLogs" / "CurrentLectionaryReference.json"
SUMMARY = ROOT / "ConversionLogs" / "CurrentLectionaryReference.md"
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
ALLOWED = {
    "systems": ("ID", "Name", "CycleType", "Active", "Note"),
    "propers": (
        "ID", "LectionarySystemID", "Cycle", "Sort", "Season",
        "LiturgicalDate", "Color", "AltColor", "Theme", "Note",
    ),
    "readings": ("ID", "PropersID", "Reading", "Reference", "Note"),
    "hymn_suggestions": (
        "ID", "PropersID", "HymnID", "SuggestedAs", "Note",
        "PrintedReference", "Hymn", "Title",
    ),
}


def _safe(value):
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, bytes):
        raise ValueError("Binary content is not permitted in the lectionary reference inventory.")
    return value


def _project(rows, fields):
    return [
        {field: _safe(row.get(field)) for field in fields if field in row}
        for row in rows
    ]


def build_inventory(systems, propers, readings, suggestions):
    """Return deterministic metadata-only reconciliation data from current rows."""
    projected = {
        "format": "churchmanager.current-lectionary-reference",
        "format_version": 1,
        "purpose": "Reference-only comparison source; not an installable package.",
        "systems": _project(systems, ALLOWED["systems"]),
        "propers": _project(propers, ALLOWED["propers"]),
        "readings": _project(readings, ALLOWED["readings"]),
        "hymn_suggestions": _project(suggestions, ALLOWED["hymn_suggestions"]),
    }
    projected["systems"].sort(key=lambda row: (str(row.get("Name") or "").casefold(), row.get("ID") or 0))
    projected["propers"].sort(key=lambda row: (
        row.get("LectionarySystemID") or 0, str(row.get("Cycle") or ""),
        row.get("Sort") or 0, row.get("ID") or 0,
    ))
    projected["readings"].sort(key=lambda row: (row.get("PropersID") or 0, row.get("ID") or 0))
    projected["hymn_suggestions"].sort(key=lambda row: (row.get("PropersID") or 0, row.get("ID") or 0))
    return projected


def _rows(connection, sql):
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
        return rows_as_dicts(cursor)
    finally:
        cursor.close()


def read_current_reference(connection):
    """Read only the current metadata needed for later package reconciliation."""
    return build_inventory(
        _rows(connection, "SELECT * FROM tblLectionarySystem"),
        _rows(connection, "SELECT * FROM tblPropers"),
        _rows(connection, "SELECT * FROM tblReading"),
        _rows(connection, "SELECT s.*,h.PrintedReference,h.Hymn,h.Title "
                          "FROM tblProperHymnSuggestion s LEFT JOIN tblHymn h ON h.ID=s.HymnID"),
    )


def write_summary(inventory, path=SUMMARY):
    """Write a short human-readable reconciliation index beside the JSON data."""
    systems = {row.get("ID"): row.get("Name") for row in inventory["systems"]}
    proper_counts = Counter(row.get("LectionarySystemID") for row in inventory["propers"])
    lines = [
        "# Current Lectionary Reference Inventory", "",
        "This is reference-only metadata for correcting future packages. It is not an installable package.", "",
        "## Counts", "",
        f"- Systems: {len(inventory['systems'])}",
        f"- Propers: {len(inventory['propers'])}",
        f"- Readings: {len(inventory['readings'])}",
        f"- Hymn suggestions: {len(inventory['hymn_suggestions'])}", "",
        "## Propers by current system", "",
    ]
    for system_id, name in sorted(systems.items(), key=lambda item: str(item[1]).casefold()):
        lines.append(f"- {name}: {proper_counts.get(system_id, 0)}")
    lines.extend(["", "The future import process may accept corrections from this inventory, but it does not preserve these IDs.", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    """Connect only to the configured local test database and write the inventory."""
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    if str(testing.get("host") or "").casefold() not in LOCAL_HOSTS:
        raise RuntimeError("Safety stop: the lectionary reference source is not local.")
    if "test" not in str(testing.get("database") or "").casefold():
        raise RuntimeError("Safety stop: the lectionary reference source is not a test database.")
    connection = connect(
        testing, testing.get("credential_target", "ChurchManager/Test"), testing["database"],
    )
    try:
        inventory = read_current_reference(connection)
    finally:
        connection.close()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(inventory)
    print(f"systems={len(inventory['systems'])} propers={len(inventory['propers'])} "
          f"readings={len(inventory['readings'])} suggestions={len(inventory['hymn_suggestions'])}")
    print(f"reference={OUTPUT}")
    print(f"summary={SUMMARY}")


if __name__ == "__main__":
    main()
