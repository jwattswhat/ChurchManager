"""Keep the maintained screen inventory synchronized with JSON definitions."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "Documentation" / "SCREEN_INVENTORY.md"


class ScreenInventoryTests(unittest.TestCase):
    RETIRED_DEVELOPMENT_FORMS = {
        "frmAltReading", "frmAnnouncementKiosk", "frmAsset", "frmChecklist",
        "frmchoices", "frmEditCheckList", "frmGenerateOS",
        "frmGenerateWorshipPlanning", "frmHymnHistory", "frmHymnSearch",
        "frmHymnUsage", "frmHymnUsageDisplay", "frmMembershipMain", "frmNote",
        "frmOpenMembership", "frmOpenWorship", "frmPersonDateGrid", "frmReading",
        "frmReadingList", "frmSchedule", "frmService", "frmServiceSchedule",
    }

    def test_every_development_json_screen_is_in_inventory(self):
        text = INVENTORY.read_text(encoding="utf-8")
        missing = [
            path.stem for path in sorted((ROOT / "Forms").glob("*.json"))
            if f"`{path.stem}`" not in text
        ]
        self.assertEqual(missing, [])

    def test_inventory_has_required_ownership_columns(self):
        text = INVENTORY.read_text(encoding="utf-8")
        self.assertIn("Why ChurchManager-only?", text)
        self.assertIn("Last reviewed:", text)

    def test_retired_definitions_do_not_return_to_development(self):
        present = {path.stem for path in (ROOT / "Forms").glob("*.json")}
        self.assertEqual(present & self.RETIRED_DEVELOPMENT_FORMS, set())


if __name__ == "__main__":
    unittest.main()
