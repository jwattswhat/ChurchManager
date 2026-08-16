"""Protect ChurchManager's public documentation and project boundaries."""

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProjectDocumentationTests(unittest.TestCase):
    def test_public_project_documents_exist(self):
        required = (
            "README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md", "SUPPORT.md",
            "Documentation/ARCHITECTURE.md", "Documentation/DEVELOPMENT.md",
            "Documentation/ChurchManager.Application.md",
            "Documentation/ChurchManager.UserPersonLink.Specification.md",
            "Documentation/DATABASE_STRUCTURE_INVENTORY.md",
            "Documentation/SCREEN_INVENTORY.md", "Documentation/VERSIONING.md",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_user_person_link_is_documented_in_public_inventories(self):
        specification = (
            ROOT / "Documentation" / "ChurchManager.UserPersonLink.Specification.md"
        ).read_text(encoding="utf-8")
        roadmap = (ROOT / "Documentation" / "ChurchManager.FixList.md").read_text(
            encoding="utf-8"
        )
        screens = (ROOT / "Documentation" / "SCREEN_INVENTORY.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("ON DELETE SET NULL", specification)
        self.assertIn("temporary password is never", specification)
        self.assertIn("ChurchManager.UserPersonLink.Specification.md", roadmap)
        self.assertIn("optional person links", screens)

    def test_license_and_readme_identify_gpl(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("GPL-3.0-or-later", license_text)
        self.assertIn("GPL-3.0-or-later", readme)
        self.assertIn("self-contained ChurchManager application", readme)

    def test_top_level_python_modules_have_docstrings(self):
        for path in ROOT.glob("*.py"):
            with self.subTest(module=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8-sig"))
                self.assertTrue(ast.get_docstring(tree), f"{path.name} needs a module docstring")


if __name__ == "__main__":
    unittest.main()
