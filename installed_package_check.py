"""Password-free verification of resources bundled with installed executables."""

from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path

import JSForm

from churchmanager_version import __version__
from development_boundary import assert_development_isolation
from installation_readiness import REQUIRED_MODULES


def package_check(output_path, *, module_file=__file__):
    """Write evidence that an installed bundle contains its required resources."""

    root = Path(module_file).resolve().parent
    if bool(getattr(sys, "frozen", False)):
        assert_development_isolation(JSForm, root, frozen=True)
    required = {
        "forms": root / "JSForm" / "Forms" / "frmMain.json",
        "main_menu": root / "Menus" / "main.menu.json",
        "jsform_icon": root / "JSForm" / "assets" / "jsform.ico",
        "schema": root / "installation" / "baseline_schema.sql",
        "seed": root / "installation" / "baseline_seed.sql",
        "lectionary_packages": root / "packages" / "lectionary",
        "report_definitions": root / "visual_reports" / "definitions",
        "user_guide": root / "Documentation" / "ChurchManager.UserGuide.pdf",
    }
    missing = [name for name, path in required.items() if not path.exists()]
    checked_modules = tuple(REQUIRED_MODULES) + (
        "mysql.connector.locales.eng.client_error",
        "mysql.connector.plugins.mysql_native_password",
    )
    missing_components = [
        name for name in checked_modules if importlib.util.find_spec(name) is None
    ]
    missing.extend(f"component:{name}" for name in missing_components)
    evidence = {
        "release": __version__,
        "passed": not missing,
        "missing": missing,
        "missing_components": missing_components,
        "forms": len(list((root / "JSForm" / "Forms").glob("*.json"))),
        "migrations": len(list((root / "migrations").glob("[0-9][0-9][0-9]_*.sql"))),
        "catalog_packages": len(list((root / "packages").glob("*/*.json"))),
    }
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return 0 if evidence["passed"] else 2
