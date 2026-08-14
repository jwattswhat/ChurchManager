"""Checks for ChurchManager's authoritative semantic version."""

import unittest

import JSForm

from churchmanager_version import __version__
from startup import main_window_title


class VersioningTests(unittest.TestCase):
    def test_application_version_is_semantic_development_version(self):
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+-dev$")

    def test_window_titles_include_version_and_preserve_test_warning(self):
        self.assertEqual(main_window_title({"test_mode": False}), "ChurchManager 0.1.0-dev")
        self.assertEqual(
            main_window_title({"test_mode": True, "database": "ChurchDBTest"}),
            "ChurchManager 0.1.0-dev - TEST MODE - ChurchDBTest",
        )

    def test_framework_has_independent_semantic_version(self):
        self.assertEqual(JSForm.__version__, "0.1.0-dev")


if __name__ == "__main__":
    unittest.main()
