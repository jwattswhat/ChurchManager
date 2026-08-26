"""Install or reset the versioned fictional beta dataset in ChurchDBTest.

The coordinator deliberately delegates to the maintained subsystem fixture
utilities.  Each utility retains its own database guard and transaction, while
this module adds one explicit whole-dataset confirmation and release check.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path

from churchmanager_version import __version__


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "TestData" / "BetaDataset" / "manifest.json"
TARGET = "ChurchDBTest"


class BetaDatasetError(RuntimeError):
    """Raised when the guarded beta dataset cannot be installed."""


def load_manifest(path=MANIFEST):
    """Load and validate the release-bound beta dataset manifest."""
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if value.get("dataset_id") != "churchmanager-beta-test-data":
        raise BetaDatasetError("The beta dataset identifier is invalid.")
    if str(value.get("target_database", "")).casefold() != TARGET.casefold():
        raise BetaDatasetError("The beta dataset is not restricted to ChurchDBTest.")
    if value.get("release_version") != __version__:
        raise BetaDatasetError("The beta dataset does not match this ChurchManager release.")
    stages = value.get("stages")
    if not isinstance(stages, list) or not stages:
        raise BetaDatasetError("The beta dataset has no installation stages.")
    return value


def stage_commands(manifest, python=sys.executable, root=ROOT):
    """Return explicit, reviewable commands for every maintained stage."""
    commands = []
    for stage in manifest["stages"]:
        name = str(stage["service"])
        script = Path(root) / f"{name}.py"
        if not getattr(sys, "frozen", False) and not script.is_file():
            raise BetaDatasetError(f"Beta dataset stage is missing: {name}")
        arguments = [str(value) for value in stage.get("arguments", ["--apply"])]
        commands.append([str(python), str(script), *arguments])
    return commands


def _run_stage(command):
    """Run one packaged stage without requiring a separate Python executable."""
    module_name = Path(command[1]).stem
    module = importlib.import_module(module_name)
    previous = sys.argv
    previous_directory = Path.cwd()
    runtime_root = os.environ.get("CHURCHMANAGER_BETA_RUNTIME_ROOT")
    try:
        if runtime_root:
            runtime_path = Path(runtime_root)
            if hasattr(module, "ROOT"):
                module.ROOT = runtime_path
            os.chdir(runtime_path)
        sys.argv = [module_name, *command[2:]]
        result = module.main()
    finally:
        sys.argv = previous
        os.chdir(previous_directory)
    if result not in (None, 0):
        raise BetaDatasetError(f"Beta dataset stage failed: {module_name}")


def install(manifest, *, runner=None, notify=print):
    """Run all guarded stages in order and stop at the first failure."""
    for index, command in enumerate(stage_commands(manifest), 1):
        notify(f"beta_stage_{index}={Path(command[1]).stem}")
        if runner is None:
            _run_stage(command)
        else:
            runner(command)
    notify(f"beta_dataset_id={manifest['dataset_id']}")
    notify(f"beta_dataset_version={manifest['dataset_version']}")
    notify("beta_dataset_installed=true")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm", default="", help="must be exactly ChurchDBTest")
    args = parser.parse_args()
    manifest = load_manifest()
    print(f"release={__version__}")
    print(f"dataset={manifest['dataset_id']} {manifest['dataset_version']}")
    print(f"target={TARGET}")
    for command in stage_commands(manifest):
        print("stage=" + Path(command[1]).stem)
    if not args.apply:
        print("No changes made. Re-run with --apply --confirm ChurchDBTest.")
        return 2
    if args.confirm != TARGET:
        raise BetaDatasetError("Type ChurchDBTest exactly to confirm the fictional data reset.")
    install(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
