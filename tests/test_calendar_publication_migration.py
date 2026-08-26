"""Contract tests for provider-neutral calendar publication state."""

from pathlib import Path
import unittest


class CalendarPublicationMigrationTests(unittest.TestCase):
    def setUp(self):
        self.sql = Path("Migrations/116_add_calendar_publication_state.sql").read_text(encoding="utf-8")

    def test_binding_is_unique_and_source_is_indexed(self):
        self.assertIn("CREATE TABLE IF NOT EXISTS tblCalendarPublication", self.sql)
        self.assertIn("uq_calendar_publication_binding", self.sql)
        self.assertIn("ix_calendar_publication_source", self.sql)

    def test_credentials_and_event_text_are_not_stored(self):
        lowered = self.sql.casefold()
        for prohibited in ("oauth", "access_token", "refresh_token", "password", "description longtext"):
            self.assertNotIn(prohibited, lowered)

    def test_approved_source_and_result_values_are_constrained(self):
        for value in ("CHURCH_EVENT", "WORSHIP_SERVICE", "GROUP_MEETING", "PROJECT_MILESTONE"):
            self.assertIn(value, self.sql)
        for value in ("PENDING", "SUCCESS", "ERROR", "CANCELLED", "REMOVED"):
            self.assertIn(value, self.sql)


if __name__ == "__main__": unittest.main()
