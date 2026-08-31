"""Checks for ChurchManager's authoritative semantic version."""

import unittest

import JSForm

from churchmanager_version import __version__
from startup import main_window_title


class VersioningTests(unittest.TestCase):
    def test_application_version_is_an_approved_semantic_prerelease(self):
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+-(?:dev|beta\.\d+)$")

    def test_window_titles_include_version_and_preserve_test_warning(self):
        self.assertEqual(main_window_title({"test_mode": False}), "ChurchManager 0.3.0-beta.4")
        self.assertEqual(
            main_window_title({"test_mode": True, "database": "ChurchDBTest"}),
            "ChurchManager 0.3.0-beta.4 - TEST MODE - ChurchDBTest",
        )

    def test_framework_has_independent_semantic_version(self):
        self.assertRegex(JSForm.__version__, r"^\d+\.\d+\.\d+-(?:dev|beta\.\d+)$")
        self.assertNotEqual(JSForm.__version__, __version__)


if __name__ == "__main__":
    unittest.main()
