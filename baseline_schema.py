"""Build a deterministic, hygiene-checked fresh-install schema baseline."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from migration_service import MigrationService
from schema_hygiene import require_clean_schema


_DATABASE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,63}$")
_DEFINER = re.compile(
    r"\bDEFINER\s*=\s*(?:`[^`]*`|'[^']*'|[^\s@]+)\s*@\s*"
    r"(?:`[^`]*`|'[^']*'|[^\s*/]+)", re.IGNORECASE,
)
_AUTO_INCREMENT = re.compile(r"\s+AUTO_INCREMENT\s*=\s*\d+", re.IGNORECASE)


@dataclass(frozen=True)
class BaselineArtifact:
    """Canonical schema text and its password-free release manifest."""

    sql: str
    manifest: dict


def canonical_schema_dump(dump_sql, source_database):
    """Remove permitted dump-specific state without hiding obsolete schema."""
    database = str(source_database or "").strip()
    if not _DATABASE.fullmatch(database):
        raise ValueError("The schema source database name is invalid.")
    qualifier = re.compile(rf"`{re.escape(database)}`\.", re.IGNORECASE)
    result = []
    for line in str(dump_sql).replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        stripped = line.strip()
        if stripped.startswith("--") or stripped.startswith("/*M!"):
            continue
        line = qualifier.sub("", line)
        line = _DEFINER.sub("", line)
        line = _AUTO_INCREMENT.sub("", line)
        if line.strip():
            result.append(line.rstrip())
    canonical = "\n".join(result).strip() + "\n"
    require_clean_schema(canonical)
    return canonical


def build_baseline_artifact(dump_sql, source_database, migration_directory, version):
    """Return canonical SQL plus the represented immutable migration ledger."""
    sql = canonical_schema_dump(dump_sql, source_database)
    records = MigrationService(None, migration_directory).records()
    migrations = [
        {"version": record.version, "checksum": record.checksum}
        for record in records
    ]
    manifest = {
        "artifact": "ChurchManager fresh-install schema baseline",
        "format_version": 1,
        "release_version": str(version),
        "schema_sha256": hashlib.sha256(sql.encode("utf-8")).hexdigest(),
        "represented_migrations": migrations,
    }
    return BaselineArtifact(sql, manifest)


def write_baseline_artifact(artifact, directory):
    """Write an already validated baseline and manifest to the release tree."""
    if not isinstance(artifact, BaselineArtifact):
        raise TypeError("A validated baseline artifact is required.")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    schema_path = root / "baseline_schema.sql"
    manifest_path = root / "baseline_manifest.json"
    schema_path.write_text(artifact.sql, encoding="utf-8", newline="\n")
    manifest_path.write_text(
        json.dumps(artifact.manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    return schema_path, manifest_path
