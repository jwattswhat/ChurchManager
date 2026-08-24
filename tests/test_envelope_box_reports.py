"""Tests for protected envelope-box labels and assignment registers."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import tempfile
import unittest

import JSForm
from pypdf import PdfReader

from giving.reporting import (
    DEFINITIONS,
    ENVELOPE_LABEL_MANIFEST,
    ENVELOPE_REGISTER_MANIFEST,
    EnvelopeBoxReportProvider,
)


class Authorization:
    def require(self, permission, _action):
        if permission != "giving.reports.confidential":
            raise PermissionError(permission)


class Service:
    def __init__(self, count=5):
        self.count = count

    def envelope_assignments(self, _year, **_options):
        return [
            (str(index), f"Contributor {index}", "PERSON", 1,
             date(2027, 1, 1), date(2027, 12, 31))
            for index in range(1, self.count + 1)
        ]

    def all(self, sql, _values=()):
        if "SELECT Church,Logo" in sql:
            return [("Sample Church", None)]
        if "SELECT Church" in sql:
            return [("Sample Church",)]
        return []


class EnvelopeBoxReportTests(unittest.TestCase):
    def provider(self, count=5):
        provider = EnvelopeBoxReportProvider.__new__(EnvelopeBoxReportProvider)
        provider.service = Service(count)
        provider.authorization = Authorization()
        return provider

    def test_labels_pack_three_boxes_per_physical_row(self):
        dataset = self.provider().labels(2027, False, True, True)
        rows = dataset.collections["labelrows"]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["Box1"], "Envelope Box 1")
        self.assertEqual(rows[0]["Box3"], "Envelope Box 3")
        self.assertEqual(rows[1]["Box2"], "Envelope Box 5")
        self.assertEqual(rows[1]["Box3"], "")
        self.assertEqual(rows[0]["Church1"], "Sample Church")

    def test_label_definition_renders_thirty_labels_on_first_page(self):
        definition = JSForm.ReportDefinitionLoader().load(
            DEFINITIONS / "CMGV09.json"
        )
        ENVELOPE_LABEL_MANIFEST.validate(definition)
        dataset = self.provider(31).labels(2027, False, True, False)
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "labels.pdf"
            JSForm.PDFReportRenderer().render(definition, dataset, output)
            reader = PdfReader(output)
            self.assertEqual(len(reader.pages), 2)
            first = reader.pages[0].extract_text()
            second = reader.pages[1].extract_text()
            self.assertIn("Envelope Box 30", first)
            self.assertNotIn("Envelope Box 31", first)
            self.assertIn("Envelope Box 31", second)

    def test_register_contains_effective_dates_and_identity(self):
        definition = JSForm.ReportDefinitionLoader().load(
            DEFINITIONS / "CMGV10.json"
        )
        ENVELOPE_REGISTER_MANIFEST.validate(definition)
        dataset = self.provider(2).register(2027, False, True)
        self.assertEqual(dataset.collections["church"][0]["Church"], "Sample Church")
        self.assertEqual(dataset.collections["records"][0]["From"], date(2027, 1, 1))
        self.assertEqual(dataset.collections["records"][1]["Name"], "Contributor 2")


if __name__ == "__main__":
    unittest.main()
