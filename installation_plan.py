"""Validate a proposed ChurchManager installation without applying it."""

from __future__ import annotations

import re
from dataclasses import dataclass

from installation_readiness import CatalogPackage, ReadinessReport


_DATABASE_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,63}$")
_USERNAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,99}$")


class InstallationPlanError(ValueError):
    """Raised when a proposed installation is incomplete or inconsistent."""


@dataclass(frozen=True)
class InstallationRequest:
    """Non-secret choices collected by the future setup wizard."""

    church_name: str
    database_name: str
    master_username: str
    master_display_name: str
    hymnal_packages: tuple[str, ...] = ()
    lectionary_packages: tuple[str, ...] = ()
    order_of_service_packages: tuple[str, ...] = ()
    primary_hymnal: str | None = None
    default_lectionary: str | None = None


@dataclass(frozen=True)
class InstallationPlan:
    """Validated, password-free plan safe to show on the review screen."""

    church_name: str
    database_name: str
    master_username: str
    master_display_name: str
    selected_packages: tuple[CatalogPackage, ...]
    primary_hymnal: str | None
    default_lectionary: str | None


def _required_text(value, label, maximum):
    text = str(value or "").strip()
    if not text:
        raise InstallationPlanError(f"{label} is required.")
    if len(text) > maximum:
        raise InstallationPlanError(f"{label} is too long.")
    return text


def build_installation_plan(request, readiness):
    """Validate host readiness, catalog choices, dependencies, and defaults."""
    if not isinstance(request, InstallationRequest):
        raise InstallationPlanError("The installation request is invalid.")
    if not isinstance(readiness, ReadinessReport) or not readiness.ready:
        raise InstallationPlanError("Installation prerequisites need attention.")

    church = _required_text(request.church_name, "Congregation name", 255)
    database = _required_text(request.database_name, "Database name", 64)
    if not _DATABASE_NAME.fullmatch(database):
        raise InstallationPlanError(
            "Database name must begin with a letter and contain only letters, numbers, or underscores.",
        )
    username = _required_text(request.master_username, "Master username", 100)
    if not _USERNAME.fullmatch(username):
        raise InstallationPlanError(
            "Master username must contain at least three letters, numbers, periods, hyphens, or underscores.",
        )
    display_name = _required_text(request.master_display_name, "Master display name", 255)

    available = {(item.family, item.code.casefold()): item for item in readiness.packages}
    selections = {
        "hymnal": tuple(request.hymnal_packages),
        "lectionary": tuple(request.lectionary_packages),
        "order_of_service": tuple(request.order_of_service_packages),
    }
    selected = []
    selected_codes = {family: set() for family in selections}
    for family, codes in selections.items():
        for original in codes:
            code = str(original or "").strip().casefold()
            key = (family, code)
            if not code or key not in available:
                raise InstallationPlanError(f"Selected {family} package is unavailable: {original}.")
            package = available[key]
            if not package.valid:
                raise InstallationPlanError(f"Selected package is invalid: {package.title}.")
            if code in selected_codes[family]:
                raise InstallationPlanError(f"Package was selected more than once: {package.title}.")
            selected_codes[family].add(code)
            selected.append(package)

    for package in selected:
        dependency = (package.dependency_code or "").casefold()
        if dependency and dependency not in selected_codes["hymnal"]:
            raise InstallationPlanError(
                f"{package.title} requires the hymnal package {dependency}.",
            )

    primary = str(request.primary_hymnal or "").strip().casefold() or None
    if primary and primary not in selected_codes["hymnal"]:
        raise InstallationPlanError("The primary hymnal must be one of the selected hymnals.")
    default = str(request.default_lectionary or "").strip().casefold() or None
    if default and default not in selected_codes["lectionary"]:
        raise InstallationPlanError("The default lectionary must be one of the selected lectionaries.")

    return InstallationPlan(
        church, database, username, display_name, tuple(selected), primary, default,
    )
