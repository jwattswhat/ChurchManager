"""Reusable checksum-verified ChurchManager database migration service."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MigrationRecord:
    """One migration file with its exact source and checksum."""

    path: Path
    sql: str
    checksum: str

    @property
    def version(self):
        """Return the migration version recorded in the database."""
        return self.path.name


@dataclass(frozen=True)
class MigrationResult:
    """Summary returned after previewing or applying migrations."""

    applied: tuple[str, ...]
    pending: tuple[str, ...]
    newly_applied: tuple[str, ...]


class MigrationServiceError(RuntimeError):
    """Raised when migration history or execution is unsafe."""


def split_sql_statements(sql):
    """Split MariaDB migration source while honoring DELIMITER directives."""
    delimiter = ";"
    buffer = []
    result = []
    for line in str(sql).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        if stripped.upper().startswith("DELIMITER "):
            delimiter = stripped.split(None, 1)[1]
            continue
        buffer.append(line)
        joined = "\n".join(buffer).rstrip()
        if joined.endswith(delimiter):
            statement = joined[:-len(delimiter)].strip()
            if statement:
                result.append(statement)
            buffer = []
    if buffer:
        statement = "\n".join(buffer).strip()
        if statement:
            result.append(statement)
    return result


class MigrationService:
    """Preview and apply immutable numbered migrations on an open connection.

    The caller owns target selection, credentials, connection lifetime, backup,
    and authorization. This service never discovers or opens a database itself.
    """

    def __init__(
        self, connection, migration_directory, *, database_errors=(Exception,),
        before_apply=None, after_apply=None,
    ):
        self.connection = connection
        self.migration_directory = Path(migration_directory)
        self.database_errors = database_errors
        self.before_apply = before_apply
        self.after_apply = after_apply

    def records(self):
        """Load numbered migrations and calculate their source checksums."""
        records = []
        for path in sorted(self.migration_directory.glob("[0-9][0-9][0-9]_*.sql")):
            sql = path.read_text(encoding="utf-8-sig")
            records.append(MigrationRecord(
                path, sql, hashlib.sha256(sql.encode("utf-8")).hexdigest(),
            ))
        return tuple(records)

    @staticmethod
    def _history(cursor):
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='schema_migrations'"
        )
        if not cursor.fetchone()[0]:
            return {}
        cursor.execute("SELECT version, checksum FROM schema_migrations")
        return dict(cursor.fetchall())

    def run(self, *, apply=False, notify=None):
        """Preview or apply pending migrations and return a structured result."""
        notify = notify or (lambda _message: None)
        cursor = self.connection.cursor()
        try:
            history = self._history(cursor)
            applied = []
            pending = []
            for record in self.records():
                if record.version in history:
                    if history[record.version] != record.checksum:
                        raise MigrationServiceError(
                            f"Applied migration checksum changed: {record.version}"
                        )
                    applied.append(record.version)
                    notify(f"applied {record.version}")
                else:
                    pending.append(record)
                    notify(f"pending {record.version}")

            if pending and not apply:
                return MigrationResult(
                    tuple(applied), tuple(item.version for item in pending), (),
                )
            if pending:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS schema_migrations ("
                    "version varchar(100) NOT NULL PRIMARY KEY, "
                    "checksum char(64) NOT NULL, "
                    "applied_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP"
                    ") ENGINE=InnoDB"
                )
            newly_applied = []
            for record in pending:
                notify(f"applying {record.version}")
                if self.before_apply:
                    self.before_apply(cursor, record)
                for statement in split_sql_statements(record.sql):
                    try:
                        cursor.execute(statement)
                    except self.database_errors as error:
                        first_line = statement.splitlines()[0][:120]
                        raise MigrationServiceError(
                            f"Migration {record.version} failed at: {first_line}"
                        ) from error
                if self.after_apply:
                    self.after_apply(cursor, record)
                cursor.execute(
                    "INSERT INTO schema_migrations (version, checksum) VALUES (?, ?)",
                    (record.version, record.checksum),
                )
                newly_applied.append(record.version)
            return MigrationResult(
                tuple(applied), tuple(item.version for item in pending),
                tuple(newly_applied),
            )
        finally:
            cursor.close()
