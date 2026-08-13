"""Convert legacy Proper HymnSug text into structured hymn suggestions."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from import_lsb_from_production import connect, rows_as_dicts


ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "ConversionLogs" / "LSB-HymnSuggestion-Conversion.md"
NUMBER_PATTERN = re.compile(r"(?<!\d)(\d{3,4})(?!\d)")
ROLE_PATTERN = re.compile(
    r"(?P<entrance>Entrance|Opening|Hymn of Invocation)\s*:|"
    r"(?P<day>Of the Day|Hymn of the Day)\s*:|"
    r"(?P<communion>Distribution|Communion)\s*:|"
    r"(?P<closing>Closing|Sending)\s*:",
    re.IGNORECASE,
)
ROLE_NAMES = {
    "entrance": "Hymn of Invocation",
    "day": "Hymn of the Day",
    "communion": "Communion",
    "closing": "Closing",
}
HYMN_GUESSES = {
    "341": "Lift Up Your Heads, Ye Mighty Gates",
    "407": "To Jordan Came the Christ, Our Lord",
    "499": "Come, Holy Ghost, Creator Blest",
    "530": "No Temple Now, No Gift of Price",
    "576": "My Hope Is Built on Nothing Less",
    "824": "May God Bestow on Us His Grace",
    "879": "Stay with Us",
}
IGNORED_NUMBER_TOKENS = {"2020"}


def rows(connection, sql, values=()):
    cursor = connection.cursor()
    try:
        cursor.execute(sql, values)
        return rows_as_dicts(cursor)
    finally:
        cursor.close()


def catalog_number(label):
    match = re.search(r"(?:^|\b)LSB\s*(\d{3,4})(?:\b|$)", str(label or ""), re.I)
    return match.group(1) if match else None


def suggestion_tokens(text):
    """Return hymn numbers with the closest preceding recognized service role."""
    text = str(text or "")
    headings = []
    for match in ROLE_PATTERN.finditer(text):
        role_key = next(name for name, value in match.groupdict().items() if value)
        headings.append((match.start(), ROLE_NAMES[role_key]))
    result = []
    for match in NUMBER_PATTERN.finditer(text):
        role = ""
        for position, candidate in headings:
            if position > match.start():
                break
            role = candidate
        result.append((match.group(1), role))
    return result


def write_review_log(status, summary, missed_records):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# LSB legacy hymn-suggestion conversion log",
        "",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"Status: {status}",
        "",
        "## Summary",
        "",
    ]
    lines.extend(f"- {name}: {value}" for name, value in summary.items())
    lines.extend(["", "## Best-guess catalog records", ""])
    for number, title in sorted(HYMN_GUESSES.items(), key=lambda item: int(item[0])):
        lines.append(f"- LSB {number}: {title}")
    lines.extend(["", "## Records needing review", ""])
    if not missed_records:
        lines.append("No missed or partially missed records.")
    for item in missed_records:
        lines.extend(
            [
                f"### Proper {item['id']}: {item['name']}",
                "",
                f"- Matched suggestions: {item['matched']}",
                f"- Unmatched number tokens: {', '.join(item['unmatched']) or '(none)'}",
                f"- Ambiguous number tokens: {', '.join(item['ambiguous']) or '(none)'}",
                "- Original text:",
                "",
            ]
        )
        lines.extend("> " + line for line in str(item["text"]).splitlines())
        lines.append("")
    LOG_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Insert verified suggestions")
    args = parser.parse_args()
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    if str(testing["host"]).casefold() not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("Safety stop: the target database is not local.")
    if "test" not in str(testing["database"]).casefold():
        raise RuntimeError("Safety stop: the target is not a test database.")
    connection = connect(testing, testing["credential_target"], testing["database"])
    try:
        proper_rows = rows(
            connection,
            "SELECT p.ID,p.LiturgicalDate,p.HymnSug FROM tblPropers p "
            "JOIN tblLectionarySystem ls ON ls.ID=p.LectionarySystemID "
            "WHERE ls.Name LIKE 'LSB %' AND p.HymnSug IS NOT NULL "
            "AND TRIM(p.HymnSug)<>'' ORDER BY p.ID",
        )
        hymn_rows = rows(
            connection,
            "SELECT h.ID,h.Hymn,h.Title FROM tblHymn h "
            "JOIN tblHymnal hy ON hy.ID=h.HymnalID WHERE UPPER(TRIM(hy.Hymnal))='LSB'",
        )
        catalog = defaultdict(list)
        for hymn in hymn_rows:
            number = catalog_number(hymn["Hymn"])
            if number:
                catalog[number].append(hymn)
        inferred_present = [number for number in HYMN_GUESSES if len(catalog.get(number, [])) == 1]
        ambiguous_catalog = {number: items for number, items in catalog.items() if len(items) > 1}
        existing = {
            (row["PropersID"], row["HymnID"], str(row["SuggestedAs"] or ""))
            for row in rows(
                connection,
                "SELECT PropersID,HymnID,SuggestedAs FROM tblProperHymnSuggestion",
            )
        }
        planned = []
        unmatched = Counter()
        ambiguous = Counter()
        ignored = Counter()
        guessed = Counter()
        no_match_propers = []
        missed_records = []
        for proper in proper_rows:
            found_for_proper = 0
            seen = set()
            proper_unmatched = []
            proper_ambiguous = []
            for number, role in suggestion_tokens(proper["HymnSug"]):
                if number in IGNORED_NUMBER_TOKENS:
                    ignored[number] += 1
                    continue
                matches = catalog.get(number, [])
                if not matches:
                    if number in HYMN_GUESSES:
                        guessed[number] += 1
                        matches = [{
                            "ID": "guess:" + number,
                            "Hymn": "LSB " + number,
                            "Title": HYMN_GUESSES[number],
                        }]
                    else:
                        unmatched[number] += 1
                        proper_unmatched.append(number)
                        continue
                if len(matches) != 1:
                    ambiguous[number] += 1
                    proper_ambiguous.append(number)
                    continue
                hymn = matches[0]
                key = (proper["ID"], hymn["ID"], role)
                if key in seen:
                    continue
                seen.add(key)
                found_for_proper += 1
                planned.append(
                    {
                        "key": key,
                        "proper": proper["LiturgicalDate"],
                        "number": number,
                        "title": hymn["Title"],
                    }
                )
            if not found_for_proper:
                no_match_propers.append((proper["ID"], proper["LiturgicalDate"]))
            if proper_unmatched or proper_ambiguous or not found_for_proper:
                missed_records.append(
                    {
                        "id": proper["ID"],
                        "name": proper["LiturgicalDate"],
                        "matched": found_for_proper,
                        "unmatched": proper_unmatched,
                        "ambiguous": proper_ambiguous,
                        "text": proper["HymnSug"],
                    }
                )
        new_rows = [
            item for item in planned
            if not str(item["key"][1]).startswith("guess:") and item["key"] not in existing
            or str(item["key"][1]).startswith("guess:")
        ]
        existing_rows = len(planned) - len(new_rows)
        print(f"target={testing['host']}/{testing['database']}")
        print(f"legacy_text_records={len(proper_rows)} lsb_catalog_hymns={len(hymn_rows)}")
        print(f"parsed_unique_suggestions={len(planned)} already_structured={existing_rows}")
        print(f"would_insert={len(new_rows)} would_update=0 would_delete=0")
        print(f"unmatched_occurrences={sum(unmatched.values())} unmatched_numbers={dict(unmatched)}")
        print(f"ambiguous_occurrences={sum(ambiguous.values())} ambiguous_numbers={dict(ambiguous)}")
        print(f"ignored_nonhymn_tokens={dict(ignored)}")
        print(f"would_create_catalog_hymns={len(guessed)} guessed_numbers={dict(guessed)}")
        print(f"legacy_records_without_matched_hymns={len(no_match_propers)}")
        if ambiguous_catalog:
            print(f"duplicate_catalog_numbers={sorted(ambiguous_catalog)}")
        summary = {
            "Legacy text records": len(proper_rows),
            "Parsed unique structured suggestions": len(planned),
            "New suggestions": len(new_rows),
            "Already structured": existing_rows,
            "Unmatched number occurrences": sum(unmatched.values()),
            "Ambiguous number occurrences": sum(ambiguous.values()),
            "Ignored non-hymn number occurrences": sum(ignored.values()),
            "Best-guess catalog records to create": len(guessed),
            "Best-guess catalog records present": len(inferred_present),
            "Records with no matched hymns": len(no_match_propers),
            "Records needing review": len(missed_records),
        }
        if not args.apply:
            if new_rows or not LOG_PATH.exists():
                write_review_log("Preview only - no database changes", summary, missed_records)
            print(f"review_log={LOG_PATH}")
            print("No changes made. Re-run with --apply after reviewing these counts.")
            return 2
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT h.ID FROM tblHymnal h WHERE UPPER(TRIM(h.Hymnal))='LSB'"
            )
            hymnal_rows = cursor.fetchall()
            if len(hymnal_rows) != 1:
                raise RuntimeError(f"Expected one LSB hymnal; found {len(hymnal_rows)}.")
            lsb_hymnal_id = hymnal_rows[0][0]
            guessed_ids = {}
            for number in sorted(guessed, key=int):
                cursor.execute(
                    "SELECT ID FROM tblHymn WHERE HymnalID=? AND TRIM(Hymn)=?",
                    (lsb_hymnal_id, "LSB " + number),
                )
                found = cursor.fetchall()
                if len(found) > 1:
                    raise RuntimeError(f"Multiple LSB {number} catalog records exist.")
                if found:
                    guessed_ids[number] = found[0][0]
                else:
                    cursor.execute(
                        "INSERT INTO tblHymn (HymnalID,Hymn,Title,Note) VALUES (?,?,?,?)",
                        (
                            lsb_hymnal_id,
                            "LSB " + number,
                            HYMN_GUESSES[number],
                            "Created from a legacy Proper hymn suggestion; title inferred from source text.",
                        ),
                    )
                    guessed_ids[number] = cursor.lastrowid
            for item in new_rows:
                proper_id, hymn_id, role = item["key"]
                if str(hymn_id).startswith("guess:"):
                    hymn_id = guessed_ids[str(hymn_id).split(":", 1)[1]]
                if (proper_id, hymn_id, role) in existing:
                    continue
                cursor.execute(
                    "INSERT INTO tblProperHymnSuggestion "
                    "(PropersID,HymnID,SuggestedAs,Note) VALUES (?,?,?,?)",
                    (
                        proper_id,
                        hymn_id,
                        role,
                        "Converted from the legacy HymnSug text; the original text remains on the Proper.",
                    ),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
        final_count = rows(
            connection,
            "SELECT COUNT(*) AS Total FROM tblProperHymnSuggestion s "
            "JOIN tblPropers p ON p.ID=s.PropersID "
            "JOIN tblLectionarySystem ls ON ls.ID=p.LectionarySystemID "
            "WHERE ls.Name LIKE 'LSB %'",
        )[0]["Total"]
        print(f"applied: inserted={len(new_rows)} final_lsb_suggestions={final_count}")
        summary["Final LSB structured suggestions"] = final_count
        write_review_log("Applied", summary, missed_records)
        print(f"review_log={LOG_PATH}")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
