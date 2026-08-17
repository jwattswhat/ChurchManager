"""Tests for permission-independent local lectionary maintenance."""

from pathlib import Path
import unittest

from local_lectionary_dialog import clean_citation, clean_name, local_key
from main_menu import FORM_ROUTES, SPECIAL_CONTROLS


class LocalLectionaryDialogTests(unittest.TestCase):
    def test_local_keys_are_unique_and_reserved(self):
        first = local_key("system"); second = local_key("system")
        self.assertTrue(first.startswith("local-system-"))
        self.assertNotEqual(first, second)

    def test_names_are_required_and_bounded(self):
        self.assertEqual(clean_name("  Parish Cycle "), "Parish Cycle")
        with self.assertRaises(ValueError): clean_name(" ")
        with self.assertRaises(ValueError): clean_name("x" * 256)

    def test_reading_appointments_accept_citations_not_body_text(self):
        self.assertEqual(clean_citation("  John  3:16-17 "), "John 3:16-17")
        with self.assertRaises(ValueError): clean_citation(" ")
        with self.assertRaises(ValueError): clean_citation("John 3:16\nFor God so loved")

    def test_main_menu_uses_protected_local_editor(self):
        self.assertNotIn("lblPropers", FORM_ROUTES)
        self.assertIn("lblPropers", SPECIAL_CONTROLS)
        source = Path("cm.py").read_text(encoding="utf-8")
        self.assertIn('case "lblPropers":', source)
        self.assertIn("show_local_lectionaries", source)

    def test_repository_queries_exclude_package_owned_rows(self):
        source = Path("local_lectionary_dialog.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(source.count("PackageID IS NULL"), 6)
        self.assertNotIn("DELETE FROM", source)
        for value in ('("a", "Year A", 1)', '("b", "Year B", 2)',
                      '("c", "Year C", 3)'):
            self.assertIn(value, source)
        self.assertIn("ON DUPLICATE KEY UPDATE", source)
        self.assertIn("def save_cycle", source)
        self.assertIn("def set_cycle_active", source)
        self.assertIn("JOIN tblLectionaryEdition e", source)
        self.assertIn("def save_proper", source)
        self.assertIn("def set_proper_active", source)
        self.assertIn("local_key(\"proper\")", source)
        self.assertIn("p.PackageID IS NULL", source)
        self.assertIn('("Propers...", self.on_propers)', source)
        self.assertIn("class _PropersDialog", source)
        self.assertIn("rule_date(calendar_rule, 2026)", source)
        self.assertIn("def save_appointment", source)
        self.assertIn("def set_appointment_active", source)
        self.assertIn("class _AppointmentsDialog", source)
        self.assertIn('("Readings...", self.on_readings)', source)
        self.assertIn("Enter the biblical citation only", source)

    def test_unchanged_local_records_are_not_treated_as_missing(self):
        source = Path("local_lectionary_dialog.py").read_text(encoding="utf-8")
        self.assertIn("def _require_record", source)
        self.assertIn("zero affected rows when an UPDATE writes", source)
        self.assertNotIn("if cursor.rowcount != 1", source)


if __name__ == "__main__":
    unittest.main()
