"""Hard separation between development and the Frozen application."""

from pathlib import Path
from types import SimpleNamespace
import unittest

import JSForm

from development_boundary import DevelopmentIsolationError, assert_development_isolation


ROOT = Path(__file__).resolve().parents[1]


class DevelopmentBoundaryTests(unittest.TestCase):
    def test_current_development_jsform_is_the_independent_sibling(self):
        self.assertTrue(assert_development_isolation(JSForm, ROOT))

    def test_frozen_build_accepts_only_its_internal_bundled_jsform(self):
        bundled = SimpleNamespace(__file__=str(ROOT / "JSForm" / "__init__.py"))
        self.assertTrue(assert_development_isolation(bundled, ROOT, frozen=True))
        outside = SimpleNamespace(
            __file__=str(ROOT.parent / "JSForm" / "__init__.py")
        )
        with self.assertRaises(DevelopmentIsolationError):
            assert_development_isolation(outside, ROOT, frozen=True)

    def test_legacy_jsform_is_rejected(self):
        legacy = SimpleNamespace(
            __file__=str(
                ROOT.parent / "ChurchManager-Legacy" / "JSForm" / "__init__.py"
            )
        )
        with self.assertRaises(DevelopmentIsolationError):
            assert_development_isolation(legacy, ROOT)

    def test_running_development_from_legacy_tree_is_rejected(self):
        fake_project = ROOT.parent / "ChurchManager-Legacy" / "ChurchManager"
        fake_jsform = SimpleNamespace(
            __file__=str(ROOT.parent / "ChurchManager-Legacy" / "JSForm" / "__init__.py")
        )
        with self.assertRaises(DevelopmentIsolationError):
            assert_development_isolation(fake_jsform, fake_project)

    def test_project_instructions_make_frozen_app_read_only_and_out_of_scope(self):
        instructions = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Never edit, delete, migrate, synchronize", instructions)
        self.assertIn("separate project", instructions)


if __name__ == "__main__":
    unittest.main()
