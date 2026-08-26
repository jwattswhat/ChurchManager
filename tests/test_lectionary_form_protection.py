"""Contract tests for package-owned lectionary edit protection."""

from pathlib import Path
import unittest


class LectionaryFormProtectionTests(unittest.TestCase):
    def test_package_owned_systems_and_propers_are_protected(self):
        source = Path("cm.py").read_text(encoding="utf-8")
        self.assertIn('{"frmLectionarySystem", "frmPropers"}', source)
        self.assertIn('record.get("PackageID") is not None', source)
        self.assertIn("Packaged lectionary records are read-only", source)
        self.assertIn("Retire the owning", source)

    def test_protection_does_not_apply_to_unrelated_forms(self):
        source = Path("cm.py").read_text(encoding="utf-8")
        method = source.split("def _protected_lectionary_record", 1)[1]
        self.assertIn("return False", method)


if __name__ == "__main__":
    unittest.main()
