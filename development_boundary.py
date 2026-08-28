"""Fail closed when ChurchManager resolves components outside its allowed tree."""

import sys
from pathlib import Path


class DevelopmentIsolationError(RuntimeError):
    """Raised when development and Frozen application paths are mixed."""


def assert_development_isolation(jsform_module, project_root=None, *, frozen=None):
    """Accept the adjacent development JSForm or the packaged bundled JSForm."""
    project = Path(project_root or Path(__file__).resolve().parent).resolve()
    jsform_file = Path(jsform_module.__file__).resolve()
    is_frozen = bool(getattr(sys, "frozen", False)) if frozen is None else bool(frozen)
    expected_jsform = (
        project / "JSForm" if is_frozen else project.parent / "JSForm"
    ).resolve()

    if "churchmanager-legacy" in {part.casefold() for part in project.parts}:
        raise DevelopmentIsolationError(
            "Development ChurchManager cannot run from the Frozen application tree."
        )
    if not jsform_file.is_relative_to(expected_jsform):
        raise DevelopmentIsolationError(
            "ChurchManager must use its designated JSForm at {}. "
            "Resolved JSForm was {}.".format(expected_jsform, jsform_file)
        )
    return True
