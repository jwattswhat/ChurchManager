"""Create a checksum-verified dump of the configured local test database."""

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


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
    testing = config["testing"]
    host = str(testing["host"])
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("Safety stop: local test backup host is not local.")
    database = str(testing["database"])
    if "test" not in database.casefold():
        raise RuntimeError("Safety stop: only test databases may be backed up here.")
    username, password = read_credential(testing["credential_target"])
    destination = BACKUP_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S")
    destination.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy(); environment["MYSQL_PWD"] = password
    results = []
    try:
        for database in (database,):
            output = destination / "{}.sql".format(database)
            command = [str(DUMP_EXE), "--host", host,
                       "--port", str(testing.get("port", 3306)), "--user", username,
                       "--skip-ssl", "--single-transaction", "--routines", "--events",
                       "--triggers", "--hex-blob", "--default-character-set=utf8mb4",
                       "--databases", database]
            with output.open("wb") as stream:
                subprocess.run(command, stdout=stream, check=True, env=environment)
            size = output.stat().st_size
            if size < 100:
                raise RuntimeError("Backup for {} is unexpectedly small.".format(database))
            results.append({"database":database, "file":output.name,
                            "bytes":size, "sha256":sha256(output)})
    finally:
        environment.pop("MYSQL_PWD", None); password = ""
    (destination / "manifest.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(destination)
    for result in results:
        print(result["database"], result["bytes"], result["sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
