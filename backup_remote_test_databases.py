"""Create verified, read-only dumps of the remote test databases."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
import subprocess

from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "churchmanager.json"
DUMP_EXE = Path(r"C:\Program Files\MariaDB 12.1\bin\mariadb-dump.exe")
BACKUP_ROOT = ROOT / "LocalTestMigrationBackups"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    settings = config["database_settings"]
    testing = config["testing"]
    username, password = read_credential(testing["credential_target"])
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = BACKUP_ROOT / stamp
    destination.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    environment["MYSQL_PWD"] = password
    results = []
    try:
        for database in (testing["database"], testing["jsform_database"]):
            output = destination / f"{database}.sql"
            command = [
                str(DUMP_EXE),
                "--host", str(settings["host"]),
                "--port", str(settings.get("port", 3306)),
                "--user", username,
                "--skip-ssl",
                "--single-transaction",
                "--routines",
                "--events",
                "--triggers",
                "--hex-blob",
                "--default-character-set=utf8mb4",
                "--databases", database,
            ]
            with output.open("wb") as stream:
                subprocess.run(command, stdout=stream, check=True, env=environment)
            size = output.stat().st_size
            if size == 0:
                raise RuntimeError(f"Empty backup created for {database}")
            results.append({
                "database": database,
                "file": output.name,
                "bytes": size,
                "sha256": sha256(output),
            })
    finally:
        environment.pop("MYSQL_PWD", None)
        password = ""
    manifest = destination / "manifest.json"
    manifest.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(destination)
    for result in results:
        print(result["database"], result["bytes"], result["sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
