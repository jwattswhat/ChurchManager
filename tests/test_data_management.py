"""Tests for guarded membership data management."""

import json
from pathlib import Path
import tempfile
import unittest

from data_management import (
    duplicate_pairs,
    mapped_csv_preview,
    normalized_contact,
    normalized_text,
    read_csv_rows,
    suggested_csv_mapping,
)


ROOT = Path(__file__).resolve().parents[1]


class DataManagementTests(unittest.TestCase):
    def test_comparison_normalization_is_exact_but_presentation_neutral(self):
        self.assertEqual(normalized_text("  Sarah  O'Neil "), "sarah o neil")
        self.assertEqual(normalized_contact("(218) 555-0100"), "2185550100")
        self.assertEqual(normalized_contact(" Sarah@Example.COM "), "sarah@example.com")

    def test_duplicate_pairs_ignore_blanks_and_do_not_self_match(self):
        rows = [(1, "Sarah Johnson", 1), (2, "Sarah  Johnson", 1), (3, "", 1)]
        found = duplicate_pairs(
            rows, lambda row: (row[2], normalized_text(row[1])), "Person", "Same full name"
        )
        self.assertEqual(len(found), 1)
        self.assertEqual((found[0].first_id, found[0].second_id), (1, 2))

    def test_csv_preview_maps_people_without_database_access(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "people.csv"
            path.write_text(
                "First Name,Last Name,Email\nSarah,Johnson,sarah@example.com\n",
                encoding="utf-8",
            )
            headers, rows = read_csv_rows(path)
        mapping = suggested_csv_mapping(headers, "People")
        preview = mapped_csv_preview(rows, "People", mapping)
        self.assertEqual(preview[0]["FirstName"], "Sarah")
        self.assertEqual(preview[0]["LastName"], "Johnson")
        self.assertEqual(preview[0]["Email"], "sarah@example.com")

    def test_reviewed_import_has_history_and_atomic_safety_boundaries(self):
        migration = (ROOT / "migrations" / "099_add_membership_import_history.sql").read_text(
            encoding="utf-8"
        )
        source = (ROOT / "data_management.py").read_text(encoding="utf-8")
        self.assertIn("CREATE TABLE tblMembershipImportHistory", migration)
        self.assertIn("SourceSHA256", migration)
        self.assertNotIn("SourceContent", migration)
        self.assertIn("self.connection.rollback()", source)
        self.assertIn("This creates new records", source)
        self.assertIn("does not merge or replace", source)
        self.assertIn("SELECT ID,Church FROM tblChurch", source)
        self.assertNotIn("SELECT ID,ChurchName FROM tblChurch", source)

    def test_export_is_privacy_safe_and_records_history(self):
        migration = (ROOT / "migrations" / "100_add_membership_export_history.sql").read_text(
            encoding="utf-8"
        )
        source = (ROOT / "data_management.py").read_text(encoding="utf-8")
        self.assertIn("CREATE TABLE tblMembershipExportHistory", migration)
        self.assertIn("IncludedUnlistedContacts", migration)
        self.assertIn("COALESCE(pc.Unlisted,0)=0", source)
        self.assertIn("COALESCE(fc.Unlisted,0)=0", source)
        self.assertIn("COALESCE(candidate.Unlisted,0)=0", source)
        self.assertNotIn("PasswordHash", source)
        self.assertNotIn("tblContribution", source)
        self.assertNotIn("tblPastoral", source)

    def test_duplicate_resolution_is_audited_and_non_destructive(self):
        migration = (ROOT / "migrations" / "101_add_duplicate_review_resolution.sql").read_text(
            encoding="utf-8"
        )
        source = (ROOT / "data_management.py").read_text(encoding="utf-8")
        self.assertIn("CREATE TABLE tblDuplicateReviewResolution", migration)
        self.assertIn("NOT_DUPLICATE", migration)
        self.assertIn("DEFERRED", migration)
        self.assertIn("ResolvedByUserID", migration)
        self.assertIn("Decisions never delete, merge", source)
        self.assertNotIn("DELETE FROM tblPerson", source)
        self.assertNotIn("DELETE FROM tblFamily", source)

    def test_duplicate_fixture_is_explicitly_guarded_and_idempotent(self):
        source = (ROOT / "seed_duplicate_review_test_data.py").read_text(encoding="utf-8")
        self.assertIn('!= "churchdbtest"', source)
        self.assertIn("if not args.apply", source)
        self.assertIn("while existing < 2", source)
        self.assertIn("CMTEST: duplicate review fixture", source)

    def test_csv_preview_requires_explicit_required_and_unique_mappings(self):
        rows = [{"Name": "Johnson", "Other": "Sarah"}]
        with self.assertRaisesRegex(ValueError, "First name"):
            mapped_csv_preview(rows, "People", {"LastName": "Name"})
        with self.assertRaisesRegex(ValueError, "only one"):
            mapped_csv_preview(
                rows, "People", {"FirstName": "Name", "LastName": "Name"}
            )

    def test_csv_reader_rejects_blank_data_files(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "empty.csv"
            path.write_text("First Name,Last Name\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no data rows"):
                read_csv_rows(path)

    def test_main_menu_opens_data_management_with_membership_permission(self):
        controls = json.loads((ROOT / "Forms" / "frmMain.json").read_text(encoding="utf-8"))[
            "frmMainFORM"
        ]["CONTROLS"]
        self.assertEqual(
            controls["lblDataManagement"]["security"]["invoke"], "membership.manage"
        )
        menu = (ROOT / "main_menu.py").read_text(encoding="utf-8")
        application = (ROOT / "cm.py").read_text(encoding="utf-8")
        permissions = (ROOT / "permission_catalog.py").read_text(encoding="utf-8")
        self.assertIn('"lblDataManagement"', menu)
        self.assertIn('case "lblDataManagement"', application)
        self.assertIn('"lblDataManagement": "membership.manage"', permissions)

    def test_specification_requires_preview_privacy_and_human_review(self):
        specification = (ROOT / "Documentation" / "ChurchManager.DataManagement.Specification.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Import preview never writes", specification)
        self.assertIn("never silently merges", specification)
        self.assertIn("unlisted contact", specification)
        self.assertIn("Portable archives", specification)
        self.assertIn("explicit column mapping", specification)


if __name__ == "__main__":
    unittest.main()
