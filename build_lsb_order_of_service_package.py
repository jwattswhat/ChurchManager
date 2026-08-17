"""Build the metadata-only LSB Order of Service package deterministically."""

from __future__ import annotations

import json
import re
from pathlib import Path

from order_of_service_packages import canonical_package_checksum


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "packages" / "order_of_service" / "lsb-services-1.0.0.json"


def _key(text):
    """Return a stable package key from a short planning label."""
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")


def _type(label):
    """Infer the supported planning type for a metadata-only outline label."""
    lowered = label.casefold()
    if "hymn" in lowered or lowered in {"offertory"}:
        return "HYMN"
    if "reading" in lowered or lowered in {"epistle", "holy gospel", "gospel"}:
        return "READING"
    if "sermon" in lowered or "homily" in lowered:
        return "SERMON"
    if "offering" in lowered:
        return "OFFERING"
    if lowered in {"distribution", "service of the sacrament"}:
        return "COMMUNION"
    if lowered.startswith("service of ") or lowered in {"preparation", "opening", "closing"}:
        return "HEADING"
    return "LITURGY"


def _lines(labels, page=None):
    """Create numbered outline lines without including published service text."""
    result = []
    used = {}
    for sequence, label in enumerate(labels, start=1):
        base = _key(label)
        used[base] = used.get(base, 0) + 1
        line_key = base if used[base] == 1 else f"{base}-{used[base]}"
        line = {
            "line_key": line_key,
            "sequence": sequence,
            "line_type": _type(label),
            "label": label,
        }
        if sequence == 1 and page:
            line["reference"] = f"LSB p. {page}"
        if line["line_type"] == "HYMN":
            line.update({
                "value_source": "SUGGESTED_USE",
                "value_key": _key(label),
                "reference": label,
            })
        if label == "Service of the Sacrament" or label.startswith("Distribution"):
            line["condition"] = "COMMUNION"
        result.append(line)
    return result


DIVINE_SERVICE = [
    "Preparation", "Hymn of Invocation", "Confession and Absolution",
    "Service of the Word", "Introit or Psalm", "Kyrie", "Hymn of Praise",
    "Salutation and Collect of the Day", "Old Testament Reading", "Epistle",
    "Verse", "Holy Gospel", "Creed", "Hymn of the Day", "Sermon",
    "Offering", "Prayer of the Church", "Service of the Sacrament", "Preface",
    "Sanctus", "Lord's Prayer", "Words of Institution", "Pax Domini",
    "Agnus Dei", "Distribution", "Distribution Hymn", "Distribution Hymn",
    "Distribution Hymn", "Post-Communion Canticle", "Post-Communion Collect",
    "Benediction", "Closing Hymn",
]


SERVICE_DEFINITIONS = [
    ("divine-service-setting-one", "LSB Divine Service, Setting One", 151, DIVINE_SERVICE),
    ("divine-service-setting-two", "LSB Divine Service, Setting Two", 167, DIVINE_SERVICE),
    ("divine-service-setting-three", "LSB Divine Service, Setting Three", 184, DIVINE_SERVICE),
    ("divine-service-setting-four", "LSB Divine Service, Setting Four", 203, DIVINE_SERVICE),
    ("divine-service-setting-five", "LSB Divine Service, Setting Five", 213, DIVINE_SERVICE),
    ("matins", "LSB Matins", 219, [
        "Opening", "Invitatory", "Venite", "Psalmody", "Office Hymn", "Reading",
        "Responsory", "Sermon", "Canticle", "Prayer", "Lord's Prayer", "Collects", "Benedicamus", "Benediction",
    ]),
    ("vespers", "LSB Vespers", 229, [
        "Opening", "Psalmody", "Office Hymn", "Reading", "Responsory", "Sermon",
        "Magnificat", "Prayer", "Kyrie", "Lord's Prayer", "Collects", "Benedicamus", "Benediction",
    ]),
    ("morning-prayer", "LSB Morning Prayer", 235, [
        "Opening", "Confession and Absolution", "Psalmody", "Office Hymn", "Reading",
        "Responsory", "Sermon", "Benedictus", "Prayer", "Lord's Prayer", "Collects", "Benedicamus", "Benediction",
    ]),
    ("evening-prayer", "LSB Evening Prayer", 243, [
        "Opening", "Service of Light", "Psalmody", "Office Hymn", "Reading", "Responsory",
        "Sermon", "Magnificat", "Prayer", "Litany", "Lord's Prayer", "Collects", "Benedicamus", "Benediction",
    ]),
    ("compline", "LSB Compline", 253, [
        "Opening", "Confession and Absolution", "Psalmody", "Office Hymn", "Reading",
        "Responsory", "Prayer", "Lord's Prayer", "Collects", "Nunc Dimittis", "Benediction",
    ]),
    ("service-of-prayer-and-preaching", "LSB Service of Prayer and Preaching", 260, [
        "Opening Hymn", "Opening", "Old Testament Canticle", "Reading", "Responsory",
        "Catechism", "Sermon", "Hymn", "Prayer", "Litany", "Collects", "New Testament Canticle", "Benediction",
    ]),
    ("responsive-prayer-1", "LSB Responsive Prayer 1—Suffrages", 282, [
        "Opening", "Creed", "Versicles", "Lord's Prayer", "Collects", "Morning or Evening Prayer", "Benedicamus",
    ]),
    ("responsive-prayer-2", "LSB Responsive Prayer 2", 285, [
        "Opening", "Reading", "Responsory", "Creed", "Litany", "Lord's Prayer", "Collects", "Benedicamus",
    ]),
    ("the-litany", "LSB The Litany", 288, ["Opening Hymn", "Invocation", "The Litany", "Lord's Prayer", "Collect", "Closing Hymn"]),
    ("corporate-confession-and-absolution", "LSB Corporate Confession and Absolution", 290, [
        "Opening Hymn", "Invocation", "Exhortation", "Confession", "Absolution", "Thanksgiving", "Closing Hymn",
    ]),
    ("holy-baptism", "LSB Holy Baptism", 268, [
        "Opening Hymn", "Invocation", "Presentation", "Readings", "Address", "Renunciation",
        "Creed", "Baptism", "Blessing", "Prayer", "Lord's Prayer", "Closing Hymn",
    ]),
    ("holy-baptism-alternate", "LSB Holy Baptism—Alternate Form", None, [
        "Opening Hymn", "Invocation", "Presentation", "Readings", "Address", "Renunciation",
        "Creed", "Baptism", "Blessing", "Prayer", "Lord's Prayer", "Closing Hymn",
    ]),
    ("confirmation", "LSB Confirmation", 272, [
        "Opening Hymn", "Presentation", "Address", "Creed", "Questions", "Blessing",
        "Prayer", "Lord's Prayer", "Closing Hymn",
    ]),
    ("holy-matrimony", "LSB Holy Matrimony", 275, [
        "Processional Hymn", "Invocation", "Readings", "Address", "Declaration of Intent",
        "Vows", "Giving of Rings", "Blessing", "Prayer", "Lord's Prayer", "Benediction", "Recessional Hymn",
    ]),
    ("entrance-of-the-body", "LSB Entrance of the Body into the Church", None, [
        "Opening", "Entrance", "Processional Hymn", "Remembrance of Baptism", "Prayer",
    ]),
    ("funeral-service", "LSB Funeral Service", 278, [
        "Opening", "Processional Hymn", "Remembrance of Baptism", "Psalm", "Kyrie",
        "Prayer", "Old Testament Reading", "Epistle", "Holy Gospel", "Hymn", "Sermon",
        "Creed", "Prayer of the Church", "Lord's Prayer", "Nunc Dimittis", "Commendation", "Benediction", "Recessional Hymn",
    ]),
    ("individual-confession-and-absolution", "LSB Individual Confession and Absolution", 292, [
        "Opening", "Confession", "Absolution", "Closing",
    ]),
]


def build_package():
    """Return the complete safe catalog with a canonical checksum."""
    templates = []
    for template_key, name, page, labels in SERVICE_DEFINITIONS:
        templates.append({
            "template_key": f"lsb-{template_key}",
            "name": name,
            "description": "Metadata-only planning outline; no published service text is included.",
            "hymnal_package_code": "lsb",
            "lines": _lines(labels, page),
            "required_positions": [],
        })
    package = {
        "package_code": "lsb-service-outlines",
        "package_version": "1.0.0",
        "title": "LSB Order of Service Outlines",
        "template_prefix": "LSB ",
        "source_name": "Lutheran Service Book",
        "source_reference": "Official CPH LSB contents listing and congregation-owned publication",
        "package_notice": "Planning metadata and short labels only; no liturgical text, lyrics, music, prayers, rubrics, or artwork.",
        "hymnal_package_code": "lsb",
        "minimum_hymnal_version": "1.0.0",
        "schema_version": 1,
        "checksum": "",
        "templates": templates,
    }
    package["checksum"] = canonical_package_checksum(package)
    return package


def main():
    """Write stable formatted JSON for review and installation."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build_package(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote={OUTPUT}")


if __name__ == "__main__":
    main()
