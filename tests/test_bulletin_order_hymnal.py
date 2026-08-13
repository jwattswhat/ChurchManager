import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BulletinOrderHymnalTests(unittest.TestCase):
    def test_hymnal_link_is_optional_and_foreign_keyed(self):
        migration = (ROOT / "migrations" / "028_link_bulletin_orders_to_hymnals.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("HymnalID int NULL", migration)
        self.assertIn("REFERENCES tblHymnal(ID)", migration)
        self.assertIn("ON DELETE SET NULL", migration)

    def test_custom_copy_inherits_hymnal_and_can_select_no_hymnal(self):
        repository = (ROOT / "bulletin_orders.py").read_text(encoding="utf-8")
        dialog = (ROOT / "bulletin_order_dialog.py").read_text(encoding="utf-8")
        self.assertIn("(ChurchID,HymnalID,Name,Description", repository)
        self.assertIn('self.hymnal.Append("No hymnal")', dialog)
        self.assertIn("set_template_hymnal", dialog)

    def test_weekly_choices_follow_church_hymnal_and_include_neutral_templates(self):
        repository = (ROOT / "bulletin_orders.py").read_text(encoding="utf-8")
        weekly = (ROOT / "weekly_bulletin_order_dialog.py").read_text(encoding="utf-8")
        self.assertIn("c.PrimaryHymnalID", repository)
        self.assertIn("template[5] is None", repository)
        self.assertIn("templates_for_service(service_id)", weekly)


if __name__ == "__main__":
    unittest.main()
