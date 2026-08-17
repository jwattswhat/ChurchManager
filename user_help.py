"""Locate and open the installed ChurchManager user guide."""

from __future__ import annotations

import os
import sys
from pathlib import Path


class UserGuideError(RuntimeError):
    """Raised when the maintained user guide cannot be opened."""


def user_guide_candidates(application_root: Path | None = None) -> tuple[Path, ...]:
    """Return development and installed locations in preferred order."""
    root = Path(application_root or Path(__file__).resolve().parent)
    executable_root = Path(sys.executable).resolve().parent
    return (
        root / "output" / "pdf" / "ChurchManager.UserGuide.pdf",
        root / "Documentation" / "ChurchManager.UserGuide.pdf",
        executable_root / "Documentation" / "ChurchManager.UserGuide.pdf",
        executable_root / "ChurchManager.UserGuide.pdf",
    )


def find_user_guide(application_root: Path | None = None) -> Path:
    """Find the first readable User Guide or raise a useful error."""
    for candidate in user_guide_candidates(application_root):
        if candidate.is_file():
            return candidate
    raise UserGuideError(
        "The ChurchManager User Guide is not installed. Repair the installation "
        "or contact ChurchManager support."
    )


def open_user_guide(application_root: Path | None = None) -> Path:
    """Open the User Guide in the operating system's normal PDF viewer."""
    path = find_user_guide(application_root)
    try:
        os.startfile(path)  # type: ignore[attr-defined]
    except OSError as error:
        raise UserGuideError(
            "Windows could not open the ChurchManager User Guide. Confirm that a "
            "PDF viewer is installed."
        ) from error
    return path
