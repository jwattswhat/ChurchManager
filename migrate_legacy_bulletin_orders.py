"""Convert legacy HTML Order of Service records in the isolated test database."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mariadb

from bulletin_orders import migrate_legacy_orders
from credential_store import read_credential


ROOT = Path(__file__).resolve().parent
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    config = json.loads((ROOT / "churchmanager.json").read_text(encoding="utf-8-sig"))["testing"]
    if config["host"] not in LOCAL_HOSTS or config["database"].casefold() != "churchdbtest":
        raise RuntimeError("Safety stop: conversion requires local ChurchDBTest.")
    username, password = read_credential(config["credential_target"])
    connection = mariadb.connect(
        host=config["host"], port=int(config.get("port", 3306)),
        database=config["database"], user=username, password=password, autocommit=False,
    )
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(DISTINCT OrderofService), COUNT(*) FROM tblOrderofService")
        templates, lines = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM tblBulletinOrderTemplate")
        existing_templates = cursor.fetchone()[0]
        print(f"target={config['host']}/{config['database']}")
        print(f"legacy_templates={templates} legacy_lines={lines}")
        print(f"existing_structured_templates={existing_templates}")
        if not args.apply:
            print("No changes made. Re-run with --apply after reviewing this preview.")
            connection.rollback()
            return
        result = migrate_legacy_orders(connection)
        print(
            f"structured_templates={result['templates']} "
            f"lines_added={result['lines_added']} needs_review={result['needs_review']}"
        )
    finally:
        connection.close()


if __name__ == "__main__":
    main()
