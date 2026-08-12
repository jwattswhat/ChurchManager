"""Run one staged local test report and display LimeReport diagnostics only."""

from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT.parent / "JSForm")]

import mariadb
from churchmanager_mode import load_config, resolve_database
from JSForm.fnReport import prepare_lime_report_template
from JSForm.report_credentials import decode_lime_password


def main():
    config = load_config()
    base = config["database_settings"]
    settings = resolve_database({
        "server": base["host"], "database": base["database"],
        "user": base["user"], "password": None, "test_mode": True,
        "jsform_database": None,
    }, config)
    print(
        "Current local credential matches historical LimeReport credential:",
        settings["password"] == decode_lime_password("dJlfSRL7RII="),
    )
    probe = mariadb.connect(
        host=settings["server"], port=settings["port"], database=settings["database"],
        user=settings["user"], password=settings["password"],
    )
    probe_cursor = probe.cursor()
    probe_cursor.execute("SHOW VARIABLES LIKE 'require_secure_transport'")
    print("MariaDB requires secure transport:", probe_cursor.fetchone()[1])
    probe_cursor.execute("SHOW STATUS LIKE 'Ssl_cipher'")
    print("Python connection uses TLS:", bool(probe_cursor.fetchone()[1]))
    probe_cursor.close()
    probe.close()
    framework = mariadb.connect(
        host=settings["server"], port=settings["port"],
        database=settings["database"], user=settings["user"],
        password=settings["password"],
    )
    cursor = framework.cursor()
    cursor.execute(
        "SELECT ConfigValue FROM tblConfig "
        "WHERE ConfigFamily='Location' AND ConfigType='LimeReport'"
    )
    row = cursor.fetchone()
    lime_dir = Path(os.environ.get("CHURCHMANAGER_DIAGNOSTIC_LIME") or (row[0] if row else ROOT.parent / "LimeReports"))
    cursor.close()
    framework.close()
    staged_name, staged = prepare_lime_report_template(
        ROOT / "LimeReportPattern" / "CMMD01.lrxml",
        settings["database"], settings,
    )
    output = ROOT / "tmp" / "pdfs" / "cmmd01-diagnostic.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            [str(lime_dir / "limereport"), f"-s{staged_name}", f"-d{output}", "-pchurchID=1"],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "QT_DEBUG_PLUGINS": "1"},
        )
        print(f"LimeReport exit status: {result.returncode}")
        if result.stdout.strip():
            print("stdout:", result.stdout.strip())
        if result.stderr.strip():
            print("stderr:", result.stderr.strip())
        print("Diagnostic PDF created:", output.exists())
        base_text = Path(staged_name).read_text(encoding="utf-8")
        mapping = {
            "rpt_church_identity": "tblChurch",
            "rpt_directory_family": "tblFamily",
            "rpt_family_address": "tblFamilyAddress",
            "rpt_family_contact": "tblFamilyContact",
            "rpt_person_address": "tblPersonAddress",
            "rpt_person_contact": "tblPersonContact",
            "rpt_membership_person": "tblPerson",
        }
        for view, table in mapping.items():
            base_text = base_text.replace(view, table)
        base_template = Path(staged_name).with_name(Path(staged_name).stem + "-base.lrxml")
        base_template.write_text(base_text, encoding="utf-8")
        base_output = ROOT / "tmp" / "pdfs" / "cmmd01-base-diagnostic.pdf"
        try:
            base_result = subprocess.run(
                [str(lime_dir / "limereport"), f"-s{base_template}", f"-d{base_output}", "-pchurchID=1"],
                capture_output=True, text=True, timeout=60,
            )
            print(f"Base-table comparison exit status: {base_result.returncode}")
            print("Base-table comparison PDF created:", base_output.exists())
        finally:
            base_template.unlink(missing_ok=True)
    finally:
        if staged:
            staged.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
