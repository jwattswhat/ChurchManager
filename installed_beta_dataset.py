"""Installed entry point for the guarded fictional beta dataset utility."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from configuration_paths import configuration_path, ensure_configuration
from credential_store import read_credential, write_credential
from install_beta_test_dataset import BetaDatasetError, TARGET, install, load_manifest
from installed_package_check import package_check


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def prepare_test_configuration(path=None):
    """Convert an exact local ChurchDBTest setup into explicit test mode."""
    path = ensure_configuration(path or configuration_path())
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    production = config.get("database_settings", {})
    host = str(production.get("host") or "").casefold()
    database = str(production.get("database") or "")
    if host not in LOCAL_HOSTS or database.casefold() != TARGET.casefold():
        raise BetaDatasetError(
            "The beta dataset requires a local installation whose database is named ChurchDBTest."
        )
    source_target = production.get("credential_target", "ChurchManager/Production")
    username, password = read_credential(source_target)
    test_target = "ChurchManager/Test"
    write_credential(test_target, username, password)
    testing = config.setdefault("testing", {})
    testing.update({
        "host": production["host"], "port": production.get("port", 3306),
        "user": username, "database": TARGET, "jsform_database": TARGET,
        "credential_target": test_target,
    })
    security = config.setdefault("security", {})
    security["testing_enabled"] = True
    security["production_enabled"] = False
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(config, indent=4) + "\n", encoding="utf-8")
    temporary.replace(path)
    return path


def _resource_path(*parts):
    """Return one source-tree or packaged beta resource path."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base.joinpath(*parts)


def prepare_runtime_root(configuration):
    """Create the private working area used by packaged fixture services."""
    runtime = configuration.parent / "BetaDatasetRuntime"
    (runtime / "TestData").mkdir(parents=True, exist_ok=True)
    (runtime / "Documents").mkdir(parents=True, exist_ok=True)
    (runtime / "BackupDB").mkdir(parents=True, exist_ok=True)
    shutil.copy2(configuration, runtime / "churchmanager.json")
    for source_parts, destination in (
        (("TestData", "Reformation-Lutheran-Church-Test-Logo.png"),
         runtime / "TestData" / "Reformation-Lutheran-Church-Test-Logo.png"),
        (("Documents", "Sample Congregational Document.txt"),
         runtime / "Documents" / "Sample Congregational Document.txt"),
    ):
        source = _resource_path(*source_parts)
        if not source.is_file():
            raise BetaDatasetError(f"Packaged beta resource is missing: {source.name}")
        shutil.copy2(source, destination)
    return runtime


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-check")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm", default="")
    args = parser.parse_args(argv)
    if args.package_check:
        return package_check(args.package_check)
    manifest = load_manifest()
    if not args.apply or args.confirm != TARGET:
        raise BetaDatasetError("Beta installation requires --apply --confirm ChurchDBTest.")
    configuration = prepare_test_configuration()
    runtime = prepare_runtime_root(configuration)
    previous = os.environ.get("CHURCHMANAGER_BETA_RUNTIME_ROOT")
    os.environ["CHURCHMANAGER_BETA_RUNTIME_ROOT"] = str(runtime)
    try:
        install(manifest)
    finally:
        if previous is None:
            os.environ.pop("CHURCHMANAGER_BETA_RUNTIME_ROOT", None)
        else:
            os.environ["CHURCHMANAGER_BETA_RUNTIME_ROOT"] = previous
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
