"""Safety tests for disposing of development worship-service records."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ClearTestWorshipServicesTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / "migrations" / "082_clear_test_worship_services.sql").read_text(
            encoding="utf-8"
        )

    def test_cleanup_is_hard_limited_to_churchdbtest(self):
        self.assertIn("IF LOWER(DATABASE()) = 'churchdbtest'", self.source)
        self.assertNotIn("DROP TABLE", self.source)

    def test_service_linked_attendance_and_services_are_cleared(self):
        self.assertIn("DELETE FROM tblAttendanceEvent", self.source)
        self.assertIn("WHERE ServiceID IS NOT NULL", self.source)
        self.assertIn("DELETE FROM tblService", self.source)


if __name__ == "__main__":
    unittest.main()
