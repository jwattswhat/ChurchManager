"""Resolve writable ChurchManager configuration paths for source and installed use."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = ROOT / "installation" / "default_churchmanager.json"


def configuration_path(*, frozen=None, environment=None):
    """Return the explicit, development, or installed configuration path."""

    environment = environment or os.environ
    override = str(environment.get("CHURCHMANAGER_CONFIG") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    is_frozen = bool(getattr(sys, "frozen", False)) if frozen is None else bool(frozen)
    if not is_frozen:
        return ROOT / "churchmanager.json"
    local = Path(environment.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return local / "ChurchManager" / "churchmanager.json"


def application_data_root(*, frozen=None, environment=None):
    """Return the writable application-data root for the active runtime mode."""

    environment = environment or os.environ
    is_frozen = bool(getattr(sys, "frozen", False)) if frozen is None else bool(frozen)
    if not is_frozen:
        return ROOT
    local = Path(environment.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return local / "ChurchManager"


def writable_directory(name, *, frozen=None, environment=None):
    """Create and return one named ChurchManager output directory."""

    target = application_data_root(frozen=frozen, environment=environment) / str(name)
    target.mkdir(parents=True, exist_ok=True)
    return target


def ensure_configuration(path=None, template=DEFAULT_TEMPLATE):
    """Create a writable installed configuration from the non-secret template."""

    target = Path(path) if path is not None else configuration_path()
    if target.is_file():
        return target
    source = Path(template)
    if not source.is_file():
        raise FileNotFoundError("The ChurchManager default configuration is unavailable.")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    shutil.copyfile(source, temporary)
    temporary.replace(target)
    return target
