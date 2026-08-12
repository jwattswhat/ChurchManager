"""Compare remote and local test database objects and exact table row counts."""

from __future__ import annotations

import json

import mariadb

from credential_store import read_credential


DATABASES = ("ChurchDBTest", "JSFormTest")


def connect(host, port, target):
    username, password = read_credential(target)
    return mariadb.connect(
        host=host, port=port, user=username, password=password
    )


def quote_identifier(value):
    return "`" + value.replace("`", "``") + "`"


def inventory(connection, database):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT TABLE_NAME, TABLE_TYPE FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA=? ORDER BY TABLE_NAME",
        (database,),
    )
    source_objects = cursor.fetchall()
    objects = [(name.casefold(), object_type) for name, object_type in source_objects]
    rows = {}
    for name, object_type in source_objects:
        if object_type == "BASE TABLE":
            cursor.execute(
                f"SELECT COUNT(*) FROM {quote_identifier(database)}."
                f"{quote_identifier(name)}"
            )
            rows[name.casefold()] = cursor.fetchone()[0]
    extras = {}
    for label, sql in (
        ("triggers", "SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=? ORDER BY TRIGGER_NAME"),
        ("routines", "SELECT ROUTINE_NAME, ROUTINE_TYPE FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=? ORDER BY ROUTINE_NAME, ROUTINE_TYPE"),
        ("events", "SELECT EVENT_NAME FROM information_schema.EVENTS WHERE EVENT_SCHEMA=? ORDER BY EVENT_NAME"),
    ):
        cursor.execute(sql, (database,))
        extras[label] = [
            tuple(value.casefold() if isinstance(value, str) else value for value in row)
            for row in cursor.fetchall()
        ]
    return objects, rows, extras


def main():
    config = json.load(open("churchmanager.json", encoding="utf-8"))
    settings = config["database_settings"]
    testing = config["testing"]
    remote = connect(
        settings["host"], int(settings.get("port", 3306)),
        testing["credential_target"],
    )
    local = connect("127.0.0.1", 3306, "ChurchManager/LocalTestAdmin")
    failures = []
    try:
        for database in DATABASES:
            remote_data = inventory(remote, database)
            local_data = inventory(local, database)
            labels = ("objects", "row counts", "triggers/routines/events")
            for label, remote_part, local_part in zip(labels, remote_data, local_data):
                if remote_part != local_part:
                    failures.append(f"{database} {label} differ")
                    if label == "objects":
                        print("  remote-only objects:", sorted(set(remote_part) - set(local_part)))
                        print("  local-only objects:", sorted(set(local_part) - set(remote_part)))
                    elif label == "row counts":
                        changed = sorted(
                            name for name in set(remote_part) | set(local_part)
                            if remote_part.get(name) != local_part.get(name)
                        )
                        for name in changed:
                            print(
                                f"  {name}: remote={remote_part.get(name)}, "
                                f"local={local_part.get(name)}"
                            )
                    else:
                        print("  remote metadata:", remote_part)
                        print("  local metadata:", local_part)
            print(
                f"{database}: {len(remote_data[0])} objects, "
                f"{len(remote_data[1])} base tables, "
                f"{sum(remote_data[1].values())} rows"
            )
    finally:
        remote.close()
        local.close()
    if failures:
        raise RuntimeError("; ".join(failures))
    print("Remote and local inventories and exact row counts match.")


if __name__ == "__main__":
    main()
