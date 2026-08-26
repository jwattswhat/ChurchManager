"""Preview, clear, or rebuild worship test data in local ChurchDBTest.

``--seed`` creates a small deterministic planning scenario after the guarded
backup and cleanup.  It is intentionally unavailable for any other database.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

import mariadb

from backup_service import BackupService
from churchmanager_mode import resolve_database


ROOT = Path(__file__).resolve().parent
TABLES = (
    "tblAttendance",
    "tblAttendanceEvent",
    "tblServiceRole",
    "tblHymnUsage",
    "tblServiceBulletinOrderLine",
    "tblServiceBulletinOrder",
    "tblService",
)

TEST_SERVICES = (
    (datetime(2026, 8, 16, 9, 0), "Eleventh Sunday after Pentecost", True, "COMPLETE"),
    (datetime(2026, 8, 30, 9, 0), "Thirteenth Sunday after Pentecost", True, "PLANNED"),
    (datetime(2026, 9, 6, 9, 0), "Fourteenth Sunday after Pentecost", False, "INCOMPLETE"),
)


def settings():
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))
    database = config["database_settings"]
    arguments = {
        "server": database["host"],
        "database": database["database"],
        "user": database["user"],
        "password": None,
        "test_mode": True,
        "jsform_database": None,
    }
    try:
        resolved = resolve_database(arguments, config)
    except KeyError:
        arguments["password"] = getpass.getpass(
            f"MariaDB password for {database['user']}: "
        )
        resolved = resolve_database(arguments, config)
    if str(resolved["server"]).casefold() not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("Safety stop: worship cleanup is restricted to local MariaDB.")
    if str(resolved["database"]).casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: worship cleanup is restricted to ChurchDBTest.")
    return config, resolved


def counts(cursor):
    result = {}
    cursor.execute(
        "SELECT COUNT(*) FROM tblAttendance a JOIN tblAttendanceEvent e "
        "ON e.ID=a.AttendanceEventID WHERE e.ServiceID IS NOT NULL"
    )
    result["service_attendance_records"] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tblAttendanceEvent WHERE ServiceID IS NOT NULL")
    result["service_attendance_events"] = cursor.fetchone()[0]
    for table in TABLES[2:]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        result[table] = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM tblSecurityAuditEvent "
        "WHERE EntityType='WORSHIP_SERVICE' OR Action='WORSHIP_SERVICE_DELETED'"
    )
    result["worship_service_audit_events"] = cursor.fetchone()[0]
    return result


def one(cursor, sql, values=()):
    cursor.execute(sql, values)
    return cursor.fetchone()


def required_fixture_rows(cursor):
    """Resolve reusable catalog rows without assuming database IDs."""
    church = one(
        cursor,
        "SELECT ID FROM tblChurch WHERE Church='Reformation Lutheran Church' "
        "ORDER BY ID LIMIT 1",
    ) or one(cursor, "SELECT ID FROM tblChurch ORDER BY ID LIMIT 1")
    template = one(
        cursor,
        "SELECT ID,Name FROM tblBulletinOrderTemplate WHERE Active=1 "
        "ORDER BY IsStarter DESC,ID LIMIT 1",
    )
    cursor.execute(
        "SELECT ID FROM tblParticipant WHERE Active=1 ORDER BY ID LIMIT 4"
    )
    participants = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        "SELECT ID FROM tblWorshipRole WHERE Active=1 ORDER BY DisplayOrder,ID LIMIT 4"
    )
    roles = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        "SELECT ID,COALESCE(Hymn,''),COALESCE(Title,''),COALESCE(PrintedReference,'') "
        "FROM tblHymn ORDER BY ID LIMIT 12"
    )
    hymns = cursor.fetchall()
    if not church or not template or len(participants) < 3 or len(roles) < 2:
        raise RuntimeError(
            "Worship test data needs a church, an active Order of Service template, "
            "three active participants, and two active worship positions."
        )
    return church[0], template, participants, roles, hymns


def copy_weekly_order(cursor, service_id, church_id, template, hymns, state):
    """Copy one template into a service-owned weekly snapshot."""
    template_id, template_name = template
    cursor.execute(
        "INSERT INTO tblServiceBulletinOrder (ServiceID,TemplateID,TemplateName) "
        "VALUES (?,?,?)", (service_id, template_id, template_name),
    )
    cursor.execute(
        "SELECT ID,Sequence,LineType,Label,ValueSource,ValueKey,ReferenceText,"
        "StyleName,LabelBold,ValueBold,Italic,IndentLevel,TabPosition,TabAlignment,"
        "TabLeader,ConditionType,ConditionValue,Note FROM tblBulletinOrderLine "
        "WHERE TemplateID=? ORDER BY Sequence,ID", (template_id,),
    )
    lines = cursor.fetchall()
    hymn_index = 0
    reading_index = 0
    citations = ("Isaiah 29:17-24", "Ephesians 5:22-33", "Mark 7:1-13")
    for position, line in enumerate(lines, 1):
        (line_id, _sequence, line_type, label, source, key, reference, style,
         label_bold, value_bold, italic, indent, tab_position, tab_alignment,
         tab_leader, condition_type, condition_value, note) = line
        weekly_value = None
        hymn = None
        upper_type = str(line_type or "").upper()
        if upper_type == "HYMN" and hymns and not (state == "INCOMPLETE" and hymn_index > 0):
            hymn = hymns[hymn_index % len(hymns)]
            weekly_value = hymn[2] or hymn[1]
            reference = str(hymn[3] or hymn[1] or "").strip() or None
            hymn_index += 1
        elif upper_type == "READING" and not (state == "INCOMPLETE" and reading_index > 0):
            weekly_value = citations[reading_index % len(citations)]
            reading_index += 1
        cursor.execute(
            "INSERT INTO tblServiceBulletinOrderLine "
            "(ServiceID,TemplateLineID,Sequence,Included,LineType,Label,ValueSource,"
            "ValueKey,WeeklyValue,ReferenceText,StyleName,LabelBold,ValueBold,Italic,"
            "IndentLevel,TabPosition,TabAlignment,TabLeader,ConditionType,ConditionValue,Note) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (service_id, line_id, position, 1, line_type, label, source, key,
             weekly_value, reference, style, label_bold, value_bold, italic, indent,
             tab_position, tab_alignment, tab_leader, condition_type, condition_value, note),
        )
        weekly_line_id = cursor.lastrowid
        if hymn:
            cursor.execute(
                "INSERT INTO tblHymnUsage "
                "(ChurchID,ServiceID,ServiceBulletinOrderLineID,HymnID,UsedAs,Stanzas) "
                "VALUES (?,?,?,?,?,?)",
                (church_id, service_id, weekly_line_id, hymn[0], key or label, "1-4"),
            )


def seed_worship_data(cursor):
    """Create services that exercise weekly planning and volunteer responses."""
    church_id, template, participants, roles, hymns = required_fixture_rows(cursor)
    for role_id in roles[:2]:
        cursor.execute(
            "INSERT INTO tblWorshipRoleRequirement "
            "(BulletinOrderTemplateID,WorshipRoleID,RequiredCount,Active) VALUES (?,?,1,1) "
            "ON DUPLICATE KEY UPDATE RequiredCount=1,Active=1",
            (template[0], role_id),
        )
    service_ids = []
    for service_date, title, communion, state in TEST_SERVICES:
        cursor.execute(
            "INSERT INTO tblService "
            "(ChurchID,DateTime,Location,LiturgicalDate,HolyCommunion,"
            "BulletinOrderTemplateID,OSNote,CheckListComplete,Note) "
            "VALUES (?,?,?,?,?,?,?, ?,?)",
            (church_id, service_date, "Main Sanctuary", title, int(communion),
             template[0], "TEST - Weekly Order of Service snapshot",
             int(state == "COMPLETE"), f"TEST - {state.title()} worship planning scenario"),
        )
        service_id = cursor.lastrowid
        service_ids.append(service_id)
        copy_weekly_order(cursor, service_id, church_id, template, hymns, state)
        cursor.execute(
            "INSERT INTO tblAttendanceEvent "
            "(ChurchID,ServiceID,DateTime,Description,AttendanceType,CommunionOffered,"
            "HandCount,HandCountCommunion) VALUES (?,?,?,?,?,?,?,?)",
            (church_id, service_id, service_date, title, "Worship Service", int(communion),
             42 if state == "COMPLETE" else 0, 31 if state == "COMPLETE" else 0),
        )
        checklist_statuses = (
            ("Confirm worship participants", "DONE" if state == "COMPLETE" else "NOT_DONE"),
            ("Select hymns and readings", "NOT_DONE" if state == "INCOMPLETE" else "DONE"),
            ("Prepare bulletin outline", "NOT_NEEDED" if state == "INCOMPLETE" else "DONE"),
        )
        for sequence, (task, status) in enumerate(checklist_statuses, 1):
            cursor.execute(
                "INSERT INTO tblServiceChecklistItem "
                "(ServiceID,Sequence,Task,CompletionSource,Required,Status,Note,CompletedAt) "
                "VALUES (?,?,?,'MANUAL',1,?,?,?)",
                (service_id, sequence, task, status, "TEST - Preparation checklist scenario",
                 service_date if status == "DONE" else None),
            )

    statuses = (
        (service_ids[0], participants[0], roles[0], "CONFIRMED", TEST_SERVICES[0][0], "In person"),
        (service_ids[0], participants[1], roles[1], "CONFIRMED", TEST_SERVICES[0][0], "In person"),
        (service_ids[1], participants[0], roles[0], "CONFIRMED", TEST_SERVICES[1][0], "Email"),
        (service_ids[1], participants[1], roles[1], "DECLINED", TEST_SERVICES[1][0], "Email"),
        (service_ids[2], participants[2], roles[0], "PENDING", None, None),
    )
    for service_id, participant_id, role_id, status, responded, source in statuses:
        cursor.execute(
            "INSERT INTO tblServiceRole "
            "(ServiceID,ParticipantID,WorshipRoleID,AssignmentStatus,RespondedAt,ResponseSource,Note) "
            "VALUES (?,?,?,?,?,?,?)",
            (service_id, participant_id, role_id, status, responded, source,
             "TEST - Volunteer response scenario"),
        )
    cursor.execute(
        "INSERT INTO tblParticipantAvailabilityException "
        "(ParticipantID,WorshipRoleID,StartDate,EndDate,Reason,Active) "
        "VALUES (?,?,?,?,?,1)",
        (participants[2], roles[0], TEST_SERVICES[2][0].date(), TEST_SERVICES[2][0].date(),
         "TEST - Intentional scheduling conflict"),
    )
    return service_ids


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Create a backup and perform cleanup")
    parser.add_argument(
        "--seed", action="store_true",
        help="Create a backup, clear worship data, and load the standard test scenario",
    )
    args = parser.parse_args()
    config, resolved = settings()
    connection = mariadb.connect(
        host=resolved["server"],
        port=int(config["testing"].get("port", 3306)),
        database=resolved["database"],
        user=resolved["user"],
        password=resolved["password"],
        autocommit=False,
    )
    cursor = connection.cursor()
    try:
        before = counts(cursor)
        print(f"target={resolved['server']}/{resolved['database']}")
        for name, count in before.items():
            print(f"before_{name}={count}")
        if not (args.apply or args.seed):
            print("No changes made. Re-run with --apply or --seed after reviewing these counts.")
            return 2

        def non_ssl_dump(command, **kwargs):
            return subprocess.run(command[:2] + ["--skip-ssl"] + command[2:], **kwargs)

        backup = BackupService(runner=non_ssl_dump).create(
            resolved,
            Path(r"C:\Program Files\MariaDB 12.1\bin"),
            ROOT / "BackupDB" / "ChurchDBTest.pre-worship-reset",
        )
        size = backup.path.stat().st_size
        digest = hashlib.sha256(backup.path.read_bytes()).hexdigest()
        if size < 1024:
            raise RuntimeError("Backup verification failed: output is unexpectedly small.")
        print(f"backup={backup.path}")
        print(f"backup_bytes={size}")
        print(f"backup_sha256={digest}")

        cursor.execute(
            "DELETE a FROM tblAttendance a JOIN tblAttendanceEvent e "
            "ON e.ID=a.AttendanceEventID WHERE e.ServiceID IS NOT NULL"
        )
        cursor.execute("DELETE FROM tblAttendanceEvent WHERE ServiceID IS NOT NULL")
        cursor.execute("DELETE FROM tblServiceRole")
        cursor.execute(
            "DELETE FROM tblParticipantAvailabilityException "
            "WHERE Reason='TEST - Intentional scheduling conflict'"
        )
        cursor.execute("DELETE FROM tblHymnUsage")
        cursor.execute("DELETE FROM tblServiceBulletinOrderLine")
        cursor.execute("DELETE FROM tblServiceBulletinOrder")
        cursor.execute(
            "DELETE FROM tblSecurityAuditEvent "
            "WHERE EntityType='WORSHIP_SERVICE' OR Action='WORSHIP_SERVICE_DELETED'"
        )
        cursor.execute("DELETE FROM tblService")
        service_ids = seed_worship_data(cursor) if args.seed else []
        connection.commit()

        after = counts(cursor)
        for name, count in after.items():
            print(f"after_{name}={count}")
        if not args.seed and any(after.values()):
            raise RuntimeError("Worship cleanup verification failed: dependent rows remain.")
        if args.seed:
            print(f"seeded_services={len(service_ids)}")
            print("seeded_weekly_orders=3")
            print("seeded_response_states=CONFIRMED,DECLINED,PENDING")
            print("seeded_availability_conflicts=1")
            print("worship_test_dataset_verified=true")
        else:
            print("cleanup_verified=true")
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
