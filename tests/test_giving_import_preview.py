"""Tests for non-writing contribution import preview validation."""

from datetime import date
from decimal import Decimal
import unittest

from giving.import_parser import ContributionImportRow
from giving.import_preview import ContributionImportPreviewService


def row(**changes):
    values = dict(row_number=2, received_date=date(2026, 8, 2), amount=Decimal("25.00"),
                  envelope_number="1", contributor="Jonathan Watt", method="ELECTRONIC",
                  reference="A1", purpose="General", description="Gift", fingerprint="same")
    values.update(changes)
    return ContributionImportRow(**values)


class Preview(ContributionImportPreviewService):
    def __init__(self, *, envelope=4, contributor=4, purpose=8, existing=False):
        self.envelope = envelope; self.contributor = contributor
        self.purpose = purpose; self.existing = existing
    def _envelope_contributor(self, source): return self.envelope if source.envelope_number else None
    def _named_contributor(self, source): return self.contributor if source.contributor else None
    def _purpose(self, source): return self.purpose if source.purpose else None
    def _already_imported(self, source): return self.existing


class GivingImportPreviewTests(unittest.TestCase):
    def test_ready_row_resolves_without_writes(self):
        result = Preview().preview((row(),))[0]
        self.assertTrue(result.ready)
        self.assertEqual((result.contributor_id, result.purpose_id), (4, 8))

    def test_identity_disagreement_and_unknown_purpose_are_explicit(self):
        result = Preview(contributor=5, purpose=None).preview((row(),))[0]
        self.assertIn("Envelope and contributor disagree", result.issues)
        self.assertIn("Unknown or inactive purpose", result.issues)

    def test_duplicates_in_file_and_database_are_flagged(self):
        results = Preview(existing=True).preview((row(), row(row_number=3)))
        self.assertTrue(all("Duplicate row in file" in item.issues for item in results))
        self.assertTrue(all("Possible existing contribution" in item.issues for item in results))

    def test_source_uses_only_selects(self):
        from pathlib import Path
        source = (Path(__file__).parents[1] / "giving" / "import_preview.py").read_text(encoding="utf-8")
        self.assertNotIn("INSERT INTO", source)
        self.assertNotIn("UPDATE ", source)
        self.assertNotIn("DELETE FROM", source)


if __name__ == "__main__":
    unittest.main()
