"""Restore the approved fictional family and person pictures to local ChurchDBTest."""

import argparse
from datetime import datetime
from getpass import getpass
from io import BytesIO
import json
from pathlib import Path

import mariadb
from PIL import Image

from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
DEFAULT_SOURCES = (
    ROOT / "BackupDB" / "TestDatabaseFamilyPictures",
    Path(r"D:\Backup.ChurchManager\DatabaseArchive\TestDatabaseFamilyPictures"),
)


def source_directory():
    for candidate in DEFAULT_SOURCES:
        if candidate.is_dir():
            return candidate
    raise RuntimeError("The approved TestDatabaseFamilyPictures backup was not found.")


def credentials(target, configured_user):
    try:
        return read_credential(target)
    except KeyError:
        password = getpass(f"MariaDB password for {configured_user}: ")
        if not password:
            raise RuntimeError("No database password was entered.")
        return configured_user, password


def portrait_crops(image, count):
    """Return portraits in the same left-to-right, top-to-bottom order used by the composites."""
    if image.size != (512, 320):
        raise RuntimeError(f"Unexpected family-picture size: {image.size}")
    if count == 0:
        return []
    if count == 1:
        boxes = [(168, 72, 344, 249)]
    elif count == 2:
        boxes = [(73, 72, 249, 249), (264, 72, 440, 249)]
    elif count in (3, 4):
        boxes = [
            (110, 14, 249, 153), (264, 14, 403, 153),
            (110, 168, 249, 307), (264, 168, 403, 307),
        ][:count]
    elif count == 5:
        boxes = [
            (74, 41, 186, 153), (200, 41, 312, 153), (327, 41, 439, 153),
            (74, 168, 186, 280), (200, 168, 312, 280),
        ]
    else:
        raise RuntimeError(f"No approved portrait layout exists for a {count}-person family.")
    results = []
    for box in boxes:
        output = BytesIO()
        image.crop(box).convert("RGB").save(output, "JPEG", quality=92)
        results.append(output.getvalue())
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write after displaying the exact plan")
    args = parser.parse_args()

    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))["testing"]
    host = config["host"]
    database = config["database"]
    if host not in LOCAL_HOSTS or database.casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: picture restore requires local ChurchDBTest.")

    source = source_directory()
    username, password = credentials(config["credential_target"], config.get("user", "church"))
    connection = mariadb.connect(
        host=host, port=int(config.get("port", 3306)), database=database,
        user=username, password=password, autocommit=False,
    )
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT ID, FamilyName, Image FROM tblFamily ORDER BY ID")
        families = cursor.fetchall()
        plan = []
        for family_id, family_name, old_family_image in families:
            picture_path = source / f"Family.{family_id:03d}.jpg"
            if not picture_path.is_file():
                raise RuntimeError(f"Missing approved family picture for {family_id}: {family_name}")
            family_image = picture_path.read_bytes()
            if not (family_image.startswith(b"\xff\xd8\xff") and family_image.endswith(b"\xff\xd9")):
                raise RuntimeError(f"Invalid JPEG: {picture_path.name}")
            cursor.execute(
                "SELECT ID, FirstName, LastName, Picture FROM tblPerson "
                "WHERE FamilyID=? ORDER BY ID", (family_id,),
            )
            people = cursor.fetchall()
            portraits = portrait_crops(Image.open(BytesIO(family_image)), len(people))
            plan.append((family_id, family_name, old_family_image, family_image, people, portraits))

        person_count = sum(len(item[4]) for item in plan)
        print(f"target={host}/{database}")
        print(f"source={source}")
        print(f"families={len(plan)} people={person_count}")
        print(f"existing_family_images={sum(bool(item[2]) for item in plan)}")
        print(f"existing_person_images={sum(bool(person[3]) for item in plan for person in item[4])}")
        if not args.apply:
            connection.rollback()
            print("No changes made. Re-run with --apply after reviewing this preview.")
            return

        backup = ROOT / "BackupDB" / (
            "ChurchDBTest.DirectoryPictures.before-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        )
        backup.mkdir(parents=True, exist_ok=False)
        manifest = []
        for family_id, family_name, old_family_image, family_image, people, portraits in plan:
            if old_family_image:
                (backup / f"Family.{family_id:03d}.bin").write_bytes(bytes(old_family_image))
            cursor.execute("UPDATE tblFamily SET Image=? WHERE ID=?", (family_image, family_id))
            family_entry = {
                "ID": family_id, "FamilyName": family_name,
                "HadImage": bool(old_family_image), "People": [],
            }
            for person, portrait in zip(people, portraits):
                person_id, first_name, last_name, old_picture = person
                if old_picture:
                    (backup / f"Person.{person_id:03d}.bin").write_bytes(bytes(old_picture))
                cursor.execute("UPDATE tblPerson SET Picture=? WHERE ID=?", (portrait, person_id))
                family_entry["People"].append({
                    "ID": person_id, "Name": f"{first_name} {last_name}".strip(),
                    "HadPicture": bool(old_picture),
                })
            manifest.append(family_entry)
        (backup / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
        )
        connection.commit()

        cursor.execute("SELECT COUNT(*) FROM tblFamily WHERE Image IS NOT NULL AND OCTET_LENGTH(Image)>0")
        restored_families = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tblPerson WHERE Picture IS NOT NULL AND OCTET_LENGTH(Picture)>0")
        restored_people = cursor.fetchone()[0]
        if restored_families != len(plan) or restored_people != person_count:
            raise RuntimeError(
                f"Verification failed: families {restored_families}/{len(plan)}, "
                f"people {restored_people}/{person_count}"
            )
        print(f"restored_families={restored_families} restored_people={restored_people}")
        print(f"backup={backup}")
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
