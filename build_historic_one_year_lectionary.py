"""Build ChurchManager's redistributable historic one-year lectionary package."""

from __future__ import annotations

import json
from pathlib import Path

from build_lectionary_package import build_package


PACKAGE_CODE = "cm-historic-one-year"
SOURCE = "Common Service Book of the Lutheran Church (1919)"
SOURCE_REFERENCE = "https://archive.org/details/commonserviceboo00unit"

# Occasion, season, Epistle/first reading, Gospel, calendar rule.
# This is a citation index only. No Scripture or liturgical text is retained.
APPOINTMENTS = [
    ("First Sunday in Advent", "Advent", "Romans 13:11-14", "Matthew 21:1-9", "advent-sunday-1"),
    ("Second Sunday in Advent", "Advent", "Romans 15:4-13", "Luke 21:25-36", "advent-sunday-2"),
    ("Third Sunday in Advent", "Advent", "1 Corinthians 4:1-5", "Matthew 11:2-10", "advent-sunday-3"),
    ("Fourth Sunday in Advent", "Advent", "Philippians 4:4-7", "John 1:19-28", "advent-sunday-4"),
    ("Christmas Day", "Christmas", "Hebrews 1:1-12", "John 1:1-14", "fixed:12-25"),
    ("The Name of Jesus", "Christmas", "Galatians 3:23-29", "Luke 2:21", "fixed:01-01"),
    ("The Epiphany of Our Lord", "Epiphany", "Isaiah 60:1-6", "Matthew 2:1-12", "fixed:01-06"),
    ("First Sunday after Epiphany", "Epiphany", "Romans 12:1-5", "Luke 2:41-52", None),
    ("Second Sunday after Epiphany", "Epiphany", "Romans 12:6-16", "John 2:1-11", None),
    ("Third Sunday after Epiphany", "Epiphany", "Romans 12:16-21", "Matthew 8:1-13", None),
    ("Fourth Sunday after Epiphany", "Epiphany", "Romans 13:8-10", "Matthew 8:23-27", None),
    ("Fifth Sunday after Epiphany", "Epiphany", "Colossians 3:12-17", "Matthew 13:24-30", None),
    ("The Transfiguration of Our Lord", "Epiphany", "2 Peter 1:16-21", "Matthew 17:1-9", None),
    ("Septuagesima", "Pre-Lent", "1 Corinthians 9:24-10:5", "Matthew 20:1-16", "easter:-63"),
    ("Sexagesima", "Pre-Lent", "2 Corinthians 11:19-12:9", "Luke 8:4-15", "easter:-56"),
    ("Quinquagesima", "Pre-Lent", "1 Corinthians 13:1-13", "Luke 18:31-43", "easter:-49"),
    ("Ash Wednesday", "Lent", "Joel 2:12-19", "Matthew 6:16-21", "easter:-46"),
    ("First Sunday in Lent", "Lent", "2 Corinthians 6:1-10", "Matthew 4:1-11", "easter:-42"),
    ("Second Sunday in Lent", "Lent", "1 Thessalonians 4:1-7", "Matthew 15:21-28", "easter:-35"),
    ("Third Sunday in Lent", "Lent", "Ephesians 5:1-9", "Luke 11:14-28", "easter:-28"),
    ("Fourth Sunday in Lent", "Lent", "Galatians 4:21-31", "John 6:1-15", "easter:-21"),
    ("Fifth Sunday in Lent", "Lent", "Hebrews 9:11-15", "John 8:46-59", "easter:-14"),
    ("Palm Sunday", "Holy Week", "Philippians 2:5-11", "Matthew 21:1-9", "easter:-7"),
    ("Maundy Thursday", "Holy Week", "1 Corinthians 11:23-32", "John 13:1-15", "easter:-3"),
    ("Good Friday", "Holy Week", "Isaiah 52:13-53:12", "John 18:1-19:42", "easter:-2"),
    ("Easter Day", "Easter", "1 Corinthians 5:6-8", "Mark 16:1-8", "easter:0"),
    ("First Sunday after Easter", "Easter", "1 John 5:4-12", "John 20:19-31", "easter:7"),
    ("Second Sunday after Easter", "Easter", "1 Peter 2:21-25", "John 10:11-16", "easter:14"),
    ("Third Sunday after Easter", "Easter", "1 Peter 2:11-20", "John 16:16-23", "easter:21"),
    ("Fourth Sunday after Easter", "Easter", "James 1:16-21", "John 16:5-15", "easter:28"),
    ("Fifth Sunday after Easter", "Easter", "James 1:22-27", "John 16:23-30", "easter:35"),
    ("The Ascension of Our Lord", "Easter", "Acts 1:1-11", "Mark 16:14-20", "easter:39"),
    ("Sunday after the Ascension", "Easter", "1 Peter 4:7-11", "John 15:26-16:4", "easter:42"),
    ("The Day of Pentecost", "Pentecost", "Acts 2:1-13", "John 14:23-31", "easter:49"),
    ("The Holy Trinity", "Trinity", "Romans 11:33-36", "John 3:1-15", "easter:56"),
]

TRINITY = [
    ("1 John 4:16-21", "Luke 16:19-31"), ("1 John 3:13-18", "Luke 14:16-24"),
    ("1 Peter 5:6-11", "Luke 15:1-10"), ("Romans 8:18-23", "Luke 6:36-42"),
    ("1 Peter 3:8-15", "Luke 5:1-11"), ("Romans 6:3-11", "Matthew 5:20-26"),
    ("Romans 6:19-23", "Mark 8:1-9"), ("Romans 8:12-17", "Matthew 7:15-23"),
    ("1 Corinthians 10:6-13", "Luke 16:1-9"), ("1 Corinthians 12:1-11", "Luke 19:41-48"),
    ("1 Corinthians 15:1-10", "Luke 18:9-14"), ("2 Corinthians 3:4-11", "Mark 7:31-37"),
    ("Galatians 3:15-22", "Luke 10:23-37"), ("Galatians 5:16-24", "Luke 17:11-19"),
    ("Galatians 5:25-6:10", "Matthew 6:24-34"), ("Ephesians 3:13-21", "Luke 7:11-17"),
    ("Ephesians 4:1-6", "Luke 14:1-11"), ("1 Corinthians 1:4-9", "Matthew 22:34-46"),
    ("Ephesians 4:22-28", "Matthew 9:1-8"), ("Ephesians 5:15-21", "Matthew 22:1-14"),
    ("Ephesians 6:10-17", "John 4:46-54"), ("Philippians 1:3-11", "Matthew 18:23-35"),
    ("Philippians 3:17-21", "Matthew 22:15-22"), ("Colossians 1:9-14", "Matthew 9:18-26"),
    ("1 Thessalonians 4:13-18", "Matthew 24:15-28"), ("2 Peter 3:3-14", "Matthew 25:31-46"),
    ("1 Thessalonians 5:1-11", "Matthew 25:1-13"),
]
ORDINALS = ("First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh",
            "Eighth", "Ninth", "Tenth", "Eleventh", "Twelfth", "Thirteenth",
            "Fourteenth", "Fifteenth", "Sixteenth", "Seventeenth", "Eighteenth",
            "Nineteenth", "Twentieth", "Twenty-First", "Twenty-Second",
            "Twenty-Third", "Twenty-Fourth", "Twenty-Fifth", "Twenty-Sixth",
            "Twenty-Seventh")


def _key(text):
    return "-".join("".join(c.casefold() if c.isalnum() else " " for c in text).split())


def build_draft():
    """Return the citation-only package draft from the reviewed appointment index."""
    rows = list(APPOINTMENTS)
    rows.extend((f"{ORDINALS[number - 1]} Sunday after Trinity", "Trinity", epistle, gospel,
                 f"easter:{56 + number * 7}")
                for number, (epistle, gospel) in enumerate(TRINITY, 1))
    propers = []
    for sequence, (title, season, epistle, gospel, rule) in enumerate(rows, 1):
        proper_key = f"{PACKAGE_CODE}-{_key(title)}"
        readings = []
        for order, (role, label, citation) in enumerate((
            ("SECOND_READING", "Epistle", epistle), ("GOSPEL", "Gospel", gospel)), 1):
            readings.append({
                "appointment_key": f"{proper_key}-{role.casefold().replace('_', '-')}",
                "role": role, "display_role": label, "display_citation": citation,
                "normalized_citation": citation, "track_code": None,
                "option_group_code": None, "option_type": "DEFAULT",
                "paired_appointment_key": None, "sequence": order,
                "is_default": True, "note": "",
            })
        propers.append({
            "proper_key": proper_key, "cycle_key": None, "liturgical_date": title,
            "season": season, "sort": sequence * 10,
            "default_color": None, "alternate_color": None,
            "calendar_rule": rule, "note": "", "appointments": readings,
        })
    return {
        "package_code": PACKAGE_CODE, "package_version": "1.0.0", "schema_version": 1,
        "checksum": "0" * 64, "title": "ChurchManager Historic One-Year Lectionary",
        "source_name": SOURCE, "source_reference": SOURCE_REFERENCE,
        "package_notice": "Public-domain source; biblical citations and planning metadata only.",
        "distribution_scope": "REDISTRIBUTABLE", "systems": [{
            "system_key": f"{PACKAGE_CODE}-system", "name": "Historic One-Year Lectionary",
            "note": "Historic Epistle and Gospel cycle from a public-domain Lutheran source.",
            "editions": [{
                "edition_key": f"{PACKAGE_CODE}-1919", "name": "1919 Citation Edition",
                "edition_year": 1919, "status": "STABLE", "valid_from": None,
                "valid_through": None, "source_note": "Citation index derived from the 1919 Common Service Book.",
                "resolver_version": "1", "cycle_rule": "none", "cycles": [], "propers": propers,
            }],
        }],
    }


def main():
    """Validate and write the maintained redistributable package."""
    draft = build_draft()
    provenance = {
        "package_code": PACKAGE_CODE, "package_version": "1.0.0",
        "approval_status": "APPROVED", "reviewed_by": "Jonathan C. Watt",
        "reviewed_date": "2026-08-17", "source_owner": "Public domain",
        "redistribution_basis": "United States public-domain publication from 1919",
        "distribution_scope": "REDISTRIBUTABLE", "metadata_only_confirmed": True,
        "notes": "Only occasion names, calendar rules, roles, and biblical citations are included.",
    }
    package, summary = build_package(draft, provenance)
    target = Path("packages/lectionary/cm-historic-one-year-1.0.0.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    print(f"built={target} propers={summary.proper_count} appointments={summary.appointment_count}")


if __name__ == "__main__":
    main()
