"""Render representative report-inventory proofs without database access."""

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import JSForm
from JSForm.report_dataset import ReportDataset

from visual_reports.tabular_dataset import contract_for


ROOT = Path(__file__).resolve().parent
PROOF_CODES = ("CMGN01", "CMAT02", "CMGN02", "CMMB03", "CMPC03")


def sample_value(field, number):
    kind = field.data_type
    if kind == "integer":
        return number * 12
    if kind in ("decimal", "currency"):
        return Decimal("11700.00") + number
    if kind == "date":
        return date(2026, 8, min(number + 1, 28))
    if kind == "datetime":
        return datetime(2026, 8, min(number + 1, 28), 10, 30)
    if kind == "boolean":
        return number % 2 == 0
    return f"Sample {field.label} {number + 1}"


def main():
    output = ROOT / "Reports" / "VisualReportProofs"
    output.mkdir(parents=True, exist_ok=True)
    logo = (ROOT / "TestData" / "Reformation-Lutheran-Church-Test-Logo.png").read_bytes()
    loader = JSForm.ReportDefinitionLoader()
    renderer = JSForm.PDFReportRenderer()
    for code in PROOF_CODES:
        definition = loader.load(ROOT / "visual_reports" / "definitions" / f"{code}.json")
        contract = contract_for(code)
        record_contract = contract.collection("records")
        records = [
            {field.name: sample_value(field, number) for field in record_contract.fields}
            for number in range(38)
        ]
        dataset = ReportDataset.create(contract, {
            "church": [{"ID": 1, "Church": "Reformation Lutheran Church", "Logo": logo}],
            "parameters": [{"Display": "Church: Reformation Lutheran Church; Date range: 8/1/2026 - 8/31/2026"}],
            "records": records,
        })
        renderer.render(definition, dataset, output / f"{code}-proof.pdf")
    print(f"Rendered {len(PROOF_CODES)} proofs in {output}")


if __name__ == "__main__":
    main()
