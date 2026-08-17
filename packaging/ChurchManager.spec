# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specification for the ordinary installed ChurchManager entry."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


ROOT = Path(SPEC).resolve().parents[1]
JSFORM = ROOT.parent / "JSForm"

datas = [
    (str(ROOT / "Forms"), "JSForm/Forms"),
    (str(ROOT / "Forms"), "Forms"),
    (str(ROOT / "assets"), "assets"),
    (str(ROOT / "installation"), "installation"),
    (str(ROOT / "migrations"), "migrations"),
    (str(ROOT / "packages"), "packages"),
    (str(ROOT / "visual_reports" / "definitions"), "visual_reports/definitions"),
    (str(ROOT / "accounting" / "report_definitions"), "accounting/report_definitions"),
    (str(JSFORM / "schema"), "JSForm/schema"),
    (str(JSFORM / "jsformschema.json"), "JSForm"),
    (str(ROOT / "output" / "pdf" / "ChurchManager.UserGuide.pdf"), "Documentation"),
]

a = Analysis(
    [str(ROOT / "installed_launcher.py")],
    pathex=[str(ROOT), str(JSFORM.parent)],
    binaries=[], datas=datas,
    hiddenimports=[
        name for name in collect_submodules("JSForm")
        if not name.startswith(("JSForm.tests", "JSForm.examples", "JSForm.DevelopmentTesting"))
        and name != "JSForm.run_jsform_tests"
    ],
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=["JSForm.tests", "JSForm.examples", "JSForm.DevelopmentTesting", "JSForm.run_jsform_tests"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name="ChurchManager", debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False, console=False,
    icon=str(ROOT / "cm.ico"),
)
coll = COLLECT(
    exe, a.binaries, a.datas, strip=False, upx=False,
    name="ChurchManager",
)
