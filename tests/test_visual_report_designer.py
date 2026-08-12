from pathlib import Path
import tempfile
import unittest

from visual_reports.designer import (
    ensure_user_definition, open_directory_designer, user_definition_directory,
    user_definition_path,
)


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
            self.assertEqual(first.parent, user_definition_directory(folder))

    def test_designer_requires_design_permission_before_opening(self):
        class DeniedAuthorization:
            def __init__(self):
                self.checked = []

            def require(self, permission, operation=None):
                self.checked.append(permission)
                raise PermissionError(permission)

        authorization = DeniedAuthorization()
        with self.assertRaises(PermissionError):
            open_directory_designer(authorization=authorization)
        self.assertEqual(authorization.checked, ["reports.design"])


if __name__ == "__main__":
    unittest.main()
