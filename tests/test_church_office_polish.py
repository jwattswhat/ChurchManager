"""Protect the Church menu, report activation, People layout, and test fixture."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


def menu_by_label(label):
    definition = json.loads((ROOT / "Menus" / "main.menu.json").read_text(encoding="utf-8"))
    return next(menu for menu in definition["menus"] if menu["label"] == label)


def commands(items):
    for item in items:
        if "command" in item:
            yield item["command"]
        yield from commands(item.get("items", ()))


class TestChurchOfficePolish(unittest.TestCase):
    def test_church_menu_owns_congregation_documents_journal_and_assets(self):
        church = set(commands(menu_by_label("&Church")["items"]))
        self.assertEqual(
            church,
            {
                "churchmanager.church", "churchmanager.journal",
                "churchmanager.document", "churchmanager.assets",
                "churchmanager.asset_locations", "churchmanager.asset_maintenance",
                "churchmanager.asset_reports",
            },
        )
        people = set(commands(menu_by_label("&People")["items"]))
        self.assertTrue(
            {"churchmanager.church", "churchmanager.journal", "churchmanager.document"}.isdisjoint(people)
        )
        labels = [menu["label"] for menu in json.loads(
            (ROOT / "Menus" / "main.menu.json").read_text(encoding="utf-8")
        )["menus"]]
        self.assertNotIn("A&ssets", labels)

    def test_report_grid_double_click_runs_selected_report(self):
        source = (ROOT / "cm.py").read_text(encoding="utf-8")
        report_case = source.split('case "lblReports":', 1)[1].split(
            'case "lblAssets":', 1
        )[0]
        self.assertIn(
            'CONTROLID["ReportID"].Bind(wx.EVT_LIST_ITEM_ACTIVATED, _runReports)',
            report_case,
        )

    def test_person_secondary_controls_are_compact_and_picture_is_lower(self):
        controls = json.loads((ROOT / "Forms" / "frmPerson.json").read_text(
            encoding="utf-8"
        ))["frmPersonFORM"]["CONTROLS"]
        self.assertEqual(controls["btnPersonAddress"]["label"], "Addresses...")
        self.assertEqual(controls["btnPersonContact"]["label"], "Contacts...")
        self.assertEqual(controls["btnPersonDate"]["label"], "Significant Dates...")
        self.assertEqual(controls["lblPicture"]["posch"], [37, 9])
        self.assertEqual(controls["Picture"]["posch"], [37, 11])

    def test_document_and_journal_fixture_is_guarded_and_repeatable(self):
        source = (ROOT / "seed_document_journal_test_data.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('database.casefold() != "churchdbtest"', source)
        self.assertIn('CHURCH_NAME = "Reformation Lutheran Church"', source)
        self.assertIn('parser.add_argument("--apply"', source)
        self.assertIn("DELETE FROM tblDocument WHERE Note=?", source)
        self.assertIn("DELETE FROM tblJournal WHERE Note LIKE ?", source)
        self.assertTrue((ROOT / "Documents" / "Sample Congregational Document.txt").is_file())
        self.assertIn("create_sample_docx", source)
        self.assertIn("Test.Document.70.docx", source)

    def test_user_guide_and_github_pages_site_cover_current_capabilities(self):
        guide = (ROOT / "Documentation" / "ChurchManager.UserGuide.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("**Church > Documents**", guide)
        church_records = guide.split("## 3. Church records", 1)[1].split(
            "## 4. People and congregation records", 1
        )[0]
        people_records = guide.split("## 4. People and congregation records", 1)[1].split(
            "## 5. Worship planning", 1
        )[0]
        self.assertIn("### Church information", church_records)
        self.assertNotIn("### Church information", people_records)
        self.assertIn("double-click the selected report row", guide)
        site = (ROOT / "website" / "index.html").read_text(encoding="utf-8")
        people_card = site.split("<h3>People and congregation</h3>", 1)[1].split(
            "</article>", 1
        )[0]
        self.assertNotIn("documents", people_card.casefold())
        self.assertNotIn("journal", people_card.casefold())
        for capability in ("Member giving", "Groups and pastoral care", "Church office", "Events and calendars"):
            self.assertIn(capability, site)
        self.assertIn("Version 0.3.0-beta.1", site)
        self.assertIn("ChurchManager-Beta-Test-With-Fictional-Data.zip", site)
        self.assertIn("ChurchManager-Clean-Installation.zip", site)
        self.assertTrue((ROOT / "website" / ".nojekyll").is_file())


if __name__ == "__main__":
    unittest.main()
