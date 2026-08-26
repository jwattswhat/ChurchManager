"""Installed ChurchManager entry point with guarded first-run setup."""

from __future__ import annotations

import argparse
from churchmanager_mode import load_config
from configuration_paths import ensure_configuration
from installed_package_check import package_check


def setup_required(config=None):
    """Return whether the installed production connection is not configured."""

    config = config or load_config()
    values = config.get("database_settings", {})
    return not (
        config.get("security", {}).get("production_enabled")
        and str(values.get("user") or "").strip()
        and str(values.get("database") or "").strip()
    )


def main(argv=None):
    """Run protected setup when needed, then open ordinary ChurchManager."""

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--setup", action="store_true")
    parser.add_argument("--package-check")
    known, remaining = parser.parse_known_args(argv)
    if known.package_check:
        return package_check(known.package_check)
    ensure_configuration()
    if known.setup or setup_required():
        from installed_setup import main as run_setup
        run_setup()
    if setup_required():
        return 0
    from cm import main as run_churchmanager
    return run_churchmanager(remaining)


if __name__ == "__main__":
    raise SystemExit(main())
