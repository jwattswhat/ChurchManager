"""Mechanically replace legacy LimeReport base-table sources with report views."""

from pathlib import Path
import re


SOURCE_MAP = {
    "tblChurch": "rpt_church_identity",
    "tblAsset": "rpt_asset",
    "tblDocument": "rpt_document",
    "tblAttendanceEvent": "rpt_attendance_event",
    "tblAttendance": "rpt_attendance",
    "tblService": "rpt_service",
    "tblPerson": "rpt_membership_person",
    "tblPersonContact": "rpt_person_contact",
    "tblPersonAddress": "rpt_person_address",
    "tblPersonDate": "rpt_person_date",
    "tblFamily": "rpt_directory_family",
    "tblFamilyAddress": "rpt_family_address",
    "tblFamilyContact": "rpt_family_contact",
    "tblHymn": "rpt_hymn",
    "tblHymnUsage": "rpt_hymn_usage",
    "tblPropers": "rpt_propers",
    "tblReading": "rpt_reading",
    "tblParticipant": "rpt_participant",
    "tblServiceRole": "rpt_service_role",
    "tblProject": "rpt_project",
    "tblTask": "rpt_task",
    "tblTaskWorker": "rpt_task_worker",
    "tblJournal": "rpt_journal",
    "tblPastor": "rpt_pastor_report",
    "tblReports": "rpt_report_catalog",
    "tblSermon": "rpt_sermon",
    "tblEnhancement": "rpt_enhancement",
}


def main():
    report_dir = Path(__file__).resolve().parents[1] / "LimeReportPattern"
    paths = sorted(report_dir.glob("*.lrxml")) + sorted(report_dir.glob("*.lrsml"))
    replacements = sorted(SOURCE_MAP.items(), key=lambda item: -len(item[0]))
    changed = []
    for path in paths:
        original = path.read_text(encoding="utf-8")
        converted = original
        for table, view in replacements:
            converted = re.sub(rf"\b{re.escape(table)}\b", view, converted, flags=re.I)
        for tag in ("databaseName", "host", "userName"):
            converted = re.sub(
                rf'(<{tag}\s+Type="QString">)[^<]*(</{tag}>)',
                rf'\1\2',
                converted,
            )
        converted = re.sub(
            r'(<password\b[^>]*\bValue=")[^"]*("[^>]*/>)',
            r'\1\2',
            converted,
        )
        if converted != original:
            path.write_text(converted, encoding="utf-8")
            changed.append(path.name)
    print(f"Converted {len(changed)} report templates")
    for name in changed:
        print(name)


if __name__ == "__main__":
    main()
