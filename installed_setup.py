"""Installed entry point for protected ChurchManager setup and maintenance."""

from __future__ import annotations

import argparse

import wx

from configuration_paths import ensure_configuration
from installed_package_check import package_check
from setup_wizard import show_setup_wizard


def main(argv=None):
    """Open the reviewed setup wizard with installation actions enabled."""

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--package-check")
    known, _remaining = parser.parse_known_args(argv)
    if known.package_check:
        return package_check(known.package_check)
    ensure_configuration()
    application = wx.App(False)
    try:
        return 0 if show_setup_wizard(apply=True) else 1
    finally:
        application.Destroy()


if __name__ == "__main__":
    raise SystemExit(main())
