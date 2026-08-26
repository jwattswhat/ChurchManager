"""Tests for the development launcher that does not expose a console."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WindowlessLauncherTests(unittest.TestCase):
    def test_windowless_launcher_uses_test_database_boundary(self):
        source = (ROOT / "ChurchManager-Test.pyw").read_text(encoding="utf-8")
        self.assertIn("assert_development_isolation", source)
        self.assertIn('"--test"', source)
        self.assertIn('"127.0.0.1"', source)
        self.assertIn('"church"', source)

    def test_documentation_prefers_windowless_launcher(self):
        self.assertIn("ChurchManager-Test.pyw", (ROOT / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
