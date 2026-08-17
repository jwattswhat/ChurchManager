"""Guard the documented no-permission, no-distribution boundary."""

from pathlib import Path
import unittest


class LectionaryProvenanceDocumentationTests(unittest.TestCase):
    def test_public_packages_remain_blocked_without_written_permission(self):
        text = Path(
            "Documentation/ChurchManager.LectionaryPackageProvenance.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Distribution blocked pending written permission", text)
        self.assertIn("LOCAL_ONLY", text)
        self.assertIn("must not commit or distribute", text)
        self.assertIn("Scripture text", text)
        self.assertIn("Permission request: CCT / Augsburg Fortress", text)
        self.assertIn("Permission request: Concordia Publishing House", text)


if __name__ == "__main__":
    unittest.main()
