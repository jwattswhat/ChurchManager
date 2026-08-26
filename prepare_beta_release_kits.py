"""Create clean-install and fictional-beta release kit directories."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from churchmanager_version import __version__
from install_beta_test_dataset import MANIFEST, load_manifest
import JSForm


ROOT = Path(__file__).resolve().parent


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def prepare(root=ROOT):
    """Stage both release profiles without rebuilding or modifying the MSI."""
    root = Path(root)
    installer = root / "dist" / f"ChurchManager-{__version__}.msi"
    if not installer.is_file():
        raise FileNotFoundError(
            f"Build the current installer first; expected {installer.name}."
        )
    manifest = load_manifest(root / "TestData" / "BetaDataset" / "manifest.json")
    release = root / "dist" / "release-kits" / __version__
    clean = release / "Clean-Installation"
    beta = release / "Beta-Test-With-Fictional-Data"
    if release.exists():
        shutil.rmtree(release)
    clean.mkdir(parents=True); beta.mkdir(parents=True)
    for destination in (clean, beta):
        shutil.copy2(installer, destination / installer.name)
    data = beta / "Beta-Test-Data"
    data.mkdir()
    shutil.copy2(MANIFEST, data / "manifest.json")
    (beta / "Install Fictional Beta Data.cmd").write_text(
        "@echo off\r\n"
        "\"%ProgramFiles%\\ChurchManager\\ChurchManagerBetaData.exe\" --apply --confirm ChurchDBTest\r\n"
        "if errorlevel 1 pause\r\n",
        encoding="ascii",
    )
    (beta / "Start ChurchManager Beta Test.cmd").write_text(
        "@echo off\r\n\"%ProgramFiles%\\ChurchManager\\ChurchManager.exe\" --test\r\n",
        encoding="ascii",
    )
    (clean / "README.txt").write_text(
        "ChurchManager clean installation\n\nRun the MSI. No fictional congregation data is installed.\n",
        encoding="utf-8",
    )
    (beta / "README.txt").write_text(
        "ChurchManager beta test installation\n\n"
        "1. Run the MSI and create the local ChurchDBTest test installation.\n"
        "2. Start ChurchManager once and finish the Master Administrator setup.\n"
        "3. Run Install Fictional Beta Data.cmd once.\n"
        "4. Use Start ChurchManager Beta Test.cmd for beta testing.\n"
        "Never use this dataset with a real congregation database.\n",
        encoding="utf-8",
    )
    evidence = {
        "release": __version__, "installer": installer.name,
        "installer_bytes": installer.stat().st_size,
        "installer_sha256": sha256(installer),
        "profiles": [clean.name, beta.name],
        "beta_dataset": manifest["dataset_id"],
        "beta_dataset_version": manifest["dataset_version"],
        "bundled_jsform_version": JSForm.__version__,
    }
    clean_zip = Path(shutil.make_archive(
        str(release / "ChurchManager-Clean-Installation"), "zip", clean,
    ))
    beta_zip = Path(shutil.make_archive(
        str(release / "ChurchManager-Beta-Test-With-Fictional-Data"), "zip", beta,
    ))
    evidence["archives"] = {
        clean_zip.name: {"bytes": clean_zip.stat().st_size, "sha256": sha256(clean_zip)},
        beta_zip.name: {"bytes": beta_zip.stat().st_size, "sha256": sha256(beta_zip)},
    }
    (release / "release-kit-evidence.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )
    return release, evidence


if __name__ == "__main__":
    folder, result = prepare()
    print(f"release_kits={folder}")
    print(json.dumps(result, indent=2))
