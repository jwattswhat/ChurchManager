"""Build and verify the ChurchManager Windows executable bundle and MSI."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import JSForm
from churchmanager_version import __version__


ROOT = Path(__file__).resolve().parent


def msi_version(release: str) -> str:
    """Return the numeric three-part MSI version for an application release."""
    numeric = release.split("-", 1)[0].split("+", 1)[0]
    parts = numeric.split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValueError(f"ChurchManager release is not MSI-compatible: {release}")
    return numeric


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    """Run one release command and stop immediately if it fails."""
    print("Running:", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def sha256(path: Path) -> str:
    """Return the lowercase SHA-256 digest of one release artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    """Create the shared bundle, prove both entry points, and build the MSI."""
    python = ROOT / ".runtime-venv" / "Scripts" / "python.exe"
    wix = ROOT / ".tools" / "wix" / "wix.exe"
    dotnet = ROOT / ".tools" / "dotnet"
    for required in (python, wix, dotnet):
        if not required.exists():
            raise FileNotFoundError(f"Required release tool is missing: {required}")

    bundle = ROOT / "dist" / "ChurchManagerBundle"
    run([
        str(python), "-m", "PyInstaller", "--noconfirm", "--clean",
        "--distpath", "dist", "--workpath", "build",
        str(ROOT / "packaging" / "ChurchManagerBundle.spec"),
    ])

    evidence_files = []
    for executable in (
        "ChurchManager.exe", "ChurchManagerSetup.exe", "ChurchManagerBetaData.exe"
    ):
        evidence = ROOT / "dist" / f"{Path(executable).stem}.package-check.json"
        run([str(bundle / executable), "--package-check", str(evidence)])
        result = json.loads(evidence.read_text(encoding="utf-8"))
        if not result.get("passed"):
            raise RuntimeError(f"Packaged resource proof failed: {executable}")
        evidence_files.append(evidence)

    environment = os.environ.copy()
    environment["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    environment["DOTNET_ROOT"] = str(dotnet)
    environment["PATH"] = f"{dotnet}{os.pathsep}{environment.get('PATH', '')}"
    artifact = ROOT / "dist" / f"ChurchManager-{__version__}.msi"
    command = [
        str(wix), "build", "-arch", "x64",
        "-d", f"ProductVersion={msi_version(__version__)}",
        "-b", f"AppFiles={bundle}", "-o", str(artifact),
        str(ROOT / "packaging" / "ChurchManager.wxs"),
    ]
    print("Running:", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=environment, check=True)

    files = [path for path in bundle.rglob("*") if path.is_file()]
    summary = {
        "release": __version__,
        "bundled_jsform_version": JSForm.__version__,
        "msi_version": msi_version(__version__),
        "bundle_files": len(files),
        "bundle_bytes": sum(path.stat().st_size for path in files),
        "msi": str(artifact),
        "msi_bytes": artifact.stat().st_size,
        "msi_sha256": sha256(artifact),
        "package_checks": [str(path) for path in evidence_files],
    }
    summary_path = ROOT / "dist" / "windows-release-evidence.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
