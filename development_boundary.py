"""Fail closed when development resolves components from the Frozen application."""

from pathlib import Path


class DevelopmentIsolationError(RuntimeError):
    """Raised when development and Frozen application paths are mixed."""


def assert_development_isolation(jsform_module, project_root=None):
    project = Path(project_root or Path(__file__).resolve().parent).resolve()
    jsform_file = Path(jsform_module.__file__).resolve()
    expected_jsform = (project.parent / "JSForm").resolve()

    if "churchmanager-legacy" in {part.casefold() for part in project.parts}:
        raise DevelopmentIsolationError(
            "Development ChurchManager cannot run from the Frozen application tree."
        )
    if not jsform_file.is_relative_to(expected_jsform):
        raise DevelopmentIsolationError(
            "Development ChurchManager must use its independent JSForm at {}. "
            "Resolved JSForm was {}.".format(expected_jsform, jsform_file)
        )
    return True
