from pathlib import Path
import tempfile
import unittest

from visual_reports.designer import ensure_user_definition, user_definition_path


class TestVisualReportDesignerStorage(unittest.TestCase):
    def test_starter_is_copied_without_being_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            first = ensure_user_definition("CMMD01", folder)
            original = first.read_text(encoding="utf-8")
            first.write_text(original.replace("Member Directory", "Custom Directory", 1), encoding="utf-8")
            second = ensure_user_definition("CMMD01", folder)
            self.assertEqual(first, second)
            self.assertIn("Custom Directory", second.read_text(encoding="utf-8"))
            self.assertEqual(first, user_definition_path("CMMD01", folder))


if __name__ == "__main__":
    unittest.main()
