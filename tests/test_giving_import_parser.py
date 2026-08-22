"""Tests for non-destructive contribution CSV parsing."""

from decimal import Decimal
import unittest

from giving.import_parser import (
    ContributionCsvMapping, ContributionImportError, csv_headers, file_hash, parse_csv,
)


CSV = b"Date,Envelope,Name,Amount,Method,Reference,Purpose,Description\n8/2/2026,001,,25.00,ACH,A1,General,Online gift\n8/9/2026,,Sarah Johnson,$40.00,Check,104,Building,Weekly gift\n"


class GivingImportParserTests(unittest.TestCase):
    def mapping(self, **changes):
        values = dict(date_column="Date", envelope_column="Envelope", contributor_column="Name",
                      amount_column="Amount", method_column="Method", reference_column="Reference",
                      purpose_column="Purpose", description_column="Description")
        values.update(changes)
        return ContributionCsvMapping(**values)

    def test_headers_and_hash_are_stable(self):
        self.assertEqual(csv_headers(CSV)[:3], ("Date", "Envelope", "Name"))
        self.assertEqual(file_hash(CSV), file_hash(CSV))

    def test_rows_are_normalized_without_database_access(self):
        rows = parse_csv(CSV, self.mapping())
        self.assertEqual(len(rows), 2)
        self.assertEqual((rows[0].envelope_number, rows[0].method, rows[0].amount),
                         ("1", "ELECTRONIC", Decimal("25.00")))
        self.assertEqual((rows[1].contributor, rows[1].method), ("Sarah Johnson", "CHECK"))

    def test_missing_identity_is_rejected_with_row_number(self):
        content = b"Date,Envelope,Name,Amount\n8/2/2026,,,25\n"
        with self.assertRaisesRegex(ContributionImportError, "Row 2"):
            parse_csv(content, self.mapping(method_column=None, reference_column=None,
                                             purpose_column=None, description_column=None))

    def test_nonpositive_and_malformed_amounts_are_rejected(self):
        for value in (b"0", b"-1", b"abc"):
            content = b"Date,Envelope,Amount\n8/2/2026,1," + value + b"\n"
            mapping = ContributionCsvMapping("Date", "Amount", envelope_column="Envelope")
            with self.assertRaises(ContributionImportError):
                parse_csv(content, mapping)

    def test_mapping_requires_identity_and_known_columns(self):
        with self.assertRaisesRegex(ContributionImportError, "envelope or contributor"):
            parse_csv(CSV, ContributionCsvMapping("Date", "Amount"))
        with self.assertRaisesRegex(ContributionImportError, "Missing"):
            parse_csv(CSV, self.mapping(amount_column="Missing"))


if __name__ == "__main__":
    unittest.main()
