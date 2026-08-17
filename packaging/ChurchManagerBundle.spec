# -*- mode: python ; coding: utf-8 -*-
"""Single-folder PyInstaller bundle containing ChurchManager and Setup."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


ROOT = Path(SPEC).resolve().parents[1]
JSFORM = ROOT.parent / "JSForm"
HIDDEN = [
    name for name in collect_submodules("JSForm")
    if not name.startswith(("JSForm.tests", "JSForm.examples", "JSForm.DevelopmentTesting"))
    and name != "JSForm.run_jsform_tests"
]
EXCLUDES = ["JSForm.tests", "JSForm.examples", "JSForm.DevelopmentTesting", "JSForm.run_jsform_tests"]
DATAS = [
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

main_a = Analysis(
    [str(ROOT / "installed_launcher.py")], pathex=[str(ROOT), str(JSFORM.parent)],
    binaries=[], datas=DATAS, hiddenimports=HIDDEN, hookspath=[], hooksconfig={},
    runtime_hooks=[], excludes=EXCLUDES, noarchive=False,
)
setup_a = Analysis(
    [str(ROOT / "installed_setup.py")], pathex=[str(ROOT), str(JSFORM.parent)],
    binaries=[], datas=[], hiddenimports=HIDDEN, hookspath=[], hooksconfig={},
    runtime_hooks=[], excludes=EXCLUDES, noarchive=False,
)

main_pyz = PYZ(main_a.pure)
setup_pyz = PYZ(setup_a.pure)
main_exe = EXE(
    main_pyz, main_a.scripts, [], exclude_binaries=True, name="ChurchManager",
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
    console=False, icon=str(ROOT / "cm.ico"),
)
setup_exe = EXE(
    setup_pyz, setup_a.scripts, [], exclude_binaries=True, name="ChurchManagerSetup",
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
    console=False, icon=str(ROOT / "cm.ico"),
)
coll = COLLECT(
    main_exe, setup_exe,
    main_a.binaries, main_a.datas, setup_a.binaries, setup_a.datas,
    strip=False, upx=False, name="ChurchManagerBundle",
)
