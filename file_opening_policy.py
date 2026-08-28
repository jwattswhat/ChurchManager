"""Configure JSForm file opening from ChurchManager-owned locations."""

from pathlib import Path
from pathlib import PureWindowsPath
import re


LOCATION_KEYS = (
    ("Location", "Document"),
    ("Location", "Sermon"),
    ("Location", "Outline"),
)
PASSIVE_DOCUMENT_EXTENSIONS = frozenset({".doc", ".docx", ".pdf", ".txt"})
_LOCAL_DRIVE = re.compile(r"^[A-Za-z]:$")


def _is_remote_or_device_path(value):
    normalized = str(value).strip().replace("/", "\\")
    windows = PureWindowsPath(normalized)
    return normalized.startswith("\\\\") or bool(
        windows.drive and not _LOCAL_DRIVE.fullmatch(windows.drive)
    )


def normalize_picker_directory(control, application_root):
    """Make a legacy relative picker directory absolute for JSForm validation."""
    remembered = str(getattr(control, "path", "") or "").strip()
    if not remembered:
        return None
    directory = Path(remembered).expanduser()
    if directory.is_absolute():
        return directory
    directory = Path(application_root).absolute() / directory
    control.path = str(directory)
    return directory


def configured_document_roots(config, application_root):
    """Return existing local directories named by ChurchManager configuration.

    Relative configuration values are resolved from the ChurchManager application
    directory, preserving the development/test data convention without granting
    JSForm authority to invent application locations.
    """
    base = Path(application_root).absolute()
    roots = []
    for family, key in LOCATION_KEYS:
        try:
            value = str(config.get_Config_Value(family, key) or "").strip()
        except Exception:
            # Missing application/framework configuration must fail closed without
            # turning an optional Open button into a startup failure.
            continue
        if not value:
            continue
        if _is_remote_or_device_path(value):
            continue
        root = Path(value).expanduser()
        if not root.is_absolute():
            root = base / root
        if root.is_dir() and root not in roots:
            roots.append(root)
    return tuple(roots)


def configure_churchmanager_file_opening(jsform, config, application_root):
    """Install ChurchManager's document policy, or retain deny-all if none is valid."""
    roots = configured_document_roots(config, application_root)
    if not roots:
        jsform.configure_file_opening()
        return None
    try:
        return jsform.configure_file_opening(roots, PASSIVE_DOCUMENT_EXTENSIONS)
    except (ValueError, OSError):
        jsform.configure_file_opening()
        return None
