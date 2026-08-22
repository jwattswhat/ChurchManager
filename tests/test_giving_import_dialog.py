"""Static GUI contracts for contribution import preview."""

from pathlib import Path
import unittest


class GivingImportDialogTests(unittest.TestCase):
    def test_preview_is_explicitly_non_writing_and_reachable(self):
        root = Path(__file__).parents[1]
        dialog = (root / "giving" / "import_dialog.py").read_text(encoding="utf-8")
        batches = (root / "giving" / "batch_dialog.py").read_text(encoding="utf-8")
        self.assertIn("Preview performs no database changes", dialog)
        self.assertIn("Preview Rows", dialog)
        self.assertIn("Import Ready Rows to Draft Batch", dialog)
        self.assertIn("Import CSV...", batches)


if __name__ == "__main__":
    unittest.main()
