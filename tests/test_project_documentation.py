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
            "Documentation/ChurchManager.SMTPConnection.Specification.md",
            "Documentation/ChurchManager.SMTPConnection.Review.md",
            "Documentation/ChurchManager.OrderOfServiceCatalog.Specification.md",
            "Documentation/ChurchManager.DataManagement.Specification.md",
            "Documentation/ChurchManager.LSBOrderOfService.Inventory.md",
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

    def test_secure_smtp_work_is_specified_and_on_the_roadmap(self):
        specification = (
            ROOT / "Documentation" / "ChurchManager.SMTPConnection.Specification.md"
        ).read_text(encoding="utf-8")
        roadmap = (ROOT / "Documentation" / "ChurchManager.FixList.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Windows Credential Manager", specification)
        self.assertIn("Plain unencrypted SMTP is prohibited", specification)
        self.assertIn("Send Test Email", specification)
        self.assertIn("all email\ndelivery is disabled", specification)
        self.assertIn("### 4. Secure SMTP connection", roadmap)

    def test_future_remote_access_requires_a_vendor_neutral_vpn(self):
        roadmap = (ROOT / "Documentation" / "ChurchManager.FixList.md").read_text(
            encoding="utf-8"
        )
        security = (
            ROOT / "Documentation" / "ChurchManager.UserSecurity.Specification.md"
        ).read_text(encoding="utf-8")
        self.assertIn("recommendation vendor-neutral", roadmap)
        self.assertIn("encrypted VPN", security)
        self.assertIn("must not be exposed directly to the public internet", security)

    def test_jsform_single_database_migration_is_completed(self):
        roadmap = (ROOT / "Documentation" / "ChurchManager.FixList.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Remove obsolete JSForm dual-database compatibility use", roadmap)
        self.assertIn("Resolved: migrated from JSForm's obsolete dual-database compatibility API", roadmap)
        self.assertIn("| 17 | Completed |", roadmap)
        for relative_path in (
            "startup.py", "churchmanager_mode.py", "report_support.py", "cm.py",
            "backup_restore_dialog.py", "churchmanager.json",
            "installation/default_churchmanager.json",
        ):
            source = (ROOT / relative_path).read_text(encoding="utf-8-sig")
            for compatibility_name in (
                "jsform_database", "JSConnection", "JSCredintials", "framework_settings",
            ):
                self.assertNotIn(compatibility_name, source, relative_path)

    def test_confirmed_stale_development_modules_are_retired(self):
        for name in (
            "fnDatabase.py", "network.py", "rptFormCheck.py",
            "CheckFormsWithSchema.py", "polish_screen_starters.py",
            "inspect_local_bank_matching.py",
            "inspect_local_posted_bank_lines.py",
            "inspect_local_reconciliation_state.py", "inventory_group_data.py",
        ):
            self.assertFalse((ROOT / name).exists(), name)
        roadmap = (ROOT / "Documentation" / "ChurchManager.FixList.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Remove confirmed stale development modules", roadmap)
        self.assertIn("Retire completed one-time development routines", roadmap)

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
