"""Build the canonical non-congregation starter data for a fresh installation."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from migration_service import MigrationService, split_sql_statements


SEED_TABLES = frozenset({
    "tblchoices",
    "tblmailsettings",
    "tblpermission",
    "tblreports",
    "tblrole",
    "tblrolepermission",
    "tblworshipchecklisttemplate",
    "tblworshipchecklisttemplateitem",
    "tblworshiprole",
})
EXTRACTED_SEED_TABLES = SEED_TABLES - {"tblworshiprole"}
CURRENT_SCHEMA_SEEDS = (
    "INSERT INTO tblWorshipRole (Name,Description,DisplayOrder,Active) VALUES\n"
    "('Liturgist',NULL,10,1),('Crucifer','Carries the cross',20,1),\n"
    "('Preacher',NULL,30,1),('Thurifer','Carries the thurible',40,1),\n"
    "('Candle-Bearer',NULL,50,1),('Acolyte','Lights candles',60,1),\n"
    "('Reader',NULL,70,1),('Cantor',NULL,80,1),\n"
    "('Lector','Reads the lessons',90,1),('Organist',NULL,100,1),\n"
    "('Accompanist',NULL,110,1),('Elder',NULL,120,1)\n"
    "ON DUPLICATE KEY UPDATE Description=VALUES(Description),"
    "DisplayOrder=VALUES(DisplayOrder),Active=VALUES(Active)",
)
_INSERT = re.compile(r"^INSERT(?:\s+IGNORE)?\s+INTO\s+`?([A-Za-z0-9_]+)`?", re.I)
_UPDATE = re.compile(r"^UPDATE\s+`?([A-Za-z0-9_]+)`?", re.I)
_DELETE_FROM = re.compile(r"^DELETE\s+FROM\s+`?([A-Za-z0-9_]+)`?", re.I)
_DELETE_ALIAS = re.compile(
    r"^DELETE\s+[A-Za-z0-9_]+\s+FROM\s+`?([A-Za-z0-9_]+)`?", re.I,
)


@dataclass(frozen=True)
class SeedArtifact:
    """Canonical starter-data SQL and its password-free manifest."""

    sql: str
    manifest: dict


def mutation_table(statement):
    """Return the directly mutated table for one supported DML statement."""
    text = str(statement or "").lstrip()
    for pattern in (_INSERT, _UPDATE, _DELETE_FROM, _DELETE_ALIAS):
        match = pattern.match(text)
        if match:
            return match.group(1).casefold()
    return None


def build_seed_artifact(migration_directory, version):
    """Extract approved catalog mutations from immutable migration history."""
    parts = []
    sources = []
    records = MigrationService(None, migration_directory).records()
    for record in records:
        included = 0
        for statement in split_sql_statements(record.sql):
            if mutation_table(statement) in EXTRACTED_SEED_TABLES:
                parts.append(f"-- source: {record.version}\n{statement};")
                included += 1
        if included:
            sources.append({
                "version": record.version,
                "checksum": record.checksum,
                "statements": included,
            })
    for statement in CURRENT_SCHEMA_SEEDS:
        parts.append("-- source: current-schema starter policy\n" + statement + ";")
    sql = "\n\n".join(parts).strip() + "\n"
    manifest = {
        "artifact": "ChurchManager fresh-install starter-data baseline",
        "format_version": 1,
        "release_version": str(version),
        "seed_sha256": hashlib.sha256(sql.encode("utf-8")).hexdigest(),
        "statement_count": len(parts),
        "source_migrations": sources,
        "current_schema_statements": len(CURRENT_SCHEMA_SEEDS),
        "tables": sorted(SEED_TABLES),
    }
    return SeedArtifact(sql, manifest)


def write_seed_artifact(artifact, directory):
    """Write an already constructed seed artifact to the release tree."""
    if not isinstance(artifact, SeedArtifact):
        raise TypeError("A seed artifact is required.")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    sql_path = root / "baseline_seed.sql"
    manifest_path = root / "baseline_seed_manifest.json"
    sql_path.write_text(artifact.sql, encoding="utf-8", newline="\n")
    manifest_path.write_text(
        json.dumps(artifact.manifest, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    return sql_path, manifest_path
