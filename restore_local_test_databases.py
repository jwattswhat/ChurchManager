"""Restore verified test-only dumps to localhost MariaDB."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import mariadb

from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "LocalTestMigrationBackups" / "20260811-054650"
CLIENT_EXE = Path(r"C:\Program Files\MariaDB 12.1\bin\mariadb.exe")
TARGET = "ChurchManager/LocalTestAdmin"
ALLOWED_DATABASES = ("ChurchDBTest", "JSFormTest")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    manifest = json.loads((BACKUP / "manifest.json").read_text(encoding="utf-8"))
    by_database = {entry["database"]: entry for entry in manifest}
    if set(by_database) != set(ALLOWED_DATABASES):
        raise RuntimeError("Backup manifest does not contain exactly the two test databases")
    for database in ALLOWED_DATABASES:
        entry = by_database[database]
        dump = BACKUP / entry["file"]
        if sha256(dump) != entry["sha256"]:
            raise RuntimeError(f"Checksum mismatch for {database}")

    username, password = read_credential(TARGET)
    connection = mariadb.connect(
        host="127.0.0.1", port=3306, user=username, password=password
    )
    try:
        cursor = connection.cursor()
        placeholders = ",".join("?" for _ in ALLOWED_DATABASES)
        cursor.execute(
            "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA "
            f"WHERE SCHEMA_NAME IN ({placeholders})",
            ALLOWED_DATABASES,
        )
        existing = [row[0] for row in cursor.fetchall()]
        if existing:
            raise RuntimeError(
                "Refusing to overwrite existing local test databases: "
                + ", ".join(existing)
            )
    finally:
        connection.close()

    environment = os.environ.copy()
    environment["MYSQL_PWD"] = password
    try:
        for database in ALLOWED_DATABASES:
            dump = BACKUP / by_database[database]["file"]
            restore_dump = BACKUP / f"{database}.local-restore.sql"
            restored_bytes, replacements = re.subn(
                rb"DEFINER=`[^`]+`@`[^`]+`",
                b"DEFINER=CURRENT_USER",
                dump.read_bytes(),
            )
            restore_dump.write_bytes(restored_bytes)
            print(f"{database}: normalized {replacements} remote definers.")
            command = [
                str(CLIENT_EXE),
                "--host", "127.0.0.1",
                "--port", "3306",
                "--user", username,
                "--skip-ssl",
            ]
            with restore_dump.open("rb") as stream:
                subprocess.run(command, stdin=stream, check=True, env=environment)
            print(f"Restored {database}.")
    finally:
        environment.pop("MYSQL_PWD", None)
        password = ""

    username, password = read_credential(TARGET)
    connection = mariadb.connect(
        host="127.0.0.1", port=3306, user=username, password=password
    )
    try:
        cursor = connection.cursor()
        for database in ALLOWED_DATABASES:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.TABLES "
                "WHERE TABLE_SCHEMA=?",
                (database,),
            )
            print(f"{database}: {cursor.fetchone()[0]} tables/views")
    finally:
        password = ""
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
