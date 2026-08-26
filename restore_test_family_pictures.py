"""Restore preserved family pictures to local ChurchDBTest by exact family ID."""

import argparse
from datetime import datetime
import json
from pathlib import Path

import mariadb

from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "BackupDB" / "TestDatabaseFamilyPictures"
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))["testing"]
    if config["host"] not in LOCAL_HOSTS or config["database"].casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: family-picture restore requires local ChurchDBTest.")
    username, password = read_credential(config["credential_target"])
    connection = mariadb.connect(
        host=config["host"], port=int(config.get("port", 3306)),
        database=config["database"], user=username, password=password, autocommit=False,
    )
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT ID,FamilyName,Image FROM rpt_directory_family ORDER BY ID")
        families = cursor.fetchall()
        planned = []
        for family_id, family_name, existing in families:
            path = SOURCE / f"Family.{family_id:03d}.jpg"
            if not path.is_file():
                raise RuntimeError(f"Missing preserved picture for {family_id}: {family_name}")
            data = path.read_bytes()
            if not (data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9")):
                raise RuntimeError(f"Invalid JPEG picture: {path.name}")
            planned.append((family_id, family_name, existing, data))
        print(f"target={config['database']} families={len(families)} matched={len(planned)}")
        print(f"existing_images={sum(bool(item[2]) for item in planned)}")
        if not args.apply:
            print("No changes made. Re-run with --apply after reviewing this preview.")
            connection.rollback()
            return
        backup = ROOT / "BackupDB" / (
            "ChurchDBTest.FamilyPictures.before-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        )
        backup.mkdir(parents=True, exist_ok=False)
        manifest = []
        for family_id, family_name, existing, data in planned:
            if existing:
                (backup / f"Family.{family_id:03d}.bin").write_bytes(bytes(existing))
            manifest.append({"ID": family_id, "FamilyName": family_name, "HadImage": bool(existing)})
            cursor.execute("UPDATE tblFamily SET Image=? WHERE ID=?", (data, family_id))
        (backup / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
        )
        connection.commit()
        cursor.execute(
            "SELECT COUNT(*) FROM rpt_directory_family "
            "WHERE Image IS NOT NULL AND OCTET_LENGTH(Image)>0"
        )
        restored = cursor.fetchone()[0]
        if restored != len(planned):
            raise RuntimeError(f"Verification failed: expected {len(planned)}, found {restored}")
        print(f"restored={restored} backup={backup}")
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
