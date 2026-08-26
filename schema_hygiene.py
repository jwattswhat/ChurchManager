"""Fail-closed hygiene checks for the canonical fresh-install SQL baseline."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaFinding:
    """One actionable baseline-schema problem."""

    code: str
    line: int
    message: str
    excerpt: str


_RULES = (
    ("obsolete_identifier", re.compile(
        r"\b(?:OldID|LegacyRoleID|SourceLegacyScheduleID|SourceLegacyName|LegacyContent)\b",
        re.IGNORECASE,
    ), "Obsolete conversion identifier is not allowed."),
    ("retired_table", re.compile(
        r"\b(?:tblOrderofService|tblSchedule|tblCheckList|tblAltReading|tblEnhancement)\b",
        re.IGNORECASE,
    ), "Retired table is not allowed."),
    ("test_database", re.compile(
        r"(?<![A-Za-z0-9])(?:ChurchDBTest|JSFormTest)(?![A-Za-z0-9])", re.IGNORECASE,
    ),
     "Development/test database name is not allowed."),
    ("object_definer", re.compile(r"\bDEFINER\s*=", re.IGNORECASE),
     "Database objects in the baseline must not contain an account definer."),
    ("account_statement", re.compile(
        r"^\s*(?:CREATE|ALTER|DROP)\s+USER\b|^\s*(?:GRANT|REVOKE)\b", re.IGNORECASE,
    ), "Database-account statements belong to guarded provisioning, not the baseline."),
    ("database_statement", re.compile(
        r"^\s*(?:CREATE|ALTER|DROP)\s+DATABASE\b|^\s*USE\s+", re.IGNORECASE,
    ), "Database selection and creation belong to guarded provisioning."),
    ("data_statement", re.compile(
        r"^\s*(?:INSERT|REPLACE|UPDATE|DELETE)\s+", re.IGNORECASE,
    ), "The canonical schema baseline must not contain operational or fixture data."),
    ("destructive_statement", re.compile(
        r"^\s*(?:DROP|TRUNCATE)\s+(?:TABLE|VIEW|PROCEDURE|FUNCTION|TRIGGER|EVENT)\b",
        re.IGNORECASE,
    ), "A fresh empty-database baseline must not contain destructive object statements."),
    ("dump_state", re.compile(
        r"\bAUTO_INCREMENT\s*=\s*\d+|^\s*LOCK TABLES\b|DISABLE KEYS",
        re.IGNORECASE,
    ), "Development database state is not allowed in the canonical baseline."),
    ("machine_path", re.compile(
        r"(?:[A-Za-z]:\\(?:Users|Program Files|ProgramData)\\|/home/[^/]+/)",
        re.IGNORECASE,
    ), "Machine-specific filesystem path is not allowed."),
)


def scan_schema_sql(sql):
    """Return all unapproved residue found in baseline schema SQL."""
    findings = []
    for number, line in enumerate(str(sql).splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        for code, pattern, message in _RULES:
            if pattern.search(line):
                findings.append(SchemaFinding(code, number, message, stripped[:180]))
    return tuple(findings)


def require_clean_schema(sql):
    """Raise a concise error when a proposed baseline contains any finding."""
    findings = scan_schema_sql(sql)
    if findings:
        summary = "; ".join(
            f"line {item.line}: {item.code}" for item in findings[:10]
        )
        if len(findings) > 10:
            summary += f"; and {len(findings) - 10} more"
        raise ValueError("Canonical schema hygiene check failed: " + summary)
    return True
