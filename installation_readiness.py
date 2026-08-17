"""Perform read-only checks before ChurchManager installation begins.

The inspector never connects to MariaDB, requests credentials, or changes the
computer. The future graphical setup program will consume these results before
offering any operation that can create or upgrade a database.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from lectionary_packages import LectionaryPackageValidator, load_lectionary_package
from order_of_service_packages import (
    OrderOfServicePackageValidator,
    load_order_of_service_package,
)


ROOT = Path(__file__).resolve().parent
REQUIRED_MODULES = (
    "wx", "mariadb", "mysql.connector", "jsonschema", "argon2",
    "reportlab", "pypdf", "dateutil",
)


@dataclass(frozen=True)
class ReadinessCheck:
    """One host prerequisite and its plain-language result."""

    code: str
    passed: bool
    message: str


@dataclass(frozen=True)
class CatalogPackage:
    """One validated or dependency-blocked bundled catalog."""

    family: str
    code: str
    title: str
    version: str
    path: Path
    valid: bool
    installable: bool
    message: str
    dependency_code: str | None = None


@dataclass(frozen=True)
class ReadinessReport:
    """Structured result returned to the command and future setup wizard."""

    checks: tuple[ReadinessCheck, ...]
    packages: tuple[CatalogPackage, ...]

    @property
    def ready(self):
        """Return whether host prerequisites passed."""
        return all(item.passed for item in self.checks)


def find_mariadb_tool(executable):
    """Locate a MariaDB command without launching it."""
    located = shutil.which(executable)
    if located:
        return Path(located)
    roots = {
        Path(value) for key in ("ProgramFiles", "ProgramW6432")
        if (value := os.environ.get(key))
    }
    for root in roots:
        matches = sorted(root.glob(f"MariaDB */bin/{executable}"), reverse=True)
        if matches:
            return matches[0]
    return None


def system_checks(root=ROOT):
    """Inspect the supported host, runtime, tools, and free space."""
    root = Path(root)
    checks = [
        ReadinessCheck(
            "windows", sys.platform == "win32",
            "Supported Windows host." if sys.platform == "win32"
            else "ChurchManager requires Windows.",
        ),
        ReadinessCheck(
            "python", sys.version_info >= (3, 11),
            f"Python {sys.version_info.major}.{sys.version_info.minor} detected; "
            "version 3.11 or newer is required.",
        ),
    ]
    missing = [name for name in REQUIRED_MODULES if importlib.util.find_spec(name) is None]
    checks.append(ReadinessCheck(
        "runtime_dependencies", not missing,
        "Required application components are available." if not missing
        else "Missing application components: " + ", ".join(missing),
    ))
    for code, names in (
        ("mariadb_client", ("mariadb.exe", "mysql.exe")),
        ("database_backup", ("mariadb-dump.exe", "mysqldump.exe")),
    ):
        found = next((path for name in names if (path := find_mariadb_tool(name))), None)
        checks.append(ReadinessCheck(
            code, found is not None,
            f"Found required database tool: {found}" if found
            else f"Required database tool was not found ({' or '.join(names)}).",
        ))
    free = shutil.disk_usage(root).free
    checks.append(ReadinessCheck(
        "disk_space", free >= 2 * 1024**3,
        f"{free / 1024**3:.1f} GB free; at least 2 GB is required.",
    ))
    return tuple(checks)


def _untrusted_manifest(path):
    """Read display hints only; this never marks a package valid."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}


def catalog_inventory(root=ROOT):
    """Validate included catalog files and expose unresolved dependencies."""
    root = Path(root)
    packages = []
    hymnals = root / "packages" / "hymnal"
    hymnal_codes = {
        str(_untrusted_manifest(path).get("package_code") or "").casefold()
        for path in hymnals.glob("*.json")
    } if hymnals.is_dir() else set()

    for path in sorted((root / "packages" / "lectionary").glob("*.json")):
        raw = _untrusted_manifest(path)
        try:
            package, checksum = load_lectionary_package(path)
            summary = LectionaryPackageValidator().validate(package, checksum)
            packages.append(CatalogPackage(
                "lectionary", summary.package_code,
                str(package.get("title") or summary.package_code),
                summary.package_version, path, True, True,
                "Validated and available.",
            ))
        except Exception as error:
            packages.append(CatalogPackage(
                "lectionary", str(raw.get("package_code") or path.stem),
                str(raw.get("title") or path.stem),
                str(raw.get("package_version") or ""), path, False, False,
                str(error),
            ))

    for path in sorted((root / "packages" / "order_of_service").glob("*.json")):
        raw = _untrusted_manifest(path)
        dependency = str(raw.get("hymnal_package_code") or "").casefold() or None
        try:
            package, checksum = load_order_of_service_package(path)
            summary = OrderOfServicePackageValidator(hymnal_codes).validate(package, checksum)
            installable = dependency is None or dependency in hymnal_codes
            packages.append(CatalogPackage(
                "order_of_service", summary.package_code,
                str(package.get("title") or summary.package_code),
                summary.package_version, path, True, installable,
                "Validated and available." if installable
                else f"Requires hymnal package: {dependency}.", dependency,
            ))
        except Exception as error:
            missing_dependency = bool(dependency and dependency not in hymnal_codes)
            packages.append(CatalogPackage(
                "order_of_service", str(raw.get("package_code") or path.stem),
                str(raw.get("title") or path.stem),
                str(raw.get("package_version") or ""), path,
                missing_dependency, False,
                f"Requires hymnal package: {dependency}." if missing_dependency else str(error),
                dependency,
            ))
    return tuple(packages)


def inspect_readiness(root=ROOT):
    """Return a complete read-only installation readiness report."""
    return ReadinessReport(system_checks(root), catalog_inventory(root))
