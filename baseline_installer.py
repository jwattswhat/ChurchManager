"""Install and verify a canonical ChurchManager schema in an empty database."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from migration_service import MigrationService, split_sql_statements
from schema_hygiene import require_clean_schema
from baseline_seed import build_seed_artifact


class BaselineInstallationError(RuntimeError):
    """Raised when a schema baseline is unsafe, inconsistent, or fails."""


def load_baseline(schema_path, manifest_path, migration_directory):
    """Load and verify schema, manifest checksum, and represented migrations."""
    schema = Path(schema_path).read_text(encoding="utf-8")
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    require_clean_schema(schema)
    if manifest.get("format_version") != 1:
        raise BaselineInstallationError("The baseline manifest format is unsupported.")
    digest = hashlib.sha256(schema.encode("utf-8")).hexdigest()
    if manifest.get("schema_sha256") != digest:
        raise BaselineInstallationError("The baseline schema checksum does not match.")
    expected = [
        {"version": record.version, "checksum": record.checksum}
        for record in MigrationService(None, migration_directory).records()
    ]
    if manifest.get("represented_migrations") != expected:
        raise BaselineInstallationError(
            "The baseline migration ledger does not match the release migrations."
        )
    return schema, manifest


def load_seed(seed_path, seed_manifest_path, migration_directory):
    """Load and verify starter data against its checksum and migration sources."""
    sql = Path(seed_path).read_text(encoding="utf-8")
    manifest = json.loads(Path(seed_manifest_path).read_text(encoding="utf-8"))
    expected = build_seed_artifact(migration_directory, manifest.get("release_version"))
    digest = hashlib.sha256(sql.encode("utf-8")).hexdigest()
    if manifest.get("format_version") != 1:
        raise BaselineInstallationError("The seed manifest format is unsupported.")
    if manifest.get("seed_sha256") != digest:
        raise BaselineInstallationError("The starter-data checksum does not match.")
    if manifest != expected.manifest or sql != expected.sql:
        raise BaselineInstallationError(
            "The starter data does not match the release migrations."
        )
    return sql, manifest


class BaselineInstaller:
    """Apply a verified baseline only to the currently selected empty database."""

    def __init__(self, connection, *, database_errors=(Exception,)):
        self.connection = connection
        self.database_errors = database_errors

    def install(self, schema, manifest, seed_sql):
        """Create schema objects, seed migration history, and verify the result."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()"
            )
            if int(cursor.fetchone()[0]):
                raise BaselineInstallationError(
                    "The baseline can be installed only into an empty database."
                )
            statements = split_sql_statements(schema)
            if not statements:
                raise BaselineInstallationError("The baseline schema is empty.")
            for statement in statements:
                try:
                    cursor.execute(statement)
                except self.database_errors as error:
                    first_line = statement.splitlines()[0][:120]
                    raise BaselineInstallationError(
                        "Baseline installation failed at: " + first_line
                    ) from error
            seed_statements = split_sql_statements(seed_sql)
            if not seed_statements:
                raise BaselineInstallationError("The starter-data baseline is empty.")
            for statement in seed_statements:
                try:
                    cursor.execute(statement)
                except self.database_errors as error:
                    first_line = statement.splitlines()[0][:120]
                    raise BaselineInstallationError(
                        "Starter-data installation failed at: " + first_line
                    ) from error
            for record in manifest["represented_migrations"]:
                cursor.execute(
                    "INSERT INTO schema_migrations (version, checksum) VALUES (?, ?)",
                    (record["version"], record["checksum"]),
                )
            cursor.execute("SELECT COUNT(*) FROM schema_migrations")
            migration_count = int(cursor.fetchone()[0])
            if migration_count != len(manifest["represented_migrations"]):
                raise BaselineInstallationError(
                    "The installed migration history did not verify."
                )
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()"
            )
            object_count = int(cursor.fetchone()[0])
            if not object_count:
                raise BaselineInstallationError("The installed schema contains no objects.")
            cursor.execute("SELECT COUNT(*) FROM tblRole WHERE Name='Master Administrator'")
            if int(cursor.fetchone()[0]) != 1:
                raise BaselineInstallationError(
                    "The Master Administrator role was not installed."
                )
            cursor.execute("SELECT COUNT(*) FROM tblPermission WHERE Active=1")
            permission_count = int(cursor.fetchone()[0])
            if not permission_count:
                raise BaselineInstallationError("No active permissions were installed.")
            self.connection.commit()
            return {
                "database_objects": object_count,
                "represented_migrations": migration_count,
                "active_permissions": permission_count,
                "schema_sha256": manifest["schema_sha256"],
            }
        finally:
            cursor.close()
