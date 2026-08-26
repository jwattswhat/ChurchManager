import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from user_help import UserGuideError, find_user_guide, open_user_guide
from churchmanager_version import __version__


class UserHelpTests(unittest.TestCase):
    def test_maintained_source_matches_application_version(self):
        source = (Path(__file__).parents[1] / "Documentation" / "ChurchManager.UserGuide.md").read_text(encoding="utf-8")
        self.assertIn(f"Version {__version__}", source)

    def test_finds_repository_guide(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            guide = root / "output" / "pdf" / "ChurchManager.UserGuide.pdf"
            guide.parent.mkdir(parents=True)
            guide.write_bytes(b"%PDF-test")
            self.assertEqual(find_user_guide(root), guide)

    def test_missing_guide_has_nontechnical_message(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(UserGuideError, "not installed"):
                find_user_guide(Path(folder))

    def test_opens_guide_with_windows_default_application(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            guide = root / "output" / "pdf" / "ChurchManager.UserGuide.pdf"
            guide.parent.mkdir(parents=True)
            guide.write_bytes(b"%PDF-test")
            with patch("user_help.os.startfile", create=True) as startfile:
                self.assertEqual(open_user_guide(root), guide)
            startfile.assert_called_once_with(guide)


if __name__ == "__main__":
    unittest.main()
