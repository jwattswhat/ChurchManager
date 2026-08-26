"""Password-free verification of resources bundled with installed executables."""

from __future__ import annotations

import json
from pathlib import Path

from churchmanager_version import __version__


def package_check(output_path, *, module_file=__file__):
    """Write evidence that an installed bundle contains its required resources."""

    root = Path(module_file).resolve().parent
    required = {
        "forms": root / "JSForm" / "Forms" / "frmMain.json",
        "schema": root / "installation" / "baseline_schema.sql",
        "seed": root / "installation" / "baseline_seed.sql",
        "lectionary_packages": root / "packages" / "lectionary",
        "report_definitions": root / "visual_reports" / "definitions",
        "user_guide": root / "Documentation" / "ChurchManager.UserGuide.pdf",
    }
    missing = [name for name, path in required.items() if not path.exists()]
    evidence = {
        "release": __version__,
        "passed": not missing,
        "missing": missing,
        "forms": len(list((root / "JSForm" / "Forms").glob("*.json"))),
        "migrations": len(list((root / "migrations").glob("[0-9][0-9][0-9]_*.sql"))),
        "catalog_packages": len(list((root / "packages").glob("*/*.json"))),
    }
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return 0 if evidence["passed"] else 2
